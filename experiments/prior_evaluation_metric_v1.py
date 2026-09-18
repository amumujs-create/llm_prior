#!/usr/bin/env python3
"""Frozen E1: independent pseudo-OOD metrics for structural-prior selection."""
from __future__ import annotations

import json
import math
import warnings
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "prior_evaluation_metric_v1"
FIG = ROOT / "figures"
SEED, TB, INNER, N, BOOT = 20261001, .60, .45, 100, 2000
NOISES = (.005, .015, .030)
BANDS = {"D1": (.70, .80), "D2": (.90, 1.00), "D3": (1.20, 1.30)}
CANDIDATES = ("P0", "PD", "PC", "PB", "PT")
ORDER = {name: index for index, name in enumerate(CANDIDATES)}
PARAMETERS = {"P0": 2, "PD": 2, "PC": 3, "PB": 2, "PT": 4}
OBS = {
    "regime_change": {"low": .59, "mid": .48, "high": .32},
    "emergent_curvature": {"low": .59, "mid": .48, "high": .32},
    "asymptotic_bound": {"low": .35, "mid": 1.50, "high": 3.50},
}


def pospow(x, exponent):
    return np.maximum(x, 0.) ** exponent


def regime(t, k1, k2, alpha, tau):
    return np.where(t < tau, 1 - k1 * t,
                    1 - k1 * tau - k2 * pospow(t - tau, alpha))


def curvature(t, k1, k2, alpha, tau):
    return 1 - k1 * t - k2 * pospow(t - tau, alpha)


def bound(t, lower, rate):
    return lower + (1 - lower) * np.exp(-rate * t)


def affine(t, slope, intercept):
    return slope * t + intercept


def concave_quadratic(t, a, b, c):
    return a + b * t + c * t * t


def compatible(generator, candidate):
    if candidate in ("P0", "PD"):
        return True
    return {"regime_change": {"PC", "PT"},
            "emergent_curvature": {"PC"},
            "asymptotic_bound": {"PB"}}[generator].__contains__(candidate)


def generate(generator, level, t, rng):
    if generator == "regime_change":
        params = (rng.uniform(.07, .24), rng.uniform(.35, 1.0), rng.uniform(1.35, 2.60), level)
        return regime(t, *params), {"onset": level, "observability": max(0., (TB - level) / TB)}
    if generator == "emergent_curvature":
        params = (rng.uniform(.05, .16), rng.uniform(.22, .60), rng.uniform(1.35, 2.60), level)
        return curvature(t, *params), {"onset": level, "observability": max(0., (TB - level) / TB)}
    clean = bound(t, rng.uniform(.20, .70), level)
    return clean, {"rate": level, "observability": 1 - float(np.exp(-level * TB))}


def fit(candidate, t, y, target):
    """Fit a fixed capacity candidate. Fall back to local affine only on failure."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if candidate == "P0":
                pars, _ = curve_fit(affine, t, y, p0=(-.2, 1.), maxfev=1200)
                return affine(target, *pars)
            if candidate == "PD":
                pars, _ = curve_fit(affine, t, y, p0=(-.2, 1.), bounds=([-4., -2.], [0., 3.]), maxfev=1200)
                return affine(target, *pars)
            if candidate == "PC":
                pars, _ = curve_fit(concave_quadratic, t, y, p0=(1., -.1, -.1),
                                    bounds=([-.5, -4., -8.], [2.5, 0., 0.]), maxfev=1800)
                return concave_quadratic(target, *pars)
            if candidate == "PB":
                pars, _ = curve_fit(bound, t, y, p0=(.45, 1.5), bounds=([-.5, .005], [.98, 12.]), maxfev=1800)
                return bound(target, *pars)
            pars, _ = curve_fit(regime, t, y, p0=(.15, .55, 2., .45),
                                bounds=([0., 0., 1.01, .05], [.8, 2., 4., .599]), maxfev=2600)
            return regime(target, *pars)
    except (RuntimeError, ValueError, FloatingPointError):
        slope, intercept = np.polyfit(t, y, 1)
        return affine(target, slope, intercept)


def cosine(a, b):
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return 0. if denom < 1e-12 else float(np.dot(a, b) / denom)


def score(metric, observed, predicted, parameter_count):
    err = observed - predicted
    mse = float(np.mean(err ** 2))
    if metric == "mse":
        return -mse
    if metric == "delta_cosine":
        return cosine(np.diff(observed), np.diff(predicted))
    if metric == "delta2_cosine":
        return cosine(np.diff(observed, 2), np.diff(predicted, 2))
    if metric == "derivative_sign":
        return float(np.mean(np.sign(np.diff(observed)) == np.sign(np.diff(predicted))))
    if metric == "spearman":
        val = spearmanr(observed, predicted).statistic
        return float(val) if np.isfinite(val) else -1.
    n = len(observed)
    return -float(n * math.log(mse + 1e-12) + parameter_count * math.log(n))


def bootstrap_ci(values, rng):
    x = np.asarray(values, dtype=float)
    idx = rng.integers(0, len(x), size=(BOOT, len(x)))
    means = x[idx].mean(axis=1)
    return [float(v) for v in np.quantile(means, [.025, .975])]


def pick(scores):
    return max(CANDIDATES, key=lambda k: (scores[k], -ORDER[k]))


def summarize(records):
    grouped = defaultdict(list)
    for row in records:
        grouped[(row["family"], row["observability_level"], row["noise_sd"], row["metric"], row["band"])].append(row)
    rng = np.random.default_rng(SEED + 1)
    result = []
    for key, rows in sorted(grouped.items()):
        family, level, noise, metric, band = key
        regrets = [r["regret"] for r in rows]
        result.append({"family": family, "observability_level": level, "noise_sd": noise,
                       "metric": metric, "band": band, "n": len(rows),
                       "mean_regret": float(np.mean(regrets)), "regret_ci95": bootstrap_ci(regrets, rng),
                       "incompatible_selection_rate": float(np.mean([r["incompatible"] for r in rows])),
                       "winner_disagreement_rate": float(np.mean([r["winner_disagreement"] for r in rows])),
                       "mean_selected_rmse": float(np.mean([r["selected_rmse"] for r in rows])),
                       "mean_best_rmse": float(np.mean([r["best_rmse"] for r in rows]))})
    pooled = defaultdict(list)
    for row in records:
        pooled[(row["metric"], row["band"])].append(row)
    pooled_summary = []
    for (metric, band), rows in sorted(pooled.items()):
        regrets = [r["regret"] for r in rows]
        pooled_summary.append({"metric": metric, "band": band, "n": len(rows),
                               "mean_regret": float(np.mean(regrets)), "regret_ci95": bootstrap_ci(regrets, rng),
                               "incompatible_selection_rate": float(np.mean([r["incompatible"] for r in rows])),
                               "winner_disagreement_rate": float(np.mean([r["winner_disagreement"] for r in rows]))})
    return result, pooled_summary


def figures(pooled, summary):
    FIG.mkdir(parents=True, exist_ok=True)
    metrics = ("mse", "delta_cosine", "delta2_cosine", "derivative_sign", "spearman", "bic")
    labels = {"mse": "MSE", "delta_cosine": "Δ cosine", "delta2_cosine": "Δ² cosine",
              "derivative_sign": "sign agreement", "spearman": "Spearman", "bic": "BIC"}
    colors = ["#cc4c4c", "#3978b8", "#7353ba", "#43a86b", "#dd7f28", "#555555"]
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    for metric, color in zip(metrics, colors):
        rows = [r for r in pooled if r["metric"] == metric]
        rows.sort(key=lambda r: ("D1", "D2", "D3").index(r["band"]))
        x = np.arange(3)
        y = np.array([r["mean_regret"] for r in rows])
        ci = np.array([r["regret_ci95"] for r in rows])
        ax.plot(x, y, "o-", label=labels[metric], color=color)
        ax.fill_between(x, ci[:, 0], ci[:, 1], color=color, alpha=.10)
    ax.set(xticks=np.arange(3), xticklabels=["D1: .70–.80", "D2: .90–1.00", "D3: 1.20–1.30"],
           xlabel="far-OOD distance band", ylabel="selection regret (RMSE)",
           title="Pseudo-OOD selection regret by evaluation metric")
    ax.axhline(0, color="#555", lw=1); ax.legend(ncol=2, fontsize=9)
    fig.savefig(FIG / "fig15_prior_metric_regret_by_distance.png", dpi=220)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), constrained_layout=True)
    rows = [r for r in pooled if r["band"] == "D3"]
    rows.sort(key=lambda r: metrics.index(r["metric"]))
    axes[0].bar(np.arange(len(rows)), [r["incompatible_selection_rate"] for r in rows], color=colors)
    axes[0].set(title="Incompatible-prior selection at farthest band", ylabel="rate", ylim=(0, 1),
                xticks=np.arange(len(rows)), xticklabels=[labels[r["metric"]] for r in rows])
    axes[0].tick_params(axis="x", rotation=35)
    axes[1].bar(np.arange(len(rows)), [r["winner_disagreement_rate"] for r in rows], color=colors)
    axes[1].set(title="Pseudo-OOD / far-OOD winner disagreement", ylabel="rate", ylim=(0, 1),
                xticks=np.arange(len(rows)), xticklabels=[labels[r["metric"]] for r in rows])
    axes[1].tick_params(axis="x", rotation=35)
    fig.savefig(FIG / "fig16_prior_metric_selection_risk.png", dpi=220)
    plt.close(fig)


def main():
    rng = np.random.default_rng(SEED)
    t = np.round(np.arange(0., 1.301, .01), 4)
    inner, pseudo = t <= INNER, (t > INNER) & (t <= TB)
    bands = {name: (t >= low) & (t <= high) for name, (low, high) in BANDS.items()}
    metrics = ("mse", "delta_cosine", "delta2_cosine", "derivative_sign", "spearman", "bic")
    records = []
    task_id = 0
    for family, levels in OBS.items():
        for level_name, level in levels.items():
            for noise in NOISES:
                for _ in range(N):
                    clean, meta = generate(family, level, t, rng)
                    noisy = clean.copy()
                    noisy[t <= TB] += rng.normal(0., noise, np.sum(t <= TB))
                    pseudo_pred = {candidate: fit(candidate, t[inner], noisy[inner], t[pseudo]) for candidate in CANDIDATES}
                    pseudo_scores = {metric: {candidate: score(metric, noisy[pseudo], pseudo_pred[candidate], PARAMETERS[candidate])
                                               for candidate in CANDIDATES} for metric in metrics}
                    far_pred = {candidate: fit(candidate, t[t <= TB], noisy[t <= TB], t) for candidate in CANDIDATES}
                    for metric in metrics:
                        chosen = pick(pseudo_scores[metric])
                        for band_name, mask in bands.items():
                            rmses = {candidate: float(np.sqrt(np.mean((far_pred[candidate][mask] - clean[mask]) ** 2))) for candidate in CANDIDATES}
                            winner = min(CANDIDATES, key=lambda k: (rmses[k], ORDER[k]))
                            records.append({"task_id": task_id, "family": family, "observability_level": level_name,
                                            "observability": meta["observability"], "noise_sd": noise, "metric": metric,
                                            "band": band_name, "selected": chosen, "far_winner": winner,
                                            "selected_rmse": rmses[chosen], "best_rmse": rmses[winner],
                                            "regret": rmses[chosen] - rmses[winner],
                                            "incompatible": bool(chosen != "P0" and not compatible(family, chosen)),
                                            "winner_disagreement": chosen != winner,
                                            "pseudo_scores": pseudo_scores[metric]})
                    task_id += 1
    summary, pooled = summarize(records)
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {"experiment_id": "prior_evaluation_metric_v1", "status": "development", "protocol": "PRIOR_EVALUATION_METRIC_PROTOCOL_V1.md",
               "seed": SEED, "n_tasks": task_id, "metrics": metrics, "candidates": CANDIDATES,
               "distance_bands": BANDS, "summary": summary, "pooled_summary": pooled, "records": records}
    (OUT / "results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    figures(pooled, summary)
    print(json.dumps(pooled, indent=2))


if __name__ == "__main__":
    main()
