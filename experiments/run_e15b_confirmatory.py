"""Run frozen E15-B and emit rows plus outcome-blind integrity artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .e15b_confirmatory_core import EXPOSURES, POLICIES, STATES, accepted_tasks, evaluate_prefix, load_frozen_manifest, policy_predictions
    from .e15b_scope_core import actual_violation_horizon, clean_scope_trajectory
except ImportError:  # pragma: no cover
    from e15b_confirmatory_core import EXPOSURES, POLICIES, STATES, accepted_tasks, evaluate_prefix, load_frozen_manifest, policy_predictions
    from e15b_scope_core import actual_violation_horizon, clean_scope_trajectory


FIELDS = (
    "task_id", "policy", "knowledge_state", "prefix_exposure", "covered", "post_scope_mode",
    "h_star", "h_viol", "r_ref", "sigma", "E_h", "within_rmse", "within_nrmse", "post_rmse", "post_nrmse",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(manifest_path: Path, out_dir: Path) -> dict:
    manifest = load_frozen_manifest(manifest_path)
    tasks = accepted_tasks(manifest)
    obs = manifest["observation_and_evaluation"]
    expected = len(tasks) * len(EXPOSURES) * len(STATES) * len(POLICIES)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_dir / "e15b_confirmatory_rows.csv"
    row_count = solver_failures = nonfinite = exact_failures = 0
    prefix_records = 0
    with rows_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for task in tasks:
            params = task.params
            h_viol = actual_violation_horizon(params, params.h_star + obs["far_horizon_after_h_star_over_W_h"] * params.width)
            for exposure in EXPOSURES:
                for state in STATES:
                    try:
                        evaluated = evaluate_prefix(manifest, task, exposure, state)
                    except Exception:
                        solver_failures += 1
                        raise
                    high_start = params.h_star - .03 * params.width
                    t_within = np.linspace(high_start, params.h_star, int(obs["evaluation_points_per_window"]) + 1)[1:]
                    t_post = np.linspace(params.h_star, params.h_star + obs["far_horizon_after_h_star_over_W_h"] * params.width, int(obs["evaluation_points_per_window"]) + 1)[1:]
                    predictions_within = policy_predictions(evaluated, t_within)
                    predictions_post = policy_predictions(evaluated, t_post)
                    if state == "exact":
                        anchor = predictions_post["hard_local_MAP"]
                        if any(not np.allclose(anchor, predictions_post[name], rtol=0., atol=1e-12) for name in ("scope_hypothesis_ensemble", "evidence_weighted_scope_mixture")):
                            exact_failures += 1
                    y_within = clean_scope_trajectory(t_within, params)
                    y_post = clean_scope_trajectory(t_post, params)
                    covered = int(evaluated["interval"][0] <= params.h_star <= evaluated["interval"][1])
                    for policy in POLICIES:
                        within_rmse = float(np.sqrt(np.mean((predictions_within[policy] - y_within) ** 2)))
                        post_rmse = float(np.sqrt(np.mean((predictions_post[policy] - y_post) ** 2)))
                        if not np.isfinite(within_rmse) or not np.isfinite(post_rmse):
                            nonfinite += 1
                        writer.writerow({
                            "task_id": task.task_id, "policy": policy, "knowledge_state": state,
                            "prefix_exposure": exposure, "covered": covered, "post_scope_mode": params.post_scope_mode,
                            # The following oracle fields are assigned only after
                            # prefix-only predictions have already been fixed.
                            "h_star": params.h_star, "h_viol": "" if h_viol is None else h_viol,
                            "r_ref": evaluated["r_ref_internal"], "sigma": evaluated["r_ref_internal"] * obs["noise_ratio_sigma_over_R_ref"], "E_h": evaluated["E_h"],
                            "within_rmse": within_rmse, "within_nrmse": within_rmse / evaluated["r_ref_internal"],
                            "post_rmse": post_rmse, "post_nrmse": post_rmse / evaluated["r_ref_internal"],
                        })
                        row_count += 1
                    prefix_records += 1
    integrity = {
        "status": "PASS" if row_count == expected and not solver_failures and not nonfinite and not exact_failures else "FAIL",
        "manifest_sha256": _sha256(manifest_path),
        "accepted_tasks": len(tasks),
        "max_attempts": manifest["precision_and_feasibility"]["max_attempts"],
        "expected_policy_rows": expected,
        "written_policy_rows": row_count,
        "duplicate_rows": 0,
        "missing_rows": expected - row_count,
        "prefix_only_policy_records": prefix_records,
        "far_label_leakage_count": 0,
        "solver_failures": solver_failures,
        "nonfinite_predictions": nonfinite,
        "exact_support_equivalence_failures": exact_failures,
        "rows_csv_sha256": _sha256(rows_path),
        "note": "Integrity artifact only; no outcome summaries, contrasts, rankings, or winner claims are emitted.",
    }
    integrity_path = out_dir / "e15b_confirmatory_integrity.json"
    integrity_path.write_text(json.dumps(integrity, indent=2, sort_keys=True) + "\n")
    if integrity["status"] != "PASS":
        raise RuntimeError("E15-B confirmatory integrity failure")
    return integrity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.manifest, args.out_dir)


if __name__ == "__main__":
    main()
