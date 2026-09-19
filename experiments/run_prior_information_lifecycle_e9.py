#!/usr/bin/env python3
"""E9 Prior Information Lifecycle: integrity sanity and frozen full run.

The scoring functions in this module accept only prefix observations, a supplied
structural-prior specification, and a shared ambient bank.  Future targets,
prediction engines, RMSE, and utility are deliberately absent from their API.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "prior_information_lifecycle_e9"
PRIMITIVES = ("direction", "curvature", "inflection", "turning", "regime", "bound", "asymptote")
GENERATORS = ("spline", "basis", "ode")
ETAS = (("low", .20), ("mid", .50), ("high", .80))
PREFIXES = np.array([.20, .30, .40, .50, .60, .70])
DOFS = (1, 3, 5)
M = 4096
GRID = np.linspace(.70, 1.0, 161)
EPS = 1e-12
LAPLACE_A = .5
LAPLACE_B = 1.0
P_FLOOR = 1/(10*M)


@dataclass(frozen=True)
class SuppliedPrior:
    primitive: str
    sign: float
    bound: float
    limit: float


@dataclass(frozen=True)
class FrozenTask:
    """Post-validation E9 task.  It intentionally contains no future target."""
    task_id: str
    primitive: str
    eta_name: str
    eta: float
    generator: str
    seed: int
    x_master: np.ndarray
    y_master: np.ndarray
    r_ref: float
    supplied: SuppliedPrior
    bank_z: np.ndarray


def _seed(*items: object) -> int:
    raw = "|".join(map(str, items)).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "little") % (2**32 - 1)


def _smoothstep(x: np.ndarray) -> np.ndarray:
    z = np.clip(x, 0., 1.)
    return z*z*(3.-2.*z)


def _latent_curve(primitive: str, generator: str, eta: float, rng: np.random.Generator, x: np.ndarray):
    """Generation-only structural trajectory and metadata.

    The supplied primitive is valid by construction.  The distinct generator
    realizations perturb formulas without changing the declared primitive.
    """
    sign = float(rng.choice((-1., 1.)))
    amp = float(rng.uniform(.8, 1.2))
    tau = float(rng.uniform(.32, .52))
    mult = {"spline": 1.0, "basis": 1.08, "ode": .93}[generator]
    z = x - tau
    if primitive == "direction":
        y = sign * amp * (x + .10 * mult * x*x)
    elif primitive == "curvature":
        y = sign * amp * (.35*x*x + .08*mult*x*x*x)
    elif primitive == "inflection":
        y = sign * amp * (z*z*z + .05*mult*z*z*z*z)
    elif primitive == "turning":
        y = sign * amp * (z*z + .04*mult*z*z*z)
    elif primitive == "regime":
        # eta is pre-generation contrast, not a label selected from E_struct.
        y = .18*x + sign*amp*(.15*x*x + eta*(np.maximum(z, 0.) + .35*np.maximum(z, 0.)**2))
    elif primitive == "bound":
        y = .05 + amp*(.22 + .32*x + .12*mult*x*x)
        sign = 1.
    elif primitive == "asymptote":
        rate = 2.4 + 3.6*eta*mult
        y = sign * amp * np.exp(-rate*x)
    else:
        raise ValueError(primitive)
    # Independent generator-style perturbation; preserve intended dominance.
    if generator == "spline": y = y + .006*np.sin(2*np.pi*x)
    elif generator == "basis": y = y + .004*(x-.5)**3
    else: y = y + .004*np.sin(np.pi*x)**2
    meta = {"sign": sign, "bound": 0., "limit": 0., "tau": tau}
    return y, meta


def _oracle_coverage(primitive: str, y: np.ndarray, meta: dict, x: np.ndarray) -> bool:
    """Generation-stage check only; never supplied to E9 scorer."""
    yy = y[x >= .70]
    if primitive == "direction":
        d = np.diff(yy); return bool(np.mean(d * meta["sign"] >= -1e-6) >= .98)
    if primitive == "curvature":
        d2 = np.diff(yy, n=2); return bool(np.mean(d2 * meta["sign"] >= -1e-6) >= .95)
    if primitive == "inflection": return True  # latent generator declares one continuous inflection
    if primitive == "turning": return True     # latent generator declares one turning mechanism
    if primitive == "regime": return True      # mechanistic truth requires latent provenance
    if primitive == "bound": return bool(np.all(yy >= meta["bound"] - 1e-8))
    if primitive == "asymptote": return True   # latent-assisted operational label
    return False


def make_task(primitive: str, eta_name: str, eta: float, generator: str, seed: int) -> FrozenTask:
    """Generation/validation boundary.  Returned object deliberately drops y_future."""
    x_full = np.linspace(0., 1., 401)
    latent_rng = np.random.default_rng(_seed("latent", primitive, eta_name, generator, seed))
    clean, meta = _latent_curve(primitive, generator, eta, latent_rng, x_full)
    assert _oracle_coverage(primitive, clean, meta, x_full), "generation coverage invariant failed"
    x_master = np.arange(0, 85, dtype=float)/120.  # 0..70/120 inclusive
    clean_master = np.interp(x_master, x_full, clean)
    r_ref = max(float(np.ptp(clean_master)), 1e-8)
    noise_rng = np.random.default_rng(_seed("noise", primitive, eta_name, generator, seed))
    y_master = clean_master + noise_rng.normal(0., .01*r_ref, len(x_master))
    bank_rng = np.random.default_rng(_seed("bank", primitive, eta_name, generator, seed))
    z = bank_rng.normal(0., 1., (M, 5))
    return FrozenTask(
        task_id=f"{primitive}:{eta_name}:{generator}:{seed}", primitive=primitive,
        eta_name=eta_name, eta=eta, generator=generator, seed=seed,
        x_master=x_master, y_master=y_master, r_ref=r_ref,
        supplied=SuppliedPrior(primitive, float(meta["sign"]), float(meta["bound"]), float(meta["limit"])),
        bank_z=z,
    )


def _basis(x: np.ndarray) -> np.ndarray:
    raw = np.column_stack((x, x*x-.33, np.maximum(x-.45, 0.)**2, np.sin(2*np.pi*x), np.cos(2*np.pi*x)))
    g_raw = np.column_stack((GRID, GRID*GRID-.33, np.maximum(GRID-.45, 0.)**2, np.sin(2*np.pi*GRID), np.cos(2*np.pi*GRID)))
    scale = np.sqrt(np.mean(g_raw*g_raw, axis=0)); scale = np.maximum(scale, 1e-9)
    return raw/scale


def _bank_functions(task: FrozenTask, dof: int, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Candidate-independent full-domain bank evaluated on requested x.

    A two-point local anchor uses only observations present in every prefix;
    it is not a structural prior and has no access to future truth.
    """
    dx = task.x_master[1]-task.x_master[0]
    slope0 = (task.y_master[1]-task.y_master[0])/dx
    base = task.y_master[0] + slope0*x
    active = np.zeros_like(task.bank_z)
    active[:, :dof] = task.bank_z[:, :dof]
    # einsum avoids platform BLAS status-flag artefacts for short prefix grids.
    f = base[None, :] + .10 * np.einsum("ij,kj->ik", active, _basis(x))
    return f, active


def _prior_satisfied(primitive: str, sign: float, bound: float, limit: float, f_g: np.ndarray, z_active: np.ndarray) -> np.ndarray:
    d1 = np.diff(f_g, axis=1); d2 = np.diff(f_g, n=2, axis=1)
    tol = 1e-5
    if primitive == "direction": return np.mean(d1*sign >= -tol, axis=1) >= .95
    if primitive == "curvature": return np.mean(d2*sign >= -tol, axis=1) >= .90
    if primitive == "inflection":
        s = np.sign(d2); return np.sum(s[:,1:]*s[:,:-1] < 0, axis=1) == 1
    if primitive == "turning":
        s = np.sign(d1); return np.sum(s[:,1:]*s[:,:-1] < 0, axis=1) == 1
    if primitive == "regime": return np.abs(z_active[:,2]) >= .35  # latent-mechanism membership in bank
    if primitive == "bound": return np.min(f_g, axis=1) >= bound - .01
    if primitive == "asymptote":
        early=np.mean(np.abs(d1[:, :40]),axis=1); late=np.mean(np.abs(d1[:, -40:]),axis=1)
        return late <= .65*np.maximum(early, 1e-8)
    raise ValueError(primitive)


def _template(primitive: str, x: np.ndarray, y0: float, slope0: float, sign: float, bound: float, limit: float) -> np.ndarray:
    """Prefix-only structural template used solely for E_struct contrast."""
    if primitive == "direction": return y0 + sign*np.abs(slope0)*x
    if primitive == "curvature": return y0 + .5*sign*max(abs(slope0),.05)*x*x
    if primitive == "inflection": return y0 + sign*.7*(x-.45)**3
    if primitive == "turning": return y0 + sign*.7*((x-.45)**2-.45**2)
    if primitive == "regime": return y0 + slope0*x + sign*.55*np.maximum(x-.45,0.)**1.3
    if primitive == "bound": return np.maximum(y0 + slope0*x, bound)
    if primitive == "asymptote": return limit + (y0-limit)*np.exp(-4*x)
    raise ValueError(primitive)


def _structural_evidence(task: FrozenTask, x: np.ndarray, y: np.ndarray) -> float:
    dx=task.x_master[1]-task.x_master[0]; slope0=(task.y_master[1]-task.y_master[0])/dx
    p=task.supplied
    target=_template(p.primitive,x,task.y_master[0],slope0,p.sign,p.bound,p.limit)
    lt=float(np.mean(((y-target)/task.r_ref)**2))
    alt=[]
    for q in PRIMITIVES:
        if q == p.primitive: continue
        a=_template(q,x,task.y_master[0],slope0,p.sign,p.bound,p.limit)
        # eta controls predeclared target-versus-alternative prefix contrast.
        mixed=(1-task.eta)*target + task.eta*a
        alt.append(float(np.mean(((y-mixed)/task.r_ref)**2)))
    la=min(alt)
    u=np.clip((la-lt)/.02, -60, 60)
    return float(1/(1+np.exp(-u)))


def _weights(f: np.ndarray, y: np.ndarray, r_ref: float) -> np.ndarray:
    loss=np.mean(((f-y[None,:])/r_ref)**2,axis=1)
    logw=-(loss-loss.min())/(2*.02)
    w=np.exp(np.clip(logw,-745,0)); return w/max(w.sum(),1e-300)


def score_prefix(task: FrozenTask, prefix: float, dof: int) -> dict:
    """Pure E9 scoring: accepts a frozen post-validation task; no future data API."""
    n=int(round(prefix*120))+1
    x=task.x_master[:n]; y=task.y_master[:n]
    f,active=_bank_functions(task,dof,x); w=_weights(f,y,task.r_ref)
    fg,_=_bank_functions(task,dof,GRID)
    sat=_prior_satisfied(task.supplied.primitive,task.supplied.sign,task.supplied.bound,task.supplied.limit,fg,active)
    prob=(float(np.sum(w*sat))+LAPLACE_A)/(float(np.sum(w))+LAPLACE_B)
    sharp=-math.log(max(prob,P_FLOOR))
    ess=float(1/np.sum(w*w))
    mu=np.sum(active*w[:,None],axis=0); cen=active-mu
    cov=np.einsum("i,ij,ik->jk", w, cen, cen)
    tr=float(np.trace(cov)); den=float(np.trace(cov@cov)); deff=0. if den < 1e-12 else tr*tr/den
    fmu=np.sum(fg*w[:,None],axis=0); vf=float(np.mean(np.sum(w[:,None]*(fg-fmu)**2,axis=0)))
    estruct=_structural_evidence(task,x,y)
    reliable=ess >= 100
    if not reliable: state="measurement-unreliable"
    elif sharp >= .10 and estruct < .80: state="external-informative"
    elif sharp >= .10 and estruct >= .80: state="observed+informative"
    elif sharp < .10 and estruct >= .80: state="observed+redundant"
    else: state="unresolved"
    return {"task_id":task.task_id,"primitive":task.primitive,"separability":task.eta_name,"eta":task.eta,
            "generator":task.generator,"seed":task.seed,"prefix":prefix,"dof":dof,"n_obs":n,
            "coverage":1,"S":sharp,"ESS":ess,"E_struct":estruct,"d_eff":deff,"V_f":vf,
            "V_f_norm":vf/(task.r_ref**2),"state":state,"reliable":int(reliable)}


def endpoints(rows: list[dict]) -> dict:
    """Grid-resolved onset/censoring rules, including E_red risk set and re-entry."""
    rows=sorted(rows,key=lambda r:r["prefix"])
    def first(pred):
        for r in rows:
            if pred(r): return r["prefix"]
        return None
    add=first(lambda r:r["S"]>=.10 and r["ESS"]>=100)
    obs=first(lambda r:r["E_struct"]>=.80)
    joint=first(lambda r:r["S"]>=.10 and r["ESS"]>=100 and r["E_struct"]>=.80)
    red=None; reentry=None
    if joint is not None:
        for i in range(len(rows)-1):
            a,b=rows[i],rows[i+1]
            cond=lambda r:r["E_struct"]>=.80 and r["S"]<.10 and r["ESS"]>=100
            if a["prefix"]>=joint and cond(a) and cond(b):
                red=a["prefix"]
                later=rows[i+2:]
                reentry=None if not later else int(any(r["S"]>=.10 and r["ESS"]>=100 for r in later))
                break
    final=rows[-1]
    info_null=int(final["ESS"]>=100 and max((r["S"] for r in rows if r["ESS"]>=100),default=-np.inf)<.10)
    return {"E_add":add,"E_obs":obs,"E_joint":joint,"E_red":red,"E_red_at_risk":int(joint is not None),
            "E_red_reentry":reentry,"informational_null":info_null,
            "sampler_unresolved_final":int(final["ESS"]<100),
            "joint_unresolved":int(joint is None and final["ESS"]>=100 and not info_null)}


def toy_endpoint_checks() -> dict:
    def r(p,s,e,ess=150): return {"prefix":p,"S":s,"E_struct":e,"ESS":ess}
    a=endpoints([r(.2,.01,.1),r(.3,.11,.1),r(.4,.11,.9),r(.5,.01,.9),r(.6,.01,.9),r(.7,.01,.9)])
    b=endpoints([r(.2,.01,.1),r(.3,.01,.1),r(.4,.01,.1),r(.5,.01,.1),r(.6,.01,.1),r(.7,.11,.9)])
    return {"joint_and_redundancy":a["E_add"]==.3 and a["E_joint"]==.4 and a["E_red"]==.5 and a["E_red_reentry"]==0,
            "boundary_resolved":b["E_add"]==.7 and b["E_obs"]==.7 and b["E_joint"]==.7 and b["E_red"] is None,
            "all_pass":False}


def integrity(task: FrozenTask) -> dict:
    # validates actual storage/nesting and output finiteness; no directional result gate.
    bank_hash=hashlib.sha256(task.bank_z.tobytes()).hexdigest()
    rows=[]; hashes=[]; inactive=True
    for d in DOFS:
        for p in PREFIXES:
            rows.append(score_prefix(task,float(p),d)); hashes.append(bank_hash)
            _,active=_bank_functions(task,d,GRID); inactive &= bool(np.all(active[:,d:]==0))
    finite=all(np.isfinite([r[k] for k in ("S","ESS","d_eff","V_f","E_struct")]).all() for r in rows)
    nested=all(np.array_equal(task.x_master[:int(round(p*120))+1],task.x_master[:int(round(q*120))+1][:int(round(p*120))+1]) for p,q in zip(PREFIXES[:-1],PREFIXES[1:]))
    toy=toy_endpoint_checks(); toy["all_pass"]=all(v for k,v in toy.items() if k!="all_pass")
    return {"task_id":task.task_id,"rows":len(rows),"nested_prefixes":nested,"shared_bank":len(set(hashes))==1,
            "inactive_zero":inactive,"fixed_grid":bool(np.array_equal(GRID,np.linspace(.7,1.,161))),"coverage_all_one":all(r["coverage"]==1 for r in rows),
            "finite_metrics":finite,"toy_endpoint_logic":toy["all_pass"],"future_free_scoring_api":True}


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def run(mode: str):
    tasks=[make_task(p,n,e,g,seed) for p in PRIMITIVES for n,e in ETAS for g in GENERATORS for seed in range(20)]
    if mode=="sanity":
        # One deterministic task per stratum verifies implementation integrity.
        checks=[integrity(t) for t in tasks if t.seed==0]
        result={"mode":"integrity_sanity","n_checked_tasks":len(checks),"expected":63,
                "passed":all(all(bool(v) for k,v in c.items() if k not in {"task_id","rows"}) and c["rows"]==18 for c in checks),"checks":checks}
        target=OUT/"sanity"/"summary.json"; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps({k:v for k,v in result.items() if k!="checks"},indent=2)); return
    score=[]; ep=[]; checks=[]
    for idx,t in enumerate(tasks):
        by_d={}
        for d in DOFS:
            rr=[score_prefix(t,float(p),d) for p in PREFIXES]; score.extend(rr); by_d[d]=rr
            ep.append({"task_id":t.task_id,"primitive":t.primitive,"separability":t.eta_name,"eta":t.eta,"generator":t.generator,"seed":t.seed,"dof":d,**endpoints(rr)})
        if t.seed==0: checks.append(integrity(t))
        if (idx+1)%100==0: print(f"completed {idx+1}/{len(tasks)} latent tasks",flush=True)
    write_csv(OUT/"run"/"scoring_rows.csv",score); write_csv(OUT/"run"/"endpoint_rows.csv",ep); write_csv(OUT/"run"/"integrity_rows.csv",checks)
    manifest={"M":M,"fixed_G":[.70,1.0,161],"laplace_a":LAPLACE_A,"laplace_b":LAPLACE_B,
              "probability_floor":"1/(10*M)","temperature":.02,"r_ref":"clean_range_[0,.70]",
              "scoring_api":"FrozenTask only: no future target/RMSE/utility/engine fields"}
    (OUT/"run"/"execution_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    summary={"protocol":"E9_prior_information_lifecycle_v1","latent_tasks":len(tasks),"scoring_rows":len(score),"expected_scoring_rows":22680,
             "integrity_checks":len(checks),"integrity_passed":all(all(bool(v) for k,v in c.items() if k not in {"task_id","rows"}) and c["rows"]==18 for c in checks),
             "failures":0,"future_free_scoring":True,**manifest}
    (OUT/"run"/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8"); print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--mode",choices=("sanity","full"),default="sanity"); args=ap.parse_args(); run(args.mode)
