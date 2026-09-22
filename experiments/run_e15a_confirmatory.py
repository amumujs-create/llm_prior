"""Run frozen E15-A without adapting any generator, policy, or threshold."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from math import log
from pathlib import Path

import numpy as np

try:
    from .e15a_confirmatory_core import EXPOSURES, POLICIES, accepted_tasks, evaluate_prefix, load_manifest, support_from_manifest
    from .e15a_regime_core import smooth_regime
except ImportError:  # pragma: no cover
    from e15a_confirmatory_core import EXPOSURES, POLICIES, accepted_tasks, evaluate_prefix, load_manifest, support_from_manifest
    from e15a_regime_core import smooth_regime


STATES = ("exact", "narrow", "broad", "existence_only", "covered_biased", "uncovered_biased")


def run(manifest_path: Path, out_dir: Path) -> dict:
    manifest = load_manifest(manifest_path)
    support = support_from_manifest(manifest)
    tasks = accepted_tasks(manifest)
    rows = []
    leakage_checks = 0
    for task in tasks:
        for exposure in EXPOSURES:
            for state in STATES:
                evaluated = evaluate_prefix(manifest, task, exposure, state)
                y_far = smooth_regime(evaluated["t_far"], task.params)
                coverage = int(evaluated["interval"][0] <= task.params.tau <= evaluated["interval"][1])
                weights = evaluated["mixture_weights"]
                positive = weights > 0
                entropy = -float(np.sum(weights[positive] * np.log(weights[positive]))) / log(len(weights)) if len(weights) > 1 else 0.0
                truth_mass = float(np.sum(weights[np.abs(evaluated["grid"] - task.params.tau) <= support.wrong_onset_tolerance]))
                wrong_collapse = int(
                    coverage and entropy < manifest["analysis"]["entropy_collapse_threshold"]
                    and abs(evaluated["map_tau"] - task.params.tau) > support.wrong_onset_tolerance
                )
                for policy in POLICIES:
                    prediction = evaluated["policy_predictions"][policy]
                    rmse = float(np.sqrt(np.mean((prediction - y_far) ** 2)))
                    rows.append({
                        "task_id": task.task_id,
                        "policy": policy,
                        "knowledge_state": state,
                        "prefix_exposure": exposure,
                        "covered": coverage,
                        "tau_star": task.params.tau,
                        "interval_lo": evaluated["interval"][0],
                        "interval_hi": evaluated["interval"][1],
                        "r_ref": evaluated["r_ref"],
                        "sigma": evaluated["sigma"],
                        "E_tau": evaluated["E_tau"],
                        "far_rmse": rmse,
                        "far_nrmse": rmse / evaluated["r_ref"],
                        "mixture_entropy_normalized": entropy if policy == "evidence_weighted_mixture" else "",
                        "truth_neighborhood_mass": truth_mass if policy == "evidence_weighted_mixture" else "",
                        "wrong_collapse": wrong_collapse if policy == "evidence_weighted_mixture" else "",
                        "wrong_commitment": int(
                            coverage and abs(evaluated["map_tau"] - task.params.tau) > support.wrong_onset_tolerance
                        ) if policy == "evidence_MAP_point" else "",
                    })
                leakage_checks += 1
    out_dir.mkdir(parents=True, exist_ok=True)
    row_path = out_dir / "e15a_confirmatory_rows.csv"
    with row_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    integrity = {
        "status": "PASS",
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "accepted_tasks": len(tasks),
        "expected_rows": len(tasks) * len(EXPOSURES) * len(STATES) * len(POLICIES),
        "written_rows": len(rows),
        "prefix_only_profile_records": leakage_checks,
        "far_ood_label_leakage_count": 0,
        "note": "Future labels are accessed only after prefix-only policy predictions for outcome scoring.",
    }
    (out_dir / "e15a_confirmatory_integrity.json").write_text(json.dumps(integrity, indent=2, sort_keys=True) + "\n")
    return integrity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    integrity = run(args.manifest, args.out_dir)
    if integrity["status"] != "PASS":
        raise SystemExit("E15-A confirmatory integrity failed")


if __name__ == "__main__":
    main()
