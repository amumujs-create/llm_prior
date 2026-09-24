"""Render the frozen E16-B affine point-mixture representation audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    maximum = artifact["max_abs_uniform_point_mean_minus_mean_specification"]
    rms = artifact["rms_uniform_point_mean_minus_mean_specification"]
    tolerance = artifact["tolerance"]

    plt.rcParams.update({"font.size": 11, "axes.titlesize": 13, "axes.labelsize": 11})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), constrained_layout=True)

    ax = axes[0]
    labels = ["RMS\ndifference", "Maximum\ndifference", "Frozen\ntolerance"]
    values = [rms, maximum, tolerance]
    colors = ["#4C78A8", "#F58518", "#54A24B"]
    bars = ax.bar(labels, values, color=colors)
    ax.set_yscale("log")
    ax.set_ylim(5e-16, 1e-11)
    ax.set_ylabel("Normalized prediction difference")
    ax.set_title("Uniform point mean = mean specification")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value * 1.5, f"{value:.2e}", ha="center", va="bottom")

    ax = axes[1]
    ax.axis("off")
    ax.text(0.5, 0.72, r"$\frac{1}{405}\sum_h f_h(x) = f_{\bar\theta}(x)$", ha="center", va="center", fontsize=22)
    ax.text(0.5, 0.45, "Train targets only; evaluated on all canonical X rows", ha="center", va="center")
    ax.text(0.5, 0.27, "Point NRMSE is a specification diagnostic.\nCRPS retains the 405-component predictive distribution.", ha="center", va="center", linespacing=1.5)
    ax.set_title("Frozen interpretation boundary")

    fig.suptitle("E16-B: affine point-mixture equivalence audit", fontsize=15)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
