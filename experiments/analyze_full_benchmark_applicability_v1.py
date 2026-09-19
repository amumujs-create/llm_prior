#!/usr/bin/env python3
"""Descriptive conditional-utility maps from locked full-benchmark v1 outcomes.

This is a post-run anatomy analysis: it never changes the corpus, actions,
realization engines, or frozen scoring rule.  It characterizes utility as a
function of observed-data informativeness, horizon, and structural complexity.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/"results"/"full_benchmark_v1"/"run"/"task_candidate_engine.csv"
OUT=ROOT/"results"/"full_benchmark_v1"/"applicability"
FIG=ROOT/"figures"
PRIMS=("direction","curvature","inflection","turning","regime","bound","asymptote")
AXES=("support_fraction","sample_count","noise_ratio","exposure","ood_distance","effect_strength","heterogeneity_cv")
ACTION_ORDER=("true-subset","true-full","biased-specific")

def task_average(d: pd.DataFrame) -> pd.DataFrame:
    vals=["coverage","sharpness","ess","baseline_rmse","prior_rmse","utility","normalized_utility","harmful","beneficial"]
    meta=[c for c in d.columns if c not in vals+["engine","parameter_count","sharpness_spline","sharpness_basis","sharpness_rank_gap","solver_failure"]]
    z=d.groupby(meta,dropna=False,observed=False)[vals].mean().reset_index()
    z["neutral"]=(np.abs(z.normalized_utility)<=.02).astype(int)
    z["catastrophic_harm"]=(z.prior_rmse>=2*z.baseline_rmse).astype(int)
    return z

def tercile(s: pd.Series) -> pd.Categorical:
    # Rank first makes the fixed LHS coordinates deterministically partitionable.
    return pd.qcut(s.rank(method="first"),3,labels=["low","mid","high"])

def summarize(z: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    a=z.groupby(by,dropna=False,observed=False).agg(
        n=("task_id","nunique"), coverage=("coverage","mean"), mean_sharpness=("sharpness","mean"),
        median_raw_utility=("utility","median"), mean_raw_utility=("utility","mean"),
        median_normalized_utility=("normalized_utility","median"), beneficial_rate=("beneficial","mean"),
        neutral_rate=("neutral","mean"), harmful_rate=("harmful","mean"),
        catastrophic_harm_rate=("catastrophic_harm","mean"), mean_ess=("ess","mean"),
    ).reset_index()
    return a

def primitive_long(z: pd.DataFrame) -> pd.DataFrame:
    pieces=[]
    for p in PRIMS:
        q=z[z.composition.str.split("+").apply(lambda x:p in x)].copy()
        q["primitive"]=p; pieces.append(q)
    return pd.concat(pieces,ignore_index=True)

def heat(ax, table: pd.DataFrame, row: str, col: str, title: str) -> None:
    labels=["low","mid","high"]
    q=table.pivot(index=row,columns=col,values="harmful_rate").reindex(index=labels,columns=labels)
    im=ax.imshow(q.to_numpy(),vmin=0,vmax=1,cmap="Reds")
    ax.set(xticks=range(3),xticklabels=labels,yticks=range(3),yticklabels=labels,title=title)
    for i in range(3):
        for j in range(3):
            v=q.iloc[i,j]
            ax.text(j,i,"—" if pd.isna(v) else f"{v:.2f}",ha="center",va="center",fontsize=8)
    return im

def main() -> None:
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(RUN,low_memory=False); task=task_average(raw)
    task=task[(task.null_type=="none") & task.action.isin(ACTION_ORDER)].copy()
    for axis in AXES: task[f"{axis}_tercile"]=tercile(task[axis])
    # Applicability maps use a structurally true, supplied full candidate.  This
    # isolates conditional deployment behavior from calibration error.
    true=task[task.action=="true-full"].copy(); prim=primitive_long(true)
    rows=[]
    for axis in AXES:
        q=summarize(prim,["primitive",f"{axis}_tercile"])
        q["axis"]=axis; q=q.rename(columns={f"{axis}_tercile":"level"}); rows.append(q)
    strat=pd.concat(rows,ignore_index=True)
    strat.to_csv(OUT/"true_full_condition_strata.csv",index=False)
    # Complexity is explicitly separated into composition size and the frozen
    # effect-strength coordinate (the benchmark's operational identifiability proxy).
    complexity=summarize(true,["composition_size","effect_strength_tercile"])
    complexity.to_csv(OUT/"complexity_profile.csv",index=False)
    # Three predeclared descriptive interactions.
    support_noise=summarize(prim,["primitive","support_fraction_tercile","noise_ratio_tercile"])
    support_noise.to_csv(OUT/"interaction_support_noise.csv",index=False)
    exposure_ident=summarize(prim,["primitive","exposure_tercile","effect_strength_tercile"])
    exposure_ident.to_csv(OUT/"interaction_exposure_identifiability.csv",index=False)
    distance_specificity=summarize(task,["action","ood_distance_tercile"])
    distance_specificity.to_csv(OUT/"interaction_distance_specificity.csv",index=False)
    # A compact primitive profile is the operating-region lookup table.
    profile=summarize(prim,["primitive"])
    profile.to_csv(OUT/"prior_applicability_profile.csv",index=False)
    # Plot pooled true-full interactions. Detailed CSVs retain primitive strata.
    fig,axs=plt.subplots(1,3,figsize=(13,4.1),constrained_layout=True);
    im=heat(axs[0],summarize(true,["support_fraction_tercile","noise_ratio_tercile"]),"support_fraction_tercile","noise_ratio_tercile","Harm: support × noise")
    heat(axs[1],summarize(true,["exposure_tercile","effect_strength_tercile"]),"exposure_tercile","effect_strength_tercile","Harm: exposure × identifiability")
    axs[0].set(xlabel="noise tercile",ylabel="support tercile")
    axs[1].set(xlabel="effect-strength tercile",ylabel="exposure tercile")
    for action,g in distance_specificity.groupby("action",observed=False):
        axs[2].plot(g.ood_distance_tercile.astype(str),g.harmful_rate,"o-",label=action)
    axs[2].set(ylim=(0,1),ylabel="harmful rate",title="Distance × prior specificity"); axs[2].legend(fontsize=7)
    fig.colorbar(im,ax=axs[:2],shrink=.82,label="harmful rate")
    fig.savefig(FIG/"fig30_full_v1_conditional_applicability.png",dpi=180);plt.close(fig)
    result={
        "scope":"descriptive post-run conditional analysis of frozen full-v1 outcomes",
        "prior_condition":"true-full/non-null for condition and complexity maps; tier comparison only for distance × specificity",
        "identifiability_proxy":"effect_strength, frozen as the primitive valid-range fraction",
        "axes":list(AXES),"interaction_maps":["support_fraction × noise_ratio","exposure × effect_strength","ood_distance × knowledge tier"],
        "n_true_full":int(len(true)),"n_task_action_tiers":int(len(task)),
    }
    (OUT/"manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
