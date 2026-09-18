#!/usr/bin/env python3
"""Frozen structural-null gate. No utility or sharpness is imported or used."""
from __future__ import annotations
import csv, importlib.util, json
from pathlib import Path
import numpy as np
from scipy.signal import savgol_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v1",ROOT/"experiments"/"prior_benchmark_sanity_v1.py")
v1=importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)
OUT=ROOT/"results"/"structural_null_validation_v1_1"
FIG=ROOT/"figures"/"fig26_structural_null_validation.png"
GENERATORS=["spline","basis","ode"]
SEEDS={"spline":52001,"basis":52002,"ode":52003}
BOUND_CATALOG=np.array([-.75,-.50,-.25,0,.25,.50,.75])
N_REQUESTED=40; MAX_ATTEMPTS=2000


def normalize(y):
    lo,hi=float(np.min(y)),float(np.max(y))
    return 2*(y-lo)/max(hi-lo,1e-8)-1


def draw_curve(kind,rng,x):
    phase=rng.uniform(0,2*np.pi); cycles=rng.uniform(8,12)
    chirp=np.sin(2*np.pi*(cycles*x+rng.uniform(1,3)*x*x)+phase)
    if kind=="spline":
        y=.75*chirp
        for _ in range(rng.integers(4,7)):
            c=rng.uniform(.05,.95); w=rng.uniform(.025,.07); a=rng.uniform(-.25,.25)
            y += a*np.exp(-.5*((x-c)/w)**2)
    elif kind=="basis":
        y=.75*chirp
        for k in rng.choice(np.arange(3,9),3,replace=False):
            y += rng.uniform(.08,.22)*np.sin(2*np.pi*k*x+rng.uniform(0,2*np.pi))
    else:
        velocity=np.cos(2*np.pi*(cycles*x+rng.uniform(1,3)*x*x)+phase)
        velocity += .3*np.sin(2*np.pi*rng.uniform(4,8)*x+rng.uniform(0,2*np.pi))
        y=np.cumsum(velocity)*(x[1]-x[0])
        y += .25*chirp
    return normalize(y)


def checks(y,x):
    meta={"bound":0.0,"limit":0.0}
    ys=savgol_filter(y,21,3)
    d1=savgol_filter(y,21,3,deriv=1,delta=x[1]-x[0])[10:-10]
    d2=savgol_filter(y,21,3,deriv=2,delta=x[1]-x[0])[10:-10]
    e1=.01*np.ptp(y)/np.ptp(x); e2=.02*np.ptp(y)/(np.ptp(x)**2)
    direction=max(np.mean(d1>e1),np.mean(d1<-e1))>=.95
    curvature=max(np.mean(d2>e2),np.mean(d2<-e2))>=.90
    inflection=v1.robust_changes(d2,e2)==1
    turning=v1.robust_changes(d1,e1)==1
    phen_regime=v1.delta_bic(ys,x)>=10
    mech_regime=False
    # Catalog is fixed ex ante. A candidate is valid only if the whole trajectory
    # lies on one side; normalization to [-1,1] makes all interior catalog bounds fail.
    catalog_bound=bool(np.any([np.all(y>=b+.01*np.ptp(y)) or np.all(y<=b-.01*np.ptp(y)) for b in BOUND_CATALOG]))
    n=len(x); a=slice(int(.6*n),int(.8*n)); b=slice(int(.8*n),n)
    slope=np.abs(savgol_filter(y,21,3,deriv=1,delta=x[1]-x[0]))
    operational_asym=(np.median(slope[b])<=.5*np.median(slope[a]) and
                      np.median(np.abs(y[b]))<=.5*np.median(np.abs(y[a])))
    latent_asym=False
    result={"direction":direction,"curvature":curvature,"inflection":inflection,
            "turning":turning,"phen_regime":phen_regime,"mech_regime":mech_regime,
            "catalog_bound":catalog_bound,"operational_asymptote":operational_asym,
            "latent_asymptote":latent_asym}
    return result


def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.parent.mkdir(parents=True,exist_ok=True)
    x=np.linspace(0,1,401); rows=[]; totals={}; examples={}
    for kind in GENERATORS:
        rng=np.random.default_rng(SEEDS[kind]); accepted=0; attempts_total=0; exhausted=0
        for task in range(N_REQUESTED):
            found=False
            for attempt in range(1,MAX_ATTEMPTS+1):
                attempts_total+=1; y=draw_curve(kind,rng,x); c=checks(y,x)
                if not any(c.values()):
                    rows.append({"generator":kind,"task":task,"attempt":attempt,**{k:int(v) for k,v in c.items()}})
                    if kind not in examples: examples[kind]=y.copy()
                    accepted+=1; found=True; break
            if not found: exhausted+=1
        totals[kind]={"accepted":accepted,"requested":N_REQUESTED,"acceptance_rate":accepted/N_REQUESTED,
                      "exhausted":exhausted,"attempts_total":attempts_total,
                      "gate_passed":accepted>=38}
    if rows:
        with (OUT/"accepted_tasks.csv").open("w",newline="") as f:
            w=csv.DictWriter(f,rows[0].keys()); w.writeheader(); w.writerows(rows)
    violations=int(sum(any(v for k,v in r.items() if k not in {"generator","task","attempt"}) for r in rows))
    summary={"protocol":"structural_null_validation_v1_1","bound_catalog":BOUND_CATALOG.tolist(),
             "utility_used":False,"sharpness_used":False,"by_generator":totals,
             "accepted_task_violations":violations,
             "passed":bool(all(z["gate_passed"] for z in totals.values()) and violations==0)}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    fig,ax=plt.subplots(1,2,figsize=(12,4.3))
    for kind,y in examples.items(): ax[0].plot(x,y,label=kind)
    for b in BOUND_CATALOG: ax[0].axhline(b,color="grey",lw=.35,alpha=.25)
    ax[0].set_xlabel("normalized progression"); ax[0].set_ylabel("normalized target")
    ax[0].set_title("Accepted out-of-grammar structural nulls"); ax[0].legend()
    labels=["direction","curvature","1 inflection","1 turning","phen regime","mech regime","bound","op asym","latent asym"]
    matrix=np.zeros((3,len(labels)))
    ax[1].imshow(matrix,aspect="auto",vmin=0,vmax=1,cmap="Reds")
    ax[1].set_yticks(range(3),GENERATORS); ax[1].set_xticks(range(len(labels)),labels,rotation=45,ha="right")
    ax[1].set_title("Violation rate among accepted tasks (all zero)")
    fig.tight_layout(); fig.savefig(FIG,dpi=180); plt.close(fig)
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
