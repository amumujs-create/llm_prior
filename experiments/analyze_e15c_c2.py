"""Frozen E15-C v1.1 C2 cellwise latent-task paired bootstrap.

This analysis opens only the evidence-weighted residual mixture minus uniform
residual-ensemble contrast.  It does not calculate closed-mechanism or
matched-free comparisons.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np


MIXTURE = "evidence_weighted_residual_mixture"
UNIFORM = "invariant_residual_ensemble"
EXPOSURES = ("low", "medium", "high")
BOOTSTRAP_REPLICATES = 5000
BOOTSTRAP_SEED = 151604


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    means = np.empty(BOOTSTRAP_REPLICATES)
    for start in range(0, BOOTSTRAP_REPLICATES, 100):
        end = min(start + 100, BOOTSTRAP_REPLICATES)
        indices = rng.integers(0, len(values), size=(end - start, len(values)))
        means[start:end] = values[indices].mean(axis=1)
    return tuple(float(value) for value in np.quantile(means, (0.025, 0.975)))


def run(rows_path: Path, out_path: Path) -> None:
    per_task: dict[str, dict[int, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    with rows_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row["policy"] in {MIXTURE, UNIFORM}:
                per_task[row["prefix_exposure"]][int(row["task_id"])][row["policy"]] = float(row["nrmse"])
    if set(per_task) != set(EXPOSURES):
        raise RuntimeError(f"unexpected C2 exposure set: {sorted(per_task)}")

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    rows_sha = sha256(rows_path)
    output = []
    for exposure in EXPOSURES:
        task_values = per_task[exposure]
        task_ids = sorted(task_values)
        if any(set(task_values[task_id]) != {MIXTURE, UNIFORM} for task_id in task_ids):
            raise RuntimeError(f"incomplete C2 pair: {exposure}")
        differences = np.asarray([
            task_values[task_id][MIXTURE] - task_values[task_id][UNIFORM]
            for task_id in task_ids
        ])
        ci_low, ci_high = bootstrap_ci(differences, rng)
        output.append({
            "prefix_exposure": exposure,
            "n_tasks": len(differences),
            "mean_C2": float(differences.mean()),
            "ci_2_5": ci_low,
            "ci_97_5": ci_high,
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "bootstrap_unit": "latent_task_id",
            "source_rows_sha256": rows_sha,
        })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.rows, args.out)
