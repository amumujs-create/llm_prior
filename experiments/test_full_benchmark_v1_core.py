#!/usr/bin/env python3
from __future__ import annotations
import json, numpy as np
from full_benchmark_v1_core import ENGINES,generate_truth,fit_engine,realized_prediction

def main():
    rng=np.random.default_rng(60001); x=np.linspace(0,1.2,121); obs=x<=.6; errors=[]; records=[]
    cases=[("direction",),("curvature",),("inflection",),("turning",),("regime",),("bound",),("asymptote",),
           ("direction","curvature","bound"),("regime","bound","asymptote")]
    for comp in cases:
        for gen in ("spline","basis","ode"):
            y,meta=generate_truth(comp,gen,x,rng,.8,.05); yo=y[obs]+rng.normal(0,.01*np.ptp(y),obs.sum())
            for eng in ENGINES:
                base,d=fit_engine(eng,x[obs],yo,x); pred,pd=realized_prediction(eng,x[obs],yo,x,comp,meta)
                ok=np.all(np.isfinite(y)) and np.all(np.isfinite(base)) and np.all(np.isfinite(pred)) and not d["solver_failure"]
                if not ok: errors.append(f"{comp}-{gen}-{eng}")
                records.append({"composition":"+".join(comp),"generator":gen,"engine":eng,"ok":ok,
                                "parameter_count":d["parameter_count"],"evaluations":d["solver_evaluations"]})
    result={"passed":not errors,"n_cases":len(records),"errors":errors,
            "engine_parameter_counts":{e:sorted(set(r["parameter_count"] for r in records if r["engine"]==e)) for e in ENGINES},
            "all_three_initializations":all(r["evaluations"]==3 for r in records)}
    print(json.dumps(result,indent=2)); raise SystemExit(0 if result["passed"] else 1)
if __name__=="__main__": main()
