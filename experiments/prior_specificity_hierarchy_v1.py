#!/usr/bin/env python3
"""Frozen E3: evidence-conditioned prior specificity hierarchy."""
from __future__ import annotations

import json
import warnings
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from prior_evaluation_metric_v1 import BANDS, TB, affine, bound, curvature, pospow, regime


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "prior_specificity_hierarchy_v1"
FIG = ROOT / "figures"
SEED, N, NOISE, BOOT = 20261003, 100, .015, 2000
LEVELS = {
    "regime_change": {"low": .59, "mid": .48, "high": .32, "very_high": .15},
    "emergent_curvature": {"low": .59, "mid": .48, "high": .32, "very_high": .15},
    "asymptotic_bound": {"low": .35, "mid": 1.50, "high": 3.50, "very_high": 5.00},
}
PRIOR_LEVELS = ("L0", "L1", "L2", "L3", "L4")


def quad(t, a, b, c): return a + b * t + c * t * t


def fit_curve(fn, t, y, target, p0, lower, upper):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            p, _ = curve_fit(fn, t, y, p0=p0, bounds=(lower, upper), maxfev=3500)
        return fn(target, *p)
    except (RuntimeError, ValueError, FloatingPointError):
        slope, intercept = np.polyfit(t, y, 1)
        return affine(target, slope, intercept)


def generate(family, exposure, t, rng):
    if family == "regime_change":
        p = np.array([rng.uniform(.07,.24), rng.uniform(.35,1.), rng.uniform(1.35,2.6), exposure])
        return regime(t, *p), p, max(0., (TB-exposure)/TB)
    if family == "emergent_curvature":
        p = np.array([rng.uniform(.05,.16), rng.uniform(.22,.60), rng.uniform(1.35,2.6), exposure])
        return curvature(t, *p), p, max(0., (TB-exposure)/TB)
    p = np.array([rng.uniform(.20,.70), exposure])
    return bound(t, *p), p, 1-float(np.exp(-exposure*TB))


def prediction(family, prior_level, t, y, target, true_p):
    if prior_level == "L0":
        slope, intercept = np.polyfit(t, y, 1); return affine(target, slope, intercept)
    if prior_level == "L1":
        return fit_curve(affine, t, y, target, [-.2, 1.], [-4., -2.], [0., 3.])
    if prior_level == "L2":
        if family == "asymptotic_bound":
            return fit_curve(quad, t, y, target, [1., -.2, .1], [-.5,-4.,0.], [2.5,0.,8.])
        return fit_curve(quad, t, y, target, [1., -.2, -.1], [-.5,-4.,-8.], [2.5,0.,0.])
    if family == "regime_change":
        fn, p0, lo, hi = regime, [.15,.55,2.,.45], [0.,0.,1.01,.001], [.8,2.,4.,.599]
    elif family == "emergent_curvature":
        fn, p0, lo, hi = curvature, [.10,.35,2.,.45], [0.,0.,1.01,.001], [.7,2.,4.,.599]
    else:
        fn, p0, lo, hi = bound, [.5,1.5], [0.,.005], [.95,12.]
    if prior_level == "L4":
        lo = np.maximum(np.asarray(lo), true_p * .90)
        hi = np.minimum(np.asarray(hi), true_p * 1.10)
        p0 = np.clip(true_p, lo + 1e-7, hi - 1e-7)
    return fit_curve(fn, t, y, target, p0, lo, hi)


def ci(values, rng):
    x=np.asarray(values); means=x[rng.integers(0,len(x),size=(BOOT,len(x)))].mean(1)
    return [float(v) for v in np.quantile(means,[.025,.975])]


def make_figures(summary):
    FIG.mkdir(exist_ok=True)
    order=["low","mid","high","very_high"]; labels={"L0":"L0 none","L1":"L1 direction","L2":"L2 shape","L3":"L3 family","L4":"L4 + intervals"}
    fig, axes=plt.subplots(1,3,figsize=(15,4.5),constrained_layout=True)
    for ax,family in zip(axes,LEVELS):
        for level,color in zip(PRIOR_LEVELS,["#777","#3978b8","#7353ba","#dd7f28","#43a86b"]):
            rows=[r for r in summary if r["family"]==family and r["prior_level"]==level and r["band"]=="D3"]
            rows.sort(key=lambda r:order.index(r["observability_level"]))
            x=np.arange(4); y=np.array([r["mean_rmse"] for r in rows]); band=np.array([r["rmse_ci95"] for r in rows])
            ax.plot(x,y,"o-",color=color,label=labels[level]); ax.fill_between(x,band[:,0],band[:,1],color=color,alpha=.08)
        ax.set(title=family.replace("_"," "),xticks=np.arange(4),xticklabels=order,xlabel="within-family evidence",ylabel="D3 RMSE")
    axes[-1].legend(fontsize=7); fig.suptitle("Useful prior specificity depends on available evidence")
    fig.savefig(FIG/"fig18_prior_specificity_hierarchy.png",dpi=220);plt.close(fig)


def main():
    rng=np.random.default_rng(SEED); t=np.round(np.arange(0.,1.301,.01),4); observed=t<=TB; masks={n:(t>=a)&(t<=b) for n,(a,b) in BANDS.items()}; records=[]; task=0
    for family,settings in LEVELS.items():
        for evidence_name, exposure in settings.items():
            for _ in range(N):
                clean,p,obs=generate(family,exposure,t,rng); noisy=clean.copy();noisy[observed]+=rng.normal(0,NOISE,observed.sum())
                for level in PRIOR_LEVELS:
                    pred=prediction(family,level,t[observed],noisy[observed],t,p)
                    for band,mask in masks.items(): records.append({"task_id":task,"family":family,"observability_level":evidence_name,"observability":obs,"prior_level":level,"band":band,"rmse":float(np.sqrt(np.mean((pred[mask]-clean[mask])**2)))})
                task+=1
    grouped=defaultdict(list)
    for r in records: grouped[(r["family"],r["observability_level"],r["prior_level"],r["band"])].append(r)
    brng=np.random.default_rng(SEED+1); summary=[]
    for key,rows in sorted(grouped.items()):
        f,e,l,b=key; x=[r["rmse"] for r in rows]; summary.append({"family":f,"observability_level":e,"prior_level":l,"band":b,"n":len(rows),"mean_rmse":float(np.mean(x)),"rmse_ci95":ci(x,brng)})
    contrasts=[]
    for family in LEVELS:
        for evidence_name,contrast_name,sign in [("low","over_specificity_cost_L4_minus_L1",1),("very_high","under_specificity_cost_L1_minus_L4",-1)]:
            vals=[]
            for task_id in range(task):
                subset=[r for r in records if r["task_id"]==task_id and r["family"]==family and r["observability_level"]==evidence_name and r["band"]=="D3"]
                if subset: vals.append(sign*(next(r["rmse"] for r in subset if r["prior_level"]=="L4")-next(r["rmse"] for r in subset if r["prior_level"]=="L1")))
            contrasts.append({"family":family,"contrast":contrast_name,"mean_rmse_cost":float(np.mean(vals)),"ci95":ci(vals,brng)})
    OUT.mkdir(parents=True,exist_ok=True); payload={"experiment_id":"prior_specificity_hierarchy_v1","status":"development","protocol":"PRIOR_SPECIFICITY_HIERARCHY_PROTOCOL_V1.md","n_tasks":task,"summary":summary,"contrasts":contrasts,"records":records};(OUT/"results.json").write_text(json.dumps(payload,indent=2)+"\n")
    make_figures(summary);print(json.dumps(contrasts,indent=2))


if __name__=="__main__":main()
