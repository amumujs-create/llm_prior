"""Render the E15-C C1 figure from its already frozen cellwise table only."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


EXPOSURES = ("low", "medium", "high")


def load(path: Path) -> list[dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            rows[row["prefix_exposure"]] = {
                "mean": float(row["mean_C1"]),
                "lo": float(row["ci_2_5"]),
                "hi": float(row["ci_97_5"]),
            }
    if set(rows) != set(EXPOSURES):
        raise RuntimeError(f"unexpected C1 exposure set: {sorted(rows)}")
    return [rows[exposure] for exposure in EXPOSURES]


def render(values: list[dict[str, float]], out_path: Path) -> None:
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=180)
    x = np.arange(len(EXPOSURES))
    mean = np.asarray([value["mean"] for value in values])
    lower = mean - np.asarray([value["lo"] for value in values])
    upper = np.asarray([value["hi"] for value in values]) - mean
    ax.errorbar(x, mean, yerr=np.vstack((lower, upper)), marker="o", color="#2C6E9E", linewidth=2, capsize=4)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xticks(x, ("Low", "Medium", "High"))
    ax.set_xlabel("Prefix exposure")
    ax.set_ylabel("Mean paired NRMSE contrast")
    ax.set_title("E15-C C1: weighted residual mixture − residual MAP")
    ax.text(
        0.01,
        0.02,
        "Error bars: cellwise 95% latent-task paired-bootstrap CI\nAll exposure cells retain weak realized residual evidence.",
        transform=ax.transAxes,
        va="bottom",
        fontsize=8,
    )
    fig.subplots_adjust(left=0.19, right=0.98, bottom=0.18, top=0.89)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--c1", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    render(load(args.c1), args.out)
