#!/usr/bin/env python3
"""Render static figures from frozen E13 scope-analysis CSV outputs."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "results/joint_prior_anatomy_e13/corrected_analysis_scope"
FIGURES = ROOT / "figures"


def read(name: str) -> list[dict[str, str]]:
    with (ANALYSIS / name).open() as handle:
        return list(csv.DictReader(handle))


def f(rows: list[dict[str, str]], key: str) -> list[float]:
    return [float(row[key]) for row in rows]


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    profile = read("censored_scope_profile.csv")
    horizons = [row["horizon"] for row in profile]
    x = list(range(len(horizons)))

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), constrained_layout=True)
    axes[0].plot(x, f(profile, "all_candidate_survival"), marker="o", label="all candidates")
    axes[0].plot(x, f(profile, "full_survival"), marker="s", label="oracle full")
    axes[0].set(xticks=x, xticklabels=horizons, ylim=(0, 1), xlabel="horizon", ylabel="P(C_P(h)=1)")
    axes[0].set_title("Censoring-aware scope profile")
    axes[0].legend(frameon=False)
    ext = f(profile, "proper_subset_scope_extension_rate")
    lower = f(profile, "extension_cluster_bootstrap_95ci_low")
    upper = f(profile, "extension_cluster_bootstrap_95ci_high")
    axes[1].errorbar(x, ext, yerr=[[a-b for a,b in zip(ext, lower)], [a-b for a,b in zip(upper, ext)]], marker="o", capsize=3)
    axes[1].set(xticks=x, xticklabels=horizons, ylim=(0, .16), xlabel="horizon", ylabel="P(C_P=1, C_P*=0 | proper subset)")
    axes[1].set_title("Empirical scope extension (95% cluster CI)")
    fig.savefig(FIGURES / "fig42_e13_censored_scope_profile.png", dpi=200)
    plt.close(fig)

    completeness = read("completeness_scope_profile.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), constrained_layout=True)
    for status, marker in (("survives", "o"), ("failed", "s")):
        series = [row for row in completeness if row["scope_status"] == status]
        axes[0].plot(x, f(series, "P_info_complete_exact_reliable"), marker=marker, label=status)
        axes[1].plot(x, f(series, "mean_delta_S_miss"), marker=marker, label=status)
    for axis, ylabel, title in (
        (axes[0], "P(informationally complete)", "Conditional completeness by scope status"),
        (axes[1], "mean ΔS_miss (nat)", "Missing information by scope status"),
    ):
        axis.set(xticks=x, xticklabels=horizons, xlabel="horizon", ylabel=ylabel, title=title)
        axis.legend(frameon=False)
    fig.savefig(FIGURES / "fig43_e13_completeness_scope_profile.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
