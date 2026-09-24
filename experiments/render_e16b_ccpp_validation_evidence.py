"""Render frozen validation evidence diagnostics without test targets."""

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
    weights = np.asarray(artifact["weights"], dtype=float)
    diagnostics = artifact["weight_diagnostics"]
    order = np.argsort(weights)[::-1]
    top = order[:15]

    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    ax = axes[0]
    ax.bar(np.arange(top.size), weights[top], color="#4C78A8")
    ax.set_xticks(np.arange(top.size), [str(index) for index in top], rotation=70)
    ax.set_xlabel("Frozen candidate index, decreasing validation weight")
    ax.set_ylabel("Gaussian working-likelihood weight")
    ax.set_title("Validation-selected weight concentration")
    ax.axhline(1.0 / 405.0, color="#E45756", linestyle="--", label="uniform = 1/405")
    ax.legend(frameon=False)

    ax = axes[1]
    names = ["Entropy\n(nats)", "ESS", "Candidates"]
    values = [diagnostics["entropy_natural_log"], diagnostics["effective_sample_size"], 405]
    bars = ax.bar(names, values, color=["#54A24B", "#F58518", "#9C755F"])
    ax.set_yscale("log")
    ax.set_ylabel("Count / entropy scale")
    ax.set_title("Frozen validation evidence diagnostics")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value * 1.25, f"{value:.3g}", ha="center")
    fig.suptitle("E16-B: validation evidence freeze; guard/test PE remain sealed", fontsize=14)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
