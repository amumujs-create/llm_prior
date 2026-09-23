#!/usr/bin/env python3
"""Compute one frozen E15-D R1 paired-bootstrap contrast from a config."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROWS = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2_r1" / "E15D_CONFIRMATORY_ROWS_V1_2_R1.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if sha256(args.rows) != config["source_rows_sha256"]:
        raise SystemExit("source row hash does not match frozen contrast config")
    values: dict[int, dict[str, float]] = {}
    policies = {config["left_policy"], config["right_policy"]}
    with args.rows.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["prefix_exposure"] == config["prefix_exposure"] and row["policy"] in policies:
                values.setdefault(int(row["task_id"]), {})[row["policy"]] = float(row["nrmse_clean_far"])
    task_ids = sorted(values)
    if not task_ids or any(set(values[task_id]) != policies for task_id in task_ids):
        raise SystemExit("incomplete paired contrast rows")
    paired = np.asarray([values[task_id][config["left_policy"]] - values[task_id][config["right_policy"]] for task_id in task_ids], dtype=float)
    rng = np.random.Generator(np.random.PCG64(int(config["bootstrap_rng"]["seed"])))
    indices = rng.integers(0, len(paired), size=(int(config["bootstrap_replicates"]), len(paired)))
    bootstrap = np.mean(paired[indices], axis=1)
    low, high = np.quantile(bootstrap, [0.025, 0.975], method=config["quantile_method"])
    output = [{"estimand": config["estimand"].split(" = ")[0], "prefix_exposure": config["prefix_exposure"], "n_tasks": len(paired), "mean_contrast": float(np.mean(paired)), "ci_2_5": float(low), "ci_97_5": float(high), "bootstrap_replicates": int(config["bootstrap_replicates"]), "bootstrap_unit": config["bootstrap_unit"], "source_rows_sha256": config["source_rows_sha256"]}]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)


if __name__ == "__main__":
    main()
