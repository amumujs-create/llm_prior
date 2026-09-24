"""Render only the already-frozen E16-B primary B1 CRPS result."""

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
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))["primary_estimand"]
    mean, lower, upper = artifact["mean"], artifact["ci_2_5"], artifact["ci_97_5"]
    fig, ax = plt.subplots(figsize=(6.6, 4.5), constrained_layout=True)
    color = "#E45756" if mean > 0 else "#54A24B"
    ax.errorbar([0], [mean], yerr=[[mean - lower], [upper - mean]], fmt="o", color=color, capsize=7, markersize=9, linewidth=2)
    ax.axhline(0.0, color="black", linewidth=1, linestyle="--")
    ax.set_xlim(-0.8, 0.8)
    ax.set_xticks([0], [r"$B_1^{CRPS}=CRPS_U-CRPS_M$"])
    ax.set_ylabel("Mean paired CRPS difference\n(normalized target units)")
    ax.set_title("E16-B primary confirmatory result")
    ax.text(0, upper + 0.012, f"{mean:+.4f}  [{lower:+.4f}, {upper:+.4f}]", ha="center", fontsize=11)
    ax.text(0.02, 0.04, artifact["disposition"], transform=ax.transAxes, color=color, weight="bold")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
