#!/usr/bin/env python3
"""Predeclared E10 scope analysis: integrity, survival, scope anatomy only."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]; RUN=ROOT/'results/prior_scope_validity_horizon_e10/run'; OUT=ROOT/'results/prior_scope_validity_horizon_e10/analysis'; FIG=ROOT/'figures'
PRIMS=['direction','curvature','inflection','turning','regime','bound','asymptote']

def main():
 OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
 r=pd.read_csv(RUN/'scope_rows.csv'); integ=pd.read_csv(RUN/'integrity_rows.csv'); run=json.loads((RUN/'summary.json').read_text())
 # C is the only endpoint survival process; V remains supplementary raw diagnostics.
 surv=r.groupby(['primitive','tier','generator','horizon'],as_index=False)[['V_raw','C_contiguous']].mean()
 macro=surv.groupby(['primitive','tier','horizon'],as_index=False)[['V_raw','C_contiguous']].mean(); macro.to_csv(OUT/'scope_survival_macro.csv',index=False)
 hv=r[['task_id','primitive','tier','generator','H_valid']].drop_duplicates(); hv.H_valid=pd.to_numeric(hv.H_valid,errors='coerce')
 summ=hv.groupby(['primitive','tier'],as_index=False).H_valid.agg(['count','median','mean']).reset_index(); summ.to_csv(OUT/'validity_horizon_summary.csv',index=False)
 terminal=hv.assign(persistent=(hv.H_valid==1.).astype(int)).groupby(['primitive','tier'],as_index=False).persistent.mean(); terminal.to_csv(OUT/'persistent_within_domain.csv',index=False)
 fig,axs=plt.subplots(1,3,figsize=(15,4.2),sharey=True)
 for ax,tier in zip(axs,['local','medium','persistent_within_domain']):
  z=macro[macro.tier==tier]
  for p in PRIMS:
   q=z[z.primitive==p]; ax.plot(q.horizon,q.C_contiguous,marker='o',label=p)
  ax.set_title(tier.replace('_',' ')); ax.grid(alpha=.2); ax.set_ylim(-.03,1.03); ax.set_xlabel('future horizon')
 axs[0].set_ylabel('contiguous validity survival'); axs[0].legend(fontsize=7,ncol=2); fig.tight_layout(); fig.savefig(FIG/'fig36_e10_validity_horizon_survival.png',dpi=180); plt.close(fig)
 fig,ax=plt.subplots(figsize=(10,4.5)); order=['local','medium','persistent_within_domain']; wide=summ.pivot(index='primitive',columns='tier',values='median').reindex(PRIMS)
 wide[order].plot(kind='bar',ax=ax); ax.set_ylim(.4,1.03); ax.set_ylabel('median H_valid* among tasks'); ax.set_title('E10 scope anatomy by intended tier'); ax.grid(axis='y',alpha=.2); ax.legend(title='scope tier'); fig.tight_layout(); fig.savefig(FIG/'fig37_e10_scope_anatomy.png',dpi=180); plt.close(fig)
 summary={'integrity':{'latent_tasks':int(hv.task_id.nunique()),'scope_rows':int(len(r)),'expected_latent_tasks':1890,'expected_scope_rows':13230,'all_checks_pass':bool(integ.drop(columns='task_id').all().all()),'failures':run['failures'],'clean_oracle_only':run['clean_oracle_only']},'scope_only_boundary':'No utility, information, engine, or safety conclusion. H_valid is first-failure contiguous horizon.','terminal_persistent_rate':float((hv.H_valid==1.).mean())}
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
