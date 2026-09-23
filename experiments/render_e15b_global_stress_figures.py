"""Render frozen E15-B global-overextension stress figures."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


EXPOSURES = ("low", "medium", "high")
MODES = ("-2", "0", "1")
MODE_LABELS = {"-2": "Reverse", "0": "Persist", "1": "Strengthen"}
WINDOWS = (("within_scope", "Within scope"), ("post_scope", "Post scope"))
COMPARISONS = (("G_hard", "Hard global"), ("G_soft", "Soft global"), ("G_slack", "Slack distribution"))


def load(path: Path) -> dict[tuple[str, str, str, str], dict[str, float]]:
    out = {}
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            out[(r["comparison"], r["prefix_exposure"], r["post_scope_mode"], r["window"])] = {"mean": float(r["mean_contrast"]), "lo": float(r["ci_2_5"]), "hi": float(r["ci_97_5"])}
    return out


def error(vals):
    y = np.array([v["mean"] for v in vals]); return y, np.vstack((y-np.array([v["lo"] for v in vals]), np.array([v["hi"] for v in vals])-y))


def hard_by_mode(data: dict, out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.6), dpi=180, sharey=True)
    x = np.arange(3)
    for ax, exposure in zip(axes, EXPOSURES):
        for window, label in WINDOWS:
            vals = [data[("G_hard", exposure, mode, window)] for mode in MODES]
            y, e = error(vals); ax.errorbar(x, y, yerr=e, marker="o", linewidth=1.6, capsize=3, label=label)
        ax.axhline(0, color="black", linewidth=.7); ax.set_title(exposure.title()); ax.set_xticks(x, [MODE_LABELS[m] for m in MODES]); ax.set_xlabel("Post-scope realization")
    axes[0].set_ylabel("Hard-global − local-MAP NRMSE")
    axes[-1].legend(frameon=False, fontsize=8)
    fig.suptitle("E15-B exact-scope global-overextension stress", fontsize=14)
    fig.text(.5, .01, "Error bars: cellwise 95% latent-task paired-bootstrap CI", ha="center", fontsize=9)
    fig.tight_layout(rect=(.02, .06, .99, .90)); out.parent.mkdir(parents=True, exist_ok=True); fig.savefig(out, bbox_inches="tight"); plt.close(fig)


def relaxations(data: dict, out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8), dpi=180, sharey=True)
    x = np.arange(3)
    for ax, (window, title) in zip(axes, WINDOWS):
        for comparison, label in COMPARISONS:
            vals = [data[(comparison, exposure, "all", window)] for exposure in EXPOSURES]
            y, e = error(vals); ax.errorbar(x, y, yerr=e, marker="o", linewidth=1.6, capsize=3, label=label)
        ax.axhline(0, color="black", linewidth=.7); ax.set_title(title); ax.set_xticks(x, ("Low", "Medium", "High")); ax.set_xlabel("Prefix exposure")
    axes[0].set_ylabel("Global policy − local-MAP NRMSE")
    axes[-1].legend(frameon=False, fontsize=8)
    fig.suptitle("E15-B global relaxation policies, exact scope", fontsize=14)
    fig.text(.5, .01, "Mode-balanced aggregate; error bars: cellwise 95% latent-task paired-bootstrap CI", ha="center", fontsize=8.5)
    fig.tight_layout(rect=(.02, .07, .99, .90)); out.parent.mkdir(parents=True, exist_ok=True); fig.savefig(out, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--table", type=Path, required=True); p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args(); data = load(a.table)
    hard_by_mode(data, a.out_dir / "E15B_GHARD_BY_MODE.png")
    relaxations(data, a.out_dir / "E15B_GLOBAL_RELAXATION.png")
