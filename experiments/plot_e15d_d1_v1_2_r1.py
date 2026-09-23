#!/usr/bin/env python3
"""Plot frozen E15-D R1 D1_S paired-bootstrap result."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2_r1" / "E15D_D1_CELLWISE_PAIRED_BOOTSTRAP_V1_2_R1.csv"
OUTPUT = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2_r1" / "E15D_D1_PRIMARY_RESULT_V1_2_R1.png"


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        row = next(csv.DictReader(handle))
    mean, low, high = (float(row[key]) for key in ("mean_D1", "ci_2_5", "ci_97_5"))
    fig, axis = plt.subplots(figsize=(6.5, 3.5))
    axis.axhline(0.0, color="0.35", lw=1.1)
    axis.errorbar([0], [mean], yerr=[[mean - low], [high - mean]], fmt="o", color="#1f77b4", capsize=6, ms=8, lw=2.0)
    axis.set(xlim=(-0.8, 0.8), xticks=[0], xticklabels=["S: κ selective − joint uniform"], ylabel="Mean paired NRMSE contrast", title="E15-D primary D1_S: selective κ reduction")
    axis.text(0.04, 0.95, "Negative favors κ-selective", transform=axis.transAxes, va="top")
    axis.text(0.04, 0.84, f"{mean:.4f}  [{low:.4f}, {high:.4f}]", transform=axis.transAxes, va="top")
    axis.grid(axis="y", color="0.9")
    fig.tight_layout()
    fig.savefig(OUTPUT, dpi=200)


if __name__ == "__main__":
    main()
