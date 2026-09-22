"""Frozen cellwise paired bootstrap for E15-A primary contrast artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


PRIMARY_STATES = ("narrow", "broad", "existence_only", "covered_biased")
EXPOSURES = ("low", "medium", "high")
CONTRASTS = {
    "C1": ("evidence_weighted_mixture", "evidence_MAP_point"),
    "C2": ("evidence_weighted_mixture", "uniform_hypothesis_ensemble"),
    "C3": ("evidence_MAP_point", "hard_midpoint"),
}


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def run(base_path: Path, completion_path: Path, out_dir: Path) -> dict:
    base = _read(base_path)
    completion = _read(completion_path)
    comp = {(r["task_id"], r["policy"], r["knowledge_state"], r["prefix_exposure"]): r for r in completion}
    grouped: dict[tuple[str, str, str, str], dict[int, float]] = {}
    for row in base:
        state, exposure, policy = row["knowledge_state"], row["prefix_exposure"], row["policy"]
        if state not in PRIMARY_STATES or exposure not in EXPOSURES:
            continue
        key = (row["task_id"], policy, state, exposure)
        joined = comp[key]
        metrics = {"far_nrmse": float(row["far_nrmse"]), "far_ncrps": float(joined["far_ncrps"])}
        metrics.update({f"distance_bin_{i}_nrmse": float(joined[f"distance_bin_{i}_nrmse"]) for i in range(1, 4)})
        for metric, value in metrics.items():
            grouped.setdefault((metric, policy, state, exposure), {})[int(row["task_id"])] = value
    task_ids = np.arange(125)
    rng = np.random.default_rng(151503)
    bootstrap_indices = rng.integers(0, len(task_ids), size=(5000, len(task_ids)))
    results = []
    for contrast_id, (left, right) in CONTRASTS.items():
        metrics = ("far_nrmse", "far_ncrps") if contrast_id != "C1" else (
            "far_nrmse", "far_ncrps", "distance_bin_1_nrmse", "distance_bin_2_nrmse", "distance_bin_3_nrmse"
        )
        for state in PRIMARY_STATES:
            for exposure in EXPOSURES:
                for metric in metrics:
                    lhs, rhs = grouped[(metric, left, state, exposure)], grouped[(metric, right, state, exposure)]
                    if set(lhs) != set(task_ids) or set(rhs) != set(task_ids):
                        raise RuntimeError(f"incomplete paired support for {contrast_id}/{metric}/{state}/{exposure}")
                    delta = np.array([lhs[int(task)] - rhs[int(task)] for task in task_ids])
                    draws = delta[bootstrap_indices].mean(axis=1)
                    results.append({
                        "contrast": contrast_id,
                        "metric": metric,
                        "knowledge_state": state,
                        "prefix_exposure": exposure,
                        "n_tasks": len(delta),
                        "mean_paired_difference": float(delta.mean()),
                        "ci_2_5": float(np.quantile(draws, .025)),
                        "ci_97_5": float(np.quantile(draws, .975)),
                    })
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "e15a_cellwise_paired_bootstrap.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    summary = {
        "status": "PASS",
        "bootstrap_replicates": 5000,
        "bootstrap_seed": 151503,
        "resampling_unit": "latent task_id, paired within task",
        "CI": "cellwise percentile 95%; no familywise multiplicity claim",
        "base_rows_sha256": hashlib.sha256(base_path.read_bytes()).hexdigest(),
        "completion_rows_sha256": hashlib.sha256(completion_path.read_bytes()).hexdigest(),
        "result_row_count": len(results),
    }
    (out_dir / "e15a_cellwise_paired_bootstrap_integrity.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-rows", type=Path, required=True)
    parser.add_argument("--completion-rows", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.base_rows, args.completion_rows, args.out_dir)


if __name__ == "__main__":
    main()
