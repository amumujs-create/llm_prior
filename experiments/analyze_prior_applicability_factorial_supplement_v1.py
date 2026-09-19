#!/usr/bin/env python3
"""Analyze E8 A2/C2 without replacing engine-specific safety by an average."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/"results"/"prior_applicability_factorial_supplement_v1"/"run";OUT=ROOT/"results"/"prior_applicability_factorial_supplement_v1"/"analysis";FIG=ROOT/"figures";B=5000
def seed(x):return int(hashlib.sha256(x.encode()).hexdigest()[:16],16)%(2**32)
def stat(g,key):
 r=np.random.default_rng(seed(str(key)));n=len(g);i=r.integers(0,n,(B,n));h=g.harmful.to_numpy()[i].mean(1);u=g.utility.to_numpy()[i].mean(1)
 return {"n":n,"harmful_rate":float(g.harmful.mean()),"harm_ci95_low":float(np.quantile(h,.025)),"harm_ci95_high":float(np.quantile(h,.975)),"mean_raw_utility":float(g.utility.mean()),"utility_ci95_low":float(np.quantile(u,.025)),"utility_ci95_high":float(np.quantile(u,.975)),"beneficial_rate":float(g.beneficial.mean()),"catastrophic_harm_rate":float(g.catastrophic_harm.mean())}
def summary(d,by):
 rows=[]
 for k,g in d.groupby(by,dropna=False,observed=False):k=(k,) if not isinstance(k,tuple) else k;rows.append({**dict(zip(by,k)),**stat(g,k)})
 return pd.DataFrame(rows)
def main():
 OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True);d=pd.read_csv(RUN/"records.csv");assert d.solver_failure.sum()==0
 key=[c for c in d.columns if c not in ["engine","baseline_rmse","prior_rmse","utility","normalized_utility","beneficial","harmful","catastrophic_harm","solver_failure"]]
 r=d.groupby(key,dropna=False,observed=False).agg(utility=("utility","mean"),harmful=("harmful","max"),beneficial=("beneficial","min"),catastrophic_harm=("catastrophic_harm","max")).reset_index()
 a=d[d.study.eq("A2_fixed_absolute_horizon")];ar=r[r.study.eq("A2_fixed_absolute_horizon")];c=d[d.study.eq("C2_bias_symmetry")];cr=r[r.study.eq("C2_bias_symmetry")]
 out=[]
 for name,z,by,target in [("A2",a,["engine","support_fraction","noise_ratio"],"engine_conditioned"),("A2",ar,["support_fraction","noise_ratio"],"robust_any_engine_harm"),("C2",c,["engine","ood_distance","action"],"engine_conditioned"),("C2",cr,["ood_distance","action"],"robust_any_engine_harm")]:
  q=summary(z,by);q["study"]=name;q["target"]=target;out.append(q)
 s=pd.concat(out,ignore_index=True);s.to_csv(OUT/"summary_bootstrap.csv",index=False)
 primitive=summary(d,["study","primitive","engine","action","support_fraction","noise_ratio","ood_distance"]);primitive.to_csv(OUT/"primitive_engine_strata.csv",index=False)
 fig,ax=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
 q=s[(s.study=="A2")&(s.target=="robust_any_engine_harm")].pivot(index="support_fraction",columns="noise_ratio",values="harmful_rate").reindex(index=[.35,.525,.70],columns=[.001,.01,.05]);im=ax[0].imshow(q.to_numpy(),vmin=0,vmax=1,cmap="Reds");ax[0].set(xticks=range(3),xticklabels=q.columns,yticks=range(3),yticklabels=q.index,title="A2 robust unsafe: fixed absolute horizon",xlabel="noise ratio",ylabel="support fraction")
 for i in range(3):
  for j in range(3):ax[0].text(j,i,f"{q.iloc[i,j]:.2f}",ha="center",va="center")
 q=s[(s.study=="C2")&(s.target=="robust_any_engine_harm")]
 for action,g in q.groupby("action",observed=False):g=g.sort_values("ood_distance");ax[1].plot(g.ood_distance,g.harmful_rate,"o-",label=action)
 ax[1].set(title="C2 robust unsafe: signed bias",xlabel="OOD distance",ylabel="robust-unsafe rate",ylim=(0,1));ax[1].legend();fig.colorbar(im,ax=ax[0],label="rate");fig.savefig(FIG/"fig32_e8_supplement_a2_c2.png",dpi=180);plt.close(fig)
 m={"bootstrap_replicates":B,"n_records":len(d),"n_latent_tasks":d.latent_task_id.nunique(),"solver_failures":int(d.solver_failure.sum()),"records_sha256":hashlib.sha256((RUN/"records.csv").read_bytes()).hexdigest()};(OUT/"manifest.json").write_text(json.dumps(m,indent=2)+"\n");print(json.dumps(m,indent=2))
if __name__=="__main__":main()
