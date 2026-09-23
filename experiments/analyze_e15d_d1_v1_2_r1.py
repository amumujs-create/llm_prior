#!/usr/bin/env python3
"""Open only the preregistered E15-D R1 D1_S estimand."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "experiments" / "E15D_D1_BOOTSTRAP_CONFIG_V1_2_R1.json"
DEFAULT_ROWS = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2_r1" / "E15D_CONFIRMATORY_ROWS_V1_2_R1.csv"
DEFAULT_OUT = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2_r1" / "E15D_D1_CELLWISE_PAIRED_BOOTSTRAP_V1_2_R1.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if sha256(args.rows) != config["source_rows_sha256"]:
        raise SystemExit("source row hash does not match frozen D1 bootstrap config")
    values: dict[int, dict[str, float]] = {}
    with args.rows.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["prefix_exposure"] != config["prefix_exposure"]:
                continue
            if row["policy"] not in {"kappa_selective", "joint_uniform"}:
                continue
            values.setdefault(int(row["task_id"]), {})[row["policy"]] = float(row["nrmse_clean_far"])
    task_ids = sorted(values)
    if not task_ids or any(set(values[task_id]) != {"kappa_selective", "joint_uniform"} for task_id in task_ids):
        raise SystemExit("incomplete paired D1 rows")
    paired = np.asarray([values[task_id]["kappa_selective"] - values[task_id]["joint_uniform"] for task_id in task_ids], dtype=float)
    rng = np.random.Generator(np.random.PCG64(int(config["bootstrap_rng"]["seed"])))
    samples = rng.integers(0, len(paired), size=(int(config["bootstrap_replicates"]), len(paired)))
    boot = np.mean(paired[samples], axis=1)
    ci_low, ci_high = np.quantile(boot, [0.025, 0.975], method=config["quantile_method"])
    output = [{
        "estimand": "D1_S",
        "prefix_exposure": "S",
        "n_tasks": len(paired),
        "mean_D1": float(np.mean(paired)),
        "ci_2_5": float(ci_low),
        "ci_97_5": float(ci_high),
        "bootstrap_replicates": int(config["bootstrap_replicates"]),
        "bootstrap_unit": config["bootstrap_unit"],
        "source_rows_sha256": config["source_rows_sha256"],
    }]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)


if __name__ == "__main__":
    main()
