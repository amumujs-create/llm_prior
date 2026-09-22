"""Predeclared E15-B D1 cellwise latent-task paired bootstrap."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np


MIXTURE = "evidence_weighted_scope_mixture"
MAP = "hard_local_MAP"
BOOTSTRAP_REPLICATES = 5000
BOOTSTRAP_SEED = 151602


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    n = len(values)
    means = np.empty(BOOTSTRAP_REPLICATES)
    for start in range(0, BOOTSTRAP_REPLICATES, 100):
        end = min(start + 100, BOOTSTRAP_REPLICATES)
        indices = rng.integers(0, n, size=(end - start, n))
        means[start:end] = values[indices].mean(axis=1)
    return tuple(float(x) for x in np.quantile(means, (.025, .975)))


def run(rows_path: Path, out_path: Path) -> None:
    values: dict[tuple[str, str], dict[int, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    with rows_path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["policy"] not in {MIXTURE, MAP}:
                continue
            values[(row["knowledge_state"], row["prefix_exposure"])][int(row["task_id"])][row["policy"]] = float(row["post_nrmse"])
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    output = []
    for (state, exposure), per_task in sorted(values.items()):
        ids = sorted(per_task)
        if any(set(per_task[task_id]) != {MIXTURE, MAP} for task_id in ids):
            raise RuntimeError(f"incomplete D1 pair: {state}/{exposure}")
        differences = np.asarray([per_task[task_id][MIXTURE] - per_task[task_id][MAP] for task_id in ids])
        ci_low, ci_high = bootstrap_ci(differences, rng)
        output.append({
            "knowledge_state": state,
            "prefix_exposure": exposure,
            "n_tasks": len(differences),
            "mean_D1": float(differences.mean()),
            "ci_2_5": ci_low,
            "ci_97_5": ci_high,
            "analysis_role": "equivalence_audit" if state == "exact" else ("validity_failure_stratum" if state == "uncovered_biased" else "covered_scope_result"),
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "bootstrap_unit": "latent_task_id",
            "source_rows_sha256": sha256(rows_path),
        })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.rows, args.out)


if __name__ == "__main__":
    main()
