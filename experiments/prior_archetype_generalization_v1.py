#!/usr/bin/env python3
"""E4: random monotone structural-prior archetype generalization."""
from __future__ import annotations
import json, math
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from prior_evaluation_metric_v1 import BANDS, CANDIDATES, INNER, ORDER, PARAMETERS, TB, fit

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'prior_archetype_generalization_v1'; FIG=ROOT/'figures'
SEED,N,BOOT=20261004,100,1000; SNR={'weak':.02,'medium':.08,'strong':.20}; NOISES=(.005,.015,.030)

def generate(t, scale, rng):
    phase=rng.uniform(0,2*np.pi,3); amp=rng.normal(0,.45,3)
    g=sum(amp[i]*np.sin(2*np.pi*(i+1)*t+phase[i]) for i in range(3))
    dydt=-scale*np.exp(g); return 1+np.cumsum(dydt*np.diff(t,prepend=t[0]))
def score(kind,y,p,pcount):
    mse=float(np.mean((y-p)**2)); return -mse if kind=='mse' else -float(len(y)*math.log(mse+1e-12)+pcount*math.log(len(y)))
def pick(scores): return max(CANDIDATES,key=lambda c:(scores[c],-ORDER[c]))
def ci(x,rng):
    x=np.asarray(x); draws=x[rng.integers(0,len(x),size=(BOOT,len(x)))].mean(1); return [float(v) for v in np.quantile(draws,[.025,.975])]

def main():
    rng=np.random.default_rng(SEED); t=np.round(np.arange(0,1.301,.01),4); obs=t<=TB; inner=t<=INNER; pseudo=(t>INNER)&(t<=TB); masks={k:(t>=a)&(t<=b) for k,(a,b) in BANDS.items()}; rec=[]; task=0
    for snr,scale in SNR.items():
      for noise in NOISES:
       for _ in range(N):
        clean=generate(t,scale,rng); noisy=clean.copy(); noisy[obs]+=rng.normal(0,noise,obs.sum())
        ppre={c:fit(c,t[inner],noisy[inner],t[pseudo]) for c in CANDIDATES}; pall={c:fit(c,t[obs],noisy[obs],t) for c in CANDIDATES}
        for selector in ('mse','bic'):
         selected=pick({c:score(selector,noisy[pseudo],ppre[c],PARAMETERS[c]) for c in CANDIDATES})
         for band,mask in masks.items():
          rmses={c:float(np.sqrt(np.mean((pall[c][mask]-clean[mask])**2))) for c in CANDIDATES}; winner=min(CANDIDATES,key=lambda c:(rmses[c],ORDER[c]))
          rec.append({'task_id':task,'snr_level':snr,'noise_sd':noise,'selector':selector,'band':band,'selected':selected,'far_winner':winner,'direction_utility':rmses['P0']-rmses['PD'],'regret':rmses[selected]-rmses[winner],'incompatible':selected in ('PC','PB','PT')})
        task+=1
    groups=defaultdict(list)
    for r in rec: groups[(r['snr_level'],r['noise_sd'],r['selector'],r['band'])].append(r)
    brng=np.random.default_rng(SEED+1); summary=[]
    for key,rows in sorted(groups.items()):
      snr,noise,selector,band=key; summary.append({'snr_level':snr,'noise_sd':noise,'selector':selector,'band':band,'n':len(rows),'direction_utility':float(np.mean([r['direction_utility'] for r in rows])),'direction_utility_ci95':ci([r['direction_utility'] for r in rows],brng),'mean_regret':float(np.mean([r['regret'] for r in rows])),'regret_ci95':ci([r['regret'] for r in rows],brng),'incompatible_selection_rate':float(np.mean([r['incompatible'] for r in rows]))})
    pooled=defaultdict(list)
    for r in rec: pooled[(r['snr_level'],r['selector'],r['band'])].append(r)
    ps=[]
    for key,rows in sorted(pooled.items()):
      snr,selector,band=key;ps.append({'snr_level':snr,'selector':selector,'band':band,'mean_regret':float(np.mean([r['regret'] for r in rows])),'incompatible_selection_rate':float(np.mean([r['incompatible'] for r in rows]))})
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'results.json').write_text(json.dumps({'experiment_id':'prior_archetype_generalization_v1','status':'development','protocol':'PRIOR_ARCHETYPE_GENERALIZATION_PROTOCOL_V1.md','n_tasks':task,'summary':summary,'pooled_summary':ps,'records':rec},indent=2)+'\n')
    FIG.mkdir(exist_ok=True); order=['weak','medium','strong']; fig,ax=plt.subplots(1,2,figsize=(11,4.5),constrained_layout=True)
    for noise,color in zip(NOISES,['#3978b8','#dd7f28','#cc4c4c']):
      rows=[r for r in summary if r['noise_sd']==noise and r['selector']=='mse' and r['band']=='D3']; rows.sort(key=lambda r:order.index(r['snr_level'])); ax[0].plot(range(3),[r['direction_utility'] for r in rows],'o-',label=f'noise {noise}',color=color)
    ax[0].axhline(0,color='#555');ax[0].set(title='True direction-prior utility',xticks=range(3),xticklabels=order,xlabel='direction SNR',ylabel='RMSE(P0) − RMSE(PD)');ax[0].legend(fontsize=8)
    for selector,color in zip(('mse','bic'),['#cc4c4c','#555']):
      rows=[r for r in ps if r['selector']==selector and r['band']=='D3'];rows.sort(key=lambda r:order.index(r['snr_level']));ax[1].plot(range(3),[r['incompatible_selection_rate'] for r in rows],'o-',label=selector.upper(),color=color)
    ax[1].set(title='Incompatible selection on monotone archetype',xticks=range(3),xticklabels=order,xlabel='direction SNR',ylabel='rate',ylim=(0,1));ax[1].legend();fig.savefig(FIG/'fig19_monotone_archetype_generalization.png',dpi=220);plt.close(fig)
    print(json.dumps(ps,indent=2))
if __name__=='__main__': main()
