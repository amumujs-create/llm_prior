"""Predeclared E15-B D2 cellwise latent-task paired bootstrap."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np


MIXTURE = "evidence_weighted_scope_mixture"
UNIFORM = "scope_hypothesis_ensemble"
BOOTSTRAP_REPLICATES = 5000
BOOTSTRAP_SEED = 151603


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    means = np.empty(BOOTSTRAP_REPLICATES)
    for start in range(0, BOOTSTRAP_REPLICATES, 100):
        end = min(start + 100, BOOTSTRAP_REPLICATES)
        means[start:end] = values[rng.integers(0, len(values), size=(end - start, len(values)))].mean(axis=1)
    return tuple(float(x) for x in np.quantile(means, (.025, .975)))


def run(rows_path: Path, out_path: Path) -> None:
    cells: dict[tuple[str, str], dict[int, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    with rows_path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["policy"] in {MIXTURE, UNIFORM}:
                cells[(row["knowledge_state"], row["prefix_exposure"])][int(row["task_id"])][row["policy"]] = float(row["post_nrmse"])
    rng, output = np.random.default_rng(BOOTSTRAP_SEED), []
    for (state, exposure), by_task in sorted(cells.items()):
        ids = sorted(by_task)
        if any(set(by_task[i]) != {MIXTURE, UNIFORM} for i in ids):
            raise RuntimeError(f"incomplete D2 pair: {state}/{exposure}")
        d = np.asarray([by_task[i][MIXTURE] - by_task[i][UNIFORM] for i in ids])
        lo, hi = bootstrap_ci(d, rng)
        output.append({"knowledge_state": state, "prefix_exposure": exposure, "n_tasks": len(d), "mean_D2": float(d.mean()), "ci_2_5": lo, "ci_97_5": hi, "analysis_role": "equivalence_audit" if state == "exact" else ("validity_failure_stratum" if state == "uncovered_biased" else "covered_scope_result"), "bootstrap_replicates": BOOTSTRAP_REPLICATES, "bootstrap_unit": "latent_task_id", "source_rows_sha256": sha256(rows_path)})
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]))
        writer.writeheader(); writer.writerows(output)


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--rows", type=Path, required=True); p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(); run(a.rows, a.out)
