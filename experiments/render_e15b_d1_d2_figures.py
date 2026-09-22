"""Render E15-B D1/D2 figures from already frozen cellwise tables only."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


STATES = ("broad", "existence_only", "narrow", "covered_biased")
LABELS = {"broad": "Broad", "existence_only": "Endpoint-unspecified", "narrow": "Narrow", "covered_biased": "Covered-biased"}
EXPOSURES = ("low", "medium", "high")


def load(path: Path, field: str) -> dict[tuple[str, str], dict[str, float]]:
    result = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["knowledge_state"] in STATES:
                result[(row["knowledge_state"], row["prefix_exposure"])] = {"mean": float(row[field]), "lo": float(row["ci_2_5"]), "hi": float(row["ci_97_5"])}
    return result


def render(data: dict, metric: str, out: Path) -> None:
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=180)
    x = np.arange(len(EXPOSURES))
    for state in STATES:
        vals = [data[(state, exposure)] for exposure in EXPOSURES]
        y = np.array([v["mean"] for v in vals])
        lower = y - np.array([v["lo"] for v in vals])
        upper = np.array([v["hi"] for v in vals]) - y
        ax.errorbar(x, y, yerr=np.vstack((lower, upper)), marker="o", linewidth=1.8, capsize=3, label=LABELS[state])
    ax.axhline(0., color="black", linewidth=.8)
    ax.set_xticks(x, ("Low", "Medium", "High"))
    ax.set_xlabel("Prefix exposure")
    ax.set_ylabel("Mean paired post-scope NRMSE contrast")
    ax.set_title(f"E15-B {metric} by prefix exposure")
    ax.legend(frameon=False, fontsize=8, loc="best")
    ax.text(.01, .01, "Error bars: cellwise 95% latent-task paired-bootstrap CI\nExact omitted: identically zero by equivalence; uncovered-biased omitted.", transform=ax.transAxes, va="bottom", fontsize=7.5)
    fig.subplots_adjust(left=.24, right=.98, bottom=.19, top=.88)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--d1", type=Path, required=True); p.add_argument("--d2", type=Path, required=True); p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    render(load(a.d1, "mean_D1"), "D1: weighted mixture − local MAP", a.out_dir / "E15B_D1_EXPOSURE_CELLWISE.png")
    render(load(a.d2, "mean_D2"), "D2: weighted mixture − uniform ensemble", a.out_dir / "E15B_D2_EXPOSURE_CELLWISE.png")
