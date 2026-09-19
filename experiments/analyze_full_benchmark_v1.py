#!/usr/bin/env python3
"""Locked-outcome analysis for full Prior Primitive–Composition Benchmark v1."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/"results"/"full_benchmark_v1"/"run"
OUT=ROOT/"results"/"full_benchmark_v1"/"analysis"
FIG=ROOT/"figures"
PRIMS=["direction","curvature","inflection","turning","regime","bound","asymptote"]

def agg(df,by,metrics): return df.groupby(by,dropna=False,observed=False)[metrics].mean().reset_index()
def qbin(s): return pd.qcut(s.rank(method="first"),5,labels=["Q1","Q2","Q3","Q4","Q5"])
def hierarchical_ci(z,value,seed=62001,B=5000):
 rng=np.random.default_rng(seed); cells=list(z.cell_id.unique()); vals=np.empty(B)
 groups={c:z[z.cell_id==c][value].to_numpy() for c in cells}
 for b in range(B):
  chosen=rng.choice(cells,len(cells),replace=True); vals[b]=np.mean([np.mean(groups[c][rng.integers(0,len(groups[c]),len(groups[c]))]) for c in chosen])
 return float(np.mean(vals)),float(np.quantile(vals,.025)),float(np.quantile(vals,.975))

def main():
 OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
 d=pd.read_csv(RUN/"task_candidate_engine.csv",low_memory=False)
 # Pair engines before all scientific summaries so each task/action counts once.
 m=["coverage","sharpness","ess","logical_specificity","baseline_rmse","prior_rmse","utility","normalized_utility","harmful","beneficial","solver_failure"]
 task=agg(d,[c for c in d.columns if c not in m+["engine","parameter_count","sharpness_spline","sharpness_basis","sharpness_rank_gap"]],m)
 task["neutral"]=(np.abs(task.normalized_utility)<=.02).astype(int)
 task["catastrophic_harm"]=(task.prior_rmse>=2*task.baseline_rmse).astype(int)
 task["informational_null"]=(task.sharpness<.10).astype(int)
 # Primitive anatomy: true-full only, memberships pool task cells but keep unit task.
 tf=task[(task.action=="true-full")&(task.null_type=="none")].copy(); pieces=[]
 for p in PRIMS:
  z=tf[tf.composition.str.split("+").apply(lambda x:p in x)].copy(); z["primitive"]=p;pieces.append(z)
 prim=pd.concat(pieces); anatomy=agg(prim,"primitive",["coverage","sharpness","informational_null","normalized_utility","harmful","catastrophic_harm","beneficial","ess"])
 anatomy.to_csv(OUT/"primitive_anatomy.csv",index=False)
 # Composition marginal information: all-vs-subset paired within each task.
 piv=task[task.action.isin(["true-subset","true-full"])].pivot(index="task_id",columns="action",values=["sharpness","normalized_utility","coverage","harmful"])
 delta=pd.DataFrame({"delta_sharpness":piv["sharpness"]["true-full"]-piv["sharpness"]["true-subset"],"delta_utility":piv["normalized_utility"]["true-full"]-piv["normalized_utility"]["true-subset"],"coverage_full":piv["coverage"]["true-full"],"harm_full":piv["harmful"]["true-full"]}).reset_index().merge(task[["task_id","composition","composition_size","generator","support_fraction","noise_ratio","exposure","ood_distance","effect_strength"]].drop_duplicates(),on="task_id")
 comp=agg(delta[delta.composition_size>1],"composition",["delta_sharpness","delta_utility","harm_full"]);comp.to_csv(OUT/"composition_deltaS_deltaU.csv",index=False)
 # Hurdle map: bins for data coordinates, true-full only.
 hm=[]
 for v in ["support_fraction","noise_ratio","exposure","ood_distance","effect_strength"]:
  z=tf.copy();z["bin"]=qbin(z[v]);a=agg(z,"bin",["sharpness","normalized_utility","harmful","informational_null"]);a["axis"]=v;hm.append(a)
 hurdle=pd.concat(hm);hurdle.to_csv(OUT/"hurdle_map.csv",index=False)
 # Knowledge sensitivity and generator robustness.
 know=agg(task[(task.action.isin(["true-subset","true-full","biased-specific"]))&(task.null_type=="none")],"action",["coverage","sharpness","normalized_utility","harmful","catastrophic_harm","beneficial"]);know.to_csv(OUT/"knowledge_sensitivity.csv",index=False)
 know_median=task[(task.action.isin(["true-subset","true-full","biased-specific"]))&(task.null_type=="none")].groupby("action")["normalized_utility"].median().reindex(know.action).to_numpy()
 robust=agg(prim,["primitive","generator"],["sharpness","normalized_utility","harmful","informational_null"]);robust.to_csv(OUT/"generator_robustness.csv",index=False)
 # Null/abstention: chosen baseline vs every supplied prior, without retroactive selection rule.
 null=task[task.null_type!="none"].copy();nullsum=agg(null,["null_type","action"],["normalized_utility","harmful","catastrophic_harm","sharpness","prior_rmse","baseline_rmse"]);nullsum.to_csv(OUT/"null_abstention.csv",index=False)
 # Frozen 5,000-replicate paired hierarchical bootstrap over composition cells then tasks.
 boot=[]
 for action in ["true-subset","true-full","biased-specific","mixed-true-false","fully-wrong"]:
  z=task[(task.action==action)&(task.null_type=="none")];mean,lo,hi=hierarchical_ci(z,"normalized_utility",62001+len(boot));boot.append({"action":action,"macro_normalized_utility":mean,"ci95_low":lo,"ci95_high":hi,"n":len(z)})
 pd.DataFrame(boot).to_csv(OUT/"hierarchical_bootstrap.csv",index=False)
 # Summary JSON.
 summary={"n_task_action":int(len(task)),"n_raw_records":int(len(d)),"primitive_anatomy":anatomy.round(6).to_dict("records"),"knowledge":know.round(6).to_dict("records"),"null":nullsum.round(6).to_dict("records"),"hierarchical_bootstrap":boot,"solver_failures":int(d.solver_failure.sum())}
 (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 # Figures.
 fig,ax=plt.subplots(1,2,figsize=(12,4.4));x=np.arange(len(anatomy))
 ax[0].bar(x-.18,anatomy.sharpness,.36,label="sharpness");ax[0].bar(x+.18,anatomy.informational_null,.36,label="info-null rate");ax[0].set_xticks(x,anatomy.primitive,rotation=35,ha="right");ax[0].legend();ax[0].set_title("Primitive information anatomy")
 ax[1].scatter(comp.delta_sharpness,comp.delta_utility,c=comp.harm_full,cmap="Reds",s=55);ax[1].axhline(0,c="k",lw=.7);ax[1].axvline(0,c="k",lw=.7);ax[1].set(xlabel="ΔS(full − subset)",ylabel="Δ normalized utility",title="Composition incremental information")
 fig.tight_layout();fig.savefig(FIG/"fig27_full_v1_anatomy_composition.png",dpi=180);plt.close(fig)
 fig,ax=plt.subplots(1,2,figsize=(12,4.4));
 for v,g in hurdle.groupby("axis"):
  ax[0].plot(g.bin.astype(str),g.normalized_utility,"o-",label=v);ax[1].plot(g.bin.astype(str),g.informational_null,"o-",label=v)
 ax[0].axhline(0,c="k",lw=.7);ax[0].set_title("Utility across data-condition quintiles");ax[0].set_ylabel("normalized utility");ax[1].set_title("Informational-null rate across quintiles");ax[1].set_ylabel("rate");
 for a in ax:a.legend(fontsize=7)
 fig.tight_layout();fig.savefig(FIG/"fig28_full_v1_hurdle_map.png",dpi=180);plt.close(fig)
 fig,ax=plt.subplots(1,2,figsize=(12,4.4));
 ax[0].bar(know.action,know_median,color=["#3978b8","#43a86b","#cc4c4c"]);ax[0].axhline(0,c="k",lw=.7);ax[0].tick_params(axis="x",rotation=25);ax[0].set_title("Knowledge quality: median normalized utility")
 for nt,g in nullsum.groupby("null_type"):
  ax[1].plot(g.action,g.harmful,"o-",label=nt)
 ax[1].tick_params(axis="x",rotation=25);ax[1].set_ylim(0,1);ax[1].set_title("Null tasks: harmful-rate by action");ax[1].legend()
 fig.tight_layout();fig.savefig(FIG/"fig29_full_v1_knowledge_null.png",dpi=180);plt.close(fig)
 print(json.dumps({"n_task_action":len(task),"n_compositions":len(comp),"solver_failures":int(d.solver_failure.sum())},indent=2))
if __name__=="__main__":main()
