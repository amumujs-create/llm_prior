#!/usr/bin/env python3
"""Frozen E2: capacity-matched and capacity-stress structural selection."""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from prior_evaluation_metric_v1 import (BANDS, CANDIDATES, INNER, NOISES, OBS,
    ORDER, PARAMETERS, SEED, TB, compatible, fit, generate)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "residual_capacity_stress_v1"
FIG = ROOT / "figures"
N, BOOT, RIDGE = 100, 2000, 1e-5
RATIOS = {"matched": 1, "stress_2x": 2, "stress_4x": 4}


def basis(t, q):
    """Polynomial correction with columns standardized on the fit subset."""
    return np.column_stack([np.asarray(t, dtype=float) ** degree for degree in range(1, q + 1)])


def residual_predict(train_t, residual, target_t, q):
    x = basis(train_t, q)
    scale = np.sqrt(np.mean(x * x, axis=0))
    scale[scale < 1e-12] = 1.
    x = x / scale
    coeff = np.linalg.solve(x.T @ x + RIDGE * np.eye(q), x.T @ residual)
    return basis(target_t, q) / scale @ coeff


def q_for(family, candidate, ratio):
    if candidate == "P0" or compatible(family, candidate):
        return 4
    return 4 * ratio


def selection_score(name, observed, predicted, p):
    mse = float(np.mean((observed - predicted) ** 2))
    if name == "mse":
        return -mse
    return -float(len(observed) * math.log(mse + 1e-12) + p * math.log(len(observed)))


def choose(scores):
    return max(CANDIDATES, key=lambda c: (scores[c], -ORDER[c]))


def ci(values, rng):
    x = np.asarray(values, dtype=float)
    draws = x[rng.integers(0, len(x), size=(BOOT, len(x)))].mean(axis=1)
    return [float(v) for v in np.quantile(draws, [.025, .975])]


def make_figures(pooled):
    FIG.mkdir(parents=True, exist_ok=True)
    selectors = ("mse", "bic")
    ratio_values = [1, 2, 4]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    for selector, color in zip(selectors, ("#cc4c4c", "#555555")):
        rows = [r for r in pooled if r["selector"] == selector and r["band"] == "D3"]
        rows.sort(key=lambda r: ratio_values.index(r["capacity_ratio"]))
        axes[0].plot([r["capacity_ratio"] for r in rows], [r["incompatible_selection_rate"] for r in rows], "o-", color=color, label=selector.upper())
        axes[1].plot([r["capacity_ratio"] for r in rows], [r["mean_regret"] for r in rows], "o-", color=color, label=selector.upper())
    axes[0].set(title="Does residual capacity induce incompatible selection?", xlabel="q wrong / q compatible", ylabel="incompatible selection rate", xticks=ratio_values, ylim=(0, 1))
    axes[1].set(title="Far-OOD selection regret under capacity stress", xlabel="q wrong / q compatible", ylabel="D3 regret (RMSE)", xticks=ratio_values)
    for ax in axes: ax.legend()
    fig.savefig(FIG / "fig17_residual_capacity_stress.png", dpi=220)
    plt.close(fig)


def main():
    rng = np.random.default_rng(SEED + 10)
    t = np.round(np.arange(0., 1.301, .01), 4)
    observed, inner, pseudo = t <= TB, t <= INNER, (t > INNER) & (t <= TB)
    masks = {name: (t >= low) & (t <= high) for name, (low, high) in BANDS.items()}
    records, task_id = [], 0
    for family, levels in OBS.items():
        for level_name, level in levels.items():
            for noise in NOISES:
                for _ in range(N):
                    clean, meta = generate(family, level, t, rng)
                    noisy = clean.copy(); noisy[observed] += rng.normal(0, noise, observed.sum())
                    base_inner = {c: fit(c, t[inner], noisy[inner], t) for c in CANDIDATES}
                    base_full = {c: fit(c, t[observed], noisy[observed], t) for c in CANDIDATES}
                    for condition, ratio in RATIOS.items():
                        pseudo_final, full_final, residual_meta = {}, {}, {}
                        for candidate in CANDIDATES:
                            q = q_for(family, candidate, ratio)
                            rin = noisy[inner] - base_inner[candidate][inner]
                            rfull = noisy[observed] - base_full[candidate][observed]
                            rpseudo = residual_predict(t[inner], rin, t[pseudo], q)
                            rall = residual_predict(t[observed], rfull, t, q)
                            pseudo_final[candidate] = base_inner[candidate][pseudo] + rpseudo
                            full_final[candidate] = base_full[candidate] + rall
                            prior_diff = np.diff(base_inner[candidate][pseudo])
                            final_diff = np.diff(pseudo_final[candidate])
                            residual_meta[candidate] = {"q": q,
                                "residual_ratio": float(np.linalg.norm(rpseudo) / (np.linalg.norm(base_inner[candidate][pseudo]) + 1e-12)),
                                "direction_override_rate": float(np.mean(np.sign(prior_diff) != np.sign(final_diff)))}
                        for selector in ("mse", "bic"):
                            scores = {c: selection_score(selector, noisy[pseudo], pseudo_final[c], PARAMETERS[c] + residual_meta[c]["q"]) for c in CANDIDATES}
                            selected = choose(scores)
                            for band, mask in masks.items():
                                rmses = {c: float(np.sqrt(np.mean((full_final[c][mask] - clean[mask]) ** 2))) for c in CANDIDATES}
                                winner = min(CANDIDATES, key=lambda c: (rmses[c], ORDER[c]))
                                records.append({"task_id": task_id, "family": family, "observability_level": level_name, "observability": meta["observability"], "noise_sd": noise,
                                                "condition": condition, "capacity_ratio": ratio, "selector": selector, "band": band,
                                                "selected": selected, "far_winner": winner, "selected_rmse": rmses[selected], "best_rmse": rmses[winner], "regret": rmses[selected]-rmses[winner],
                                                "incompatible": bool(selected != "P0" and not compatible(family, selected)), "winner_disagreement": selected != winner,
                                                "selected_q": residual_meta[selected]["q"], "selected_residual_ratio": residual_meta[selected]["residual_ratio"], "selected_direction_override_rate": residual_meta[selected]["direction_override_rate"]})
                    task_id += 1
    grouped = defaultdict(list)
    for row in records: grouped[(row["family"], row["condition"], row["capacity_ratio"], row["selector"], row["band"])].append(row)
    brng = np.random.default_rng(SEED + 11)
    summary = []
    for key, rows in sorted(grouped.items()):
        family, condition, ratio, selector, band = key; regrets = [r["regret"] for r in rows]
        summary.append({"family": family, "condition": condition, "capacity_ratio": ratio, "selector": selector, "band": band, "n": len(rows), "mean_regret": float(np.mean(regrets)), "regret_ci95": ci(regrets, brng), "incompatible_selection_rate": float(np.mean([r["incompatible"] for r in rows])), "winner_disagreement_rate": float(np.mean([r["winner_disagreement"] for r in rows])), "mean_selected_residual_ratio": float(np.mean([r["selected_residual_ratio"] for r in rows])), "mean_selected_direction_override_rate": float(np.mean([r["selected_direction_override_rate"] for r in rows]))})
    pooled_groups = defaultdict(list)
    for row in records: pooled_groups[(row["condition"], row["capacity_ratio"], row["selector"], row["band"])].append(row)
    pooled = []
    for key, rows in sorted(pooled_groups.items()):
        condition, ratio, selector, band = key; regrets = [r["regret"] for r in rows]
        pooled.append({"condition": condition, "capacity_ratio": ratio, "selector": selector, "band": band, "n": len(rows), "mean_regret": float(np.mean(regrets)), "regret_ci95": ci(regrets, brng), "incompatible_selection_rate": float(np.mean([r["incompatible"] for r in rows])), "mean_selected_residual_ratio": float(np.mean([r["selected_residual_ratio"] for r in rows])), "mean_selected_direction_override_rate": float(np.mean([r["selected_direction_override_rate"] for r in rows]))})
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {"experiment_id": "residual_capacity_stress_v1", "status": "development", "protocol": "RESIDUAL_CAPACITY_STRESS_PROTOCOL_V1.md", "n_base_tasks": task_id, "n_capacity_cases": task_id*len(RATIOS), "ridge": RIDGE, "summary": summary, "pooled_summary": pooled, "records": records}
    (OUT / "results.json").write_text(json.dumps(payload, indent=2) + "\n")
    make_figures(pooled)
    print(json.dumps(pooled, indent=2))


if __name__ == "__main__": main()
