"""Render frozen E16-B confirmatory CRPS and NRMSE summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def point_ci(ax, labels, entries, title, ylabel):
    for index, entry in enumerate(entries):
        mean = entry["mean"]
        ax.errorbar(index, mean, yerr=[[mean - entry["ci_2_5"]], [entry["ci_97_5"] - mean]], fmt="o", color="#E45756" if mean > 0 else "#54A24B", capsize=6, markersize=8, linewidth=2)
    ax.axhline(0.0, color="black", linestyle="--", linewidth=1)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--b1", type=Path, required=True)
    parser.add_argument("--b2", type=Path, required=True)
    parser.add_argument("--nrmse", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    b1 = json.loads(args.b1.read_text())["primary_estimand"]
    b2 = json.loads(args.b2.read_text())["secondary_estimand"]
    nrmse = json.loads(args.nrmse.read_text())["secondary_diagnostics"]
    n1 = nrmse["B1_NRMSE = NRMSE_uniform - NRMSE_MAP"]
    n2 = nrmse["B2_NRMSE = NRMSE_weighted - NRMSE_uniform"]
    plt.rcParams.update({"font.size": 11, "axes.titlesize": 13})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    point_ci(axes[0], [r"$B_1^{CRPS}$", r"$B_2^{CRPS}$"], [b1, b2], "Primary CRPS and secondary weighting contrast", "Mean paired CRPS difference")
    axes[0].text(0.03, 0.87, "Primary: prospective failure", transform=axes[0].transAxes, ha="left", va="top", color="#E45756", fontsize=9)
    point_ci(axes[1], [r"$B_1^{NRMSE}$", r"$B_2^{NRMSE}$"], [n1, n2], "Secondary point-specification diagnostics", "Bootstrap NRMSE difference")
    fig.suptitle("E16-B CCPP confirmatory results: high-AT compound covariate shift", fontsize=15)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
