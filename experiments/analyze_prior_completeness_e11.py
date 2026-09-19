#!/usr/bin/env python3
"""Predeclared E11 analysis: grammar-relative content and information gaps only."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'results/prior_completeness_e11/run'
OUT=ROOT/'results/prior_completeness_e11/analysis'
FIG=ROOT/'figures'
DELTA=.10

def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    rows=pd.read_csv(RUN/'rows.csv'); acct=pd.read_csv(RUN/'accounting.csv'); integ=pd.read_csv(RUN/'integrity.csv')
    run=json.loads((RUN/'summary.json').read_text())
    s=rows[rows.candidate_role=='supplied'].copy()
    s['n_supplied_atoms']=s.supplied_atoms.str.count(r'\|')+1
    s['resolved']=s.information_status.isin(['informationally_complete','informationally_incomplete'])
    s['info_complete']=(s.information_status=='informationally_complete').astype(int)
    s['info_incomplete']=(s.information_status=='informationally_incomplete').astype(int)
    s['measurement_unresolved']=(s.information_status=='measurement_unresolved').astype(int)

    by_size=s.groupby('n_supplied_atoms',as_index=False).agg(
        candidates=('task_id','size'), mean_delta_S=('delta_S_miss','mean'), median_delta_S=('delta_S_miss','median'),
        resolved_rate=('resolved','mean'), informationally_complete_rate=('info_complete','mean'),
        informationally_incomplete_rate=('info_incomplete','mean'), measurement_unresolved_rate=('measurement_unresolved','mean'), median_ESS=('ESS','median'))
    by_size.to_csv(OUT/'completeness_by_supplied_size.csv',index=False)
    by_intent=s.groupby('intent_name',as_index=False).agg(
        candidates=('task_id','size'), mean_delta_S=('delta_S_miss','mean'), median_delta_S=('delta_S_miss','median'),
        resolved_rate=('resolved','mean'), informationally_complete_rate=('info_complete','mean'),
        informationally_incomplete_rate=('info_incomplete','mean'), measurement_unresolved_rate=('measurement_unresolved','mean'), median_ESS=('ESS','median'))
    by_intent.to_csv(OUT/'completeness_by_intended_triple.csv',index=False)
    cross=s.groupby(['atom_status','information_status'],as_index=False).size(); cross.to_csv(OUT/'content_information_cross_classification.csv',index=False)

    marg=[]
    for _,r in s.iterrows():
        for atom,val in json.loads(r.marginal_json).items():
            marg.append({'task_id':r.task_id,'intent_name':r.intent_name,'generator':r.generator,'added_atom':atom,'marginal_delta_S':float(val)})
    marginal=pd.DataFrame(marg)
    marginal_summary=marginal.groupby('added_atom',as_index=False).agg(
        additions=('task_id','size'), mean_marginal_delta_S=('marginal_delta_S','mean'), median_marginal_delta_S=('marginal_delta_S','median'))
    marginal_summary.to_csv(OUT/'marginal_information_by_missing_atom.csv',index=False)

    # Figure 1: every candidate is canonical-atom-incomplete in this designed
    # corpus, but its missing content can be conditionally redundant.
    fig,ax=plt.subplots(figsize=(8,4.6))
    plot=by_size.set_index('n_supplied_atoms')[['informationally_complete_rate','informationally_incomplete_rate','measurement_unresolved_rate']]
    plot.rename(columns={'informationally_complete_rate':'informationally complete','informationally_incomplete_rate':'informationally incomplete','measurement_unresolved_rate':'measurement unresolved'}).plot(kind='bar',stacked=True,ax=ax,color=['#4C78A8','#E45756','#BAB0AC'])
    ax.axhline(1,color='black',lw=.7); ax.set_ylim(0,1.05); ax.set_xlabel('supplied canonical-atom count'); ax.set_ylabel('rate among all supplied candidates'); ax.set_title('E11: missing content is not always missing conditional information'); ax.legend(fontsize=8); ax.grid(axis='y',alpha=.2); fig.tight_layout(); fig.savefig(FIG/'fig38_e11_completeness_by_supplied_size.png',dpi=180); plt.close(fig)

    fig,ax=plt.subplots(figsize=(9,4.8))
    q=marginal_summary.sort_values('mean_marginal_delta_S')
    ax.barh(q.added_atom,q.mean_marginal_delta_S,color='#59A14F'); ax.axvline(DELTA,color='#E15759',ls='--',label='practical threshold (.10 nat)')
    ax.set_xlabel('mean marginal conditional information (nat)'); ax.set_title('E11: missing-atom marginal information is context dependent'); ax.grid(axis='x',alpha=.2); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(FIG/'fig39_e11_marginal_information.png',dpi=180); plt.close(fig)

    summary={
        'integrity':{'accepted_latent_tasks':int(s.task_id.nunique()),'candidate_rows':int(len(rows)),'supplied_candidates':int(len(s)),
                     'expected_tasks':720,'expected_rows':5760,'integrity_passed':bool(run['integrity_passed']),
                     'exhausted_cells':int(run['exhausted_cells']),'nested_floor_violations':int(s.nested_floor_violation.sum()),
                     'candidate_floor_hits':int(s.candidate_floor_hit.sum()),'oracle_floor_hits':int(s.oracle_floor_hit.sum())},
        'estimand':'Conditional on a unique inclusion-maximal compatible coverage-preserving envelope in the frozen canonical grammar.',
        'measurement':{'delta_info_threshold_nat':DELTA,'primary_ESS_threshold':100,'median_ESS':float(s.ESS.median()),
                       'measurement_unresolved_rate':float((s.information_status=='measurement_unresolved').mean())},
        'content_information':{'atom_incomplete_rate':float((s.atom_status=='atom_incomplete').mean()),
                               'informationally_complete_rate_all':float(s.info_complete.mean()),
                               'informationally_incomplete_rate_all':float(s.info_incomplete.mean()),
                               'mean_delta_S_miss':float(s.delta_S_miss.mean()),'median_delta_S_miss':float(s.delta_S_miss.median())},
        'interpretation_boundary':'No utility, prediction engine, future RMSE, or safety target is used. The corpus is a controlled grammar-relative anatomy experiment, not a population estimate of real-world priors.'}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
