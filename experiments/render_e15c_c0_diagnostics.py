"""Render E15-C0 diagnostics from the frozen outcome-free sweep only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


EXPOSURES = ("low", "medium", "high")


def selected_candidate(result: dict) -> dict:
    chosen = result["selection"]
    for row in result["candidates"]:
        if all(row[f] == chosen[f"selected_{f}"] for f in ("grid_step", "rho", "x_far")):
            return row
    raise ValueError("selected candidate is absent")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sweep", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = json.loads(args.sweep.read_text())
    row = selected_candidate(result)
    values = row["exposures"]
    x = np.arange(len(EXPOSURES))

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.9), dpi=180)

    e_median = np.array([values[e]["E_r"]["median"] for e in EXPOSURES])
    e_lo = np.array([values[e]["E_r"]["q05"] for e in EXPOSURES])
    e_hi = np.array([values[e]["E_r"]["q95"] for e in EXPOSURES])
    axes[0].errorbar(x, e_median, yerr=np.vstack((e_median-e_lo, e_hi-e_median)), marker="o", capsize=3)
    axes[0].set_yscale("log")
    axes[0].set_title("Residual evidence concentration")
    axes[0].set_ylabel(r"$E_r$ (5–95%, log scale)")

    count = np.array([values[e]["effective_residual_continuations"]["median"] for e in EXPOSURES])
    axes[1].bar(x, count, color="tab:green")
    axes[1].axhline(4, color="black", linewidth=.8, linestyle="--", label="gate = 4")
    axes[1].set_title("Effective residual continuations")
    axes[1].set_ylabel("Median count")
    axes[1].legend(frameon=False, fontsize=8)

    separation = np.array([values[e]["uniform_minus_closed_distance"]["median"] for e in EXPOSURES])
    axes[2].bar(x, separation, color="tab:orange")
    axes[2].axhline(.01, color="black", linewidth=.8, linestyle="--", label=r"$\delta_{cont}=.01$")
    axes[2].set_title("Uniform ensemble − closed mechanism")
    axes[2].set_ylabel(r"Median normalized RMS distance")
    axes[2].legend(frameon=False, fontsize=8)

    for axis in axes:
        axis.set_xticks(x, ("Low", "Medium", "High"))
        axis.set_xlabel("Prefix exposure")
    fig.suptitle(f"E15-C0 outcome-free diagnostics: Δq={row['grid_step']}, ρ={row['rho']}, x_far={row['x_far']}", fontsize=14)
    fig.text(.5, .01, "Derived only from residual evidence, continuation geometry, and numerical-stability diagnostics; no policy outcomes inspected.", ha="center", fontsize=8)
    fig.subplots_adjust(left=.08, right=.98, bottom=.22, top=.80, wspace=.34)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, bbox_inches="tight")


if __name__ == "__main__":
    main()
