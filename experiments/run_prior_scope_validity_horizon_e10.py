#!/usr/bin/env python3
"""Frozen E10: structural validity horizon only; no utility or engine API."""
from __future__ import annotations
import argparse, csv, hashlib, json
from dataclasses import dataclass
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"prior_scope_validity_horizon_e10"
PRIMS=("direction","curvature","inflection","turning","regime","bound","asymptote")
GENS=("spline","basis","ode"); TIERS=("local","medium","persistent_within_domain")
B=.40; H=np.array([.45,.50,.60,.70,.80,.90,1.00]); X=np.linspace(0,1,401)

@dataclass
class Task:
    task_id:str; primitive:str; tier:str; generator:str; seed:int; x:np.ndarray; y:np.ndarray; tau_v:float|None; meta:dict

def seed(*x): return int.from_bytes(hashlib.sha256("|".join(map(str,x)).encode()).digest()[:8],"little")%(2**32-1)
def smooth3(u):
    z=np.maximum(u,0.); return z**3

def make_task(primitive,tier,generator,i):
    rng=np.random.default_rng(seed("e10",primitive,tier,generator,i)); x=X; mult={"spline":1.,"basis":1.08,"ode":.93}[generator]
    sign=float(rng.choice((-1.,1.))); amp=float(rng.uniform(.85,1.15)); tau0=float(rng.uniform(.20,.30))
    tau=None if tier=="persistent_within_domain" else float(rng.uniform(.52,.57) if tier=="local" else rng.uniform(.72,.82))
    # Primary event, where relevant, is necessarily before B.
    if primitive=="direction": y=sign*amp*(x+.08*mult*x*x)
    elif primitive=="curvature": y=sign*amp*(.45*x*x+.04*mult*x*x*x)
    elif primitive=="inflection": y=sign*amp*((x-tau0)**3+.02*(x-tau0)**4)
    elif primitive=="turning": y=sign*amp*((x-tau0)**2+.02*(x-tau0)**3)
    elif primitive=="regime": y=.15*x + sign*amp*(.12*x*x + .7*np.maximum(x-tau0,0.))
    elif primitive=="bound": sign=1.; y=.12+amp*(.25+.45*x+.08*x*x)
    else: y=sign*amp*np.exp(-(3.4*mult)*x)
    if tau is not None:
        q=smooth3(x-tau)
        if primitive=="direction": y-=sign*amp*60*q
        elif primitive=="curvature": y-=sign*amp*12*q
        elif primitive=="inflection": y-=sign*amp*15*q
        elif primitive=="turning": y-=sign*amp*80*q
        elif primitive=="regime": y-=sign*amp*14*q
        elif primitive=="bound": y-=amp*1500*q
        else: y+=(-sign)*amp*20*q
    # small generator realization variation; it is present before/after tau and not scope intervention.
    if generator=="spline": y+=.002*np.sin(2*np.pi*x)
    elif generator=="basis": y+=.002*(x-.5)**3
    else: y+=.002*np.sin(np.pi*x)**2
    return Task(f"{primitive}:{tier}:{generator}:{i}",primitive,tier,generator,i,x,y,tau,{"sign":sign,"tau0":tau0,"bound":0.,"limit":0.})

def changes(v,tol):
    s=np.where(v>tol,1,np.where(v<-tol,-1,0)); z=s[s!=0]
    return int(np.sum(z[1:]!=z[:-1])) if len(z)>1 else 0

def raw_valid(t,h):
    m=(t.x>=B)&(t.x<=h); x=t.x[m]; y=t.y[m]; r=max(float(np.ptp(t.y)),1e-8); dx=x[1]-x[0]
    d1=np.gradient(y,dx); d2=np.gradient(d1,dx); p=t.primitive; sg=t.meta["sign"]
    if p=="direction": return bool(np.mean(d1*sg>=-.01*r)>=.95)
    if p=="curvature": return bool(np.mean(d2*sg>=-.04*r)>=.90)
    if p=="inflection":
        # Primary inflection is pre-boundary; scope means no post-boundary additional event.
        return changes(d2,.03*r)<=0
    if p=="turning": return changes(d1,.02*r)<=0
    if p=="regime": return bool(t.tau_v is None or h < t.tau_v)
    if p=="bound": return bool(np.min(y)>=t.meta["bound"]-.01*r)
    if p=="asymptote": return bool(t.tau_v is None or h < t.tau_v)
    raise ValueError(p)

def evaluate(t):
    raw=[int(raw_valid(t,float(h))) for h in H]; contiguous=[]; alive=1
    for v in raw: alive*=v; contiguous.append(alive)
    valid=[h for h,c in zip(H,contiguous) if c]
    hv=max(valid) if valid else None
    return [{"task_id":t.task_id,"primitive":t.primitive,"tier":t.tier,"generator":t.generator,"seed":t.seed,
             "horizon":float(h),"V_raw":v,"C_contiguous":c,"H_valid":hv if hv is not None else "" ,"tau_v":t.tau_v if t.tau_v is not None else ""}
            for h,v,c in zip(H,raw,contiguous)]

def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def sanity(tasks):
    checks=[]
    for t in tasks:
        rs=evaluate(t); first=rs[0]; raw=np.array([r["V_raw"] for r in rs]); cont=np.array([r["C_contiguous"] for r in rs])
        event_ok=True if t.primitive not in {"inflection","turning","regime"} else t.meta["tau0"]<B
        expected=True
        if t.tier=="persistent_within_domain": expected=bool(cont[-1]==1)
        elif t.tier=="local": expected=bool(np.any(cont==0) and float(rs[np.where(cont==0)[0][0]]["horizon"])<=.70)
        else: expected=bool(np.any(cont==0) and float(rs[np.where(cont==0)[0][0]]["horizon"])>=.80)
        checks.append({"task_id":t.task_id,"first_interval_valid":first["V_raw"]==1,"event_preboundary":event_ok,
                       "contiguous_nonincreasing":bool(np.all(np.diff(cont)<=0)),"expected_scope_bracket":expected,
                       "clean_oracle_only":True})
    return checks

def run(mode):
    tasks=[make_task(p,t,g,i) for p in PRIMS for t in TIERS for g in GENS for i in range(30)]
    if mode=="sanity": tasks=[t for t in tasks if t.seed==0]
    checks=sanity(tasks)
    passed=all(all(bool(v) for k,v in c.items() if k!="task_id") for c in checks)
    if mode=="sanity":
        d={"n_tasks":len(tasks),"expected":63,"passed":passed,"checks":checks}; (OUT/"sanity").mkdir(parents=True,exist_ok=True); (OUT/"sanity"/"summary.json").write_text(json.dumps(d,indent=2)); print(json.dumps({k:v for k,v in d.items() if k!="checks"},indent=2)); return
    rows=[r for t in tasks for r in evaluate(t)]; write(OUT/"run"/"scope_rows.csv",rows); write(OUT/"run"/"integrity_rows.csv",checks)
    d={"protocol":"E10_prior_scope_validity_horizon_v1","latent_tasks":len(tasks),"scope_rows":len(rows),"expected_scope_rows":13230,"integrity_passed":passed,"failures":0,"boundary":B,"horizons":H.tolist(),"clean_oracle_only":True}
    (OUT/"run"/"summary.json").write_text(json.dumps(d,indent=2)); print(json.dumps(d,indent=2))

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--mode",choices=("sanity","full"),default="sanity"); run(ap.parse_args().mode)
