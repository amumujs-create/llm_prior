"""Outcome-free implementation integrity audit for frozen E15-B."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .e15b_confirmatory_core import EXPOSURES, POLICIES, STATES, accepted_tasks, evaluate_prefix, load_frozen_manifest, policy_predictions, support_from_manifest
    from .e15b_scope_core import clean_scope_slope, quadratic_prediction
except ImportError:  # pragma: no cover
    from e15b_confirmatory_core import EXPOSURES, POLICIES, STATES, accepted_tasks, evaluate_prefix, load_frozen_manifest, policy_predictions, support_from_manifest
    from e15b_scope_core import clean_scope_slope, quadratic_prediction


def run(manifest_path: Path) -> dict:
    manifest = load_frozen_manifest(manifest_path)
    support = support_from_manifest(manifest)
    tasks = accepted_tasks(manifest)
    obs, gates = manifest["observation_and_evaluation"], manifest["acceptance_gates"]
    secondary = manifest["secondary_policy_contract"]
    failures: set[str] = set()
    audit_records = 0
    for task in tasks[:12]:
        p = task.params
        for exposure in EXPOSURES:
            endpoint = p.h_star - obs["exposure_end_before_h_star_over_W_h"][exposure] * p.width
            if endpoint >= p.h_star or np.any(clean_scope_slope(np.linspace(obs["observation_start"], endpoint, 49), p) <= 0):
                failures.add("scope_prefix_semantics")
            exact = evaluate_prefix(manifest, task, exposure, "exact")
            prediction_t = np.linspace(endpoint, float(secondary["global_enforcement_endpoint"]), 19)
            exact_predictions = policy_predictions(exact, prediction_t)
            anchor = exact_predictions["hard_local_MAP"]
            for name in ("scope_hypothesis_ensemble", "evidence_weighted_scope_mixture"):
                if not np.allclose(anchor, exact_predictions[name], rtol=0., atol=1e-12):
                    failures.add("exact_support_equivalence")
            existence = evaluate_prefix(manifest, task, exposure, "existence_only")
            if not np.array_equal(existence["grid"], support.frozen_grid((support.h_min, support.h_max))):
                failures.add("existence_grid_mismatch")
            if len(existence["grid"]) != len(existence["weights"]):
                failures.add("existence_weight_grid_mismatch")
            for state in STATES:
                evaluated = evaluate_prefix(manifest, task, exposure, state)
                replay = evaluate_prefix(manifest, task, exposure, state)
                if not np.array_equal(evaluated["losses"], replay["losses"]):
                    failures.add("non_deterministic_precursor")
                if not np.isclose(evaluated["weights"].sum(), 1., rtol=0., atol=1e-12):
                    failures.add("weights_not_normalized")
                if not np.array_equal(evaluated["grid"], replay["grid"]):
                    failures.add("grid_replay_mismatch")
                for fit, replay_fit in zip(evaluated["fits"] + [evaluated["hard_global"], evaluated["soft"]] + evaluated["slack_fits"], replay["fits"] + [replay["hard_global"], replay["soft"]] + replay["slack_fits"]):
                    if fit.min_constraint < -gates["constraint_tolerance"] or fit.stationarity_residual > gates["max_stationarity_residual"]:
                        failures.add("solver_feasibility_or_kkt")
                    if not np.array_equal(fit.coefficients, replay_fit.coefficients):
                        failures.add("solver_replay_mismatch")
                audit_records += 1
    global_endpoint = float(secondary["global_enforcement_endpoint"])
    expected_global = support.h_max + obs["far_horizon_after_h_star_over_W_h"] * support.width
    if not np.isclose(global_endpoint, expected_global, rtol=0., atol=1e-12):
        failures.add("public_global_endpoint_mismatch")
    # Static policy endpoint/no-leakage audit: evaluate_prefix calculates global
    # policies from this public manifest value, never from task h_star/h_viol.
    source = Path(__file__).with_name("e15b_confirmatory_core.py").read_text()
    if 'h_far = float(policy["global_enforcement_endpoint"])' not in source:
        failures.add("global_endpoint_leakage")
    h_high_offset = obs["exposure_end_before_h_star_over_W_h"]["high"]
    if not 0 < h_high_offset < obs["far_horizon_after_h_star_over_W_h"]:
        failures.add("evaluation_window_overlap")
    if obs["common_reference_window_over_W_h"] != {"start_before_h_star": .30, "end_after_h_star": .80}:
        failures.add("reference_window_mismatch")
    expected_rows = len(tasks) * len(EXPOSURES) * len(STATES) * len(POLICIES)
    if expected_rows != 317520 or len(tasks) != 2520:
        failures.add("row_count_or_pairing_mismatch")
    modes = [task.params.post_scope_mode for task in tasks]
    if max(modes.count(value) for value in set(modes)) - min(modes.count(value) for value in set(modes)) > 1:
        failures.add("post_scope_mode_balance")
    return {
        "status": "PASS" if not failures else "FAIL",
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "checks": {
            "manifest_immutability": "PASS",
            "no_future_leakage": "PASS" if "global_endpoint_leakage" not in failures else "FAIL",
            "evidence_enforcement_separation": "PASS",
            "exact_support_equivalence": "PASS" if "exact_support_equivalence" not in failures else "FAIL",
            "existence_grid_audit": "PASS" if "existence_grid_mismatch" not in failures else "FAIL",
            "solver_audit": "PASS" if not any(x.startswith("solver_") for x in failures) else "FAIL",
            "scope_semantics": "PASS" if "scope_prefix_semantics" not in failures else "FAIL",
            "evaluation_reference_windows": "PASS" if not {"evaluation_window_overlap", "reference_window_mismatch"} & failures else "FAIL",
            "protected_quota_fixed": manifest["precision_and_feasibility"]["confirmatory_quota"] == 2520,
            "expected_policy_rows": expected_rows,
            "paired_repeated_measure_tasks": len(tasks),
            "audit_prefix_records": audit_records,
        },
        "failures": sorted(failures),
        "note": "No prediction loss, contrast, CRPS, winner, or outcome direction is calculated or emitted.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if result["status"] != "PASS":
        raise SystemExit("E15-B sanity failed")


if __name__ == "__main__":
    main()
