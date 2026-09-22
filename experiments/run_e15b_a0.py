"""E15-B0 numerical/construct calibration without policy-outcome reporting.

This runner calibrates only the scope-precursor generator, full-domain ``E_h``
geometry, forecast-solver numerical behavior, and admissible evaluation windows.
It intentionally writes no policy forecasts, RMSE, CRPS, contrast, ranking, or
winner. Blinded D1/D2 variance calibration belongs in a separate protected
streaming adapter after this runner's generator contract is frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .e15b_scope_core import (
        ScopeTaskParams,
        actual_violation_horizon,
        clean_scope_slope,
        clean_scope_trajectory,
        fit_quadratic_with_direction_constraint,
        normalized_entropy_concentration,
        profile_scope_precursor,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from e15b_scope_core import (
        ScopeTaskParams,
        actual_violation_horizon,
        clean_scope_slope,
        clean_scope_trajectory,
        fit_quadratic_with_direction_constraint,
        normalized_entropy_concentration,
        profile_scope_precursor,
    )


EXPOSURES = ("low", "medium", "high")


@dataclass(frozen=True)
class CandidateTask:
    params: ScopeTaskParams
    seed: int


def _require(config: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in config]
    if missing:
        raise ValueError(f"E15-B0 contract missing required fields: {', '.join(missing)}")


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
    q = np.quantile(np.asarray(values, dtype=float), (.05, .25, .5, .75, .95))
    return {"n": len(values), "q05": float(q[0]), "q25": float(q[1]), "median": float(q[2]), "q75": float(q[3]), "q95": float(q[4])}


def _reference_range(t: np.ndarray, params: ScopeTaskParams) -> float:
    values = clean_scope_trajectory(t, params)
    result = float(np.max(values) - np.min(values))
    if not np.isfinite(result) or result <= 0.0:
        raise ValueError("nonpositive reference range")
    return result


def _draw_task(rng: np.random.Generator, config: dict[str, Any], h_star: float, mode: float) -> CandidateTask:
    ranges = config["parameter_ranges"]
    a_lo, a_hi = _pair(ranges["a"], "parameter_ranges.a")
    b_lo, b_hi = _pair(ranges["b"], "parameter_ranges.b")
    return CandidateTask(
        params=ScopeTaskParams(
            a=float(rng.uniform(a_lo, a_hi)),
            b=float(rng.uniform(b_lo, b_hi)),
            gamma=float(config["gamma0_times_scope_width"]) / float(config["scope_width"]),
            h_star=h_star,
            width=float(config["scope_width"]),
            post_scope_mode=mode,
        ),
        seed=int(rng.integers(0, 2**32 - 1)),
    )


def run(config: dict[str, Any]) -> dict[str, Any]:
    _require(
        config,
        "contract_id", "seed", "pilot_tasks", "max_attempts", "scope_domain", "observation_start",
        "scope_width", "support_margin_ratio", "parameter_ranges", "post_scope_modes", "prefix_points",
        "gamma0_times_scope_width",
        "eval_points", "exposure_offsets", "noise_ratios", "noise_reference_horizon_ratio",
        "horizon_after_scope_ratios", "far_start_after_scope_ratio", "scope_grid_points",
        "min_reference_range", "max_precursor_condition", "constraint_tolerance", "max_stationarity_residual",
        "min_window_points", "min_unique_scope_solutions", "max_normalized_slope",
    )
    h_min, h_max = _pair(config["scope_domain"], "scope_domain")
    width = float(config["scope_width"])
    if width <= 0.0 or not np.isfinite(width):
        raise ValueError("scope_width must be finite and positive")
    if not np.isfinite(float(config["gamma0_times_scope_width"])) or float(config["gamma0_times_scope_width"]) <= 0.0:
        raise ValueError("gamma0_times_scope_width must be finite and positive")
    expected_width = h_max - h_min
    if not np.isclose(width, expected_width, rtol=0.0, atol=1e-12):
        raise ValueError("scope_width must equal scope_domain width")
    exposure_offsets = {key: float(value) * width for key, value in config["exposure_offsets"].items()}
    if tuple(exposure_offsets) != EXPOSURES or any(value <= 0.0 for value in exposure_offsets.values()):
        raise ValueError("exposure_offsets must contain positive low/medium/high ratios in that order")
    modes = tuple(float(value) for value in config["post_scope_modes"])
    if not modes or not all(np.isfinite(modes)):
        raise ValueError("post_scope_modes must be a nonempty finite list")
    noise_ratios = tuple(float(value) for value in config["noise_ratios"])
    if not noise_ratios or any(value <= 0.0 for value in noise_ratios):
        raise ValueError("noise_ratios must be positive")
    horizon_ratios = tuple(float(value) for value in config["horizon_after_scope_ratios"])
    if not horizon_ratios or any(value <= 0.0 for value in horizon_ratios):
        raise ValueError("horizon_after_scope_ratios must be positive")
    noise_reference_ratio = float(config["noise_reference_horizon_ratio"])
    if noise_reference_ratio not in horizon_ratios:
        raise ValueError("noise_reference_horizon_ratio must be one of horizon_after_scope_ratios")
    far_start_ratio = float(config["far_start_after_scope_ratio"])
    if not 0.0 <= far_start_ratio < min(horizon_ratios):
        raise ValueError("far_start_after_scope_ratio must precede every horizon candidate")
    margin = float(config["support_margin_ratio"]) * width
    if margin <= 0.0 or h_min + margin >= h_max - margin:
        raise ValueError("support_margin_ratio leaves no unclipped true-scope interval")
    if float(config["observation_start"]) >= h_min + margin - max(exposure_offsets.values()):
        raise ValueError("observation_start must precede every possible low-exposure endpoint")
    if int(config["scope_grid_points"]) < 3:
        raise ValueError("scope_grid_points must be at least three")

    h_grid = np.linspace(h_min, h_max, int(config["scope_grid_points"]))
    rng = np.random.default_rng(int(config["seed"]))
    accepted: list[CandidateTask] = []
    rejections = Counter()
    rejections_by_mode: dict[str, Counter[str]] = defaultdict(Counter)
    attempts = 0
    largest_horizon = max(horizon_ratios) * width
    while len(accepted) < int(config["pilot_tasks"]) and attempts < int(config["max_attempts"]):
        attempts += 1
        h_star = float(rng.uniform(h_min + margin, h_max - margin))
        # Cycle proposals rather than accepted rows. A numerically inadmissible
        # first mode must not prevent the remaining post-scope modes from being
        # audited, and the resulting imbalance remains visible in the artifact.
        mode = modes[(attempts - 1) % len(modes)]
        task = _draw_task(rng, config, h_star, mode)
        far_end = h_star + largest_horizon
        eval_grid = np.linspace(float(config["observation_start"]), far_end, int(config["eval_points"]))
        values = clean_scope_trajectory(eval_grid, task.params)
        if not np.all(np.isfinite(values)):
            rejections["nonfinite_trajectory"] += 1
            rejections_by_mode[str(mode)]["nonfinite_trajectory"] += 1
            continue
        ref_grid = np.linspace(h_star + far_start_ratio * width, h_star + noise_reference_ratio * width, int(config["eval_points"]) + 1)[1:]
        try:
            r_ref = _reference_range(ref_grid, task.params)
        except ValueError:
            rejections["degenerate_reference_range"] += 1
            rejections_by_mode[str(mode)]["degenerate_reference_range"] += 1
            continue
        if r_ref < float(config["min_reference_range"]):
            rejections["reference_range_below_minimum"] += 1
            rejections_by_mode[str(mode)]["reference_range_below_minimum"] += 1
            continue
        slope_grid = np.linspace(float(config["observation_start"]), far_end, int(config["eval_points"]))
        normalized_max_slope = width * float(np.max(np.abs(clean_scope_slope(slope_grid, task.params)))) / r_ref
        if normalized_max_slope > float(config["max_normalized_slope"]):
            rejections["normalized_slope_above_maximum"] += 1
            rejections_by_mode[str(mode)]["normalized_slope_above_maximum"] += 1
            continue
        accepted.append(task)

    evidence: dict[str, dict[str, list[float]]] = {str(ratio): {exposure: [] for exposure in EXPOSURES} for ratio in noise_ratios}
    precursor_conditions: dict[str, dict[str, list[float]]] = {str(ratio): {exposure: [] for exposure in EXPOSURES} for ratio in noise_ratios}
    solver_geometry = {exposure: {"unique_solutions": [], "max_stationarity_residual": [], "min_constraint": []} for exposure in EXPOSURES}
    horizon_audit = {str(ratio): {"finite": [], "valid_points": [], "post_points": [], "normalized_max_slope": []} for ratio in horizon_ratios}
    mode_counts = Counter()
    violation_counts = Counter()

    for task in accepted:
        params = task.params
        mode_counts[str(params.post_scope_mode)] += 1
        standardized_noise = np.random.default_rng(task.seed).normal(0.0, 1.0, int(config["prefix_points"]))
        reference_grid = np.linspace(params.h_star + far_start_ratio * width, params.h_star + noise_reference_ratio * width, int(config["eval_points"]) + 1)[1:]
        r_ref = _reference_range(reference_grid, params)
        for horizon_ratio in horizon_ratios:
            h_far = params.h_star + horizon_ratio * width
            # The two oracle-scored windows are evaluated on their own frozen
            # grids; a coarse global grid must not erase the very short valid
            # window between the common high-prefix endpoint and h*.
            valid_grid = np.linspace(params.h_star - min(exposure_offsets.values()), params.h_star, int(config["eval_points"]) + 1)[1:]
            post_grid = np.linspace(params.h_star, h_far, int(config["eval_points"]) + 1)[1:]
            combined = np.concatenate((valid_grid, post_grid))
            max_slope = float(np.max(np.abs(clean_scope_slope(combined, params))))
            horizon_audit[str(horizon_ratio)]["finite"].append(bool(np.all(np.isfinite(clean_scope_trajectory(combined, params)))))
            horizon_audit[str(horizon_ratio)]["valid_points"].append(len(valid_grid))
            horizon_audit[str(horizon_ratio)]["post_points"].append(len(post_grid))
            horizon_audit[str(horizon_ratio)]["normalized_max_slope"].append(width * max_slope / r_ref)
        h_viol = actual_violation_horizon(params, params.h_star + largest_horizon)
        violation_counts["right_censored" if h_viol is None else "observed"] += 1

        for noise_ratio in noise_ratios:
            sigma = noise_ratio * r_ref
            for exposure, offset in exposure_offsets.items():
                endpoint = params.h_star - offset
                t_prefix = np.linspace(float(config["observation_start"]), endpoint, int(config["prefix_points"]))
                if np.any(clean_scope_slope(t_prefix, params) <= 0.0):
                    raise RuntimeError("prefix direction violation: generator contract broken")
                y_prefix = clean_scope_trajectory(t_prefix, params) + sigma * standardized_noise
                losses, conditions = profile_scope_precursor(t_prefix, y_prefix, h_grid, params.gamma, sigma)
                _, concentration = normalized_entropy_concentration(losses)
                evidence[str(noise_ratio)][exposure].append(concentration)
                precursor_conditions[str(noise_ratio)][exposure].extend(conditions.tolist())

                # Label-free forecast-solver geometry: how many different local
                # constraint solutions arise across scope hypotheses?
                eligible = h_grid[h_grid >= endpoint]
                coefficient_keys: set[tuple[float, float, float]] = set()
                fits = []
                for hypothesis in eligible:
                    fit = fit_quadratic_with_direction_constraint(t_prefix, y_prefix, float(hypothesis), tolerance=float(config["constraint_tolerance"]))
                    coefficient_keys.add(tuple(np.round(fit.coefficients, 10)))
                    fits.append(fit)
                solver_geometry[exposure]["unique_solutions"].append(float(len(coefficient_keys)))
                solver_geometry[exposure]["max_stationarity_residual"].append(float(max(fit.stationarity_residual for fit in fits)))
                solver_geometry[exposure]["min_constraint"].append(float(min(fit.min_constraint for fit in fits)))

    horizon_summary = {}
    for ratio, audit in horizon_audit.items():
        horizon_summary[ratio] = {metric: _quantiles(values) for metric, values in audit.items() if metric != "finite"}
        horizon_summary[ratio]["finite_rate"] = float(np.mean(audit["finite"])) if audit["finite"] else 0.0
        horizon_summary[ratio]["reference_range_pass"] = bool(
            all(value >= float(config["min_reference_range"]) for value in [_reference_range(np.linspace(task.params.h_star + far_start_ratio * width, task.params.h_star + noise_reference_ratio * width, int(config["eval_points"]) + 1)[1:], task.params) for task in accepted])
        )
        horizon_summary[ratio]["normalized_slope_pass"] = bool(
            all(value <= float(config["max_normalized_slope"]) for value in audit["normalized_max_slope"])
        )
        horizon_summary[ratio]["all_windows_supported"] = bool(
            all(value >= int(config["min_window_points"]) for value in audit["valid_points"] + audit["post_points"])
        )

    evidence_summary = {
        noise: {exposure: _quantiles(values) for exposure, values in by_exposure.items()}
        for noise, by_exposure in evidence.items()
    }
    condition_summary = {
        noise: {exposure: _quantiles(values) for exposure, values in by_exposure.items()}
        for noise, by_exposure in precursor_conditions.items()
    }
    solver_summary = {exposure: {metric: _quantiles(values) for metric, values in metrics.items()} for exposure, metrics in solver_geometry.items()}
    all_evidence_finite = all(
        all(np.all(np.isfinite(values)) for values in by_exposure.values())
        for by_exposure in evidence.values()
    )
    all_conditioned = all(
        all(max(values, default=np.inf) <= float(config["max_precursor_condition"]) for values in by_exposure.values())
        for by_exposure in precursor_conditions.values()
    )
    all_stationary = all(
        max(metrics["max_stationarity_residual"], default=np.inf) <= float(config["max_stationarity_residual"])
        for metrics in solver_geometry.values()
    )
    nondegenerate_scope_solutions = all(
        bool(metrics["unique_solutions"])
        and float(np.median(metrics["unique_solutions"])) >= float(config["min_unique_scope_solutions"])
        for metrics in solver_geometry.values()
    )
    modes_balanced = (
        len(mode_counts) == len(modes)
        and max(mode_counts.values(), default=0) - min(mode_counts.values(), default=0) <= 1
    )
    status = "PASS" if (
        len(accepted) == int(config["pilot_tasks"])
        and all_evidence_finite
        and all_conditioned
        and all_stationary
        and nondegenerate_scope_solutions
        and any(
            summary["all_windows_supported"] and summary["finite_rate"] == 1.0
            and summary["reference_range_pass"] and summary["normalized_slope_pass"]
            for summary in horizon_summary.values()
        )
        and modes_balanced
    ) else "FAIL"
    return {
        "status": status,
        "contract_id": config["contract_id"],
        "contract_sha256": hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "policy_outcomes_inspected": False,
        "accepted_tasks": len(accepted),
        "attempts": attempts,
        "acceptance_rate": len(accepted) / attempts if attempts else 0.0,
        "rejections": dict(sorted(rejections.items())),
        "rejections_by_post_scope_mode": {
            mode: dict(sorted(counts.items())) for mode, counts in sorted(rejections_by_mode.items())
        },
        "scope_evidence_E_h": evidence_summary,
        "precursor_condition_number": condition_summary,
        "solver_geometry": solver_summary,
        "horizon_audit": horizon_summary,
        "post_scope_mode_counts": dict(sorted(mode_counts.items())),
        "actual_violation_horizon": {"counts": dict(sorted(violation_counts.items())), "definition": "separate from h_star; right_censored means no observed violation through h_far"},
        "gates": {
            "prefix_direction_violation_count": 0,
            "full_domain_scope_evidence": True,
            "finite_scope_evidence": all_evidence_finite,
            "precursor_condition_pass": all_conditioned,
            "constraint_stationarity_pass": all_stationary,
            "nondegenerate_scope_solutions": nondegenerate_scope_solutions,
            "post_scope_modes_balanced": modes_balanced,
            "max_precursor_condition": float(config["max_precursor_condition"]),
            "constraint_tolerance": float(config["constraint_tolerance"]),
            "max_stationarity_residual": float(config["max_stationarity_residual"]),
            "min_window_points": int(config["min_window_points"]),
            "max_normalized_slope": float(config["max_normalized_slope"]),
        },
        "note": "This A0 artifact contains no policy forecast losses, policy contrasts, rankings, signs, or winners.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(json.loads(args.config.read_text()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if result["status"] != "PASS":
        raise SystemExit("E15-B0 did not reach its accepted-task quota")


if __name__ == "__main__":
    main()
