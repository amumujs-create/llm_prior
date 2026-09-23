"""Exact-state global-overextension stress analysis for frozen E15-B."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np


COMPARISONS = {"G_hard": "hard_global", "G_soft": "soft_global", "G_slack": "slack_distribution"}
LOCAL = "hard_local_MAP"
REPLICATES, SEED = 5000, 151606


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()


def ci(x: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    boot = np.empty(REPLICATES)
    for start in range(0, REPLICATES, 100):
        end = min(start + 100, REPLICATES)
        boot[start:end] = x[rng.integers(0, len(x), (end-start, len(x)))].mean(axis=1)
    return tuple(float(v) for v in np.quantile(boot, (.025, .975)))


def run(rows: Path, cellwise_out: Path, change_out: Path) -> None:
    raw: dict[tuple[str, int], dict[str, tuple[float, float, float]]] = defaultdict(dict)
    policies = set(COMPARISONS.values()) | {LOCAL}
    with rows.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["knowledge_state"] == "exact" and row["policy"] in policies:
                raw[(row["prefix_exposure"], int(row["task_id"]))][row["policy"]] = (float(row["within_nrmse"]), float(row["post_nrmse"]), float(row["post_scope_mode"]))
    grouped: dict[tuple[str, str, str], dict[int, tuple[float, float]]] = defaultdict(dict)
    for (exposure, task), policies_by_task in raw.items():
        if set(policies_by_task) != policies: raise RuntimeError("incomplete exact global-stress policy set")
        local = policies_by_task[LOCAL]
        mode = str(int(local[2]))
        for name, policy in COMPARISONS.items():
            candidate = policies_by_task[policy]
            delta = (candidate[0]-local[0], candidate[1]-local[1])
            grouped[(name, exposure, "all")][task] = delta
            grouped[(name, exposure, mode)][task] = delta
    rng, cellwise, changes = np.random.default_rng(SEED), [], []
    for (comparison, exposure, mode), values in sorted(grouped.items()):
        ids = sorted(values); within = np.asarray([values[i][0] for i in ids]); post = np.asarray([values[i][1] for i in ids])
        for window, vector in (("within_scope", within), ("post_scope", post)):
            lo, hi = ci(vector, rng)
            cellwise.append({"knowledge_state": "exact", "comparison": comparison, "prefix_exposure": exposure, "post_scope_mode": mode, "window": window, "n_tasks": len(vector), "mean_contrast": float(vector.mean()), "ci_2_5": lo, "ci_97_5": hi, "bootstrap_replicates": REPLICATES, "bootstrap_unit": "latent_task_id", "source_rows_sha256": sha(rows)})
        d = post-within; lo, hi = ci(d, rng)
        changes.append({"knowledge_state": "exact", "comparison": comparison, "prefix_exposure": exposure, "post_scope_mode": mode, "window_change": "post_minus_within", "n_tasks": len(d), "mean_change": float(d.mean()), "ci_2_5": lo, "ci_97_5": hi, "bootstrap_replicates": REPLICATES, "bootstrap_unit": "latent_task_id", "source_rows_sha256": sha(rows)})
    for path, output in ((cellwise_out, cellwise), (change_out, changes)):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(output[0])); w.writeheader(); w.writerows(output)


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--rows", type=Path, required=True); p.add_argument("--cellwise-out", type=Path, required=True); p.add_argument("--window-change-out", type=Path, required=True)
    a = p.parse_args(); run(a.rows, a.cellwise_out, a.window_change_out)
