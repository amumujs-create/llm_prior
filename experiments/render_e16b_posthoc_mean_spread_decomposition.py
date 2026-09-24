"""Render frozen E16-B post-hoc mean-spread decomposition diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def points(ax, entries, title, ylabel):
    labels = list(entries)
    for index, label in enumerate(labels):
        item = entries[label]
        mean = item["mean"]
        ax.errorbar(index, mean, yerr=[[mean - item["ci_2_5"]], [item["ci_97_5"] - mean]], fmt="o", color="#E45756" if mean > 0 else "#54A24B", capsize=5, markersize=7)
    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.set_xticks(range(len(labels)), [label.replace("_", "\n") for label in labels])
    ax.set_title(title)
    ax.set_ylabel(ylabel)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text())
    plt.rcParams.update({"font.size": 9, "axes.titlesize": 11})
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    points(axes[0], artifact["weighted_spread_table"], "Weighted: same-mean spread decomposition", "Paired CRPS difference")
    points(axes[1], artifact["uniform_to_weighted_recovery_table"], "Uniform → weighted recovery path", "Paired CRPS difference")
    curve = artifact["response_curve"]
    for name, color in [("uniform", "#4C78A8"), ("weighted", "#F58518")]:
        rhos = [float(value) for value in curve[name]]
        diffs = [curve[name][str(rho)]["difference_from_rho_0"] for rho in rhos]
        axes[2].plot(rhos, diffs, marker="o", linewidth=2, color=color, label=name)
    axes[2].axhline(0, color="black", linestyle="--", linewidth=1)
    axes[2].set_xlabel(r"Spread retention $\rho$")
    axes[2].set_ylabel(r"Mean CRPS difference from $\rho=0$")
    axes[2].set_title("Descriptive mean-preserving response curve")
    axes[2].legend(frameon=False)
    fig.suptitle("E16-B post-hoc mean–spread decomposition (not confirmatory)", fontsize=14)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
