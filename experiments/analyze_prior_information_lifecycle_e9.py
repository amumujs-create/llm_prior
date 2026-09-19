#!/usr/bin/env python3
"""Predeclared E9 analysis: integrity -> reliability -> endpoints -> states -> anatomy."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/"results"/"prior_information_lifecycle_e9"/"run"
OUT=ROOT/"results"/"prior_information_lifecycle_e9"/"analysis"
FIG=ROOT/"figures"
PREFIX=np.array([.2,.3,.4,.5,.6,.7])
PRIMS=["direction","curvature","inflection","turning","regime","bound","asymptote"]
STATES=["external-informative","observed+informative","observed+redundant","unresolved","measurement-unreliable"]

def macro(df, keys, value):
    # Equal-generator macro aggregation, then task-weighted within generator stratum.
    a=df.groupby(keys+["generator"],as_index=False)[value].mean()
    return a.groupby(keys,as_index=False)[value].mean()

def attainment(ep, endpoint):
    rows=[]
    for (p,e,d),g in ep.groupby(["primitive","separability","dof"]):
        for s in PREFIX:
            if endpoint=="E_red":
                gg=g[g.E_red_at_risk==1]
                val=np.mean((gg[endpoint].notna()) & (gg[endpoint]<=s)) if len(gg) else np.nan
                den=len(gg)
            else:
                val=np.mean((g[endpoint].notna()) & (g[endpoint]<=s)); den=len(g)
            rows.append({"primitive":p,"separability":e,"dof":d,"prefix":s,"attainment":val,"denominator":den})
    return pd.DataFrame(rows)

def bootstrap_endpoint(ep, endpoint, reps=5000):
    """Paired latent-task bootstrap inside primitive×eta×generator strata."""
    rng=np.random.default_rng(90391); out=[]
    for (p,e,g,d),z in ep.groupby(["primitive","separability","generator","dof"]):
        arr=z[endpoint].to_numpy(float); n=len(arr)
        for s in PREFIX:
            vals=np.empty(reps)
            for i in range(reps):
                draw=arr[rng.integers(0,n,n)]
                vals[i]=np.mean(np.isfinite(draw)&(draw<=s))
            out.append({"primitive":p,"separability":e,"generator":g,"dof":d,"prefix":s,
                        "lo":np.quantile(vals,.025),"hi":np.quantile(vals,.975)})
    a=pd.DataFrame(out)
    return a.groupby(["primitive","separability","dof","prefix"],as_index=False)[["lo","hi"]].mean()

def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    sc=pd.read_csv(RUN/"scoring_rows.csv"); ep=pd.read_csv(RUN/"endpoint_rows.csv"); integ=pd.read_csv(RUN/"integrity_rows.csv")
    summary=json.loads((RUN/"summary.json").read_text())
    # 1 integrity
    integrity={"latent_tasks":int(sc.task_id.nunique()),"scoring_rows":int(len(sc)),"expected_latent_tasks":1260,
               "expected_scoring_rows":22680,"failures":summary["failures"],"full_integrity_checks":int(len(integ)),
               "all_invariants_pass":bool(integ.drop(columns=["task_id"]).all().all()),"future_free_scoring":summary["future_free_scoring"]}
    # 2 reliability
    reliability={"ESS":sc.ESS.describe(percentiles=[.05,.25,.5,.75,.95]).to_dict(),
                 "sampler_unresolved_final_rate":float(ep.sampler_unresolved_final.mean()),
                 "d_eff":sc.d_eff.describe(percentiles=[.05,.5,.95]).to_dict(),
                 "V_f_norm":sc.V_f_norm.describe(percentiles=[.05,.5,.95]).to_dict()}
    rel_by=macro(sc,["primitive","separability","dof","prefix"],"ESS")
    # 3 endpoints
    att={k:attainment(ep,k) for k in ["E_add","E_obs","E_joint","E_red"]}
    att["E_add"].to_csv(OUT/"attainment_E_add.csv",index=False); att["E_obs"].to_csv(OUT/"attainment_E_obs.csv",index=False)
    att["E_joint"].to_csv(OUT/"attainment_E_joint.csv",index=False); att["E_red"].to_csv(OUT/"attainment_E_red.csv",index=False)
    # frozen bootstrap only for headline E_add and E_joint (complete risk sets).
    ci_add=bootstrap_endpoint(ep,"E_add"); ci_joint=bootstrap_endpoint(ep,"E_joint")
    ci_add.to_csv(OUT/"bootstrap_E_add_5000.csv",index=False); ci_joint.to_csv(OUT/"bootstrap_E_joint_5000.csv",index=False)
    endpoint_summary={}
    for key in ["E_add","E_obs","E_joint","E_red"]:
        valid=ep[key].notna()
        endpoint_summary[key]={"attained_rate":float(valid.mean()),"right_censored_or_not_at_risk_rate":float((~valid).mean()),
                               "median_attained":None if not valid.any() else float(ep.loc[valid,key].median())}
    endpoint_summary["informational_null_rate"]=float(ep.informational_null.mean())
    endpoint_summary["joint_unresolved_rate"]=float(ep.joint_unresolved.mean())
    # 4 lifecycle states
    state=(sc.groupby(["primitive","separability","dof","prefix","generator","state"]).size().rename("n").reset_index())
    state["fraction"]=state.groupby(["primitive","separability","dof","prefix","generator"])["n"].transform(lambda x:x/x.sum())
    state_macro=state.groupby(["primitive","separability","dof","prefix","state"],as_index=False).fraction.mean()
    state_macro.to_csv(OUT/"lifecycle_state_fractions.csv",index=False)
    # 5 difficulty anatomy, descriptive only
    anatomy=macro(sc,["primitive","separability","dof","prefix"],"S").merge(rel_by,on=["primitive","separability","dof","prefix"],how="left",suffixes=("_sharpness","_ess"))
    anatomy=anatomy.rename(columns={"S":"mean_S","ESS":"mean_ESS"})
    for field in ["E_struct","d_eff","V_f_norm"]:
        anatomy=anatomy.merge(macro(sc,["primitive","separability","dof","prefix"],field),on=["primitive","separability","dof","prefix"])
    anatomy.to_csv(OUT/"difficulty_anatomy.csv",index=False)
    # Figure 1: endpoint attainment, macro across eta/DoF, all primitives.
    fig,axs=plt.subplots(2,2,figsize=(13,8),sharex=True,sharey=True)
    for ax,key in zip(axs.flat,["E_add","E_obs","E_joint","E_red"]):
        q=att[key].groupby(["primitive","prefix"],as_index=False).attainment.mean()
        for p in PRIMS:
            z=q[q.primitive==p]; ax.plot(z.prefix,z.attainment,marker="o",lw=1.5,label=p)
        ax.set_title(key.replace("_"," ")+" attainment"); ax.set_ylim(-.03,1.03); ax.grid(alpha=.2)
    axs[0,0].legend(ncol=2,fontsize=8); fig.supxlabel("nested observed support"); fig.supylabel("attainment probability")
    fig.tight_layout(); fig.savefig(FIG/"fig33_e9_lifecycle_attainment.png",dpi=180); plt.close(fig)
    # Figure 2: reliability/multiplicity and state map (macro across generators, eta).
    fig,axs=plt.subplots(1,3,figsize=(15,4.5))
    q=anatomy.groupby(["prefix","dof"],as_index=False)[["mean_ESS","d_eff","V_f_norm"]].mean()
    for d in [1,3,5]:
        z=q[q.dof==d]; axs[0].plot(z.prefix,z.mean_ESS,marker="o",label=f"DoF {d}")
        axs[1].plot(z.prefix,z.d_eff,marker="o",label=f"DoF {d}")
        axs[2].plot(z.prefix,z.V_f_norm,marker="o",label=f"DoF {d}")
    axs[0].axhline(100,color="crimson",ls="--",lw=1); axs[0].set_title("ESS (reliability)"); axs[1].set_title("effective dimension"); axs[2].set_title("normalized function dispersion")
    for ax in axs: ax.grid(alpha=.2); ax.legend(); ax.set_xlabel("prefix support")
    fig.tight_layout(); fig.savefig(FIG/"fig34_e9_reliability_multiplicity.png",dpi=180); plt.close(fig)
    # state heatmap: states pooled only for descriptive lifecycle visualization.
    q=state_macro.groupby(["prefix","state"],as_index=False).fraction.mean().pivot(index="state",columns="prefix",values="fraction").reindex(STATES)
    fig,ax=plt.subplots(figsize=(8,3.8)); im=ax.imshow(q.fillna(0),aspect="auto",vmin=0,vmax=1,cmap="viridis")
    ax.set_yticks(range(len(q.index)),q.index); ax.set_xticks(range(len(q.columns)),[f"{x:.1f}" for x in q.columns]); ax.set_xlabel("prefix support"); ax.set_title("E9 lifecycle states (descriptive macro fraction)")
    fig.colorbar(im,ax=ax,label="fraction"); fig.tight_layout(); fig.savefig(FIG/"fig35_e9_lifecycle_states.png",dpi=180); plt.close(fig)
    final={"integrity":integrity,"measurement_reliability":reliability,"lifecycle_endpoints":endpoint_summary,
           "analysis_order":["integrity","measurement reliability","lifecycle endpoints","lifecycle states","difficulty anatomy"],
           "interpretation_boundary":"Information lifecycle only; no utility, trust, scope, completeness, fragility, or engine claim."}
    (OUT/"summary.json").write_text(json.dumps(final,indent=2),encoding="utf-8")
    print(json.dumps(final,indent=2))

if __name__=="__main__": main()
