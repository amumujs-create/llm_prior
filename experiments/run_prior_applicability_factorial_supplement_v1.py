#!/usr/bin/env python3
"""Execute E8 A2 and C2 interpretation controls from their frozen protocol."""
from __future__ import annotations
import csv, hashlib, json, time
from pathlib import Path
import numpy as np
from full_benchmark_v1_core import PRIMITIVES, fit_engine, generate_truth, realized_prediction
from run_full_benchmark_v1 import candidate, sharpness

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"prior_applicability_factorial_supplement_v1"/"run"
PROTOCOL=ROOT/"PRIOR_APPLICABILITY_FACTORIAL_SUPPLEMENT_PROTOCOL_V1.md"
ENGINES=("spline","neural"); GENERATORS=("spline","basis","ode"); REPS=20
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seed(x): return int(hashlib.sha256(x.encode()).hexdigest()[:16],16)%(2**32)
def specs():
    common={"sample_count":72,"heterogeneity_cv":.10,"exposure":.55,"effect_strength":.55}
    for support in (.35,.525,.70):
        for noise in (.001,.01,.05): yield "A2_fixed_absolute_horizon",{**common,"support_fraction":support,"noise_ratio":noise,"absolute_horizon":.21,"ood_distance":.21/support},("true-full",)
    for distance in (.10,.40,.80): yield "C2_bias_symmetry",{**common,"support_fraction":.525,"noise_ratio":.01,"ood_distance":distance,"absolute_horizon":.525*distance},("true-full","bias-negative","bias-positive")
def signed_candidate(action,truth,meta):
    if action in ("true-full",): return candidate(action,truth,meta)
    z=dict(meta); sign=-1 if action=="bias-negative" else 1
    z["tau"]=float(np.clip(z.get("tau",.5)+sign*.20,0,1)); z["rate"]=max(.05,z.get("rate",1)*(1+sign*.5)); z["bound"]=z.get("bound",0)+sign*.20
    return tuple(truth),z,"narrow-biased",0.0
def main():
    OUT.mkdir(parents=True,exist_ok=True); manifest={"protocol_sha256":sha(PROTOCOL),"script_sha256":sha(__file__),"seed_base":82000,"replicates":REPS,"complete":False}
    (OUT/"run_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n"); rec=[];tid=0;start=time.time()
    for study,cond,actions in specs():
        for primitive in PRIMITIVES:
            for generator in GENERATORS:
                for rep in range(REPS):
                    key=f"82000|{study}|{primitive}|{generator}|{rep}|{cond}";rng=np.random.default_rng(seed(key));support=cond["support_fraction"]
                    xq=np.linspace(0,support+cond["absolute_horizon"],161);xobs=np.linspace(0,support,cond["sample_count"]);yq,meta=generate_truth((primitive,),generator,xq,rng,cond["effect_strength"],cond["heterogeneity_cv"]);yclean=np.interp(xobs,xq,yq);noise_sd=cond["noise_ratio"]*max(float(np.ptp(yclean)),1e-8);yobs=yclean+rng.normal(0,noise_sd,len(xobs));tail=xq>support;base={e:fit_engine(e,xobs,yobs,xq)[0] for e in ENGINES};row={**cond,"task_id":f"e8s_{tid:05d}"};tid+=1
                    for action in actions:
                        prims,params,tier,coverage=signed_candidate(action,(primitive,),meta);qs=[];es=[]
                        for sampler,scale in (("spline",1.0),("basis",1.15)):
                            s,e,_=sharpness(prims,(primitive,),row,tier,np.random.default_rng(seed(key+action+sampler)),scale);qs.append(s);es.append(e)
                        for engine in ENGINES:
                            br=float(np.sqrt(np.mean((base[engine][tail]-yq[tail])**2)));pred,diag=realized_prediction(engine,xobs,yobs,xq,prims,params);pr=float(np.sqrt(np.mean((pred[tail]-yq[tail])**2)));u=br-pr;nu=u/max(br,1e-8)
                            rec.append({"latent_task_id":row["task_id"],"study":study,"primitive":primitive,"generator":generator,"replicate":rep,"engine":engine,"action":action,"knowledge_tier":tier,**cond,"coverage":coverage,"sharpness":float(np.mean(qs)),"ess":float(min(es)),"baseline_rmse":br,"prior_rmse":pr,"utility":u,"normalized_utility":nu,"beneficial":int(nu>.02),"harmful":int(nu<-.02),"catastrophic_harm":int(pr>=2*br),"solver_failure":int(diag["solver_failure"] or diag.get("residual_solver_failure",False))})
    with (OUT/"records.csv").open("w",newline="") as f:w=csv.DictWriter(f,rec[0].keys());w.writeheader();w.writerows(rec)
    manifest.update({"complete":True,"n_latent_tasks":tid,"n_records":len(rec),"solver_failures":sum(x["solver_failure"] for x in rec),"elapsed_seconds":time.time()-start,"records_sha256":sha(OUT/"records.csv")});(OUT/"run_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n");print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
