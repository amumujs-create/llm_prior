#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from prior_calibration_specificity_v1 import gen,spec,interval,fit,TB,EXPOSURE,NOISES,CONDS as KCONDS
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'/'prior_quality_audit_v1';FIG=ROOT/'figures';SEED,N,M=20261008,30,600
CONDS=('family_only','broad_correct','narrow_correct','narrow_mild_bias','narrow_strong_bias')
def main():
 rng=np.random.default_rng(SEED);t=np.round(np.arange(0,1.301,.01),4);obs=t<=TB;tail=(t>=1.2)&(t<=1.3);rows=[]
 for fam,levels in EXPOSURE.items():
  for ol,e in levels.items():
   for noise in NOISES:
    for task in range(N):
     clean,p=gen(fam,e,t,rng);y=clean.copy();y[obs]+=rng.normal(0,noise,obs.sum());fn,p0,lo,hi=spec(fam);draw=rng.uniform(lo,hi,size=(M,len(p)));pred=np.array([fn(t[obs],*q) for q in draw]);loss=np.mean((pred-y[obs])**2,axis=1);w=np.exp(-(loss-loss.min())/(2*max(noise**2,1e-6)));w/=w.sum();fallback=np.sqrt(np.mean((np.polyval(np.polyfit(t[obs],y[obs],1),t[tail])-clean[tail])**2))
     for cond in CONDS:
      if cond=='family_only': survive=np.ones(M,dtype=bool);cover=1.
      else:
       fn2,c,lower,upper=interval(fam,p,*KCONDS[cond][1:]);survive=np.all((draw>=lower)&(draw<=upper),axis=1);cover=float(np.all((p>=lower)&(p<=upper)))
      sharp=float(-np.log(max(float(w[survive].sum()),1e-12)));pr=np.sqrt(np.mean((fit(fam,t[obs],y[obs],t[tail],cond,p)-clean[tail])**2));rows.append({'family':fam,'observability':ol,'noise':noise,'condition':cond,'coverage':cover,'sharpness':sharp,'incremental_information':sharp,'utility':float(fallback-pr)})
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'results.json').write_text(json.dumps({'experiment_id':'prior_quality_audit_v1','status':'development','protocol':'PRIOR_QUALITY_AUDIT_PROTOCOL_V1.md','n_tasks':len(rows)//len(CONDS),'records':rows},indent=2)+'\n')
 FIG.mkdir(exist_ok=True);fig,ax=plt.subplots(figsize=(7,5.5),constrained_layout=True);colors={'family_only':'#777','broad_correct':'#3978b8','narrow_correct':'#43a86b','narrow_mild_bias':'#dd7f28','narrow_strong_bias':'#cc4c4c'}
 for c in CONDS:
  z=[r for r in rows if r['condition']==c];ax.scatter([r['sharpness'] for r in z],[r['coverage'] for r in z],s=np.clip(np.array([r['utility'] for r in z])*80+20,5,120),alpha=.35,color=colors[c],label=c)
 ax.set(xlabel='Structural sharpness: −log conditional survival',ylabel='Structural coverage',title='Prior quality audit: coverage × sharpness\n(point size = far-OOD utility)');ax.legend(fontsize=7);fig.savefig(FIG/'fig23_prior_quality_audit.png',dpi=220);plt.close(fig)
 print(json.dumps({'n_tasks':len(rows)//len(CONDS),'mean_coverage':{c:float(np.mean([r['coverage'] for r in rows if r['condition']==c])) for c in CONDS},'mean_sharpness':{c:float(np.mean([r['sharpness'] for r in rows if r['condition']==c])) for c in CONDS}},indent=2))
if __name__=='__main__':main()
