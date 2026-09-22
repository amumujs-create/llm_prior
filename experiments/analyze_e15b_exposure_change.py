"""Frozen task-paired exposure-change inference for E15-B D1/D2."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np


POLICY_PAIRS = {"D1": ("evidence_weighted_scope_mixture", "hard_local_MAP"), "D2": ("evidence_weighted_scope_mixture", "scope_hypothesis_ensemble")}
CONTRASTS = {"high_minus_low": ("high", "low", "primary"), "medium_minus_low": ("medium", "low", "secondary_diagnostic"), "high_minus_medium": ("high", "medium", "secondary_diagnostic")}
REPLICATES, SEED = 5000, 151604


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()


def ci(x: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    samples = np.empty(REPLICATES)
    for start in range(0, REPLICATES, 100):
        end = min(start + 100, REPLICATES)
        samples[start:end] = x[rng.integers(0, len(x), (end - start, len(x)))].mean(axis=1)
    return tuple(float(v) for v in np.quantile(samples, (.025, .975)))


def run(rows: Path, out: Path) -> None:
    source: dict[tuple[str, str, str, int], dict[str, float]] = defaultdict(dict)
    with rows.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["policy"] in {p for pair in POLICY_PAIRS.values() for p in pair}:
                source[(row["knowledge_state"], row["prefix_exposure"], row["policy"], int(row["task_id"]))]["nrmse"] = float(row["post_nrmse"])
    contrasts_by_metric: dict[tuple[str, str, int], dict[str, float]] = defaultdict(dict)
    for metric, (left, right) in POLICY_PAIRS.items():
        for (state, exposure, policy, task), v in source.items():
            if policy in {left, right}: contrasts_by_metric[(metric, state, task)].setdefault(exposure, {})[policy] = v["nrmse"]
    rng, output = np.random.default_rng(SEED), []
    for (metric, state, task), exposures in contrasts_by_metric.items():
        for exposure in tuple(exposures):
            if set(exposures[exposure]) != set(POLICY_PAIRS[metric]):
                raise RuntimeError("incomplete policy pair")
    grouped: dict[tuple[str, str], dict[int, dict[str, float]]] = defaultdict(dict)
    for key, exposure_values in contrasts_by_metric.items():
        metric, state, task = key
        grouped[(metric, state)][task] = {
            e: exposure_values[e][POLICY_PAIRS[metric][0]] - exposure_values[e][POLICY_PAIRS[metric][1]]
            for e in ("low", "medium", "high")
        }
    for (metric, state), tasks in sorted(grouped.items()):
        ids = sorted(tasks)
        for name, (later, earlier, role) in CONTRASTS.items():
            d = np.asarray([tasks[i][later] - tasks[i][earlier] for i in ids])
            lo, hi = ci(d, rng)
            output.append({"metric": metric, "knowledge_state": state, "exposure_change": name, "analysis_role": role if state not in {"exact", "uncovered_biased"} else ("equivalence_audit" if state == "exact" else "validity_failure_stratum"), "n_tasks": len(d), "mean_change": float(d.mean()), "ci_2_5": lo, "ci_97_5": hi, "bootstrap_replicates": REPLICATES, "bootstrap_unit": "latent_task_id", "source_rows_sha256": digest(rows)})
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(output[0])); w.writeheader(); w.writerows(output)


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--rows", type=Path, required=True); p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(); run(a.rows, a.out)
