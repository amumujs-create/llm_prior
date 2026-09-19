#!/usr/bin/env python3
"""Execute frozen 3,375-task Prior Primitive–Composition Benchmark v1."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,time
from pathlib import Path
import numpy as np
from full_benchmark_v1_core import PRIMITIVES,fit_engine,generate_truth,realized_prediction
from structural_null_validation_v1_1 import draw_curve

ROOT=Path(__file__).resolve().parents[1]
CORPUS=ROOT/"results"/"full_benchmark_v1"/"corpus"/"task_manifest.csv"
OUT=ROOT/"results"/"full_benchmark_v1"/"run"
M=4096
ACTIONS=("abstain","true-subset","true-full","biased-specific","mixed-true-false","fully-wrong")
ENGINES=("spline","neural")
DIFFICULTY={"direction":.55,"curvature":.65,"inflection":1.5,"turning":1.45,"regime":1.05,"bound":1.25,"asymptote":.85}

def seed_for(s): return int(hashlib.sha256(s.encode()).hexdigest()[:16],16)%(2**32)
def sigmoid(z): return 1/(1+np.exp(-np.clip(z,-30,30)))
def choose_wrong(truth): return next(p for p in PRIMITIVES if p not in truth)

def candidate(action,truth,meta):
    truth=tuple(truth); wrong=choose_wrong(set(truth)) if truth else "direction"
    if action=="abstain": return (),{},"none",1.0
    if action=="true-subset":
        p=(truth[0],) if truth else (wrong,); return p,{"sign":meta.get("sign",-1),"bound":meta.get("bound",0),"limit":meta.get("limit",0)},"broad",1.0 if truth else 0.0
    if action=="true-full": return truth,dict(meta),"medium",1.0
    if action=="biased-specific":
        z=dict(meta); z["tau"]=min(1.0,z.get("tau",.5)+.20); z["rate"]=z.get("rate",1)*1.5; z["bound"]=z.get("bound",0)+.20
        return truth,z,"narrow-biased",0.0
    if action=="mixed-true-false":
        p=((truth[0],wrong) if truth else (wrong,"curvature")); return p,dict(meta),"medium",0.0
    return (wrong,),{"sign":-meta.get("sign",1),"tau":.8,"rate":.5,"bound":.4,"limit":.4},"medium",0.0

def sharpness(prims,truth,row,tier,rng,scale):
    if not prims:return 0.0,float(M),1.0
    support=float(row["support_fraction"]); noise=float(row["noise_ratio"]); exposure=float(row["exposure"]); effect=float(row["effect_strength"])
    survive=np.ones(M,dtype=bool); ess_values=[]
    for p in prims:
        signal=support*(.25+exposure)*effect/(noise+.015)/DIFFICULTY[p]
        istrue=p in truth
        prob=float(sigmoid(np.log(1.5)+np.log1p(signal) if istrue else -2.2-.35*np.log1p(signal)))
        presence=rng.random(M)<prob; survive &= presence
        sd=np.clip(DIFFICULTY[p]*(noise+.015)/(support*(.2+exposure)*effect+1e-5)*scale,.02,.55)
        theta=rng.normal(.5,sd,M)
        if tier=="broad": ok=np.abs(theta-.5)<=.30
        elif tier=="narrow-biased": ok=np.abs(theta-.70)<=.05
        else: ok=np.abs(theta-.5)<=.15
        survive &= ok; ess_values.append(min(M,1/(sd*sd+1e-8)))
    phat=(survive.sum()+.5)/(M+1); S=-math.log(max(phat,1/(10*M)))
    return S,float(min(ess_values) if ess_values else M),float(phat)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--limit",type=int); ap.add_argument("--output",type=Path,default=OUT); args=ap.parse_args()
    rows=list(csv.DictReader(CORPUS.open())); rows=rows[:args.limit] if args.limit else rows
    args.output.mkdir(parents=True,exist_ok=True); rec=[]; taskdiag=[]; start=time.time()
    for ti,row in enumerate(rows):
        rng=np.random.default_rng(seed_for(row["task_id"])); support=float(row["support_fraction"]); dist=float(row["ood_distance"])
        xmax=support*(1+dist); xq=np.linspace(0,xmax,161); n=int(row["sample_count"]); xobs=np.linspace(0,support,n)
        truth=tuple(row["composition"].split("+")) if row["null_type"]=="none" else ()
        if row["null_type"]=="structural":
            fullx=np.unique(np.r_[xobs,xq]); yfull=draw_curve(row["generator"],rng,fullx); yq=np.interp(xq,fullx,yfull); yclean=np.interp(xobs,fullx,yfull); meta={"sign":1,"bound":0,"limit":0,"rate":1,"tau":support+.2}
        else:
            latent_truth=truth
            if row["null_type"]=="informational": latent_truth=(("inflection",) if ti%2==0 else ("turning",))
            yq,meta=generate_truth(latent_truth,row["generator"],xq,rng,float(row["effect_strength"]),float(row["heterogeneity_cv"])); yclean=np.interp(xobs,xq,yq)
            if row["null_type"]=="informational": truth=latent_truth
        noise=float(row["noise_ratio"])*max(float(np.ptp(yclean)),1e-8); yobs=yclean+rng.normal(0,noise,n)
        tail=xq>support; baseline={}; bdiag={}
        for eng in ENGINES: baseline[eng],bdiag[eng]=fit_engine(eng,xobs,yobs,xq)
        for action in ACTIONS:
            prims,params,tier,coverage=candidate(action,truth,meta)
            qs=[]; esses=[]
            for q,scale in (("spline",1.0),("basis",1.15)):
                s,e,_=sharpness(prims,truth,row,tier,np.random.default_rng(seed_for(row["task_id"]+action+q)),scale); qs.append(s); esses.append(e)
            for eng in ENGINES:
                br=float(np.sqrt(np.mean((baseline[eng][tail]-yq[tail])**2)))
                if action=="abstain": pred=baseline[eng]; diag=bdiag[eng]
                else: pred,diag=realized_prediction(eng,xobs,yobs,xq,prims,params)
                rr=float(np.sqrt(np.mean((pred[tail]-yq[tail])**2))); u=br-rr; un=u/max(br,1e-8)
                rec.append({**row,"engine":eng,"action":action,"candidate_primitives":"+".join(prims),"knowledge_tier":tier,
                  "coverage":coverage,"sharpness":float(np.mean(qs)),"sharpness_spline":qs[0],"sharpness_basis":qs[1],"sharpness_rank_gap":abs(qs[0]-qs[1]),
                  "ess":float(min(esses)),"logical_specificity":len(prims)+({"broad":1,"medium":2,"narrow-biased":3}.get(tier,0)),
                  "baseline_rmse":br,"prior_rmse":rr,"utility":u,"normalized_utility":un,"harmful":int(un<-.02),"beneficial":int(un>.02),
                  "solver_failure":int(diag["solver_failure"] or diag.get("residual_solver_failure",False)),"parameter_count":diag["parameter_count"]+diag.get("residual_parameter_count",0)})
        taskdiag.append({"task_id":row["task_id"],"noise_sd":noise,"target_range":float(np.ptp(yq))})
        if (ti+1)%250==0: print(f"{ti+1}/{len(rows)}",flush=True)
    with (args.output/"task_candidate_engine.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,rec[0].keys());w.writeheader();w.writerows(rec)
    with (args.output/"task_diagnostics.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,taskdiag[0].keys());w.writeheader();w.writerows(taskdiag)
    summary={"n_tasks":len(rows),"n_records":len(rec),"M":M,"elapsed_seconds":time.time()-start,
      "solver_failure_count":sum(r["solver_failure"] for r in rec),"complete":len(rows)==3375}
    (args.output/"run_summary.json").write_text(json.dumps(summary,indent=2)+"\n"); print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
