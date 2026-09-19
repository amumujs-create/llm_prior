#!/usr/bin/env python3
"""Common effect-size/safety audit over stored legacy synthetic results."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"results"/"legacy_metric_audit_v1"; OUT.mkdir(parents=True,exist_ok=True)
RNG=np.random.default_rng(20260919); B=5000
def boot(x):
 x=np.asarray(x,float); n=len(x); vals=np.empty(B)
 for i in range(B): vals[i]=np.mean(x[RNG.integers(0,n,n)])
 return float(np.mean(x)),[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]
def rows_from_pair(name,df,base,prior,extra=[]):
 z=df.copy(); z["experiment"]=name; z["baseline_rmse"]=z[base];z["prior_rmse"]=z[prior]
 z["delta_rmse"]=z[base]-z[prior];z["normalized_utility"]=z.delta_rmse/np.maximum(z[base],1e-8)
 z["class"]=np.where(z.normalized_utility>.02,"beneficial",np.where(z.normalized_utility<-.02,"harmful","neutral"))
 z["catastrophic_harm"]=z[prior]>=2*z[base];z["r2_status"]="not_recoverable: trajectories absent";return z
def summarize(z,groups):
 out=[]
 for k,g in z.groupby(groups,dropna=False):
  k=(k,) if not isinstance(k,tuple) else k; mean,ci=boot(g.normalized_utility); delta_mean,delta_ci=boot(g.delta_rmse)
  d={n:v for n,v in zip(groups,k)};d.update(n=len(g),mean_normalized_utility=mean,ci95_low=ci[0],ci95_high=ci[1],
   mean_delta_rmse=delta_mean,delta_rmse_ci95_low=delta_ci[0],delta_rmse_ci95_high=delta_ci[1],beneficial_rate=float((g['class']=="beneficial").mean()),neutral_rate=float((g['class']=="neutral").mean()),harmful_rate=float((g['class']=="harmful").mean()),catastrophic_harm_rate=float(g.catastrophic_harm.mean()))
  out.append(d)
 return out
def main():
 audits=[]; availability=[]; gap_rows=[]; selection_rows=[]
 # E5 calibration/specificity
 p=ROOT/"results"/"prior_calibration_specificity_v1"/"results.json"; d=pd.DataFrame(json.loads(p.read_text())["records"]);z=rows_from_pair("E5_prior_calibration_specificity",d,"fallback_rmse","prior_rmse");audits+=summarize(z,["experiment","family","condition"]);availability.append({"experiment":"E5","coverage_sharpness":"coverage recoverable only by condition semantics; conditional sharpness not recoverable: no trajectories/ensemble"})
 # E5b: narrow vs broad comparator
 p=ROOT/"results"/"calibration_tolerance_v1"/"results.json";d=pd.DataFrame(json.loads(p.read_text())["records"]);z=rows_from_pair("E5b_calibration_tolerance",d,"broad_correct_rmse","narrow_biased_rmse");audits+=summarize(z,["experiment","family","fields","b_norm"]);availability.append({"experiment":"E5b","coverage_sharpness":"logical broad/narrow coverage available; conditional sharpness not recoverable: no trajectories/ensemble"})
 # Partial realization
 p=ROOT/"results"/"partial_realization_knowledge_sweep_v1"/"results.json";d=pd.DataFrame(json.loads(p.read_text())["records"]);z=rows_from_pair("partial_realization",d,"no_prior","partial_rmse");audits+=summarize(z,["experiment","family","knowledge_subset"])
 # Exposure/oracle methods
 p=ROOT/"results"/"exposure_identifiability_extension_v1"/"results.json";d=pd.DataFrame(json.loads(p.read_text())["records"])
 methods=["generative_family_oracle","parameter_oracle","full_information_oracle"]
 for m in methods:
  z=rows_from_pair("exposure_oracle",d,"no_prior",m);z["method"]=m
  # family-to-parameter gap closure, guarded when denominator is near zero
  denom=d.generative_family_oracle-d.parameter_oracle
  z["gap_closure"]=(d.generative_family_oracle-d[m])/denom.where(abs(denom)>1e-8)
  audits+=summarize(z,["experiment","family","observability","method"])
  for (family, observability), g in z.groupby(["family","observability"],dropna=False):
   valid=g.gap_closure.dropna()
   if len(valid):
    mean,ci=boot(valid)
    gap_rows.append({"experiment":"exposure_oracle","family":family,"observability":observability,"method":m,"n_valid":len(valid),"mean_gap_closure":mean,"ci95_low":ci[0],"ci95_high":ci[1]})
 # E6 distance: pair every method with prior row
 p=ROOT/"results"/"distance_residual_trust_v1"/"results.json";d=pd.DataFrame(json.loads(p.read_text())["records"]); keys=["task_id","family","observability_level","noise_sd","architecture","distance"]
 base=d[d.method=="prior"][keys+["rmse"]].rename(columns={"rmse":"base"});q=d[d.method!="prior"].merge(base,on=keys);z=rows_from_pair("E6_distance_residual",q,"base","rmse");z["method"]=q.method;audits+=summarize(z,["experiment","family","architecture","distance","method"])
 # E1/E2 selection audit: regret is already paired to the oracle far-OOD winner.
 p=ROOT/"results"/"prior_evaluation_metric_v1"/"results.json"; d=pd.DataFrame(json.loads(p.read_text())["records"])
 for groups,g in d.groupby(["metric","band","family"],dropna=False):
  metric,band,family=groups; mean,ci=boot(g.regret)
  selection_rows.append({"experiment":"E1_E2_prior_evaluation_metric","metric":metric,"band":band,"family":family,"n":len(g),"mean_selection_regret":mean,"ci95_low":ci[0],"ci95_high":ci[1],"winner_disagreement_rate":float(g.winner_disagreement.mean()),"incompatible_selection_rate":float(g.incompatible.mean())})
 pd.DataFrame(audits).to_csv(OUT/"summary.csv",index=False);pd.DataFrame(availability).to_csv(OUT/"coverage_sharpness_availability.csv",index=False)
 pd.DataFrame(gap_rows).to_csv(OUT/"oracle_gap_closure.csv",index=False)
 pd.DataFrame(selection_rows).to_csv(OUT/"selection_regret.csv",index=False)
 result={"bootstrap_replicates":B,"utility_threshold":"beneficial > +0.02, harmful < -0.02 normalized utility relative to paired baseline RMSE","n_summary_rows":len(audits),"n_gap_closure_rows":len(gap_rows),"n_selection_regret_rows":len(selection_rows),"experiments":["E1/E2","E5","E5b","partial_realization","exposure_oracle","E6"],"r2":"supplementary unavailable because stored artifacts lack targets/predictions; explicitly flagged"}
 (OUT/"manifest.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
