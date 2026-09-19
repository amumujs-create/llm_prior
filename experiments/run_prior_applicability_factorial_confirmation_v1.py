#!/usr/bin/env python3
"""Execute the frozen E8 prior-applicability factorial confirmation."""
from __future__ import annotations
import csv, hashlib, json, time
from pathlib import Path
import numpy as np
from full_benchmark_v1_core import PRIMITIVES, fit_engine, generate_truth, realized_prediction
from run_full_benchmark_v1 import candidate, sharpness

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"prior_applicability_factorial_confirmation_v1"/"run"
PROTOCOL=ROOT/"PRIOR_APPLICABILITY_FACTORIAL_CONFIRMATION_PROTOCOL_V1.md"
ENGINES=("spline","neural"); GENERATORS=("spline","basis","ode"); REPS=20

def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def seed(key: str) -> int: return int(hashlib.sha256(key.encode()).hexdigest()[:16],16)%(2**32)

def conditions():
    common={"sample_count":72,"heterogeneity_cv":.10}
    for support in (.35,.525,.70):
        for noise in (.001,.01,.05):
            yield "support_noise",{"support_fraction":support,"noise_ratio":noise,"exposure":.55,"ood_distance":.40,"effect_strength":.55,**common},("true-full",)
    for exposure in (.10,.45,.80):
        for effect in (.15,.45,.85):
            yield "exposure_effect",{"support_fraction":.525,"noise_ratio":.01,"exposure":exposure,"ood_distance":.40,"effect_strength":effect,**common},("true-full",)
    for distance in (.10,.40,.80):
        yield "distance_specificity",{"support_fraction":.525,"noise_ratio":.01,"exposure":.55,"ood_distance":distance,"effect_strength":.55,**common},("true-subset","true-full","biased-specific")

def main() -> None:
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={"protocol_sha256":sha(PROTOCOL),"script_sha256":sha(Path(__file__)),"seed_base":81000,"replicates":REPS,
              "n_factorial_cells":{"support_noise":9,"exposure_effect":9,"distance_specificity":3},"complete":False}
    (OUT/"run_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    rec=[]; task_id=0; started=time.time()
    for factorial,cond,actions in conditions():
        for primitive in PRIMITIVES:
            for generator in GENERATORS:
                for rep in range(REPS):
                    key=f"81000|{factorial}|{primitive}|{generator}|{rep}|{cond}"
                    rng=np.random.default_rng(seed(key)); support=cond["support_fraction"]; xmax=support*(1+cond["ood_distance"])
                    xq=np.linspace(0,xmax,161); xobs=np.linspace(0,support,cond["sample_count"])
                    yq,meta=generate_truth((primitive,),generator,xq,rng,cond["effect_strength"],cond["heterogeneity_cv"])
                    yclean=np.interp(xobs,xq,yq); noise_sd=cond["noise_ratio"]*max(float(np.ptp(yclean)),1e-8); yobs=yclean+rng.normal(0,noise_sd,len(xobs)); tail=xq>support
                    base={eng:fit_engine(eng,xobs,yobs,xq)[0] for eng in ENGINES}
                    row={**cond,"task_id":f"e8_{task_id:05d}"}; task_id+=1
                    for action in actions:
                        prims,params,tier,coverage=candidate(action,(primitive,),meta)
                        qs=[]; esses=[]
                        for name,scale in (("spline",1.0),("basis",1.15)):
                            s,e,_=sharpness(prims,(primitive,),row,tier,np.random.default_rng(seed(key+action+name)),scale);qs.append(s);esses.append(e)
                        for engine in ENGINES:
                            br=float(np.sqrt(np.mean((base[engine][tail]-yq[tail])**2)))
                            pred,diag=realized_prediction(engine,xobs,yobs,xq,prims,params)
                            pr=float(np.sqrt(np.mean((pred[tail]-yq[tail])**2))); utility=br-pr; nu=utility/max(br,1e-8)
                            rec.append({"latent_task_id":row["task_id"],"factorial":factorial,"primitive":primitive,"generator":generator,"replicate":rep,"engine":engine,"action":action,"knowledge_tier":tier,**cond,
                                        "coverage":coverage,"sharpness":float(np.mean(qs)),"ess":float(min(esses)),"baseline_rmse":br,"prior_rmse":pr,"utility":utility,"normalized_utility":nu,
                                        "beneficial":int(nu>.02),"harmful":int(nu<-.02),"catastrophic_harm":int(pr>=2*br),"solver_failure":int(diag["solver_failure"] or diag.get("residual_solver_failure",False))})
                    if task_id%500==0: print(f"{task_id} latent tasks",flush=True)
    with (OUT/"records.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,rec[0].keys());w.writeheader();w.writerows(rec)
    manifest.update({"complete":True,"n_latent_tasks":task_id,"n_records":len(rec),"solver_failures":sum(r["solver_failure"] for r in rec),"elapsed_seconds":time.time()-started,"records_sha256":sha(OUT/"records.csv")})
    (OUT/"run_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n");print(json.dumps(manifest,indent=2))

if __name__=="__main__": main()
