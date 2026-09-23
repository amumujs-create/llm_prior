"""Render a four-panel E15-C v1.1 summary from frozen result tables only."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


EXPOSURES = ("low", "medium", "high")
PANELS = (
    ("C1: weighted mixture − residual MAP", "mean_C1", "#2C6E9E", "Negative favors residual-diversity retention."),
    ("C2: weighted mixture − uniform ensemble", "mean_C2", "#9E4C2C", "Negative favors likelihood weighting within retained diversity."),
    ("Closed mechanism − invariant residual ensemble", "mean_C_closed", "#8B2E3B", "Positive is the cost of treating the invariant as complete."),
    ("Invariant residual ensemble − matched free baseline", "mean_C_inv", "#246B50", "Negative favors correct invariant sharing."),
)


def load(path: Path, field: str) -> list[dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            rows[row["prefix_exposure"]] = {"mean": float(row[field]), "lo": float(row["ci_2_5"]), "hi": float(row["ci_97_5"])}
    if set(rows) != set(EXPOSURES):
        raise RuntimeError(f"unexpected exposure set in {path}: {sorted(rows)}")
    return [rows[exposure] for exposure in EXPOSURES]


def render(tables: list[Path], out_path: Path) -> None:
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), dpi=180)
    x = np.arange(len(EXPOSURES))
    if len(tables) != len(PANELS):
        raise RuntimeError("expected one frozen table per E15-C panel")
    for ax, table, (title, field, color, note) in zip(axes.flat, tables, PANELS):
        values = load(table, field)
        mean = np.asarray([value["mean"] for value in values])
        lower = mean - np.asarray([value["lo"] for value in values])
        upper = np.asarray([value["hi"] for value in values]) - mean
        ax.errorbar(x, mean, yerr=np.vstack((lower, upper)), marker="o", color=color, linewidth=1.8, capsize=3)
        ax.axhline(0.0, color="black", linewidth=0.75)
        ax.set_title(title, fontsize=10)
        ax.set_xticks(x, ("Low", "Medium", "High"))
        ax.set_xlabel("Prefix exposure")
        ax.set_ylabel("Mean paired NRMSE contrast")
        ax.text(0.02, 0.03, note, transform=ax.transAxes, va="bottom", fontsize=7.3)
    fig.suptitle("E15-C v1.1 frozen cellwise results", y=0.975, fontsize=13)
    fig.text(0.5, 0.005, "Error bars: cellwise 95% latent-task paired-bootstrap CI; signs have panel-specific interpretations.", ha="center", fontsize=8)
    fig.subplots_adjust(left=0.1, right=0.985, bottom=0.11, top=0.86, wspace=0.22, hspace=0.5)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--c1", type=Path, required=True)
    parser.add_argument("--c2", type=Path, required=True)
    parser.add_argument("--closed", type=Path, required=True)
    parser.add_argument("--inv", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    render([args.c1, args.c2, args.closed, args.inv], args.out)
