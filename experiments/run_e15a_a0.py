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


LINEAR_LSTSQ_RCOND = 1e-12


def _profile_nll_and_condition(
    t: np.ndarray,
    y: np.ndarray,
    tau_grid: np.ndarray,
    s_fixed: float,
    kappa: float,
    sigma: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic linear profile for every onset hypothesis.

    At fixed `tau_k`, task-level fixed `s_0`, and fixed `kappa`, the smooth
    regime is linear in `(a,b)`.  There is intentionally no nonlinear optimizer or
    budget: `np.linalg.lstsq` with frozen `rcond` is the entire profile rule.
    """
    result: list[float] = []
    conditions: list[float] = []
    for tau in tau_grid:
        basis = t + kappa * s_fixed * _stable_softplus((t - tau) / s_fixed)
        design = np.column_stack((np.ones_like(t), basis))
        coefficients, *_ = np.linalg.lstsq(design, y, rcond=LINEAR_LSTSQ_RCOND)
        residual = (design @ coefficients - y) / sigma
        # The Gaussian constant is included for a genuine NLL, though it cancels
        # in the T=1 evidence weights.
        result.append(float(.5 * np.sum(residual**2) + len(t) * np.log(sigma * np.sqrt(2.0 * np.pi))))
        conditions.append(float(np.linalg.cond(design)))
    return np.asarray(result, dtype=float), np.asarray(conditions, dtype=float)


def _draw_task(
    rng: np.random.Generator,
    ranges: dict[str, tuple[float, float]],
    tau: float,
    s0: float,
    seed: int,
) -> CandidateTask:
    return CandidateTask(
        params=SmoothRegimeParams(
            a=float(rng.uniform(*ranges["a"])),
            b=float(rng.choice((-1.0, 1.0)) * rng.uniform(*ranges["b_magnitude"])),
            tau=tau,
            s=s0,
            kappa=float(ranges["kappa"]),
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
        "s0", "kappa", "noise_ratios", "horizon_after_onset_ratios",
        "noise_reference_horizon_after_onset_ratio",
        "min_reference_range", "min_post_onset_fraction", "slope_scale", "min_c_ratio",
        "max_normalized_slope", "max_design_condition",
    )
    support = A0SupportContract(
        *_pair(config["onset_domain"], "onset_domain"),
        *_pair(config["observation_domain"], "observation_domain"),
    )
    ranges = {
        "a": _pair(config["parameter_ranges"]["a"], "parameter_ranges.a"),
        "b_magnitude": _pair(config["parameter_ranges"]["b_magnitude"], "parameter_ranges.b_magnitude"),
        "kappa": float(config["kappa"]),
    }
    s0 = float(config["s0"])
    if not np.isfinite(s0) or s0 <= 0.0 or not np.isfinite(ranges["kappa"]):
        raise ValueError("s0 and kappa must be finite; s0 must be positive")
    noise_ratios = [float(x) for x in config["noise_ratios"]]
    horizons_after_onset = [float(x) * support.width for x in config["horizon_after_onset_ratios"]]
    noise_reference_horizon = float(config["noise_reference_horizon_after_onset_ratio"]) * support.width
    if not noise_ratios or not horizons_after_onset:
        raise ValueError("need nonempty noise and horizon candidates")
    if noise_reference_horizon not in horizons_after_onset:
        raise ValueError("noise_reference_horizon_after_onset_ratio must be a frozen candidate")
    if int(config["pilot_tasks"]) < 1 or int(config["max_attempts"]) < int(config["pilot_tasks"]):
        raise ValueError("invalid pilot_tasks/max_attempts")

    rng = np.random.default_rng(int(config["seed"]))
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
        task = _draw_task(rng, ranges, tau, s0, int(rng.integers(0, 2**32 - 1)))
        if abs(task.params.c) / float(config["slope_scale"]) <= float(config["min_c_ratio"]):
            reject["degenerate_regime_effect"] += 1
            continue
        grids = {
            horizon: np.linspace(
                support.observation_min, task.params.tau + horizon, int(config["eval_points"])
            )
            for horizon in horizons_after_onset
        }
        if not all(numerically_admissible(grid, task.params, float(config["min_reference_range"])) for grid in grids.values()):
            reject["nonfinite_or_degenerate_trajectory"] += 1
            continue
        accepted.append(task)

    evidence: dict[str, dict[str, list[float]]] = {
        str(noise): {level: [] for level in EXPOSURE_ENDPOINT_RATIOS} for noise in noise_ratios
    }
    design_condition = {
        str(noise): {level: [] for level in EXPOSURE_ENDPOINT_RATIOS} for noise in noise_ratios
    }
    horizon_audit = {
        str(horizon): {
            "post_onset_fraction": [], "reference_range": [], "normalized_max_slope": [],
            "post_onset_admissible": [], "slope_admissible": [], "finite": [],
        }
        for horizon in horizons_after_onset
    }
    for task in accepted:
        t_eval_by_horizon = {
            horizon: np.linspace(
                support.observation_min, task.params.tau + horizon, int(config["eval_points"])
            )
            for horizon in horizons_after_onset
        }
        for horizon, grid in t_eval_by_horizon.items():
            y = smooth_regime(grid, task.params)
            post_fraction = post_onset_fraction(grid, task.params.tau)
            max_abs_slope = float(np.max(np.abs(smooth_regime_slope(grid, task.params))))
            r_ref = reference_range(grid, task.params)
            normalized_max_slope = support.width * max_abs_slope / r_ref
            horizon_audit[str(horizon)]["post_onset_fraction"].append(post_fraction)
            horizon_audit[str(horizon)]["reference_range"].append(r_ref)
            horizon_audit[str(horizon)]["normalized_max_slope"].append(normalized_max_slope)
            horizon_audit[str(horizon)]["post_onset_admissible"].append(post_fraction >= float(config["min_post_onset_fraction"]))
            horizon_audit[str(horizon)]["slope_admissible"].append(normalized_max_slope <= float(config["max_normalized_slope"]))
            horizon_audit[str(horizon)]["finite"].append(bool(np.all(np.isfinite(y))))
        # The common full-domain onset grid makes E_tau independent of supplied I.
        for noise_ratio in noise_ratios:
            # Task-specific normalized SNR, fixed once per task/noise ratio and
            # shared across prefix exposures without candidate-horizon rescaling.
            sigma = noise_ratio * reference_range(
                t_eval_by_horizon[noise_reference_horizon], task.params
            )
            noise_rng = np.random.default_rng(task.seed)
            for level in EXPOSURE_ENDPOINT_RATIOS:
                endpoint = support.exposure_endpoint(task.params.tau, level)
                t_prefix = np.linspace(support.observation_min, endpoint, int(config["prefix_points"]))
                y_prefix = smooth_regime(t_prefix, task.params) + noise_rng.normal(0.0, sigma, size=t_prefix.size)
                losses, conditions = _profile_nll_and_condition(
                t_prefix, y_prefix, full_grid, task.params.s, task.params.kappa, sigma
            )
                evidence[str(noise_ratio)][level].append(onset_evidence_concentration(losses))
                design_condition[str(noise_ratio)][level].extend(conditions.tolist())

    horizon_summary = {}
    for key, audit in horizon_audit.items():
        horizon_summary[key] = {
            metric: _quantiles(values) for metric, values in audit.items()
            if metric in {"post_onset_fraction", "reference_range", "normalized_max_slope"}
        }
        horizon_summary[key]["fraction_post_onset_admissible"] = float(np.mean(audit["post_onset_admissible"]))
        horizon_summary[key]["fraction_slope_admissible"] = float(np.mean(audit["slope_admissible"]))
        horizon_summary[key]["fraction_finite"] = float(np.mean(audit["finite"]))
        horizon_summary[key]["all_admissible"] = bool(
            all(audit["post_onset_admissible"])
            and all(audit["slope_admissible"])
            and all(audit["finite"])
        )
    condition_summary = {}
    for noise, levels in design_condition.items():
        condition_summary[noise] = {}
        for level, values in levels.items():
            summary = _quantiles(values)
            condition_summary[noise][level] = {
                **summary,
                "max": float(np.max(values)) if values else None,
                "all_within_bound": bool(values and np.max(values) <= float(config["max_design_condition"])),
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
        "linear_profile_condition_number": condition_summary,
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
