"""Run the policy-free E15-B0 ``gamma_0`` calibration sweep.

The input contract supplies an experiment-independent base configuration plus
``gamma0_times_scope_width_candidates``. Each candidate is evaluated using the
same discarded seed and no policy forecast outcomes are created or persisted.
Selection remains an explicit predeclared geometry decision: gamma, then noise,
then horizon.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .run_e15b_a0 import run
except ImportError:  # pragma: no cover
    from run_e15b_a0 import run


def _candidate_summary(result: dict[str, Any], gamma: float) -> dict[str, Any]:
    evidence = result["scope_evidence_E_h"]
    # Keep only policy-free selection diagnostics prominent in the index. Full
    # candidate artifacts remain available for audit.
    noise_summary = {
        noise: {
            exposure: {metric: values[metric] for metric in ("q05", "median", "q95")}
            for exposure, values in exposures.items()
        }
        for noise, exposures in evidence.items()
    }
    unique = {
        exposure: metrics["unique_solutions"]["median"]
        for exposure, metrics in result["solver_geometry"].items()
    }
    return {
        "gamma0_times_scope_width": gamma,
        "status": result["status"],
        "accepted_tasks": result["accepted_tasks"],
        "attempts": result["attempts"],
        "E_h_q05_median_q95": noise_summary,
        "median_unique_scope_solutions": unique,
        "gates": result["gates"],
    }


def run_sweep(config: dict[str, Any]) -> dict[str, Any]:
    candidates = [float(value) for value in config.pop("gamma0_times_scope_width_candidates")]
    if not candidates or any(value <= 0.0 for value in candidates):
        raise ValueError("gamma0_times_scope_width_candidates must be nonempty and positive")
    if "gamma0_times_scope_width" in config:
        raise ValueError("sweep contract must not also fix gamma0_times_scope_width")
    candidate_results = []
    for gamma in candidates:
        candidate = dict(config)
        candidate["gamma0_times_scope_width"] = gamma
        candidate["contract_id"] = f'{config["contract_id"]}:gamma0Wh={gamma:g}'
        result = run(candidate)
        candidate_results.append({"summary": _candidate_summary(result, gamma), "artifact": result})
    return {
        "contract_id": config["contract_id"],
        "base_contract_sha256": hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "policy_outcomes_inspected": False,
        "selection_order": ["gamma0_times_scope_width", "noise_ratio", "far_horizon"],
        "candidate_results": candidate_results,
        "note": "No gamma candidate is selected automatically: the frozen evidence-overlap and solver-geometry rules must be applied before the next numerical stage.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run_sweep(json.loads(args.config.read_text()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
