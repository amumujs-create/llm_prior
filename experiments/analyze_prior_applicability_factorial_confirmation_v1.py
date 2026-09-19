#!/usr/bin/env python3
"""Analyze locked E8 factorial outcomes without averaging engine safety."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/"results"/"prior_applicability_factorial_confirmation_v1"/"run"
OUT=ROOT/"results"/"prior_applicability_factorial_confirmation_v1"/"analysis"
FIG=ROOT/"figures"; B=5000

def seed(s: str) -> int: return int(hashlib.sha256(s.encode()).hexdigest()[:16],16)%(2**32)
def boot(g: pd.DataFrame, key: tuple) -> dict:
    rng=np.random.default_rng(seed("|".join(map(str,key))))
    n=len(g); idx=rng.integers(0,n,(B,n)); harm=g.harmful.to_numpy()[idx].mean(1); u=g.utility.to_numpy()[idx].mean(1)
    return {"harmful_rate":float(g.harmful.mean()),"harm_ci95_low":float(np.quantile(harm,.025)),"harm_ci95_high":float(np.quantile(harm,.975)),"mean_raw_utility":float(g.utility.mean()),"utility_ci95_low":float(np.quantile(u,.025)),"utility_ci95_high":float(np.quantile(u,.975)),"beneficial_rate":float(g.beneficial.mean()),"catastrophic_harm_rate":float(g.catastrophic_harm.mean()),"n":n}
def summarize(d: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    rows=[]
    for key,g in d.groupby(by,observed=False,dropna=False):
        key=(key,) if not isinstance(key,tuple) else key; rows.append({**dict(zip(by,key)),**boot(g,key)})
    return pd.DataFrame(rows)
def annotate(ax,table,row,col,val="harmful_rate"):
    x=[.35,.525,.70] if col=="support_fraction" else ([.001,.01,.05] if col=="noise_ratio" else ([.10,.45,.80] if col=="exposure" else [.15,.45,.85]))
    y=[.35,.525,.70] if row=="support_fraction" else ([.001,.01,.05] if row=="noise_ratio" else ([.10,.45,.80] if row=="exposure" else [.15,.45,.85]))
    q=table.pivot(index=row,columns=col,values=val).reindex(index=y,columns=x)
    im=ax.imshow(q.to_numpy(),vmin=0,vmax=1,cmap="Reds");ax.set(xticks=range(3),xticklabels=x,yticks=range(3),yticklabels=y)
    for i in range(3):
        for j in range(3): ax.text(j,i,f"{q.iloc[i,j]:.2f}",ha="center",va="center",fontsize=8)
    return im
def main() -> None:
    OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(RUN/"records.csv"); assert d.solver_failure.sum()==0
    # Robust unsafe is a task/action property: never replace it with engine average.
    r=d.groupby([c for c in d.columns if c not in ["engine","utility","normalized_utility","beneficial","harmful","catastrophic_harm","baseline_rmse","prior_rmse","solver_failure"]],dropna=False,observed=False).agg(
        utility=("utility","mean"), normalized_utility=("normalized_utility","mean"), beneficial=("beneficial","min"), harmful=("harmful","max"), catastrophic_harm=("catastrophic_harm","max")
    ).reset_index()
    outputs=[]
    for factorial, axes in [("support_noise",["support_fraction","noise_ratio"]),("exposure_effect",["exposure","effect_strength"]),("distance_specificity",["ood_distance","action"])]:
        q=d[d.factorial==factorial]; qr=r[r.factorial==factorial]
        # Pooled engine-conditioned CIs and pooled robust CIs are headline;
        # primitive/generator tables remain a diagnostic, not pooled evidence.
        ec=summarize(q,["engine",*axes]); ec["factorial"]=factorial; ec["target"]="engine_conditioned";outputs.append(ec)
        rb=summarize(qr,axes); rb["factorial"]=factorial; rb["target"]="robust_any_engine_harm";outputs.append(rb)
    summary=pd.concat(outputs,ignore_index=True);summary.to_csv(OUT/"factorial_summary_bootstrap.csv",index=False)
    primitive=summarize(d,["factorial","primitive","engine","action","support_fraction","noise_ratio","exposure","effect_strength","ood_distance"])
    primitive.to_csv(OUT/"primitive_engine_strata.csv",index=False)
    robust=r.groupby(["factorial","primitive","generator","action","support_fraction","noise_ratio","exposure","effect_strength","ood_distance"],dropna=False,observed=False).agg(
        n=("latent_task_id","nunique"),robust_unsafe_rate=("harmful","mean"),robust_catastrophic_rate=("catastrophic_harm","mean"),mean_raw_utility=("utility","mean"),beneficial_both_engines_rate=("beneficial","mean")
    ).reset_index();robust.to_csv(OUT/"robust_unsafe_by_task.csv",index=False)
    # Figure uses robust targets for the first two factorials, engine-conditioned
    # lines for the third; both avoid hiding disagreements in an average label.
    fig,axs=plt.subplots(1,3,figsize=(13,4.2),constrained_layout=True)
    a=summary[(summary.factorial=="support_noise")&(summary.target=="robust_any_engine_harm")]
    im=annotate(axs[0],a,"support_fraction","noise_ratio");axs[0].set(title="Robust unsafe: support × noise",xlabel="noise ratio",ylabel="support fraction")
    a=summary[(summary.factorial=="exposure_effect")&(summary.target=="robust_any_engine_harm")]
    annotate(axs[1],a,"exposure","effect_strength");axs[1].set(title="Robust unsafe: exposure × effect",xlabel="effect strength",ylabel="exposure")
    a=summary[(summary.factorial=="distance_specificity")&(summary.target=="engine_conditioned")]
    for (engine,action),g in a.groupby(["engine","action"],observed=False):
        g=g.sort_values("ood_distance");axs[2].plot(g.ood_distance,g.harmful_rate,"o-",label=f"{engine}: {action}")
    axs[2].set(title="Engine-conditioned: distance × tier",xlabel="OOD distance",ylabel="harmful rate",ylim=(0,1));axs[2].legend(fontsize=6)
    fig.colorbar(im,ax=axs[:2],shrink=.82,label="robust-unsafe rate");fig.savefig(FIG/"fig31_e8_applicability_factorial.png",dpi=180);plt.close(fig)
    manifest={"bootstrap_replicates":B,"n_records":int(len(d)),"n_latent_tasks":int(d.latent_task_id.nunique()),"solver_failures":int(d.solver_failure.sum()),"safety_target":"engine-conditioned harmful plus robust unsafe = harmful in either engine","records_sha256":hashlib.sha256((RUN/"records.csv").read_bytes()).hexdigest()}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n");print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
