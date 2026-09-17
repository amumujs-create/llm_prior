#!/usr/bin/env python3
"""Which retrieved realization constraints make a true family useful?"""
from __future__ import annotations

import itertools
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "partial_realization_knowledge_sweep_v1"
FIG = ROOT / "figures"
RNG = np.random.default_rng(20260926)
TB, NOISE, O, N, BOOT = .60, .015, .90, 200, 2000
NOISE_TIERS = (0.0, .05, .10, .20, .40)
FIELDS = ("onset", "scale", "shape")


def pospow(x, exponent):
    return np.maximum(x, 0.0) ** exponent


def regime(t, initial_rate, scale, shape, onset):
    return np.where(t < onset, 1 - initial_rate * t,
                    1 - initial_rate * onset - scale * pospow(t - onset, shape))


def curvature(t, initial_rate, scale, shape, onset):
    return 1 - initial_rate * t - scale * pospow(t - onset, shape)


FAMILIES = {
    "regime_change": {
        "function": regime, "p0": np.array([.15, .50, 2.0, .20]),
        "lower": np.array([0.0, 0.0, 1.01, .001]),
        "upper": np.array([.8, 2.0, 4.0, .599]),
        "ranges": ((.07, .24), (.35, 1.0), (1.35, 2.6)),
    },
    "emergent_curvature": {
        "function": curvature, "p0": np.array([.10, .35, 2.0, .20]),
        "lower": np.array([0.0, 0.0, 1.01, .001]),
        "upper": np.array([.7, 2.0, 4.0, .599]),
        "ranges": ((.05, .16), (.22, .60), (1.35, 2.6)),
    },
}
FIELD_INDEX = {"scale": 1, "shape": 2, "onset": 3}


def affine_fit(t, y, x):
    slope, intercept = np.polyfit(t, y, 1)
    return slope * x + intercept


def rmse(prediction, truth):
    return float(np.sqrt(np.mean((prediction - truth) ** 2)))


def generate(family_name, t, rng):
    spec = FAMILIES[family_name]
    initial, scale, shape = (rng.uniform(*bounds) for bounds in spec["ranges"])
    params = np.array([initial, scale, shape, TB * (1 - O)])
    return spec["function"](t, *params), params


def retrieve(true_params, known_fields, noise_tier, rng):
    """Create a noisy external constraint for just the requested fields."""
    known = {}
    for field in known_fields:
        index = FIELD_INDEX[field]
        if field == "onset":
            sigma = {0.0: 0.0, .05: .02, .10: .05, .20: .10, .40: .20}[noise_tier]
            known[index] = float(np.clip(true_params[index] + rng.normal(0, sigma), .001, .999))
        elif field == "scale":
            known[index] = float(np.clip(true_params[index] * (1 + rng.normal(0, noise_tier)), .001, 2.0))
        else:
            known[index] = float(np.clip(true_params[index] * (1 + rng.normal(0, noise_tier)), 1.01, 4.0))
    return known


def fit_with_knowledge(family_name, t, y, x, known):
    """Fix retrieved fields and fit all remaining parameters on the prefix."""
    spec = FAMILIES[family_name]
    free_indices = [index for index in range(4) if index not in known]
    x0 = spec["p0"][free_indices]
    lower, upper = spec["lower"][free_indices], spec["upper"][free_indices]

    def unpack(free):
        params = spec["p0"].copy()
        params[free_indices] = free
        for index, value in known.items():
            params[index] = value
        return params

    try:
        result = least_squares(lambda free: spec["function"](t, *unpack(free)) - y,
                               x0=x0, bounds=(lower, upper), max_nfev=4000)
        if not result.success:
            raise RuntimeError(result.message)
        return spec["function"](x, *unpack(result.x)), True
    except (RuntimeError, ValueError):
        return affine_fit(t, y, x), False


def bootstrap_mean_ci(values, rng):
    values = np.asarray(values)
    samples = values[rng.integers(0, len(values), size=(BOOT, len(values)))].mean(axis=1)
    return float(np.quantile(samples, .025)), float(np.quantile(samples, .975))


def bootstrap_closure_ci(family_values, partial_values, parameter_values, rng):
    family_values, partial_values, parameter_values = map(np.asarray, (family_values, partial_values, parameter_values))
    idx = rng.integers(0, len(family_values), size=(BOOT, len(family_values)))
    numerator = family_values[idx].mean(axis=1) - partial_values[idx].mean(axis=1)
    denominator = family_values[idx].mean(axis=1) - parameter_values[idx].mean(axis=1)
    estimates = numerator / denominator
    return float(np.quantile(estimates, .025)), float(np.quantile(estimates, .975))


def subset_name(fields):
    return "family_only" if not fields else "+".join(fields)


def main():
    grid = np.linspace(0, 1, 101)
    observed, tail = grid <= TB, grid > .70
    subsets = [()] + [combo for size in (1, 2, 3) for combo in itertools.combinations(FIELDS, size)]
    base = []
    for family_name in FAMILIES:
        for task_id in range(N):
            clean, params = generate(family_name, grid, RNG)
            noisy = clean + RNG.normal(0, NOISE, len(grid))
            base.append({"family": family_name, "task_id": task_id, "clean": clean,
                         "params": params, "noisy": noisy})

    records = []
    retrieval_rng = np.random.default_rng(20260927)
    for task in base:
        family_name, params, noisy, truth = task["family"], task["params"], task["noisy"], task["clean"][tail]
        fallback = rmse(affine_fit(grid[observed], noisy[observed], grid[tail]), truth)
        for fields in subsets:
            tiers = (None,) if not fields else NOISE_TIERS
            for tier in tiers:
                known = {} if not fields else retrieve(params, fields, tier, retrieval_rng)
                prediction, fit_success = fit_with_knowledge(family_name, grid[observed], noisy[observed], grid[tail], known)
                score = rmse(prediction, truth)
                row = {"family": family_name, "task_id": task["task_id"], "knowledge_subset": subset_name(fields),
                       "fields": list(fields), "precision_tier": tier, "onset_noise_sd": None if tier is None else {0.0: 0.0, .05: .02, .10: .05, .20: .10, .40: .20}[tier],
                       "fit_success": fit_success, "no_prior": fallback, "partial_rmse": score,
                       "utility_vs_fallback": fallback - score}
                for index, value in known.items():
                    row[{1: "retrieved_scale", 2: "retrieved_shape", 3: "retrieved_onset"}[index]] = value
                records.append(row)

    grouped = defaultdict(list)
    for row in records:
        grouped[(row["family"], row["knowledge_subset"], row["precision_tier"])].append(row)
    family_only = {(row["family"], row["task_id"]): row["partial_rmse"]
                   for row in records if row["knowledge_subset"] == "family_only"}
    parameter_oracle = {(row["family"], row["task_id"]): row["partial_rmse"]
                        for row in records if row["knowledge_subset"] == "onset+scale+shape" and row["precision_tier"] == 0.0}
    bootstrap_rng = np.random.default_rng(20260928)
    summary = []
    for (family_name, subset, tier), rows in sorted(grouped.items()):
        f = np.array([family_only[(family_name, row["task_id"])] for row in rows])
        p = np.array([parameter_oracle[(family_name, row["task_id"])] for row in rows])
        x = np.array([row["partial_rmse"] for row in rows])
        gap = x - p
        denominator = f.mean() - p.mean()
        closure = (f.mean() - x.mean()) / denominator
        summary.append({"family": family_name, "knowledge_subset": subset, "precision_tier": tier,
                        "onset_noise_sd": rows[0]["onset_noise_sd"], "n_tasks": len(rows),
                        "fit_success_rate": float(np.mean([row["fit_success"] for row in rows])),
                        "no_prior_rmse": float(np.mean([row["no_prior"] for row in rows])),
                        "partial_rmse": float(x.mean()), "parameter_oracle_rmse": float(p.mean()),
                        "family_only_rmse": float(f.mean()), "utility_vs_fallback": float(np.mean([row["utility_vs_fallback"] for row in rows])),
                        "gap_to_parameter_oracle": float(gap.mean()),
                        "gap_to_parameter_oracle_ci95": list(bootstrap_mean_ci(gap, bootstrap_rng)),
                        "fraction_family_parameter_gap_closed": float(closure),
                        "fraction_gap_closed_ci95": list(bootstrap_closure_ci(f, x, p, bootstrap_rng))})

    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "experiment_id": "partial_realization_knowledge_sweep_v1", "status": "development",
        "question": "Which realization fields and retrieval precisions are useful beyond a true family label?",
        "generator": {"families": list(FAMILIES), "seed": 20260926, "observability": O, "boundary": TB,
                      "tail": "t > .70 (clean, evaluation-only)", "noise_sd": NOISE, "tasks_per_family": N},
        "knowledge_model": {"fields": list(FIELDS), "subsets": [subset_name(x) for x in subsets],
                            "precision_tiers": list(NOISE_TIERS), "onset_noise_sd": [0, .02, .05, .10, .20],
                            "scale_shape_noise": "multiplicative zero-mean Gaussian relative noise"},
        "primary_endpoint": {"name": "gap_to_parameter_oracle", "definition": "RMSE(partial knowledge) - RMSE(parameter oracle)",
                             "bootstrap_resamples": BOOT},
        "summary": summary, "records": records}
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")

    FIG.mkdir(exist_ok=True)
    labels = {"family_only": "family only", "onset": "onset", "scale": "scale", "shape": "shape",
              "onset+scale": "onset + scale", "onset+shape": "onset + shape",
              "scale+shape": "scale + shape", "onset+scale+shape": "all fields"}
    family_labels = {"regime_change": "Regime change", "emergent_curvature": "Emergent curvature"}
    exact = [row for row in summary if row["precision_tier"] in (None, 0.0)]
    fig, axes = plt.subplots(1, 2, figsize=(15, 5), constrained_layout=True)
    for ax, family_name in zip(axes, FAMILIES):
        rows = [row for row in exact if row["family"] == family_name]
        rows.sort(key=lambda row: (len(row["knowledge_subset"].split("+")) if row["knowledge_subset"] != "family_only" else 0, row["knowledge_subset"]))
        x = np.arange(len(rows))
        closure = [row["fraction_family_parameter_gap_closed"] for row in rows]
        lower = [row["fraction_gap_closed_ci95"][0] for row in rows]
        upper = [row["fraction_gap_closed_ci95"][1] for row in rows]
        ax.bar(x, closure, color="#3978b8")
        ax.errorbar(x, closure, yerr=np.vstack((np.array(closure)-lower, np.array(upper)-closure)), fmt="none", color="#1b4f72", capsize=3)
        ax.axhline(0, color="#555", lw=1); ax.axhline(1, color="#43a86b", lw=1, ls="--")
        ax.set(title=f"Exact retrieved constraints: {family_labels[family_name]}", ylabel="fraction of family→parameter gap closed",
               xticks=x, xticklabels=[labels[row["knowledge_subset"]] for row in rows])
        ax.tick_params(axis="x", rotation=30)
    fig.suptitle("Which realization fields close the extrapolation gap?")
    fig.savefig(FIG / "fig13_partial_knowledge_exact_gap_closure.png", dpi=220)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    colors = {"onset": "#cc4c4c", "scale": "#3978b8", "shape": "#7353ba", "onset+scale+shape": "#43a86b"}
    for row_index, family_name in enumerate(FAMILIES):
        for col, metric in enumerate(("gap_to_parameter_oracle", "utility_vs_fallback")):
            ax = axes[row_index, col]
            for subset, color in colors.items():
                rows = sorted([row for row in summary if row["family"] == family_name and row["knowledge_subset"] == subset],
                              key=lambda row: row["precision_tier"])
                ax.plot([row["precision_tier"] for row in rows], [row[metric] for row in rows], "o-", color=color, label=labels[subset])
            ax.set(title=f"{family_labels[family_name]} — {'gap to parameter oracle' if col == 0 else 'utility vs fallback'}",
                   xlabel="relative retrieval-noise tier", ylabel="RMSE" if col == 0 else "RMSE improvement")
            ax.axhline(0, color="#555", lw=1)
            ax.legend(fontsize=7)
    fig.suptitle("Knowledge precision determines whether retrieved constraints remain useful")
    fig.savefig(FIG / "fig14_partial_knowledge_precision_sweep.png", dpi=220)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
