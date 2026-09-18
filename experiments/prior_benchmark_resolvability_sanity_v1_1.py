#!/usr/bin/env python3
"""V1.1 measurement-resolvability sanity; diagnostic, not predictive eval."""
from __future__ import annotations
import csv, json, math, importlib.util
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v1", ROOT/"experiments"/"prior_benchmark_sanity_v1.py")
v1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)
OUT = ROOT/"results"/"prior_benchmark_resolvability_sanity_v1_1"
FIG = ROOT/"figures"/"fig25_resolvability_sanity_v1_1.png"
SEEDS = {"spline": 51001, "basis": 51002, "ode": 51003}


def measure(primitive, true_u, qkind, rng):
    x = np.linspace(0, .35, 24)
    theta = rng.uniform(0, 1, v1.M)
    curves = v1.curve_matrix(primitive, theta, x, qkind)
    clean = v1.curve_matrix(primitive, np.array([true_u]), x, qkind)[0]
    noise_sd = .03*max(float(np.ptp(clean)), 1e-8)
    observed = clean + rng.normal(0, noise_sd, len(x))
    loss = np.mean((curves-observed)**2, axis=1)
    temp = noise_sd**2 + (.01*max(float(np.ptp(observed)), 1e-8))**2
    w = np.exp(-(loss-loss.min())/(2*temp)); w *= v1.M/w.sum()
    ess = float(w.sum()**2/np.sum(w*w))
    ans = {}
    for name, hw in [("broad",.30),("medium",.15),("narrow",.05)]:
        ok = np.abs(theta-true_u) <= hw
        p = (np.sum(w*ok)+.5)/(v1.M+1)
        ans[name] = -math.log(max(p, 1/(10*v1.M)))
    ans["ess"] = ess
    return ans


def percentile_ci(x, rng, n=2000):
    a=np.asarray(x); vals=np.empty(n)
    for i in range(n): vals[i]=np.median(rng.choice(a, len(a), replace=True))
    return [float(np.percentile(vals,2.5)), float(np.percentile(vals,97.5))]


def main():
    OUT.mkdir(parents=True, exist_ok=True); FIG.parent.mkdir(parents=True, exist_ok=True)
    rows=[]
    for gen in v1.GENERATORS:
        rng=np.random.default_rng(SEEDS[gen])
        for prim in v1.PRIMITIVES:
            for task in range(v1.N_PER):
                true_u=rng.uniform(.30,.70)
                for q in ["spline","basis"]:
                    z=measure(prim,true_u,q,rng)
                    rows.append({"generator":gen,"primitive":prim,"task":task,"sampler":q,**z,
                                 "delta_mb":z["medium"]-z["broad"],
                                 "delta_nm":z["narrow"]-z["medium"],
                                 "delta_nb":z["narrow"]-z["broad"],
                                 "saturated":int(z["narrow"]<.01),
                                 "informational_null":int(z["narrow"]<.10)})
    with (OUT/"task_metrics.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,rows[0].keys()); w.writeheader(); w.writerows(rows)
    rng=np.random.default_rng(51999); by={}
    for p in v1.PRIMITIVES:
        by[p]={}
        for q in ["spline","basis"]:
            z=[r for r in rows if r["primitive"]==p and r["sampler"]==q]
            by[p][q]={}
            for d in ["delta_mb","delta_nm","delta_nb"]:
                a=[r[d] for r in z]
                by[p][q][d]={"median":float(np.median(a)),"ci95":percentile_ci(a,rng),
                              "positive_rate":float(np.mean(np.asarray(a)>0)),
                              "gt_005_rate":float(np.mean(np.asarray(a)>.05))}
            by[p][q]["saturation_rate"]=float(np.mean([r["saturated"] for r in z]))
            by[p][q]["informational_null_rate"]=float(np.mean([r["informational_null"] for r in z]))
            by[p][q]["median_ess"]=float(np.median([r["ess"] for r in z]))
    logical_violations=sum(r["narrow"]+1e-8<r["medium"] or r["medium"]+1e-8<r["broad"] for r in rows)
    summary={"protocol":"v1.1","n_measurements":len(rows),"M":v1.M,
             "logical_nesting_violations":int(logical_violations),
             "logical_gate_passed":bool(logical_violations==0),"by_primitive":by,
             "structural_null_gate":"not_run","full_v1_unblocked":False}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    fig,ax=plt.subplots(1,2,figsize=(12,4.5)); xx=np.arange(len(v1.PRIMITIVES)); width=.36
    for j,q in enumerate(["spline","basis"]):
        ax[0].bar(xx+(j-.5)*width,[by[p][q]["delta_nb"]["median"] for p in v1.PRIMITIVES],width,label=f"Q_{q}")
        ax[1].bar(xx+(j-.5)*width,[by[p][q]["saturation_rate"] for p in v1.PRIMITIVES],width,label=f"Q_{q}")
    for a in ax: a.set_xticks(xx,v1.PRIMITIVES,rotation=35,ha="right"); a.legend()
    ax[0].axhline(0,color="black",lw=.8); ax[0].set_ylabel("Median ΔS(narrow−broad), nat"); ax[0].set_title("Effective conditional specificity")
    ax[1].set_ylim(0,1); ax[1].set_ylabel("S(narrow) < .01 rate"); ax[1].set_title("Conditional-information saturation")
    fig.tight_layout(); fig.savefig(FIG,dpi=180); plt.close(fig)
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
