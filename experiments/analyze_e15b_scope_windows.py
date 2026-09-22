"""Frozen E15-B within/post-scope decomposition for D1 and D2."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np


PAIRS = {"D1": ("evidence_weighted_scope_mixture", "hard_local_MAP"), "D2": ("evidence_weighted_scope_mixture", "scope_hypothesis_ensemble")}
REPLICATES, SEED = 5000, 151605


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()


def bootstrap(x: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    out = np.empty(REPLICATES)
    for start in range(0, REPLICATES, 100):
        end = min(start + 100, REPLICATES)
        out[start:end] = x[rng.integers(0, len(x), (end-start, len(x)))].mean(axis=1)
    return tuple(float(v) for v in np.quantile(out, (.025, .975)))


def run(rows: Path, cellwise_out: Path, window_change_out: Path) -> None:
    raw: dict[tuple[str, str, str, int], dict[str, tuple[float, float]]] = defaultdict(dict)
    all_policies = {p for pair in PAIRS.values() for p in pair}
    with rows.open(newline="") as f:
        for r in csv.DictReader(f):
            if r["policy"] in all_policies:
                raw[(r["knowledge_state"], r["prefix_exposure"], r["policy"], int(r["task_id"]))]["value"] = (float(r["within_nrmse"]), float(r["post_nrmse"]))
    values: dict[tuple[str, str, str], dict[int, tuple[float, float]]] = defaultdict(dict)
    for metric, (left, right) in PAIRS.items():
        states = {(s, e, t) for s, e, p, t in raw if p in {left, right}}
        for state, exposure, task in sorted(states):
            l = raw[(state, exposure, left, task)].get("value")
            r = raw[(state, exposure, right, task)].get("value")
            if l is None or r is None: raise RuntimeError("incomplete window pair")
            values[(metric, state, exposure)][task] = (l[0] - r[0], l[1] - r[1])
    rng, cellwise, changes = np.random.default_rng(SEED), [], []
    for (metric, state, exposure), by_task in sorted(values.items()):
        ids = sorted(by_task)
        within = np.asarray([by_task[i][0] for i in ids]); post = np.asarray([by_task[i][1] for i in ids])
        for window, vector in (("within_scope", within), ("post_scope", post)):
            lo, hi = bootstrap(vector, rng)
            cellwise.append({"metric": metric, "knowledge_state": state, "prefix_exposure": exposure, "window": window, "n_tasks": len(vector), "mean_contrast": float(vector.mean()), "ci_2_5": lo, "ci_97_5": hi, "analysis_role": "equivalence_audit" if state == "exact" else ("validity_failure_stratum" if state == "uncovered_biased" else "covered_scope_result"), "bootstrap_replicates": REPLICATES, "bootstrap_unit": "latent_task_id", "source_rows_sha256": sha(rows)})
        delta = post - within; lo, hi = bootstrap(delta, rng)
        changes.append({"metric": metric, "knowledge_state": state, "prefix_exposure": exposure, "window_change": "post_minus_within", "n_tasks": len(delta), "mean_change": float(delta.mean()), "ci_2_5": lo, "ci_97_5": hi, "analysis_role": "equivalence_audit" if state == "exact" else ("validity_failure_stratum" if state == "uncovered_biased" else "covered_scope_result"), "bootstrap_replicates": REPLICATES, "bootstrap_unit": "latent_task_id", "source_rows_sha256": sha(rows)})
    for path, output in ((cellwise_out, cellwise), (window_change_out, changes)):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(output[0])); w.writeheader(); w.writerows(output)


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--rows", type=Path, required=True); p.add_argument("--cellwise-out", type=Path, required=True); p.add_argument("--window-change-out", type=Path, required=True)
    a = p.parse_args(); run(a.rows, a.cellwise_out, a.window_change_out)
