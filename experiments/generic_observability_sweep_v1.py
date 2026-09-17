#!/usr/bin/env python3
"""Domain-neutral observability sweep for structural extrapolation priors."""
from __future__ import annotations

import json
import warnings
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "generic_observability_sweep_v1"
FIG = ROOT / "figures"
SEED, TB, NOISE_SD, N_PER_LEVEL = 20260919, 0.60, 0.015, 60
TAU_LEVELS = (0.78, 0.68, 0.60, 0.55, 0.48, 0.38, 0.28)
EXPOSURE_LEVELS = (0.10, 0.25, 0.50, 0.90, 1.50, 2.30, 3.20)
WINDOWS = ((0.25, 0.40), (0.40, 0.50), (0.50, 0.60))
TAIL_WEIGHTS = np.array((0.10, 0.25, 0.65))
FAMILIES = ("regime_change", "emergent_curvature", "asymptotic_bound")
CONTRAST = {"regime_change": "asymptotic_bound", "emergent_curvature": "asymptotic_bound", "asymptotic_bound": "emergent_curvature"}


def pospow(x: np.ndarray, alpha: float) -> np.ndarray:
    return np.maximum(x, 0.0) ** alpha


def linear(t: np.ndarray, k: float) -> np.ndarray:
    return 1.0 - k * t


def regime_change(t: np.ndarray, k1: float, k2: float, alpha: float, tau: float) -> np.ndarray:
    at_tau = 1.0 - k1 * tau
    return np.where(t < tau, 1.0 - k1 * t, at_tau - k2 * pospow(t - tau, alpha))


def emergent_curvature(t: np.ndarray, k1: float, k2: float, alpha: float, tau: float) -> np.ndarray:
    return 1.0 - k1 * t - k2 * pospow(t - tau, alpha)


def asymptotic_bound(t: np.ndarray, lower: float, rate: float) -> np.ndarray:
    return lower + (1.0 - lower) * np.exp(-rate * t)


FITS = {
    "regime_change": (regime_change, [0.18, 0.55, 2.0, 0.50], ([0., 0., 1.01, .15], [.8, 2., 4., .90])),
    "emergent_curvature": (emergent_curvature, [.12, .35, 2., .50], ([0., 0., 1.01, .15], [.7, 2., 4., .90])),
    "asymptotic_bound": (asymptotic_bound, [.50, 1.5], ([0., .01], [.95, 10.])),
}


def fit_predict(family: str, tx: np.ndarray, yx: np.ndarray, target: np.ndarray) -> np.ndarray:
    if family == "linear_fallback":
        slope, intercept = np.polyfit(tx, yx, 1)
        return slope * target + intercept
    fn, p0, bounds = FITS[family]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pars, _ = curve_fit(fn, tx, yx, p0=p0, bounds=bounds, maxfev=3000)
        pred = fn(target, *pars)
        if not np.all(np.isfinite(pred)):
            raise FloatingPointError
        return pred
    except (RuntimeError, ValueError, FloatingPointError):
        return fit_predict("linear_fallback", tx, yx, target)


def pseudo_losses(candidates: tuple[str, ...], t: np.ndarray, y: np.ndarray) -> tuple[dict[str, float], dict[str, list[float]]]:
    losses: dict[str, float] = {}
    per_window: dict[str, list[float]] = {}
    for candidate in candidates:
        vals = []
        for train_end, valid_end in WINDOWS:
            tr, va = t <= train_end, (t > train_end) & (t <= valid_end)
            pred = fit_predict(candidate, t[tr], y[tr], t[va])
            vals.append(float(np.mean((pred - y[va]) ** 2)))
        per_window[candidate] = vals
        losses[candidate] = float(np.mean(vals))
    return losses, per_window


def generate(family: str, level: float, t: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, float]:
    if family == "regime_change":
        return regime_change(t, rng.uniform(.07, .24), rng.uniform(.35, 1.0), rng.uniform(1.35, 2.60), level), max(0., (TB - level) / TB)
    if family == "emergent_curvature":
        return emergent_curvature(t, rng.uniform(.05, .16), rng.uniform(.22, .60), rng.uniform(1.35, 2.60), level), max(0., (TB - level) / TB)
    return asymptotic_bound(t, rng.uniform(.20, .70), level / TB), 1.0 - float(np.exp(-level))


def ci(values: np.ndarray, rng: np.random.Generator, n: int = 2000) -> list[float]:
    samples = np.empty(n)
    for i in range(n):
        samples[i] = rng.choice(values, len(values), replace=True).mean()
    return [float(x) for x in np.quantile(samples, (.025, .975))]


def r(x: float) -> float:
    return float(round(x, 6))


def build_figures(summary: list[dict], records: list[dict]) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    colors = {"regime_change": "#cc4c4c", "emergent_curvature": "#3978b8", "asymptotic_bound": "#43a86b"}
    labels = {"regime_change": "Regime change", "emergent_curvature": "Emergent curvature", "asymptotic_bound": "Asymptotic bound"}
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.8), constrained_layout=True)
    for ax, family in zip(axes, FAMILIES):
        rows = sorted((z for z in summary if z["family"] == family), key=lambda z: z["observability"])
        x = np.array([z["observability"] for z in rows])
        y = np.array([z["oracle_utility"] for z in rows])
        band = np.array([z["oracle_utility_ci"] for z in rows])
        ax.axhline(0, color="#555", lw=1)
        ax.plot(x, y, "o-", color=colors[family], lw=2)
        ax.fill_between(x, band[:, 0], band[:, 1], color=colors[family], alpha=.18)
        ax.set(title=labels[family], xlabel="true observability", ylabel="prior utility\n(RMSE fallback − RMSE prior)")
    fig.suptitle("A true prior becomes useful only after its evidence is observable", fontsize=14)
    fig.savefig(FIG / "fig01_observability_to_utility.png", dpi=220)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(14, 3.8), constrained_layout=True)
    for index, (ax, family) in enumerate(zip(axes, FAMILIES)):
        rows = sorted((z for z in summary if z["family"] == family), key=lambda z: z["observability"])
        x = np.array([z["observability"] for z in rows])
        ax.plot(x, [z["uniform_admit_rate"] for z in rows], "o-", label="uniform gate", color="#7a5195")
        ax.plot(x, [z["tail_admit_rate"] for z in rows], "o-", label="tail-weighted gate", color="#ef8a3a")
        ax.set(title=labels[family], xlabel="true observability", ylabel="admit probability", ylim=(-.05, 1.05))
        ax.legend(fontsize=8)
    fig.suptitle("Admission must distinguish low-O rejection from high-O acceptance", fontsize=14)
    fig.savefig(FIG / "fig02_admission_rates.png", dpi=220)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(14, 3.8), constrained_layout=True)
    for index, (ax, family) in enumerate(zip(axes, FAMILIES)):
        rows = [z for z in records if z["family"] == family]
        jitter = np.random.default_rng(SEED + index).normal(0, .006, len(rows))
        x = np.array([z["observability"] for z in rows]) + jitter
        ax.axhline(0, color="#555", lw=1)
        ax.scatter(x, [z["uniform_score"] for z in rows], s=8, alpha=.30, color="#7a5195", label="uniform A")
        ax.scatter(x, [z["tail_score"] for z in rows], s=8, alpha=.24, color="#ef8a3a", label="tail A")
        ax.set(title=labels[family], xlabel="true observability", ylabel="pseudo-OOD improvement score")
        ax.legend(fontsize=8)
    fig.suptitle("Does the validation score measure observability?", fontsize=14)
    fig.savefig(FIG / "fig03_score_diagnostic.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 4.1), constrained_layout=True)
    ax.axis("off")
    stages = [("1", "True structure", "Family matches the generator"), ("2", "Observable evidence", "Diagnostic shape is in prefix"), ("3", "Admission", "Score accepts or rejects prior"), ("4", "Far-OOD utility", "Tail error validates outcome")]
    for i, (number, title, desc) in enumerate(stages):
        x = .03 + i * .245
        ax.text(x, .58, number, fontsize=20, color="white", ha="center", va="center", bbox=dict(boxstyle="circle", facecolor="#255f85", edgecolor="none"))
        ax.text(x + .04, .68, title, fontsize=13, weight="bold", ha="left")
        ax.text(x + .04, .38, desc, fontsize=10, ha="left", wrap=True)
        if i < 3:
            ax.annotate("", xy=(x + .22, .58), xytext=(x + .12, .58), arrowprops=dict(arrowstyle="->", lw=2, color="#6d7880"))
    ax.text(.5, .09, "Key distinction: truth alone does not license use; observability must be established before utility can be expected.", ha="center", fontsize=12, style="italic")
    fig.savefig(FIG / "fig04_experiment_logic.png", dpi=220)
    plt.close(fig)


def main() -> None:
    rng = np.random.default_rng(SEED)
    t = np.linspace(0., 1., 101)
    observed, tail = t <= TB, t > .70
    levels = {"regime_change": TAU_LEVELS, "emergent_curvature": TAU_LEVELS, "asymptotic_bound": EXPOSURE_LEVELS}
    records: list[dict] = []
    for family, sweep in levels.items():
        contrast = CONTRAST[family]
        for level in sweep:
            for _ in range(N_PER_LEVEL):
                clean, obs = generate(family, level, t, rng)
                noisy = clean + rng.normal(0., NOISE_SD, len(t))
                candidates = ("linear_fallback", family, contrast)
                pseudo, per_window = pseudo_losses(candidates, t[observed], noisy[observed])
                uniform_score = pseudo["linear_fallback"] - pseudo[family]
                tail_score = float(np.dot(TAIL_WEIGHTS, np.array(per_window["linear_fallback"]) - np.array(per_window[family])))
                uniform_admit, tail_admit = uniform_score > 0., tail_score > 0.
                chosen = min(candidates, key=lambda x: (pseudo[x], x))
                preds = {name: fit_predict(name, t[observed], noisy[observed], t[tail]) for name in candidates}
                preds["candidate_select_uniform"] = fit_predict(chosen, t[observed], noisy[observed], t[tail])
                preds["oracle_gate_uniform"] = preds[family] if uniform_admit else preds["linear_fallback"]
                preds["oracle_gate_tail"] = preds[family] if tail_admit else preds["linear_fallback"]
                rmse = {name: float(np.sqrt(np.mean((pred - clean[tail]) ** 2))) for name, pred in preds.items()}
                records.append({"family": family, "level": float(level), "observability": obs, "uniform_score": uniform_score, "tail_score": tail_score, "uniform_admit": uniform_admit, "tail_admit": tail_admit, "oracle_utility": rmse["linear_fallback"] - rmse[family], **{f"rmse_{k}": v for k, v in rmse.items()}})

    groups: dict[tuple[str, float], list[dict]] = defaultdict(list)
    by_family: dict[str, list[dict]] = defaultdict(list)
    for row in records:
        groups[(row["family"], row["level"])].append(row)
        by_family[row["family"]].append(row)
    brng = np.random.default_rng(SEED + 1)
    summary = []
    for (family, level), rows in groups.items():
        util = np.array([z["oracle_utility"] for z in rows])
        metrics = ("linear_fallback", family, CONTRAST[family], "candidate_select_uniform", "oracle_gate_uniform", "oracle_gate_tail")
        summary.append({"family": family, "sweep_level": level, "observability": r(rows[0]["observability"]), "oracle_utility": r(util.mean()), "oracle_utility_ci": [r(x) for x in ci(util, brng)], "uniform_admit_rate": r(np.mean([z["uniform_admit"] for z in rows])), "tail_admit_rate": r(np.mean([z["tail_admit"] for z in rows])), "mean_rmse": {metric: r(np.mean([z[f"rmse_{metric}"] for z in rows])) for metric in metrics}})
    family_summary = {}
    for family, rows in by_family.items():
        o = np.array([z["observability"] for z in rows])
        family_summary[family] = {"n": len(rows), "spearman_O_utility": r(spearmanr(o, [z["oracle_utility"] for z in rows]).statistic), "spearman_O_uniform_score": r(spearmanr(o, [z["uniform_score"] for z in rows]).statistic), "spearman_O_tail_score": r(spearmanr(o, [z["tail_score"] for z in rows]).statistic)}
    zero = [z for z in records if z["observability"] == 0.]
    all_o = [z["observability"] for z in records]
    result = {"experiment_id": "generic_observability_sweep_v1", "evidence_status": "development", "seed": SEED, "n_total": len(records), "n_per_level": N_PER_LEVEL, "contract": {"boundary": TB, "far_ood_tail": "t > .70", "noise_sd": NOISE_SD, "tail_weights": TAIL_WEIGHTS.tolist()}, "sweep_summary": sorted(summary, key=lambda z: (z["family"], z["sweep_level"])), "family_summary": family_summary, "pooled": {"spearman_O_utility": r(spearmanr(all_o, [z["oracle_utility"] for z in records]).statistic), "spearman_O_uniform_score": r(spearmanr(all_o, [z["uniform_score"] for z in records]).statistic), "spearman_O_tail_score": r(spearmanr(all_o, [z["tail_score"] for z in records]).statistic), "zero_O_n": len(zero), "uniform_reject_rate_at_zero_O": r(1 - np.mean([z["uniform_admit"] for z in zero])), "tail_reject_rate_at_zero_O": r(1 - np.mean([z["tail_admit"] for z in zero]))}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    build_figures(summary, records)
    print(json.dumps({"family_summary": family_summary, "pooled": result["pooled"]}, indent=2))


if __name__ == "__main__":
    main()
