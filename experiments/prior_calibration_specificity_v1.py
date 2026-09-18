#!/usr/bin/env python3
"""E5 frozen calibration × specificity sweep."""
from __future__ import annotations
import json, warnings
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from prior_evaluation_metric_v1 import TB, affine, regime, curvature, bound

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'prior_calibration_specificity_v1'; FIG=ROOT/'figures'
SEED,N,BOOT=20261005,100,1000; NOISES=(.005,.015,.030); TAIL=(1.20,1.30)
EXPOSURE={'regime_change':{'low':.59,'mid':.48,'high':.32},'emergent_curvature':{'low':.59,'mid':.48,'high':.32},'asymptotic_bound':{'low':.35,'mid':1.5,'high':3.5}}
CONDS={'family_only':('family',None,None),'broad_correct':('interval','broad','correct'),'medium_correct':('interval','medium','correct'),'narrow_correct':('interval','narrow','correct'),'narrow_mild_bias':('interval','narrow','mild'),'narrow_strong_bias':('interval','narrow','strong')}

def gen(f,e,t,rng):
 if f=='regime_change':
  p=np.array([rng.uniform(.07,.24),rng.uniform(.35,1),rng.uniform(1.35,2.6),e]);return regime(t,*p),p
 if f=='emergent_curvature':
  p=np.array([rng.uniform(.05,.16),rng.uniform(.22,.6),rng.uniform(1.35,2.6),e]);return curvature(t,*p),p
 p=np.array([rng.uniform(.2,.7),e]);return bound(t,*p),p
def spec(f):
 return (regime,[.15,.55,2,.45],[0,0,1.01,.001],[.8,2,4,.95]) if f=='regime_change' else ((curvature,[.1,.35,2,.45],[0,0,1.01,.001],[.7,2,4,.95]) if f=='emergent_curvature' else (bound,[.5,1.5],[0,.005],[.95,12]))
def interval(f,p,width,bias):
 fn,p0,lo,hi=spec(f);p=np.array(p);lo=np.array(lo,float);hi=np.array(hi,float)
 frac={'broad':.30,'medium':.15,'narrow':.05}[width]; shift={'correct':0,'mild':.10,'strong':.30}[bias]
 center=p*(1+shift); half=np.abs(p)*frac
 if f!='asymptotic_bound': center[-1]=p[-1]+{'correct':0,'mild':.05,'strong':.15}[bias];half[-1]={'broad':.20,'medium':.10,'narrow':.03}[width]
 lower=np.maximum(lo,center-half);upper=np.minimum(hi,center+half);bad=upper-lower<1e-6;lower[bad]=np.maximum(lo[bad],p[bad]-.0001);upper[bad]=np.minimum(hi[bad],p[bad]+.0001)
 return fn,np.clip(center,lower+1e-7,upper-1e-7),lower,upper
def fit(f,t,y,target,condition,p):
 if condition=='family_only': fn,p0,lo,hi=spec(f)
 else: fn,p0,lo,hi=interval(f,p,*CONDS[condition][1:])
 try:
  with warnings.catch_warnings():
   warnings.simplefilter('ignore');q,_=curve_fit(fn,t,y,p0=p0,bounds=(lo,hi),maxfev=3500)
  return fn(target,*q)
 except (RuntimeError,ValueError,FloatingPointError):
  s,b=np.polyfit(t,y,1);return affine(target,s,b)
def ci(x,rng):
 x=np.asarray(x);return [float(v) for v in np.quantile(x[rng.integers(0,len(x),size=(BOOT,len(x)))].mean(1),[.025,.975])]
def main():
 rng=np.random.default_rng(SEED);t=np.round(np.arange(0,1.301,.01),4);obs=t<=TB;tail=(t>=TAIL[0])&(t<=TAIL[1]);rec=[];task=0
 for family,levels in EXPOSURE.items():
  for oname,e in levels.items():
   for noise in NOISES:
    for _ in range(N):
     clean,p=gen(family,e,t,rng);noisy=clean.copy();noisy[obs]+=rng.normal(0,noise,obs.sum());fallback=(lambda q:float(np.sqrt(np.mean((q-clean[tail])**2))))(affine(t[tail],*np.polyfit(t[obs],noisy[obs],1)))
     for condition in CONDS:
      pred=fit(family,t[obs],noisy[obs],t[tail],condition,p);score=float(np.sqrt(np.mean((pred-clean[tail])**2)));rec.append({'task_id':task,'family':family,'observability_level':oname,'noise_sd':noise,'condition':condition,'fallback_rmse':fallback,'prior_rmse':score,'utility':fallback-score})
     task+=1
 groups=defaultdict(list)
 for r in rec:groups[(r['family'],r['observability_level'],r['noise_sd'],r['condition'])].append(r)
 brng=np.random.default_rng(SEED+1);summary=[]
 for key,rows in sorted(groups.items()):
  f,o,n,c=key;x=[r['utility'] for r in rows];summary.append({'family':f,'observability_level':o,'noise_sd':n,'condition':c,'n':len(rows),'mean_utility':float(np.mean(x)),'utility_ci95':ci(x,brng),'mean_prior_rmse':float(np.mean([r['prior_rmse'] for r in rows]))})
 pooled=defaultdict(list)
 for r in rec:pooled[r['condition']].append(r)
 ps=[{'condition':c,'mean_utility':float(np.mean([r['utility'] for r in rows])),'utility_ci95':ci([r['utility'] for r in rows],brng),'harmful_rate':float(np.mean([r['utility']<0 for r in rows]))} for c,rows in pooled.items()]
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'results.json').write_text(json.dumps({'experiment_id':'prior_calibration_specificity_v1','status':'development','protocol':'PRIOR_CALIBRATION_SPECIFICITY_PROTOCOL_V1.md','n_tasks':task,'summary':summary,'pooled_summary':ps,'records':rec},indent=2)+'\n')
 FIG.mkdir(exist_ok=True);fig,axes=plt.subplots(1,3,figsize=(15,4.4),constrained_layout=True);order=['family_only','broad_correct','medium_correct','narrow_correct','narrow_mild_bias','narrow_strong_bias'];labels=['family','broad\ncorrect','medium\ncorrect','narrow\ncorrect','narrow\nmild bias','narrow\nstrong bias']
 for ax,family in zip(axes,EXPOSURE):
  rows=[r for r in summary if r['family']==family];
  for noise,color in zip(NOISES,['#3978b8','#dd7f28','#cc4c4c']):
   z=[]
   for c in order:
    q=[r['mean_utility'] for r in rows if r['noise_sd']==noise and r['condition']==c];z.append(float(np.mean(q)))
   ax.plot(range(6),z,'o-',label=f'noise {noise}',color=color)
  ax.axhline(0,color='#555');ax.set(title=family.replace('_',' '),xticks=range(6),xticklabels=labels,xlabel='knowledge calibration / specificity',ylabel='D3 utility');ax.tick_params(axis='x',rotation=25)
 axes[-1].legend(fontsize=7);fig.suptitle('Prior specificity helps only while realization constraints remain calibrated');fig.savefig(FIG/'fig20_prior_calibration_specificity.png',dpi=220);plt.close(fig)
 print(json.dumps(ps,indent=2))
if __name__=='__main__':main()
