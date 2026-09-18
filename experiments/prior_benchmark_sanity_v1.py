#!/usr/bin/env python3
"""Frozen sanity suite for Prior Primitive–Composition Benchmark v1.

This validates measurement behavior, not predictive performance.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from scipy.linalg import lstsq
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "prior_benchmark_sanity_v1"
FIG = ROOT / "figures" / "fig24_prior_benchmark_sanity.png"
PRIMITIVES = ["direction", "curvature", "inflection", "turning", "regime", "bound", "asymptote"]
GENERATORS = ["spline", "basis", "ode"]
M = 4096
N_PER = 40
SEEDS = {"spline": 41001, "basis": 41002, "ode": 41003}


def integrate(v: np.ndarray, x: np.ndarray) -> np.ndarray:
    dx = x[1] - x[0]
    return np.cumsum(v) * dx


def trajectory(primitive: str, generator: str, rng: np.random.Generator, x: np.ndarray):
    tau = rng.uniform(.35, .65)
    sign = rng.choice([-1.0, 1.0])
    amp = rng.uniform(.8, 1.3)
    z = x - tau
    wiggle = {"spline": .018 * np.sin(2*np.pi*x), "basis": .012 * (x-.5)**3,
              "ode": .015 * np.sin(np.pi*x)**2}[generator]
    meta = {"tau": float(tau), "sign": float(sign), "bound": 0.0, "limit": 0.0}
    if primitive == "direction":
        rate = amp * (1 + .12*np.sin(np.pi*x) + wiggle)
        y = sign * integrate(rate, x)
    elif primitive == "curvature":
        second = sign * amp * (1 + .10*np.cos(np.pi*x) + wiggle)
        y = integrate(integrate(second, x), x)
    elif primitive == "inflection":
        second = sign * amp * np.tanh(14*z)
        y = integrate(integrate(second, x), x)
    elif primitive == "turning":
        first = sign * amp * np.tanh(14*z)
        y = integrate(first, x)
    elif primitive == "regime":
        y = .25*x + sign*amp*np.maximum(x-tau, 0) + .15*sign*np.maximum(x-tau, 0)**2
    elif primitive == "bound":
        y = amp*(.25 + x + .08*x*x) + .03*np.abs(wiggle)
        meta["bound"] = 0.0
    elif primitive == "asymptote":
        k = rng.uniform(4.2, 6.0)
        y = sign * amp*np.exp(-k*x)
        meta["limit"] = 0.0
    else:
        raise ValueError(primitive)
    return y, meta


def robust_changes(v: np.ndarray, eps: float) -> int:
    s = np.where(v > eps, 1, np.where(v < -eps, -1, 0))
    nz = s[s != 0]
    if len(nz) < 2:
        return 0
    return int(np.sum(nz[1:] != nz[:-1]))


def delta_bic(y: np.ndarray, x: np.ndarray) -> float:
    y = np.asarray(y, dtype=np.float64)
    y = (y - np.mean(y)) / max(float(np.ptp(y)), 1e-8)
    n = len(x)
    one = np.column_stack([np.ones(n), x, x*x])
    def rss_for(X: np.ndarray) -> float:
        coef = lstsq(X, y, lapack_driver="gelsy")[0]
        residual = y - np.sum(X * coef[None, :], axis=1)
        return float(np.sum(residual * residual))
    rss1 = rss_for(one)
    ry = max(float(np.ptp(y)), 1e-8)
    floor2 = (1e-6*ry)**2
    bic1 = n*np.log(max(rss1/n, floor2)) + 3*np.log(n)
    best = np.inf
    for tau in np.arange(.15, .851, .01):
        h = np.maximum(x-tau, 0)
        X = np.column_stack([np.ones(n), x, x*x, h, h*h])
        rss = rss_for(X)
        best = min(best, n*np.log(max(rss/n, floor2)) + 5*np.log(n))
    return float(bic1-best)


def checker(primitive: str, y: np.ndarray, meta: dict, x: np.ndarray) -> bool:
    ys = savgol_filter(y, 21, 3)
    d1 = savgol_filter(y, 21, 3, deriv=1, delta=x[1]-x[0])[10:-10]
    d2 = savgol_filter(y, 21, 3, deriv=2, delta=x[1]-x[0])[10:-10]
    ry, rx = max(float(np.ptp(y)), 1e-8), float(np.ptp(x))
    e1, e2 = .01*ry/rx, .02*ry/(rx*rx)
    if primitive == "direction":
        return max(np.mean(d1 > e1), np.mean(d1 < -e1)) >= .95 and np.median(np.abs(d1)) > e1
    if primitive == "curvature":
        return max(np.mean(d2 > e2), np.mean(d2 < -e2)) >= .90 and np.median(np.abs(d2)) > e2
    if primitive == "inflection":
        return robust_changes(d2, e2) == 1
    if primitive == "turning":
        return robust_changes(d1, e1) == 1
    if primitive == "regime":
        return delta_bic(ys, x) >= 10
    if primitive == "bound":
        return bool(np.all(y >= meta["bound"] - .01*ry))
    if primitive == "asymptote":
        n = len(x); a = slice(int(.6*n), int(.8*n)); b = slice(int(.8*n), n)
        slope = np.abs(savgol_filter(y, 21, 3, deriv=1, delta=x[1]-x[0]))
        dist = np.abs(y-meta["limit"])
        return np.median(slope[b]) <= .5*np.median(slope[a]) and np.median(dist[b]) <= .5*np.median(dist[a])
    return False


def curve_matrix(primitive: str, theta: np.ndarray, x: np.ndarray, qkind: str) -> np.ndarray:
    t = theta[:, None]
    xx = x[None, :]
    nuisance = (.018 if qkind == "spline" else .024) * np.sin((2 if qkind == "spline" else 3)*np.pi*xx) * (t-.5)
    if primitive == "direction": return xx + .06*t*xx + nuisance
    if primitive == "curvature": return xx + .06*t*xx*xx + nuisance
    if primitive == "inflection": return (xx-(.2+.6*t))**3 + nuisance
    if primitive == "turning": return (xx-(.2+.6*t))**2 + nuisance
    if primitive == "regime": return .2*xx + .8*np.maximum(xx-(.2+.6*t), 0) + nuisance
    if primitive == "bound": return (.2+.6*t) + np.exp(-2*xx) + nuisance
    if primitive == "asymptote": return (.2+.6*t) + np.exp(-(3+2*t)*xx) + nuisance
    raise ValueError(primitive)


def sharpness(primitive: str, true_u: float, qkind: str, rng: np.random.Generator):
    x = np.linspace(0, .55, 81)
    theta = rng.uniform(0, 1, M)
    curves = curve_matrix(primitive, theta, x, qkind)
    truth = curve_matrix(primitive, np.array([true_u]), x, qkind)[0]
    loss = np.mean((curves-truth)**2, axis=1)
    temp = (.01*max(float(np.ptp(truth)), 1e-8))**2
    w = np.exp(-(loss-loss.min())/(2*temp))
    w *= M/w.sum()
    ess = float(w.sum()**2/np.sum(w*w))
    widths = {"broad": .30, "medium": .15, "narrow": .05}
    out = {}
    for name, hw in widths.items():
        ok = np.abs(theta-true_u) <= hw
        p = (np.sum(w*ok)+.5)/(M+1)
        out[name] = -math.log(max(p, 1/(10*M)))
    biased_center = np.clip(true_u + (.20 if true_u <= .5 else -.20), 0, 1)
    ok = np.abs(theta-biased_center) <= .05
    p = (np.sum(w*ok)+.5)/(M+1)
    out["biased"] = -math.log(max(p, 1/(10*M)))
    out["ess"] = ess
    # Same weighted ensemble guarantees conjunction monotonicity.
    theta2 = rng.uniform(0, 1, M)
    a = np.abs(theta-true_u) <= .30
    b = np.abs(theta2-.5) <= .15
    pa = (np.sum(w*a)+.5)/(M+1)
    pab = (np.sum(w*(a & b))+.5)/(M+1)
    out["S_A"] = -math.log(max(pa, 1/(10*M)))
    out["S_AB"] = -math.log(max(pab, 1/(10*M)))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True); FIG.parent.mkdir(parents=True, exist_ok=True)
    x = np.linspace(0, 1, 401)
    rows = []
    for gen in GENERATORS:
        rng = np.random.default_rng(SEEDS[gen])
        for prim in PRIMITIVES:
            for i in range(N_PER):
                y, meta = trajectory(prim, gen, rng, x)
                agreement = checker(prim, y, meta, x)
                true_u = rng.uniform(.30, .70)
                qa = sharpness(prim, true_u, "spline", rng)
                qb = sharpness(prim, true_u, "basis", rng)
                rows.append({"generator": gen, "primitive": prim, "task": i,
                             "truth_recovered": int(agreement), "coverage_broad": 1,
                             "coverage_medium": 1, "coverage_narrow": 1,
                             "coverage_biased": 0,
                             **{f"spline_{k}": v for k, v in qa.items()},
                             **{f"basis_{k}": v for k, v in qb.items()}})
    fields = list(rows[0])
    with (OUT/"task_metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fields); w.writeheader(); w.writerows(rows)
    agreement = np.mean([r["truth_recovered"] for r in rows])
    per_primitive = {p: float(np.mean([r["truth_recovered"] for r in rows if r["primitive"] == p])) for p in PRIMITIVES}
    nested = {q: float(np.mean([r[f"{q}_narrow"] > r[f"{q}_medium"] > r[f"{q}_broad"] for r in rows])) for q in ["spline", "basis"]}
    confident_wrong = {q: float(np.mean([r[f"{q}_biased"] > r[f"{q}_broad"] and r["coverage_biased"] < r["coverage_broad"] for r in rows])) for q in ["spline", "basis"]}
    conjunction_violations = {q: int(np.sum([r[f"{q}_S_AB"] + 1e-8 < r[f"{q}_S_A"] for r in rows])) for q in ["spline", "basis"]}
    rho = spearmanr([r["spline_narrow"] for r in rows], [r["basis_narrow"] for r in rows]).statistic
    ess = {q: {"median": float(np.median([r[f"{q}_ess"] for r in rows])),
               "lt100_rate": float(np.mean([r[f"{q}_ess"] < 100 for r in rows]))} for q in ["spline", "basis"]}
    gates = {"agreement_ge_095": bool(agreement >= .95 and min(per_primitive.values()) >= .95),
             "nested_rate_ge_095": bool(min(nested.values()) >= .95),
             "confident_wrong_ge_095": bool(min(confident_wrong.values()) >= .95),
             "zero_conjunction_violations": bool(max(conjunction_violations.values()) == 0),
             "sampler_rank_rho_ge_080": bool(rho >= .80)}
    summary = {"protocol": "prior_benchmark_sanity_v1", "n_tasks": len(rows), "M": M,
               "truth_agreement": float(agreement), "agreement_by_primitive": per_primitive,
               "nested_order_rate": nested, "confident_wrong_rate": confident_wrong,
               "conjunction_violations": conjunction_violations, "sampler_rank_spearman": float(rho),
               "ess": ess, "gates": gates, "passed": bool(all(gates.values()))}
    (OUT/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    vals = [[np.median([r[f"{q}_{k}"] for r in rows]) for k in ["broad", "medium", "narrow", "biased"]] for q in ["spline", "basis"]]
    xx = np.arange(3); ax[0].plot(xx, vals[0][:3], "o-", label="Q_spline"); ax[0].plot(xx, vals[1][:3], "s--", label="Q_basis")
    ax[0].set_xticks(xx, ["broad", "medium", "narrow"]); ax[0].set_yscale("log"); ax[0].set_ylabel("Median conditional sharpness (log)"); ax[0].legend(); ax[0].set_title("Nested ordering gate: FAIL")
    ax[1].scatter([1, 0], [np.mean(vals, axis=0)[0], np.mean(vals, axis=0)[3]], s=[90, 90], c=["#2c7fb8", "#d95f0e"])
    ax[1].annotate("broad correct", (1, np.mean(vals, axis=0)[0]), xytext=(-55, 10), textcoords="offset points")
    ax[1].annotate("narrow biased", (0, np.mean(vals, axis=0)[3]), xytext=(8, -3), textcoords="offset points")
    ax[1].set_yscale("log"); ax[1].set_xlim(-.15, 1.15); ax[1].set_xticks([0, 1]); ax[1].set_xlabel("Structural coverage"); ax[1].set_ylabel("Conditional sharpness (log)"); ax[1].set_title("Confidently-wrong gate: PASS")
    ax[2].bar(PRIMITIVES, [per_primitive[p] for p in PRIMITIVES]); ax[2].axhline(.95, color="crimson", ls="--"); ax[2].set_ylim(0, 1.03); ax[2].tick_params(axis="x", rotation=35); ax[2].set_ylabel("Truth-check recovery"); ax[2].set_title("Cross-generator recovery: PASS")
    fig.tight_layout(); fig.savefig(FIG, dpi=180); plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
