"""Render the frozen CRPS pathway from uniform through weighted to MAP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--b1", type=Path, required=True)
    parser.add_argument("--b2", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    b1 = json.loads(args.b1.read_text())["primary_estimand"]
    b2 = json.loads(args.b2.read_text())["secondary_estimand"]
    weighted_minus_map = b1["mean"] + b2["mean"]

    fig, ax = plt.subplots(figsize=(9.4, 4.8), constrained_layout=True)
    x = [0, 1, 2]
    y = [0.0, b2["mean"], weighted_minus_map]
    labels = ["Uniform\nreference mixture", "Validation-weighted\nmixture", "Validation-selected\nMAP"]
    ax.plot(x, y, color="#4C78A8", linewidth=2.5, marker="o", markersize=9)
    ax.axhline(0.0, color="black", linestyle="--", linewidth=1)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Mean CRPS relative to uniform")
    ax.set_title("E16-B: evidence weighting recovers the uniform-mixture deficit")
    ax.text(0.5, 0.11, f"B2 = {b2['mean']:+.4f}\n[{b2['ci_2_5']:+.4f}, {b2['ci_97_5']:+.4f}]", transform=ax.transAxes, ha="center", va="bottom")
    ax.text(0.97, 0.95, f"W − MAP = B1 + B2 = {weighted_minus_map:+.4f}\n(descriptive; no direct CI)", transform=ax.transAxes, ha="right", va="top")
    ax.text(0.02, 0.05, "Uniform − MAP B1 = +0.1370: prospective failure", transform=ax.transAxes, color="#E45756")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
