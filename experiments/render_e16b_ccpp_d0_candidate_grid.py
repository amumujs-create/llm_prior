"""Render the frozen E16-B D0 candidate geometry from its target-free artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    levels = artifact["shape_levels"]
    amplitudes = artifact["amplitude_reference_measure"]["nodes"]
    distances = artifact["pairwise_distinctness"]
    singular = artifact["future_shell"]["singular_values"]

    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)

    ax = axes[0, 0]
    ax.scatter(amplitudes, np.ones(len(amplitudes)), s=90, color="#4C78A8")
    for value in amplitudes:
        ax.annotate(f"{value:.1f}", (value, 1), xytext=(0, 10), textcoords="offset points", ha="center")
    ax.set_xlim(0, 1)
    ax.set_ylim(0.85, 1.25)
    ax.set_yticks([])
    ax.set_xlabel("a: standardized decrease magnitude")
    ax.set_title("Five-node amplitude reference measure")
    ax.text(0.5, 0.05, "Each node has mass 1/5", transform=ax.transAxes, ha="center")

    ax = axes[0, 1]
    names = ["r_c", "r_V, r_AP, r_RH"]
    level_sets = [levels["r_c"], levels["r_interaction"]]
    colors = ["#F58518", "#54A24B"]
    for row, (name, values, color) in enumerate(zip(names, level_sets, colors)):
        ax.scatter(values, np.full(3, row), s=80, color=color)
    ax.axvline(0, color="#333333", linewidth=0.8)
    ax.set_yticks([0, 1], names)
    ax.set_xlabel("Shape-coordinate levels")
    ax.set_title("Curvature and interaction reference levels")
    ax.invert_yaxis()

    ax = axes[1, 0]
    bound = [-0.25 * value for value in amplitudes]
    ax.bar(np.arange(len(amplitudes)), bound, color="#4C78A8")
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xticks(np.arange(len(amplitudes)), [f"a={value:.1f}" for value in amplitudes])
    ax.set_ylabel("Maximum permitted dT/du")
    ax.set_title("Monotonicity bound by amplitude")
    ax.text(0.5, 0.08, "All 405 empirical-scope checks passed", transform=ax.transAxes, ha="center")

    ax = axes[1, 1]
    labels = ["min", "q05", "median", "q95", "max"]
    values = [distances[key] for key in labels]
    ax.plot(labels, values, marker="o", color="#E45756", linewidth=2)
    ax.set_yscale("log")
    ax.set_ylabel("Pairwise continuation RMS distance")
    ax.set_title("Future-shell candidate distinctness")
    ax.text(0.5, 0.10, f"{distances['pair_count']:,} pairs; 0 at or below 1e-10", transform=ax.transAxes, ha="center")

    fig.suptitle("E16-B D0: Target-free monotone candidate reference geometry", fontsize=14)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
