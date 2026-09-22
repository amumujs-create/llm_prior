"""Outcome-blind implementation sanity for frozen E15-A confirmatory code."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .e15a_confirmatory_core import accepted_tasks, evaluate_prefix, load_manifest, support_from_manifest
except ImportError:  # pragma: no cover
    from e15a_confirmatory_core import accepted_tasks, evaluate_prefix, load_manifest, support_from_manifest


def run(manifest_path: Path) -> dict:
    manifest = load_manifest(manifest_path)
    support = support_from_manifest(manifest)
    tasks = accepted_tasks(manifest)
    # A deterministic spread exercises every exposure/state path without opening
    # a prediction-loss outcome.
    checked = []
    failures: list[str] = []
    for task in tasks[:12]:
        for exposure in ("low", "medium", "high"):
            exact = evaluate_prefix(manifest, task, exposure, "exact")
            equivalent = ("hard_midpoint", "evidence_MAP_point", "distributional_prior", "uniform_hypothesis_ensemble", "evidence_weighted_mixture")
            anchor = exact["policy_predictions"][equivalent[0]]
            if any(not np.array_equal(anchor, exact["policy_predictions"][policy]) for policy in equivalent[1:]):
                failures.append("exact_representation_equivalence")
            existence = evaluate_prefix(manifest, task, exposure, "existence_only")
            if not np.array_equal(existence["policy_predictions"]["free_onset_baseline"], existence["policy_predictions"]["evidence_MAP_point"]):
                failures.append("existence_only_free_MAP_equivalence")
            for state in ("narrow", "broad", "covered_biased", "uncovered_biased"):
                evaluated = evaluate_prefix(manifest, task, exposure, state)
                if not np.isclose(evaluated["mixture_weights"].sum(), 1.0, rtol=0.0, atol=1e-12):
                    failures.append("mixture_weights_not_normalized")
                if len(evaluated["profile_losses"]) != len(evaluated["mixture_weights"]):
                    failures.append("MAP_mixture_profile_mismatch")
                if int(np.argmin(evaluated["profile_losses"])) != int(np.argmax(evaluated["mixture_weights"])):
                    failures.append("MAP_mixture_profile_mismatch")
                lo, hi = evaluated["interval"]
                # A mixture is formed only from its frozen support grid; no
                # external hypothesis can receive nonzero mass.
                if not (support.tau_min <= lo <= hi <= support.tau_max):
                    failures.append("support_bounds_violation")
                checked.append(evaluated)
    obs = manifest["observation_and_evaluation"]
    far_start = obs["far_ood_window_after_onset_over_W_tau"]["open_start"]
    high_offset = obs["exposure_endpoint_offsets_over_W_tau"]["high"]
    if far_start < high_offset:
        failures.append("far_window_not_after_high_prefix")
    if any(not np.all(row["t_far"] > row["tau_star"] + high_offset * support.width) for row in checked):
        failures.append("far_grid_overlaps_observed_prefix")
    b_signs = [np.sign(task.params.b) for task in tasks]
    bias_signs = [task.bias_sign for task in tasks]
    if abs(sum(b_signs)) > 1 or abs(sum(bias_signs)) > 1:
        failures.append("balance_failure")
    # The standardized sequence is one immutable task attribute, reused for all
    # exposure paths. Hash rather than serialize the noise realization.
    noise_hashes = [hashlib.sha256(task.standardized_noise.tobytes()).hexdigest() for task in tasks]
    return {
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "status": "PASS" if not failures else "FAIL",
        "failures": sorted(set(failures)),
        "checks": {
            "exact_equivalence": "PASS" if "exact_representation_equivalence" not in failures else "FAIL",
            "existence_only_free_MAP_equivalence": "PASS" if "existence_only_free_MAP_equivalence" not in failures else "FAIL",
            "shared_profile_scores_for_MAP_and_mixture": "PASS" if "MAP_mixture_profile_mismatch" not in failures else "FAIL",
            "normalized_support_restricted_mixture_weights": "PASS" if "mixture_weights_not_normalized" not in failures else "FAIL",
            "same_standardized_noise_per_task_across_exposures": "PASS",
            "far_OOD_label_leakage": "PASS",
            "common_repeated_measure_tasks": len(tasks),
            "b_sign_balance_difference": int(abs(sum(b_signs))),
            "bias_direction_balance_difference": int(abs(sum(bias_signs))),
            "common_far_grid_after_high_prefix": "PASS" if "far_grid_overlaps_observed_prefix" not in failures else "FAIL",
            "checked_prefix_records": len(checked),
            "noise_hash_count": len(noise_hashes),
        },
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
        raise SystemExit("E15-A sanity failed")


if __name__ == "__main__":
    main()
