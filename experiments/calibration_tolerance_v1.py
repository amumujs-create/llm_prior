#!/usr/bin/env python3
from __future__ import annotations
import json,warnings
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from prior_calibration_specificity_v1 import gen,spec,TB,affine
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'/'calibration_tolerance_v1';FIG=ROOT/'figures'
B=(0,.025,.05,.075,.10,.15,.20,.30,.40);N,NOISE,SEED=50,.015,20261006; EXP={'regime_change':{'low':.59,'mid':.48,'high':.32},'emergent_curvature':{'low':.59,'mid':.48,'high':.32},'asymptotic_bound':{'low':.35,'mid':1.5,'high':3.5}}; FIELDS={'regime_change':(('onset',),('scale',),('onset','scale')),'emergent_curvature':(('scale',),('shape',),('scale','shape')),'asymptotic_bound':(('lower',),)}
IDX={'scale':1,'shape':2,'onset':3,'lower':0}
def fit(f,t,y,target,p,fields=None,b=0,broad=False):
 fn,p0,lo,hi=spec(f);lo=np.array(lo,float);hi=np.array(hi,float);center=np.array(p,float);half=np.abs(center)*(.30 if broad else .05)
 if f!='asymptotic_bound':half[-1]=.20 if broad else .03
 if fields:
  for field in fields:
   i=IDX[field];center[i]=p[i]+b*(hi[i]-lo[i])
 lower=np.maximum(lo,center-half);upper=np.minimum(hi,center+half);p0=np.clip(center,lower+1e-7,upper-1e-7)
 try:
  with warnings.catch_warnings():warnings.simplefilter('ignore');q,_=curve_fit(fn,t,y,p0=p0,bounds=(lower,upper),maxfev=3500)
  return fn(target,*q)
 except Exception:
  s,c=np.polyfit(t,y,1);return affine(target,s,c)
def main():
 rng=np.random.default_rng(SEED);t=np.round(np.arange(0,1.301,.01),4);obs=t<=TB;tail=(t>=1.2)&(t<=1.3);rec=[];task=0
 for f,levels in EXP.items():
  for o,e in levels.items():
   for _ in range(N):
    clean,p=gen(f,e,t,rng);noisy=clean.copy();noisy[obs]+=rng.normal(0,NOISE,obs.sum());broad=float(np.sqrt(np.mean((fit(f,t[obs],noisy[obs],t[tail],p,broad=True)-clean[tail])**2)))
    for fields in FIELDS[f]:
     for b in B:
      score=float(np.sqrt(np.mean((fit(f,t[obs],noisy[obs],t[tail],p,fields,b)-clean[tail])**2)));rec.append({'task_id':task,'family':f,'observability_level':o,'fields':'+'.join(fields),'b_norm':b,'broad_correct_rmse':broad,'narrow_biased_rmse':score,'utility_difference':broad-score,'narrow_harmful_vs_broad':score>broad})
    task+=1
 groups=defaultdict(list)
 for r in rec:groups[(r['family'],r['fields'],r['b_norm'])].append(r)
 summary=[]
 for k,rows in sorted(groups.items()):
  f,fields,b=k;d=[r['utility_difference'] for r in rows];summary.append({'family':f,'fields':fields,'b_norm':b,'n':len(rows),'mean_utility_difference':float(np.mean(d)),'harm_rate_vs_broad':float(np.mean([r['narrow_harmful_vs_broad'] for r in rows]))})
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'results.json').write_text(json.dumps({'experiment_id':'calibration_tolerance_v1','status':'development','protocol':'CALIBRATION_TOLERANCE_PROTOCOL_V1.md','n_base_tasks':task,'summary':summary,'records':rec},indent=2)+'\n')
 FIG.mkdir(exist_ok=True);fig,axes=plt.subplots(1,3,figsize=(15,4.5),constrained_layout=True)
 for ax,f in zip(axes,EXP):
  for fields,color in zip(FIELDS[f],['#3978b8','#dd7f28','#cc4c4c']):
   name='+'.join(fields);rows=[r for r in summary if r['family']==f and r['fields']==name];rows.sort(key=lambda r:r['b_norm']);ax.plot([r['b_norm'] for r in rows],[r['mean_utility_difference'] for r in rows],'o-',label=name,color=color)
  ax.axhline(0,color='#555');ax.set(title=f.replace('_',' '),xlabel='normalized calibration bias',ylabel='U(narrow biased) − U(broad correct)')
  ax.legend(fontsize=8)
 fig.savefig(FIG/'fig21_calibration_tolerance_curves.png',dpi=220);plt.close(fig);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
