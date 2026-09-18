#!/usr/bin/env python3
"""Frozen E6-v1: distance-dependent trust in prefix-trained corrections."""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from prior_evaluation_metric_v1 import TB, OBS, NOISES, fit, regime, curvature, bound

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'/'distance_residual_trust_v1'; FIG=ROOT/'figures'
SEED,N=20261007,50; DS=np.array([.05,.10,.20,.30,.40,.60,.80,1.00]); ARCH=('spline','nn')

def truth(f,e,t,rng):
 if f=='regime_change': return regime(t,rng.uniform(.07,.24),rng.uniform(.35,1),rng.uniform(1.35,2.6),e)
 if f=='emergent_curvature': return curvature(t,rng.uniform(.05,.16),rng.uniform(.22,.6),rng.uniform(1.35,2.6),e)
 return bound(t,rng.uniform(.2,.7),e)
def prior(f): return {'regime_change':'PT','emergent_curvature':'PC','asymptotic_bound':'PB'}[f]
def model(a,seed):
 if a=='spline': return make_pipeline(SplineTransformer(n_knots=5,degree=3,extrapolation='linear'),Ridge(alpha=.01))
 return make_pipeline(StandardScaler(),MLPRegressor(hidden_layer_sizes=(8,),alpha=.01,solver='lbfgs',max_iter=700,random_state=seed))
def rmse(a,b): return float(abs(a-b))

def main():
 rng=np.random.default_rng(SEED);t=np.round(np.arange(0,1.601,.01),4);obs=t<=TB;inner=t<=.45;pseudo=(t>.45)&(t<=TB);query=np.array([TB*(1+d) for d in DS]);rec=[];tasks=[];tid=0
 for fam,levels in OBS.items():
  for ol,e in levels.items():
   for noise in NOISES:
    for _ in range(N):
     ytrue=truth(fam,e,t,rng);y=ytrue.copy();y[obs]+=rng.normal(0,noise,obs.sum());pname=prior(fam)
     pf=fit(pname,t[obs],y[obs],t); pi=fit(pname,t[inner],y[inner],t); ai=fit('P0',t[inner],y[inner],t[pseudo])
     prior_good=np.mean((pi[pseudo]-y[pseudo])**2)<np.mean((ai-y[pseudo])**2)
     for arch in ARCH:
      mf=model(arch,tid);mf.fit(t[obs,None],y[obs]-pf[obs]);rf=mf.predict(t[:,None])
      mi=model(arch,tid+100000);mi.fit(t[inner,None],y[inner]-pi[inner]);ri=mi.predict(t[pseudo,None])
      residual_good=np.mean((pi[pseudo]+ri-y[pseudo])**2)<np.mean((pi[pseudo]-y[pseudo])**2)
      near_gain=float(np.sqrt(np.mean((pi[pseudo]-y[pseudo])**2))-np.sqrt(np.mean((pi[pseudo]+ri-y[pseudo])**2)))
      deltas=[]
      for d,x in zip(DS,query):
       j=np.argmin(abs(t-x));p=pf[j];r=rf[j];base=rmse(p,ytrue[j]);pred={'prior':p,'fixed':p+r,'decay':p+np.exp(-2*d)*r,'evidence':p+(np.exp(-2*d)*r if prior_good and residual_good else 0.)}
       deltas.append(base-rmse(pred['fixed'],ytrue[j]))
       for method,v in pred.items(): rec.append({'task_id':tid,'family':fam,'observability_level':ol,'noise_sd':noise,'architecture':arch,'distance':float(d),'method':method,'rmse':rmse(v,ytrue[j]),'prior_rmse':base,'delta_fixed':deltas[-1],'catastrophic':bool(base>1e-12 and rmse(v,ytrue[j])>=2*base),'near_gain':near_gain,'prior_pseudo_good':bool(prior_good),'residual_pseudo_good':bool(residual_good)})
      first=next((float(d) for d,z in zip(DS,deltas) if z<=0),None);tasks.append({'task_id':tid,'family':fam,'architecture':arch,'d_star':first,'right_censored':first is None,'near_gain':near_gain,'far_delta_fixed':deltas[-1]});tid+=1
 groups=defaultdict(list)
 for r in rec: groups[(r['architecture'],r['method'],r['distance'])].append(r)
 summary=[]
 for k,rows in sorted(groups.items()):
  a,m,d=k;summary.append({'architecture':a,'method':m,'distance':d,'n':len(rows),'mean_rmse':float(np.mean([r['rmse'] for r in rows])),'mean_delta_fixed':float(np.mean([r['delta_fixed'] for r in rows])),'catastrophic_rate':float(np.mean([r['catastrophic'] for r in rows]))})
 task_summary=[]
 for a in ARCH:
  z=[r for r in tasks if r['architecture']==a];task_summary.append({'architecture':a,'d_star_right_censored_rate':float(np.mean([r['right_censored'] for r in z])),'d_star_immediate_failure_rate':float(np.mean([r['d_star']==.05 for r in z])),'near_gain_far_delta_spearman':float(spearmanr([r['near_gain'] for r in z],[r['far_delta_fixed'] for r in z]).statistic)})
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'results.json').write_text(json.dumps({'experiment_id':'distance_residual_trust_v1','status':'development','protocol':'DISTANCE_RESIDUAL_TRUST_PROTOCOL_V1.md','n_base_tasks':tid,'summary':summary,'task_summary':task_summary,'task_records':tasks,'records':rec},indent=2)+'\n')
 FIG.mkdir(exist_ok=True);fig,ax=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
 for a,c in zip(ARCH,['#3978b8','#dd7f28']):
  for m,ls in [('fixed','-'),('decay','--'),('evidence',':')]:
   z=sorted([r for r in summary if r['architecture']==a and r['method']==m],key=lambda r:r['distance']);ax[0].plot([r['distance'] for r in z],[r['mean_delta_fixed'] for r in z],ls,color=c,label=f'{a} {m}');ax[1].plot([r['distance'] for r in z],[r['catastrophic_rate'] for r in z],ls,color=c,label=f'{a} {m}')
 ax[0].axhline(0,color='#555');ax[0].set(xlabel='normalized support distance',ylabel='mean ΔR(d)',title='Fixed-residual utility');ax[1].set(xlabel='normalized support distance',ylabel='catastrophic harm rate',title='Method harm');ax[1].legend(fontsize=7);fig.savefig(FIG/'fig24_distance_residual_trust.png',dpi=220);plt.close(fig)
 print(json.dumps(task_summary,indent=2))
if __name__=='__main__': main()
