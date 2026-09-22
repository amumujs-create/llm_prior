"""Render frozen E15-B scope-window decomposition figures only."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


STATES = ("broad", "existence_only", "narrow", "covered_biased")
LABELS = {"broad": "Broad", "existence_only": "Endpoint-unspecified", "narrow": "Narrow", "covered_biased": "Covered-biased"}
EXPOSURES = ("low", "medium", "high")
WINDOWS = (("within_scope", "Within scope"), ("post_scope", "Post scope"))


def load(path: Path, metric: str) -> dict[tuple[str, str, str], dict[str, float]]:
    out = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["metric"] == metric and row["knowledge_state"] in STATES:
                out[(row["knowledge_state"], row["prefix_exposure"], row["window"])] = {"mean": float(row["mean_contrast"]), "lo": float(row["ci_2_5"]), "hi": float(row["ci_97_5"])}
    return out


def render(data: dict, metric: str, out: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.3), dpi=180, sharex=True)
    x = np.arange(3)
    for ax, state in zip(axes.flat, STATES):
        for window, label in WINDOWS:
            vals = [data[(state, e, window)] for e in EXPOSURES]
            y = np.array([v["mean"] for v in vals])
            error = np.vstack((y - np.array([v["lo"] for v in vals]), np.array([v["hi"] for v in vals]) - y))
            ax.errorbar(x, y, yerr=error, marker="o", linewidth=1.6, capsize=3, label=label)
        ax.axhline(0, color="black", linewidth=.7)
        ax.set_title(LABELS[state], fontsize=10)
        ax.set_xticks(x, ("Low", "Medium", "High"))
        ax.set_ylabel("Mean paired NRMSE contrast")
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle(f"E15-B {metric}: within-scope versus post-scope", fontsize=14)
    fig.text(.5, .02, "Prefix exposure; error bars are cellwise 95% latent-task paired-bootstrap CI", ha="center", fontsize=9)
    fig.tight_layout(rect=(.02, .05, .99, .94))
    out.parent.mkdir(parents=True, exist_ok=True); fig.savefig(out, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--table", type=Path, required=True); p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    render(load(a.table, "D1"), "D1: weighted mixture − local MAP", a.out_dir / "E15B_D1_SCOPE_WINDOWS.png")
    render(load(a.table, "D2"), "D2: weighted mixture − uniform ensemble", a.out_dir / "E15B_D2_SCOPE_WINDOWS.png")
