#!/usr/bin/env python3
"""Render the frozen, outcome-free E15-D0 v1.2 evidence-geometry figure."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "results" / "prior_utilization_e15d" / "d0_v1_2" / "E15D_D0_ARTIFACT_V1_2.json"
OUTPUT = ROOT / "results" / "prior_utilization_e15d" / "d0_v1_2" / "E15D_D0_EVIDENCE_GEOMETRY_V1_2.png"


def main() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    selected = artifact["selected_candidate"]
    if selected is None:
        raise SystemExit("no selected D0 candidate; no arbitrary failed candidate may be plotted")

    regimes = ["L", "S", "J"]
    labels = ["L", "S", "J"]
    e_kappa = selected["evidence"]
    fig, axes = plt.subplots(2, 2, figsize=(10.0, 7.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.09, top=0.85, wspace=0.20, hspace=0.32)
    x = np.linspace(0.0, 1.0, 501)
    axes[0, 0].plot(x, x**2, color="#1f77b4", lw=2.4, label=r"$x^2$")
    axes[0, 0].plot(x, x**6, color="#d62728", lw=2.4, label=r"$x^6$")
    axes[0, 0].axvline(selected["exposure_triple"]["L"], color="0.45", lw=1.0)
    axes[0, 0].axvline(selected["exposure_triple"]["S"], color="0.45", lw=1.0)
    axes[0, 0].axvline(selected["exposure_triple"]["J"], color="0.45", lw=1.0)
    axes[0, 0].set(title="Basis leverage", xlabel="Public time coordinate x", ylabel="Basis value", xlim=(0, 1), ylim=(0, 1.03))
    axes[0, 0].legend(frameon=False, loc="upper left")

    for axis, dimension, color, title in ((axes[0, 1], "E_kappa", "#1f77b4", r"Marginal evidence: $E_\kappa$"), (axes[1, 0], "E_lambda", "#d62728", r"Marginal evidence: $E_\lambda$")):
        med = np.array([e_kappa[regime][dimension]["median"] for regime in regimes])
        low = np.array([e_kappa[regime][dimension]["q05"] for regime in regimes])
        high = np.array([e_kappa[regime][dimension]["q95"] for regime in regimes])
        axis.errorbar(np.arange(3), med, yerr=np.vstack([med - low, high - med]), fmt="o-", color=color, ecolor=color, capsize=4, lw=2.0, ms=6)
        axis.set(title=title, xlabel="Prefix exposure regime", ylabel="Concentration (natural-log entropy)", xticks=np.arange(3), xticklabels=labels, ylim=(-0.02, 0.70))
        axis.grid(axis="y", color="0.9")

    k_med = np.array([e_kappa[regime]["E_kappa"]["median"] for regime in regimes])
    l_med = np.array([e_kappa[regime]["E_lambda"]["median"] for regime in regimes])
    axes[1, 1].plot(k_med, l_med, color="0.35", lw=1.4, zorder=1)
    for label, k_value, l_value in zip(labels, k_med, l_med):
        axes[1, 1].scatter(k_value, l_value, s=52, color="#2ca02c", zorder=2)
        axes[1, 1].annotate(label, (k_value, l_value), xytext=(6, 5), textcoords="offset points")
    axes[1, 1].set(title="Median evidence-vector path", xlabel=r"$E_\kappa$", ylabel=r"$E_\lambda$", xlim=(-0.02, 0.70), ylim=(-0.02, 0.42))
    axes[1, 1].grid(color="0.9")

    figure_note = (
        "E15-D0 v1.2 outcome-free calibration | selected: broad, Δ=.05, ρ=.10, T2=(.25,.60,.85), xfar=1.00\n"
        "Points: medians; whiskers: 5–95% across 400 fresh discarded tasks. No policy outcome is shown."
    )
    fig.suptitle(figure_note, fontsize=10.5, y=0.975)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=200, bbox_inches="tight")


if __name__ == "__main__":
    main()
