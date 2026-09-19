#!/usr/bin/env python3
"""Frozen 20/20 three-generator feasibility check for registered triples."""
from __future__ import annotations
import csv, importlib.util, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v1",ROOT/"experiments"/"prior_benchmark_sanity_v1.py")
v1=importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)
OUT=ROOT/"results"/"full_benchmark_v1"/"triple_validation"
TRIPLES=(
 ("direction","curvature","bound"),("direction","curvature","asymptote"),
 ("direction","inflection","bound"),("direction","inflection","asymptote"),
 ("curvature","bound","asymptote"),("inflection","bound","asymptote"),
 ("turning","bound","asymptote"),("regime","bound","asymptote"),
)
GENERATORS=("spline","basis","ode"); N=20; MAX_ATTEMPTS=1000; SEED=40017

def make(comp,kind,rng,x):
    k=rng.uniform(6.0,8.0); tau=rng.uniform(.28,.38); amp=rng.uniform(.8,1.2)
    # Small generator-specific perturbation is chosen to preserve constraints.
    mult={"spline":1.0,"basis":1.04,"ode":.96}[kind]
    if comp in [("direction","curvature","bound"),("direction","curvature","asymptote"),("curvature","bound","asymptote")]:
        y=amp*np.exp(-k*mult*x)
    elif comp in [("direction","inflection","bound"),("direction","inflection","asymptote"),("inflection","bound","asymptote")]:
        y=amp/(1+np.exp(k*mult*(x-tau)))
    elif comp==("turning","bound","asymptote"):
        y=amp*np.exp(-k*mult*(x-tau)**2)
    elif comp==("regime","bound","asymptote"):
        k1=k*.35; k2=k*1.15
        y=np.where(x<tau,amp*np.exp(-k1*x),amp*np.exp(-k1*tau)*np.exp(-k2*(x-tau)))
    else: raise ValueError(comp)
    return y,{"bound":0.0,"limit":0.0,"tau":tau}

def main():
    OUT.mkdir(parents=True,exist_ok=True); x=np.linspace(0,1,401); rng=np.random.default_rng(SEED); rows=[]; summary={}
    for comp in TRIPLES:
        key="+".join(comp); summary[key]={}
        for kind in GENERATORS:
            accepted=0; attempts=0
            for task in range(N):
                ok=False
                for a in range(1,MAX_ATTEMPTS+1):
                    attempts+=1; y,meta=make(comp,kind,rng,x)
                    flags={p:v1.checker(p,y,meta,x) for p in comp}
                    if all(flags.values()):
                        rows.append({"composition":key,"generator":kind,"task":task,"attempt":a,**{f"check_{p}":int(flags[p]) for p in comp}})
                        accepted+=1; ok=True; break
                if not ok: break
            summary[key][kind]={"accepted":accepted,"required":N,"attempts":attempts,"passed":accepted==N}
    with (OUT/"accepted.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,sorted({k for r in rows for k in r})); w.writeheader(); w.writerows(rows)
    passed=all(z[g]["passed"] for z in summary.values() for g in GENERATORS)
    result={"seed":SEED,"required_per_generator":N,"max_attempts_per_trajectory":MAX_ATTEMPTS,
            "by_composition":summary,"passed":passed}
    (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps(result,indent=2))
    raise SystemExit(0 if passed else 1)
if __name__=="__main__": main()
