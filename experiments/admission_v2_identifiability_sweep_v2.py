#!/usr/bin/env python3
"""Frozen v2 generic-prior admission experiment; see ADMISSION_V2_PROTOCOL.md."""
from __future__ import annotations
import json, warnings
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'admission_v2_identifiability_sweep_v2'; FIG=ROOT/'figures'
SEED=20260920; TB=.60; NOISES=(.005,.010,.020,.035,.055); N_SEEDS=50
TAUS=(.75,.60,.50,.40,.30,.20); EXPS=(.10,.35,.70,1.20,2.0,3.0); WINDOWS=((.25,.40),(.40,.50),(.50,.60))
FAMS=('regime_change','emergent_curvature','asymptotic_bound')

def pp(x,a): return np.maximum(x,0.)**a
def reg(t,k1,k2,a,tau): return np.where(t<tau,1-k1*t,1-k1*tau-k2*pp(t-tau,a))
def curv(t,k1,k2,a,tau): return 1-k1*t-k2*pp(t-tau,a)
def bound(t,l,k): return l+(1-l)*np.exp(-k*t)
FITS={'regime_change':(reg,[.15,.5,2.,.5],([0,0,1.01,.12],[.8,2,4,.9])), 'emergent_curvature':(curv,[.1,.35,2.,.5],([0,0,1.01,.12],[.7,2,4,.9])), 'asymptotic_bound':(bound,[.5,1.5],([0,.01],[.95,10]))}

def linfit(t,y,target):
 s,b=np.polyfit(t,y,1); return s*target+b, np.array([s,b]), np.full((2,2),np.inf)
def fit(fam,t,y,target):
 if fam=='linear': return linfit(t,y,target)
 fn,p0,bounds=FITS[fam]
 try:
  with warnings.catch_warnings():
   warnings.simplefilter('ignore'); p,c=curve_fit(fn,t,y,p0=p0,bounds=bounds,maxfev=2500)
  z=fn(target,*p)
  if not np.all(np.isfinite(z)): raise FloatingPointError
  return z,p,c
 except (RuntimeError,ValueError,FloatingPointError): return linfit(t,y,target)

def sim(fam,level,t,rng):
 if fam=='regime_change': return reg(t,rng.uniform(.07,.24),rng.uniform(.35,1.),rng.uniform(1.35,2.6),level),max(0,(TB-level)/TB)
 if fam=='emergent_curvature': return curv(t,rng.uniform(.05,.16),rng.uniform(.22,.6),rng.uniform(1.35,2.6),level),max(0,(TB-level)/TB)
 return bound(t,rng.uniform(.2,.7),level/TB),1-np.exp(-level)

def slope(t,y): return np.polyfit(t,y,1)[0]
def bic(rss,n,p): return n*np.log(max(rss/n,1e-12))+p*np.log(n)
def primitives(fam,t,y,p,c):
 # Three boundary-local windows; all values are prefix-only.
 bins=((.30,.40),(.40,.50),(.50,.60)); ss=[]
 for lo,hi in bins:
  m=(t>=lo)&(t<=hi); ss.append(slope(t[m],y[m]))
 s0,s1,s2=ss; noise=max(np.std(y-np.polyval(np.polyfit(t,y,1),t)),1e-5)
 slope_change=abs(s2-s0)/noise; slope_decay=abs(s2)/(abs(s0)+1e-6)
 # Best piecewise-linear change evidence, retaining post-change support.
 single=np.polyfit(t,y,1); rss1=np.sum((y-np.polyval(single,t))**2); best=(bic(rss1,len(t),2),0)
 for j in range(12,len(t)-8):
  a,b=t[:j],t[j:]; ya,yb=y[:j],y[j:]; rss=np.sum((ya-np.polyval(np.polyfit(a,ya,1),a))**2)+np.sum((yb-np.polyval(np.polyfit(b,yb,1),b))**2)
  q=bic(rss,len(t),4)
  if q<best[0]: best=(q,len(t)-j)
 change_bic=bic(rss1,len(t),2)-best[0]; post_support=best[1]/len(t)
 # Quadratic curvature sign evidence.
 qcoef,qcov=np.polyfit(t,y,2,cov=True); qse=max(np.sqrt(max(qcov[0,0],0)),1e-8); curvature_z=max(0,-qcoef[0]/qse)
 # Bound-specific proximity comes from the matched candidate fit only.
 if fam=='asymptotic_bound' and len(p)==2:
  prox=1-min(1,abs(y[-1]-p[0])/(np.ptp(y)+1e-6))
 else: prox=0.
 # Identifiability: local parameter precision + covariance conditioning.
 if np.all(np.isfinite(c)) and c.shape[0]==len(p):
  se=np.sqrt(np.maximum(np.diag(c),0)); precision=float(np.median(np.abs(p)/(se+.01))); condition=-min(np.log10(max(np.linalg.cond(c),1)),12)
 else: precision=0.; condition=-12.
 # Stability is change in extrapolated boundary-near prediction after removing recent support.
 _,_,_=slope_change,slope_decay,change_bic
 return np.array([slope_change,slope_decay,change_bic,post_support,curvature_z,prox,precision,condition])

def pseudo_v1(fam,t,y):
 imps=[]
 for end,stop in WINDOWS:
  tr=t<=end; va=(t>end)&(t<=stop); a,_,_=fit('linear',t[tr],y[tr],t[va]); b,_,_=fit(fam,t[tr],y[tr],t[va]); imps.append(np.mean((y[va]-a)**2)-np.mean((y[va]-b)**2))
 return float(np.mean(imps))

def metrics(admit,useful):
 harm=~useful; cov=float(admit.mean()); far=float(admit[harm].mean()) if harm.any() else float('nan'); risk=float(harm[admit].mean()) if admit.any() else float('nan'); tpr=float(admit[useful].mean()) if useful.any() else float('nan')
 return {'coverage':cov,'false_admission_rate':far,'harm_risk_among_admitted':risk,'useful_prior_admit_rate':tpr}

def main():
 rng=np.random.default_rng(SEED); t=np.linspace(0,1,101); obs=t<=TB; tail=t>.70; rows=[]
 for fi,fam in enumerate(FAMS):
  levels=TAUS if fam!='asymptotic_bound' else EXPS
  for li,level in enumerate(levels):
   for ni,noise in enumerate(NOISED:=NOISES):
    for seed_idx in range(N_SEEDS):
     local=np.random.default_rng(np.random.SeedSequence([SEED,fi,li,ni,seed_idx])); clean,o=sim(fam,level,t,local); y=clean+local.normal(0,noise,len(t))
     prior,p,c=fit(fam,t[obs],y[obs],t[tail]); fallback,_,_=fit('linear',t[obs],y[obs],t[tail]); utility=float(np.sqrt(np.mean((clean[tail]-fallback)**2))-np.sqrt(np.mean((clean[tail]-prior)**2)))
     ev=primitives(fam,t[obs],y[obs],p,c)
     # Prefix perturbation stability at a fixed unobserved-in-tail reference point .70.
     p50,_,_=fit(fam,t[t<=.50],y[t<=.50],np.array([.70])); p60,_,_=fit(fam,t[obs],y[obs],np.array([.70])); stability=-abs(float(p60[0]-p50[0]))/(np.ptp(y[obs])+1e-6)
     v1=pseudo_v1(fam,t[obs],y[obs])
     rows.append({'family':fam,'level':float(level),'noise':noise,'seed_idx':seed_idx,'o_true':float(o),'utility':utility,'useful':utility>0,'v1_score':v1,'stability':stability,**{f'e{i}':float(x) for i,x in enumerate(ev)}})
 # Model has no O_true or tail-derived fields in features.
 num=[f'e{i}' for i in range(8)]+['stability','v1_score']; Xnum=np.array([[z[k] for k in num] for z in rows]); Xcat=np.array([[z['family']] for z in rows],dtype=object); y=np.array([z['useful'] for z in rows]); train=np.array([z['seed_idx']<35 for z in rows]); test=~train
 pre=ColumnTransformer([('num',StandardScaler(),list(range(len(num)))),('fam',OneHotEncoder(handle_unknown='ignore'),[len(num)])])
 X=np.column_stack([Xnum,Xcat]); clf=Pipeline([('pre',pre),('lr',LogisticRegression(C=1.,class_weight='balanced',max_iter=1000,random_state=SEED))]); clf.fit(X[train],y[train]); prob=clf.predict_proba(X)[:,1]
 for z,q in zip(rows,prob): z['v2_probability']=float(q); z['v1_admit']=z['v1_score']>0; z['v2_admit']=q>=.5
 base=metrics(np.array([z['v1_admit'] for z in rows])[test],y[test]); v2=metrics(np.array([z['v2_admit'] for z in rows])[test],y[test])
 family={}
 for fam in FAMS:
  m=test & np.array([z['family']==fam for z in rows]); family[fam]={'n_test':int(m.sum()),'v1':metrics(np.array([z['v1_admit'] for z in rows])[m],y[m]),'v2':metrics(np.array([z['v2_admit'] for z in rows])[m],y[m])}
 curve=[]
 for th in np.linspace(.05,.95,19):
  a=prob[test]>=th; curve.append({'threshold':float(th),**metrics(a,y[test])})
 # Coefficients are saved with transformed feature names for development interpretation.
 names=clf.named_steps['pre'].get_feature_names_out().tolist(); coefs=clf.named_steps['lr'].coef_[0].tolist(); importance=sorted([{'feature':n,'coefficient':float(v)} for n,v in zip(names,coefs)],key=lambda z:abs(z['coefficient']),reverse=True)
 OUT.mkdir(parents=True,exist_ok=True); result={'experiment_id':'admission_v2_identifiability_sweep_v2','status':'development','seed':SEED,'n_tasks':len(rows),'split':{'train_seed_indices':'0..34','locked_test_seed_indices':'35..49'},'feature_names':num+['family_one_hot'],'test_metrics':{'v1':base,'v2':v2,'by_family':family},'coverage_harm_curve_v2_test':curve,'feature_coefficients':importance,'mechanism_checks':{fam:float(np.corrcoef([z['o_true'] for z in rows if z['family']==fam],[z['utility'] for z in rows if z['family']==fam])[0,1]) for fam in FAMS}}
 (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
 FIG.mkdir(exist_ok=True)
 fig,ax=plt.subplots(figsize=(6.4,4.5)); ax.plot([z['coverage'] for z in curve],[z['harm_risk_among_admitted'] for z in curve],'o-',color='#3978b8',label='v2 probability threshold'); ax.scatter([base['coverage']],[base['harm_risk_among_admitted']],color='#cc4c4c',s=70,label='v1 fixed gate'); ax.scatter([v2['coverage']],[v2['harm_risk_among_admitted']],color='#43a86b',s=70,label='v2 threshold .50'); ax.set(xlabel='coverage: P(admit)',ylabel='harm risk: P(harmful | admit)',title='Locked-test coverage–harm-risk trade-off'); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(FIG/'fig05_v2_coverage_harm_risk.png',dpi=220); plt.close(fig)
 fig,ax=plt.subplots(figsize=(8,4.8)); top=importance[:10][::-1]; ax.barh([z['feature'] for z in top],[z['coefficient'] for z in top],color=['#3978b8' if z['coefficient']>0 else '#cc4c4c' for z in top]); ax.axvline(0,color='#555'); ax.set(title='Admission-v2 evidence coefficients (train seeds only)',xlabel='standardized logistic coefficient'); fig.tight_layout(); fig.savefig(FIG/'fig06_v2_evidence_coefficients.png',dpi=220); plt.close(fig)
 print(json.dumps({'v1':base,'v2':v2,'by_family':family},indent=2))
if __name__=='__main__': main()
