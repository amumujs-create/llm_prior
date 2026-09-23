"""Render the frozen E15-B primary high-minus-low exposure changes."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


STATES = ("broad", "existence_only", "narrow", "covered_biased")
LABELS = {
    "broad": "Broad",
    "existence_only": "Endpoint-unspecified",
    "narrow": "Narrow",
    "covered_biased": "Covered-biased",
}


def load(path: Path, metric: str) -> list[dict[str, float | str]]:
    rows = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if (
                row["metric"] == metric
                and row["knowledge_state"] in STATES
                and row["exposure_change"] == "high_minus_low"
            ):
                rows.append({
                    "state": row["knowledge_state"],
                    "mean": float(row["mean_change"]),
                    "lo": float(row["ci_2_5"]),
                    "hi": float(row["ci_97_5"]),
                })
    return sorted(rows, key=lambda row: STATES.index(str(row["state"])))


def render_panel(ax: plt.Axes, rows: list[dict[str, float | str]], metric: str) -> None:
    x = np.arange(len(rows))
    mean = np.array([float(row["mean"]) for row in rows])
    lo = np.array([float(row["lo"]) for row in rows])
    hi = np.array([float(row["hi"]) for row in rows])
    colors = plt.get_cmap("tab10")(np.arange(len(rows)))
    ax.errorbar(x, mean, yerr=np.vstack((mean - lo, hi - mean)), fmt="none", color="black", capsize=3, linewidth=1.1, zorder=3)
    ax.scatter(x, mean, s=48, color=colors, zorder=4)
    ax.axhline(0, color="black", linewidth=.8)
    ax.set_xticks(x, [LABELS[str(row["state"])] for row in rows], rotation=18, ha="right")
    ax.set_title(metric)
    ax.set_ylabel("High − low mean paired NRMSE contrast")
    ax.spines[["top", "right"]].set_visible(False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    plt.rcParams.update({"font.size": 10})
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.6), dpi=180, sharey=False)
    render_panel(axes[0], load(args.table, "D1"), "D1: weighted mixture − local MAP")
    render_panel(axes[1], load(args.table, "D2"), "D2: weighted mixture − uniform ensemble")
    figure.suptitle("E15-B primary exposure modification", fontsize=15)
    figure.text(.5, .02, "Error bars: 95% latent-task paired-bootstrap CI; exact omitted (identically zero).", ha="center", fontsize=8)
    figure.subplots_adjust(left=.10, right=.98, bottom=.27, top=.82, wspace=.30)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.out, bbox_inches="tight")


if __name__ == "__main__":
    main()
