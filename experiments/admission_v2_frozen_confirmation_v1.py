#!/usr/bin/env python3
"""Independent-draw confirmation of the immutable admission-v2 rule."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import joblib, matplotlib.pyplot as plt, numpy as np
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import admission_v2_identifiability_sweep_v2 as base

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'admission_v2_frozen_confirmation_v1'; FIG=ROOT/'figures'; MANIFEST=json.loads((ROOT/'FROZEN_ADMISSION_V2_MANIFEST.json').read_text())
NUM=[f'e{i}' for i in range(8)]+['stability','v1_score']

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rows_for(run_seed):
 t=np.linspace(0,1,101); obs=t<=base.TB; tail=t>.70; rows=[]
 for fi,fam in enumerate(base.FAMS):
  levels=base.TAUS if fam!='asymptotic_bound' else base.EXPS
  for li,level in enumerate(levels):
   for ni,noise in enumerate(base.NOISES):
    for task in range(base.N_SEEDS):
     r=np.random.default_rng(np.random.SeedSequence([run_seed,fi,li,ni,task])); clean,o=base.sim(fam,level,t,r); y=clean+r.normal(0,noise,len(t))
     prior,p,c=base.fit(fam,t[obs],y[obs],t[tail]); fallback,_,_=base.fit('linear',t[obs],y[obs],t[tail])
     u=float(np.sqrt(np.mean((clean[tail]-fallback)**2))-np.sqrt(np.mean((clean[tail]-prior)**2)))
     ev=base.primitives(fam,t[obs],y[obs],p,c); p50,_,_=base.fit(fam,t[t<=.50],y[t<=.50],np.array([.70])); p60,_,_=base.fit(fam,t[obs],y[obs],np.array([.70])); stability=-abs(float(p60[0]-p50[0]))/(np.ptp(y[obs])+1e-6)
     rows.append({'family':fam,'o_true':float(o),'utility':u,'useful':u>0,'v1_score':base.pseudo_v1(fam,t[obs],y[obs]),'stability':stability,**{f'e{i}':float(x) for i,x in enumerate(ev)}})
 return rows
def matrix(rows): return np.column_stack([np.array([[z[k] for k in NUM] for z in rows]),np.array([[z['family']] for z in rows],dtype=object)])
def metrics(admit,useful): return base.metrics(admit,useful)
def boot_delta(v2,v1,harm,n=10000):
 d=(v2[harm].astype(float)-v1[harm].astype(float)); r=np.random.default_rng(20260922); means=np.array([r.choice(d,len(d),replace=True).mean() for _ in range(n)]); return {'delta_far':float(d.mean()),'ci95':[float(x) for x in np.quantile(means,[.025,.975])],'n_harmful':int(len(d))}
def main():
 if sha(base.__file__)!=MANIFEST['frozen_v2_source_sha256']: raise RuntimeError('Frozen v2 source hash mismatch; refusing confirmation.')
 dev=rows_for(MANIFEST['config']['development_seed']); ydev=np.array([z['useful'] for z in dev]); pre=ColumnTransformer([('num',StandardScaler(),list(range(len(NUM)))),('fam',OneHotEncoder(handle_unknown='ignore'),[len(NUM)])]); pipe=Pipeline([('pre',pre),('lr',LogisticRegression(C=1.,class_weight='balanced',max_iter=1000,random_state=base.SEED))]); pipe.fit(matrix(dev),ydev)
 OUT.mkdir(parents=True,exist_ok=True); joblib.dump(pipe,OUT/'frozen_admission_v2_pipeline.joblib')
 conf=rows_for(MANIFEST['config']['confirmation_seed']); useful=np.array([z['useful'] for z in conf]); p=pipe.predict_proba(matrix(conf))[:,1]; v1=np.array([z['v1_score']>0 for z in conf]); v2=p>=.5
 pooled={'v1':metrics(v1,useful),'v2':metrics(v2,useful),'paired_primary':boot_delta(v2,v1,~useful)}
 families={}
 for fam in base.FAMS:
  m=np.array([z['family']==fam for z in conf]); families[fam]={'n':int(m.sum()),'v1':metrics(v1[m],useful[m]),'v2':metrics(v2[m],useful[m]),'spearman_O_utility':float(spearmanr([z['o_true'] for z in np.array(conf,dtype=object)[m]],[z['utility'] for z in np.array(conf,dtype=object)[m]]).statistic)}
 curve=[]
 for th in np.linspace(.05,.95,19): curve.append({'threshold':float(th),**metrics(p>=th,useful)})
 result={'experiment_id':'admission_v2_frozen_confirmation_v1','status':'confirmatory_synthetic_independent_draw','manifest_sha256':sha(ROOT/'FROZEN_ADMISSION_V2_MANIFEST.json'),'n_confirmation_tasks':len(conf),'data_independence':'New SeedSequence root 20260921; no shared parameter draws or noise realizations with development root 20260920.','primary_endpoint':pooled,'by_family':families,'pooled_spearman_O_utility':float(spearmanr([z['o_true'] for z in conf],[z['utility'] for z in conf]).statistic),'coverage_harm_curve_supplementary':curve}
 (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
 FIG.mkdir(exist_ok=True); fig,ax=plt.subplots(figsize=(6.6,4.5)); ax.plot([z['coverage'] for z in curve],[z['harm_risk_among_admitted'] for z in curve],'o-',label='v2 supplementary threshold curve'); ax.scatter([pooled['v1']['coverage']],[pooled['v1']['harm_risk_among_admitted']],s=75,label='v1 frozen baseline'); ax.scatter([pooled['v2']['coverage']],[pooled['v2']['harm_risk_among_admitted']],s=75,label='v2 frozen threshold .50'); ax.set(xlabel='coverage: P(admit)',ylabel='harm risk: P(harmful | admit)',title='Independent confirmation: coverage–harm-risk'); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(FIG/'fig08_confirmation_coverage_harm_risk.png',dpi=220); plt.close(fig)
 print(json.dumps(pooled,indent=2))
if __name__=='__main__': main()
