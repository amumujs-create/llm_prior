#!/usr/bin/env python3
"""High-exposure extension for the oracle realization decomposition."""
from __future__ import annotations

import json
import warnings
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "exposure_identifiability_extension_v1"
FIG = ROOT / "figures"
RNG = np.random.default_rng(20260924)
TB, NOISE, N, BOOT = 0.60, 0.015, 250, 2000
OBSERVABILITY = (0.5333333333, 0.60, 0.70, 0.80, 0.90)


def pospow(x, exponent):
    return np.maximum(x, 0.0) ** exponent


def regime(t, initial_rate, post_rate, exponent, onset):
    return np.where(t < onset, 1 - initial_rate * t,
                    1 - initial_rate * onset - post_rate * pospow(t - onset, exponent))


def curvature(t, initial_rate, curvature_scale, exponent, onset):
    return 1 - initial_rate * t - curvature_scale * pospow(t - onset, exponent)


FAMILIES = {
    "regime_change": {
        "function": regime, "p0": [.15, .5, 2.0, .2],
        "bounds": ([0, 0, 1.01, .01], [.8, 2, 4, .59]),
    },
    "emergent_curvature": {
        "function": curvature, "p0": [.10, .35, 2.0, .2],
        "bounds": ([0, 0, 1.01, .01], [.7, 2, 4, .59]),
    },
}


def affine_fit(t, y, x):
    slope, intercept = np.polyfit(t, y, 1)
    return slope * x + intercept


def family_fit(family_name, t, y, x):
    spec = FAMILIES[family_name]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            params, _ = curve_fit(spec["function"], t, y, p0=spec["p0"],
                                  bounds=spec["bounds"], maxfev=5000)
        return spec["function"](x, *params), params, True
    except (RuntimeError, ValueError):
        return affine_fit(t, y, x), None, False


def parameter_oracle(family_name, t, y, x, params):
    if family_name == "regime_change":
        _, post_rate, exponent, onset = params
        baseline = regime(t, 0, post_rate, exponent, onset)
        design = np.where(t < onset, t, onset)
        initial_rate = np.dot(design, baseline - y) / np.dot(design, design)
        return regime(x, initial_rate, post_rate, exponent, onset)
    _, curvature_scale, exponent, onset = params
    basis = pospow(t - onset, exponent)
    initial_rate = np.dot(t, 1 - y - curvature_scale * basis) / np.dot(t, t)
    return curvature(x, initial_rate, curvature_scale, exponent, onset)


def generate(family_name, observability, t, rng):
    onset = TB * (1 - observability)
    if family_name == "regime_change":
        params = np.array([rng.uniform(.07, .24), rng.uniform(.35, 1.0),
                           rng.uniform(1.35, 2.6), onset])
    else:
        params = np.array([rng.uniform(.05, .16), rng.uniform(.22, .60),
                           rng.uniform(1.35, 2.6), onset])
    return FAMILIES[family_name]["function"](t, *params), params


def rmse(prediction, truth):
    return float(np.sqrt(np.mean((prediction - truth) ** 2)))


def parameter_errors(fitted, truth):
    scale_relative = abs(fitted[1] - truth[1]) / truth[1]
    exponent_absolute = abs(fitted[2] - truth[2])
    onset_absolute = abs(fitted[3] - truth[3])
    normalized = np.mean([scale_relative, exponent_absolute / 1.25, onset_absolute / TB])
    return scale_relative, exponent_absolute, onset_absolute, normalized


def bootstrap_interval(values, rng):
    values = np.asarray(values)
    indices = rng.integers(0, len(values), size=(BOOT, len(values)))
    estimates = values[indices].mean(axis=1)
    return float(np.quantile(estimates, .025)), float(np.quantile(estimates, .975))


def main():
    grid = np.linspace(0, 1, 101)
    observed, tail = grid <= TB, grid > .70
    records = []
    for family_name in FAMILIES:
        for observability in OBSERVABILITY:
            for draw in range(N):
                clean, truth_params = generate(family_name, observability, grid, RNG)
                noisy = clean + RNG.normal(0, NOISE, len(grid))
                truth = clean[tail]
                family_prediction, fitted_params, fit_success = family_fit(
                    family_name, grid[observed], noisy[observed], grid[tail])
                prediction = {
                    "no_prior": affine_fit(grid[observed], noisy[observed], grid[tail]),
                    "generative_family_oracle": family_prediction,
                    "parameter_oracle": parameter_oracle(family_name, grid[observed], noisy[observed],
                                                          grid[tail], truth_params),
                    "full_information_oracle": truth,
                }
                row = {"family": family_name, "observability": observability, "draw": draw,
                       "fit_success": fit_success,
                       **{name: rmse(pred, truth) for name, pred in prediction.items()}}
                row["realization_gap"] = row["generative_family_oracle"] - row["parameter_oracle"]
                if fit_success:
                    scale_err, exponent_err, onset_err, normalized_err = parameter_errors(fitted_params, truth_params)
                    row.update({"scale_relative_error": scale_err, "exponent_absolute_error": exponent_err,
                                "onset_absolute_error": onset_err,
                                "normalized_realization_parameter_error": normalized_err})
                else:
                    row.update({"scale_relative_error": None, "exponent_absolute_error": None,
                                "onset_absolute_error": None, "normalized_realization_parameter_error": None})
                records.append(row)

    grouped = defaultdict(list)
    for row in records:
        grouped[(row["family"], row["observability"])].append(row)
    summary, bootstrap_rng = [], np.random.default_rng(20260925)
    metrics = ("no_prior", "generative_family_oracle", "parameter_oracle", "full_information_oracle")
    errors = ("scale_relative_error", "exponent_absolute_error", "onset_absolute_error",
              "normalized_realization_parameter_error")
    for (family_name, observability), rows in sorted(grouped.items()):
        gap_values = [row["realization_gap"] for row in rows]
        successful = [row for row in rows if row["fit_success"]]
        gap_ci = bootstrap_interval(gap_values, bootstrap_rng)
        summary.append({"family": family_name, "observability": observability,
                        "onset": TB * (1 - observability), "n_tasks": len(rows),
                        "fit_success_rate": float(np.mean([row["fit_success"] for row in rows])),
                        **{name: float(np.mean([row[name] for row in rows])) for name in metrics},
                        "realization_gap": float(np.mean(gap_values)),
                        "realization_gap_ci95": list(gap_ci),
                        "practical_convergence": bool(gap_ci[1] <= .01),
                        **{name: float(np.mean([row[name] for row in successful])) if successful else None
                           for name in errors}})

    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "experiment_id": "exposure_identifiability_extension_v1", "status": "development",
        "question": "Does the generative-family oracle converge to the parameter oracle under much longer exposure?",
        "generator": {"families": list(FAMILIES), "seed": 20260924, "boundary": TB,
                      "tail": "t > .70 (clean, evaluation-only)", "noise_sd": NOISE,
                      "draws_per_family_level": N, "observability_levels": OBSERVABILITY},
        "methods": {"generative_family_oracle": "correct family only; all parameters fitted from noisy prefix",
                    "parameter_oracle": "true onset, post-onset scale, exponent; initial rate fitted from prefix",
                    "full_information_oracle": "clean generator prediction, zero-error reference by construction"},
        "primary_endpoint": {"name": "realization_gap",
                           "definition": "RMSE(generative-family oracle) - RMSE(parameter oracle)",
                           "bootstrap_resamples": BOOT,
                           "practical_convergence_rule": "upper paired bootstrap 95% CI <= 0.01"},
        "summary": summary, "records": records}
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")

    FIG.mkdir(exist_ok=True)
    labels = {"regime_change": "Regime change", "emergent_curvature": "Emergent curvature"}
    colors = {"no_prior": "#777777", "generative_family_oracle": "#cc4c4c",
              "parameter_oracle": "#3978b8", "full_information_oracle": "#43a86b"}
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for col, family_name in enumerate(FAMILIES):
        rows = [row for row in summary if row["family"] == family_name]
        x = [row["observability"] for row in rows]
        ax = axes[0, col]
        for metric in colors:
            ax.plot(x, [row[metric] for row in rows], "o-", color=colors[metric], label=metric.replace("_", " "))
        ax.set(title=labels[family_name], xlabel="post-onset observability", ylabel="far-OOD RMSE")
        ax.legend(fontsize=7)
        ax = axes[1, col]
        gap = np.array([row["realization_gap"] for row in rows])
        lower = np.array([row["realization_gap_ci95"][0] for row in rows])
        upper = np.array([row["realization_gap_ci95"][1] for row in rows])
        ax.errorbar(x, gap, yerr=np.vstack((gap - lower, upper - gap)), fmt="o-", color="#cc4c4c",
                    label="family − parameter")
        ax.axhline(.01, color="#333333", lw=1, ls="--", label="pre-specified convergence rule")
        ax.set(title=f"Realization gap: {labels[family_name]}", xlabel="post-onset observability", ylabel="RMSE gap")
        ax.legend(fontsize=7)
    fig.suptitle("Extended exposure tests whether visible structure becomes identifiable")
    fig.savefig(FIG / "fig11_exposure_identifiability_extension.png", dpi=220)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for ax, family_name in zip(axes, FAMILIES):
        rows = [row for row in summary if row["family"] == family_name]
        ax.plot([row["observability"] for row in rows],
                [row["normalized_realization_parameter_error"] for row in rows], "o-", color="#7353ba")
        ax.set(title=f"Family-fit parameter error: {labels[family_name]}",
               xlabel="post-onset observability", ylabel="normalized realization-parameter error")
    fig.suptitle("Mechanism check: exposure improves parameter identification")
    fig.savefig(FIG / "fig12_exposure_parameter_identification.png", dpi=220)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
