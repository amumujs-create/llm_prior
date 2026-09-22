"""E15-A0: discarded-seed design calibration without policy-outcome reporting.

The runner intentionally does *not* construct forecasts, RMSE, CRPS, policy
rankings, contrast means/signs, collapse rates, or winners.  It calibrates only
generator feasibility, prefix evidence geometry, horizon admissibility,
profile-likelihood numerical convergence, and (optionally) blinded contrast
dispersion supplied by a separate protected loss adapter.

Run with an explicit JSON contract; there are no scientific default values.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import least_squares

try:  # Supports both `python experiments/run_e15a_a0.py` and `python -m ...`.
    from .e15a_a0_contract import (
        A0SupportContract,
        BlindedContrastAccumulator,
        EXPOSURE_ENDPOINT_RATIOS,
        onset_evidence_concentration,
    )
    from .e15a_regime_core import (
        SmoothRegimeParams,
        numerically_admissible,
        post_onset_fraction,
        reference_range,
        smooth_regime,
        smooth_regime_slope,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from e15a_a0_contract import (
        A0SupportContract,
        BlindedContrastAccumulator,
        EXPOSURE_ENDPOINT_RATIOS,
        onset_evidence_concentration,
    )
    from e15a_regime_core import (
        SmoothRegimeParams,
        numerically_admissible,
        post_onset_fraction,
        reference_range,
        smooth_regime,
        smooth_regime_slope,
    )


@dataclass(frozen=True)
class CandidateTask:
    params: SmoothRegimeParams
    seed: int


def _require(config: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in config]
    if missing:
        raise ValueError(f"A0 contract missing required fields: {', '.join(missing)}")


def _pair(value: Any, name: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{name} must be a two-element list")
    lo, hi = map(float, value)
    if not lo < hi:
        raise ValueError(f"{name} must have lower < upper")
    return lo, hi


def _quantiles(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "q05": None, "q25": None, "median": None, "q75": None, "q95": None}
    q = np.quantile(np.asarray(values, dtype=float), [.05, .25, .5, .75, .95])
    return {
        "n": len(values),
        "q05": float(q[0]),
        "q25": float(q[1]),
        "median": float(q[2]),
        "q75": float(q[3]),
        "q95": float(q[4]),
    }


def _stable_softplus(x: np.ndarray) -> np.ndarray:
    return np.maximum(x, 0.0) + np.log1p(np.exp(-np.abs(x)))


def _profile_nll(
    t: np.ndarray,
    y: np.ndarray,
    tau_grid: np.ndarray,
    s_fixed: float,
    sigma: float,
    nuisance_bounds: dict[str, tuple[float, float]],
    max_nfev: int,
) -> np.ndarray:
    """Common profiled `ell_k=min_phi NLL(...)` used by MAP and mixture later."""
    lower = np.array([nuisance_bounds[key][0] for key in ("a", "b", "c")])
    upper = np.array([nuisance_bounds[key][1] for key in ("a", "b", "c")])
    start = (lower + upper) / 2.0
    result: list[float] = []
    for tau in tau_grid:
        transition = s_fixed * _stable_softplus((t - tau) / s_fixed)

        def residual(phi: np.ndarray) -> np.ndarray:
            return (phi[0] + phi[1] * t + phi[2] * transition - y) / sigma

        fit = least_squares(residual, start, bounds=(lower, upper), max_nfev=max_nfev)
        # The Gaussian constant is included for a genuine NLL, though it cancels
        # in the T=1 evidence weights.
        result.append(float(.5 * np.sum(fit.fun**2) + len(t) * np.log(sigma * np.sqrt(2.0 * np.pi))))
    return np.asarray(result, dtype=float)


def _draw_task(
    rng: np.random.Generator, ranges: dict[str, tuple[float, float]], tau: float, seed: int
) -> CandidateTask:
    return CandidateTask(
        params=SmoothRegimeParams(
            a=float(rng.uniform(*ranges["a"])),
            b=float(rng.uniform(*ranges["b"])),
            c=float(rng.uniform(*ranges["c"])),
            tau=tau,
            s=float(rng.uniform(*ranges["s"])),
        ),
        seed=seed,
    )


def _read_blinded_contrasts(
    path: Path, target_half_width: float, minimum_quota: int, required_cells: list[str] | None
) -> dict[str, Any]:
    """Consume raw protected input once; emit only dispersion/quota summaries.

    Expected CSV fields: `cell_id`, `contrast_id`, `value`.  Raw values are not
    retained or emitted by this runner.
    """
    groups: dict[tuple[str, str], BlindedContrastAccumulator] = defaultdict(BlindedContrastAccumulator)
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            groups[(row["cell_id"], row["contrast_id"])].update(float(row["value"]))
    output: dict[str, dict[str, float | int]] = {}
    for (cell_id, contrast_id), accumulator in sorted(groups.items()):
        summary = accumulator.summary(target_half_width, minimum_quota)
        output[f"{cell_id}::{contrast_id}"] = {
            "n_pilot_tasks": summary.n_tasks,
            "paired_sd": summary.paired_sd,
            "paired_sd_upper_95": summary.paired_sd_upper_95,
            "required_quota": summary.normal_approx_required_tasks,
        }
    required = required_cells or sorted(output)
    missing = sorted(set(required) - set(output))
    if missing:
        raise ValueError(f"missing blinded quota cells: {missing}")
    return {
        "by_primary_cell_contrast": output,
        "required_confirmatory_quota": max(output[key]["required_quota"] for key in required),
        "primary_cells_used": required,
    }


def run(config: dict[str, Any], blinded_contrast_csv: Path | None = None) -> dict[str, Any]:
    _require(
        config,
        "contract_id", "seed", "pilot_tasks", "max_attempts", "onset_domain",
        "observation_domain", "prefix_points", "eval_points", "parameter_ranges",
        "nuisance_bounds", "noise_ratios", "horizon_candidates", "optimizer_budgets",
        "min_reference_range", "min_post_onset_fraction", "slope_scale", "min_c_ratio",
        "max_abs_slope", "profile_convergence",
    )
    support = A0SupportContract(
        *_pair(config["onset_domain"], "onset_domain"),
        *_pair(config["observation_domain"], "observation_domain"),
    )
    ranges = {key: _pair(config["parameter_ranges"][key], f"parameter_ranges.{key}") for key in ("a", "b", "c", "s")}
    nuisance_bounds = {key: _pair(config["nuisance_bounds"][key], f"nuisance_bounds.{key}") for key in ("a", "b", "c")}
    noise_ratios = [float(x) for x in config["noise_ratios"]]
    horizons = [float(x) for x in config["horizon_candidates"]]
    budgets = sorted({int(x) for x in config["optimizer_budgets"]})
    if not noise_ratios or not horizons or len(budgets) < 2 or min(budgets) < 1:
        raise ValueError("need nonempty noise/horizon candidates and at least two positive budgets")
    profile_gate = config["profile_convergence"]
    _require(profile_gate, "relative_nll_max", "evidence_delta_max", "map_agreement_min")
    if int(config["pilot_tasks"]) < 1 or int(config["max_attempts"]) < int(config["pilot_tasks"]):
        raise ValueError("invalid pilot_tasks/max_attempts")

    rng = np.random.default_rng(int(config["seed"]))
    t_eval_by_horizon = {
        horizon: np.linspace(support.observation_min, horizon, int(config["eval_points"]))
        for horizon in horizons
    }
    full_grid = support.frozen_grid((support.tau_min, support.tau_max))
    accepted: list[CandidateTask] = []
    reject = Counter()
    attempts = 0
    while len(accepted) < int(config["pilot_tasks"]) and attempts < int(config["max_attempts"]):
        attempts += 1
        tau = float(rng.uniform(support.tau_min, support.tau_max))
        if not support.accepts_true_onset(tau):
            reject["support_or_exposure_boundary"] += 1
            continue
        task = _draw_task(rng, ranges, tau, int(rng.integers(0, 2**32 - 1)))
        if abs(task.params.c) / float(config["slope_scale"]) <= float(config["min_c_ratio"]):
            reject["degenerate_regime_effect"] += 1
            continue
        if not all(numerically_admissible(grid, task.params, float(config["min_reference_range"])) for grid in t_eval_by_horizon.values()):
            reject["nonfinite_or_degenerate_trajectory"] += 1
            continue
        accepted.append(task)

    evidence: dict[str, dict[str, list[float]]] = {
        str(noise): {level: [] for level in EXPOSURE_ENDPOINT_RATIOS} for noise in noise_ratios
    }
    optimizer = {
        str(noise): {level: [] for level in EXPOSURE_ENDPOINT_RATIOS} for noise in noise_ratios
    }
    horizon_audit = {
        str(horizon): {
            "post_onset_fraction": [], "reference_range": [], "max_abs_slope": [],
            "post_onset_admissible": [], "slope_admissible": [], "finite": [],
        }
        for horizon in horizons
    }
    for task in accepted:
        for horizon, grid in t_eval_by_horizon.items():
            y = smooth_regime(grid, task.params)
            post_fraction = post_onset_fraction(grid, task.params.tau)
            max_abs_slope = float(np.max(np.abs(smooth_regime_slope(grid, task.params))))
            horizon_audit[str(horizon)]["post_onset_fraction"].append(post_fraction)
            horizon_audit[str(horizon)]["reference_range"].append(reference_range(grid, task.params))
            horizon_audit[str(horizon)]["max_abs_slope"].append(max_abs_slope)
            horizon_audit[str(horizon)]["post_onset_admissible"].append(post_fraction >= float(config["min_post_onset_fraction"]))
            horizon_audit[str(horizon)]["slope_admissible"].append(max_abs_slope <= float(config["max_abs_slope"]))
            horizon_audit[str(horizon)]["finite"].append(bool(np.all(np.isfinite(y))))
        # The common full-domain onset grid makes E_tau independent of supplied I.
        for noise_ratio in noise_ratios:
            sigma = noise_ratio * reference_range(t_eval_by_horizon[horizons[-1]], task.params)
            noise_rng = np.random.default_rng(task.seed)
            for level in EXPOSURE_ENDPOINT_RATIOS:
                endpoint = support.exposure_endpoint(task.params.tau, level)
                t_prefix = np.linspace(support.observation_min, endpoint, int(config["prefix_points"]))
                y_prefix = smooth_regime(t_prefix, task.params) + noise_rng.normal(0.0, sigma, size=t_prefix.size)
                losses_by_budget = {
                    budget: _profile_nll(t_prefix, y_prefix, full_grid, task.params.s, sigma, nuisance_bounds, budget)
                    for budget in budgets
                }
                final_losses = losses_by_budget[budgets[-1]]
                evidence[str(noise_ratio)][level].append(onset_evidence_concentration(final_losses))
                for lo, hi in zip(budgets[:-1], budgets[1:]):
                    loss_lo, loss_hi = losses_by_budget[lo], losses_by_budget[hi]
                    relative = float(np.max(np.abs(loss_hi - loss_lo) / (1.0 + np.abs(loss_hi))))
                    optimizer[str(noise_ratio)][level].append({
                        "from_budget": lo,
                        "to_budget": hi,
                        "relative_nll_change": relative,
                        "evidence_delta": abs(onset_evidence_concentration(loss_hi) - onset_evidence_concentration(loss_lo)),
                        "map_agreement": int(np.argmin(loss_hi) == np.argmin(loss_lo)),
                    })

    horizon_summary = {}
    for key, audit in horizon_audit.items():
        horizon_summary[key] = {
            metric: _quantiles(values) for metric, values in audit.items()
            if metric in {"post_onset_fraction", "reference_range", "max_abs_slope"}
        }
        horizon_summary[key]["fraction_post_onset_admissible"] = float(np.mean(audit["post_onset_admissible"]))
        horizon_summary[key]["fraction_slope_admissible"] = float(np.mean(audit["slope_admissible"]))
        horizon_summary[key]["fraction_finite"] = float(np.mean(audit["finite"]))
        horizon_summary[key]["all_admissible"] = bool(
            all(audit["post_onset_admissible"])
            and all(audit["slope_admissible"])
            and all(audit["finite"])
        )
    convergence_summary: dict[str, dict[str, dict[str, float | int | bool]]] = {}
    for noise, levels in optimizer.items():
        convergence_summary[noise] = {}
        for level, rows in levels.items():
            if not rows:
                convergence_summary[noise][level] = {"n": 0, "passed": False}
                continue
            rel = [row["relative_nll_change"] for row in rows]
            delta_e = [row["evidence_delta"] for row in rows]
            agreement = float(np.mean([row["map_agreement"] for row in rows]))
            convergence_summary[noise][level] = {
                "n": len(rows),
                "relative_nll_change_q95": float(np.quantile(rel, .95)),
                "evidence_delta_q95": float(np.quantile(delta_e, .95)),
                "map_agreement_rate": agreement,
                "passed": bool(
                    np.quantile(rel, .95) <= float(profile_gate["relative_nll_max"])
                    and np.quantile(delta_e, .95) <= float(profile_gate["evidence_delta_max"])
                    and agreement >= float(profile_gate["map_agreement_min"])
                ),
            }

    quota = None
    if blinded_contrast_csv is not None:
        _require(config, "target_ci_half_width", "minimum_confirmatory_quota")
        quota = _read_blinded_contrasts(
            blinded_contrast_csv,
            float(config["target_ci_half_width"]),
            int(config["minimum_confirmatory_quota"]),
            config.get("primary_quota_cells"),
        )
    return {
        "contract_id": config["contract_id"],
        "runner": "E15-A0 numerical calibration only; no policy-outcome metrics emitted",
        "generated_attempts": attempts,
        "accepted_tasks": len(accepted),
        "rejection_counts": dict(sorted(reject.items())),
        "all_requested_tasks_accepted": len(accepted) == int(config["pilot_tasks"]),
        "evidence_geometry": {noise: {level: _quantiles(values) for level, values in levels.items()} for noise, levels in evidence.items()},
        "horizon_admissibility": horizon_summary,
        "optimizer_convergence": convergence_summary,
        "blinded_quota_calibration": quota,
        "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--blinded-contrast-csv", type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    result = run(config, args.blinded_contrast_csv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
