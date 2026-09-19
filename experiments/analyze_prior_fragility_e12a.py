#!/usr/bin/env python3
"""Predeclared E12-A analysis: baseline-state-stratified fragility only."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'results/prior_fragility_e12a/run'; OUT=ROOT/'results/prior_fragility_e12a/analysis'; FIG=ROOT/'figures'
FIELDS=['regime_onset','inflection_location','turning_location','lower_bound_level','asymptotic_limit']

def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    r=pd.read_csv(RUN/'rows.csv'); e=pd.read_csv(RUN/'endpoints.csv'); a=pd.read_csv(RUN/'accounting.csv'); i=pd.read_csv(RUN/'integrity.csv')
    run=json.loads((RUN/'summary.json').read_text())
    primary=r.groupby(['field','baseline_specification_state','sign','epsilon'],as_index=False).agg(
        rows=('task_id','size'), coverage_rate=('coverage','mean'), violation_mean=('violation','mean'),
        sharpness_mean=('S','mean'), sharpness_median=('S','median'), CW_rate=('confidently_wrong','mean'),
        ESS_median=('ESS','median'))
    primary.to_csv(OUT/'primary_field_state_sign_curves.csv',index=False)
    ep=e.groupby(['field','baseline_specification_state','sign'],as_index=False).agg(
        endpoint_rows=('task_id','size'), break_observed_rate=('break_status',lambda x:(x=='observed').mean()),
        CW_observed_rate=('CW_status',lambda x:(x=='observed').mean()),
        median_epsilon_break=('epsilon_break','median'), median_epsilon_CW=('epsilon_CW','median'),
        median_delta_epsilon_CW=('delta_epsilon_CW','median'))
    ep.to_csv(OUT/'primary_endpoint_summary.csv',index=False)
    floor=r.groupby('delta_S_status',as_index=False).size(); floor.to_csv(OUT/'delta_S_floor_status.csv',index=False)
    observed=e.dropna(subset=['epsilon_break','epsilon_CW']).copy(); observed['immediate']=(observed.delta_epsilon_CW==0).astype(int)
    immediate=float(observed.immediate.mean()) if len(observed) else None

    # Primary endpoint grid: every displayed row is one field × state × sign stratum.
    x=ep.copy(); x['label']=x.field.str.replace('_',' ',regex=False)+'\n'+x.baseline_specification_state+'; s='+x.sign.astype(int).astype(str)
    fig,axs=plt.subplots(1,2,figsize=(14,8),sharey=True)
    for ax,col,title in zip(axs,['median_epsilon_break','median_epsilon_CW'],['Validity-break threshold','Confidently-wrong onset']):
        q=x.sort_values(['field','baseline_specification_state','sign'])
        vals=q[col].fillna(.325)
        colors=['#BAB0AC' if pd.isna(v) else '#4C78A8' for v in q[col]]
        ax.barh(range(len(q)),vals,color=colors); ax.set_yticks(range(len(q))); ax.set_yticklabels(q.label,fontsize=6.5); ax.set_xlim(0,.34); ax.set_xticks([0,.025,.05,.10,.20,.30]); ax.set_title(title); ax.grid(axis='x',alpha=.2)
    axs[0].set_xlabel('epsilon (grey: not observed / not at risk)'); axs[1].set_xlabel('epsilon (grey: censored or not at risk)'); fig.tight_layout(); fig.savefig(FIG/'fig40_e12a_signed_endpoints.png',dpi=180); plt.close(fig)

    fig,axs=plt.subplots(1,5,figsize=(18,3.8),sharey=True)
    for ax,field in zip(axs,FIELDS):
        q=primary[(primary.field==field)&(primary.sign!=0)]
        for (state,sign),g in q.groupby(['baseline_specification_state','sign']):
            ax.plot(g.epsilon,g.sharpness_mean,marker='o',label=f'{state}, {"+" if sign>0 else "-"}')
        ax.set_title(field.replace('_',' '),fontsize=9); ax.set_xlabel('epsilon'); ax.grid(alpha=.2)
    axs[0].set_ylabel('mean conditional sharpness (nat)'); axs[0].legend(fontsize=6,loc='best'); fig.suptitle('E12-A sharpness after signed specification perturbation',y=1.02); fig.tight_layout(); fig.savefig(FIG/'fig41_e12a_sharpness_curves.png',dpi=180,bbox_inches='tight'); plt.close(fig)

    summary={'integrity':{'latent_trajectories':int(r.task_id.nunique()),'perturbation_rows':int(len(r)),'endpoint_rows':int(len(e)),'expected_trajectories':450,'expected_rows':14850,'integrity_passed':bool(run['integrity_passed']),'exhausted_cells':int(run['exhausted_cells']),'ESS_invariant_pass':bool(i.ESS_invariant.all())},
             'estimand':'Conditional on accepted nondegenerate-range tasks and stratified by field × baseline specification state × sign.',
             'floor_status_counts':{str(k):int(v) for k,v in floor.set_index('delta_S_status')['size'].items()},
             'endpoint_result':{'both_endpoints_observed_rows':int(len(observed)),'immediate_CW_rate_when_both_observed':immediate,'median_delta_epsilon_CW_when_observed':float(observed.delta_epsilon_CW.median()) if len(observed) else None},
             'boundary':'Controlled specification-fragility anatomy only; no utility, engine, prediction, or real-world calibration claim.'}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
