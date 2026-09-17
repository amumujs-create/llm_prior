#!/usr/bin/env python3
"""Family-vs-parameter-vs-full-information oracle decomposition."""
from __future__ import annotations
import json, warnings
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit, lsq_linear

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'oracle_decomposition_v1'; FIG=ROOT/'figures'; RNG=np.random.default_rng(20260923)
TB=.60; TAUS=(.78,.68,.60,.55,.48,.38,.28); EXPS=(.10,.25,.5,.9,1.5,2.3,3.2); N=100
def pp(x,a): return np.maximum(x,0)**a
def reg(t,k1,k2,a,tau): return np.where(t<tau,1-k1*t,1-k1*tau-k2*pp(t-tau,a))
def curv(t,k1,k2,a,tau): return 1-k1*t-k2*pp(t-tau,a)
def sat(t,l,k): return l+(1-l)*np.exp(-k*t)
F={'regime_change':(reg,[.15,.5,2,.5],([0,0,1.01,.12],[.8,2,4,.9])),'emergent_curvature':(curv,[.1,.35,2,.5],([0,0,1.01,.12],[.7,2,4,.9])),'asymptotic_bound':(sat,[.5,1.5],([0,.01],[.95,10]))}
def linear(t,y,x):
 s,b=np.polyfit(t,y,1); return s*x+b
def family(f,t,y,x):
 fn,p0,bd=F[f]
 try:
  with warnings.catch_warnings(): warnings.simplefilter('ignore'); p,_=curve_fit(fn,t,y,p0=p0,bounds=bd,maxfev=3000)
  return fn(x,*p)
 except (RuntimeError,ValueError): return linear(t,y,x)
def param_oracle(f,t,y,x,p):
 if f=='regime_change':
  k2,a,tau=p[1:]; base=reg(t,0,k2,a,tau); g=np.where(t<tau,t,tau); coef=np.dot(g,base-y)/np.dot(g,g); return reg(x,coef,k2,a,tau)
 if f=='emergent_curvature':
  k2,a,tau=p[1:]; z=pp(t-tau,a); k1=np.dot(t,1-y-k2*z)/np.dot(t,t); return curv(x,k1,k2,a,tau)
 l=p[0]
 try:
  k,_=curve_fit(lambda q,rate:sat(q,l,rate),t,y,p0=[1.],bounds=([.01],[10.])); return sat(x,l,*k)
 except RuntimeError: return linear(t,y,x)
def generate(f,level,t,r):
 if f=='regime_change':
  p=np.array([r.uniform(.07,.24),r.uniform(.35,1.),r.uniform(1.35,2.6),level]); return reg(t,*p),p,max(0,(TB-level)/TB)
 if f=='emergent_curvature':
  p=np.array([r.uniform(.05,.16),r.uniform(.22,.6),r.uniform(1.35,2.6),level]); return curv(t,*p),p,max(0,(TB-level)/TB)
 p=np.array([r.uniform(.2,.7),level/TB]); return sat(t,*p),p,1-np.exp(-level)
def concave_spline(t,y,x):
 # Monotone nonincreasing slopes on fixed knots, extrapolated with final slope.
 knots=np.linspace(0,TB,7); means=np.array([y[(t>=knots[i])&(t<=knots[i+1])].mean() if i<6 else y[-1] for i in range(7)]); slopes=np.diff(means)/np.diff(knots); slopes=np.minimum.accumulate(np.minimum(slopes,0)); vals=np.r_[means[0],means[0]+np.cumsum(slopes*np.diff(knots))]; return np.interp(np.minimum(x,TB),knots,vals)+(np.maximum(x-TB,0))*slopes[-1]
def neural_basis(t,y,x):
 # One-hidden-layer constrained ReLU^2 network: y=a-bt-sum w relu(t-k)^2, b,w>=0.
 ks=np.array([.15,.30,.45]); A=np.column_stack([np.ones_like(t),-t,*[-pp(t-k,2) for k in ks]]); sol=lsq_linear(A,y,bounds=(np.r_[-np.inf,0,0,0,0],np.inf)).x; B=np.column_stack([np.ones_like(x),-x,*[-pp(x-k,2) for k in ks]]); return B@sol
def rmse(a,b): return float(np.sqrt(np.mean((a-b)**2)))
def main():
 t=np.linspace(0,1,101); obs=t<=TB; tail=t>.70; rec=[]; aux=defaultdict(list)
 for f in F:
  levels=TAUS if f!='asymptotic_bound' else EXPS
  for lev in levels:
   for j in range(N):
    clean,p,o=generate(f,lev,t,RNG); y=clean+RNG.normal(0,.015,len(t)); truth=clean[tail]
    pred={'no_prior':linear(t[obs],y[obs],t[tail]),'family_oracle':family(f,t[obs],y[obs],t[tail]),'parameter_oracle':param_oracle(f,t[obs],y[obs],t[tail],p),'full_information_oracle':truth}
    scores={k:rmse(v,truth) for k,v in pred.items()}; rec.append({'family':f,'level':float(lev),'observability':float(o),**scores})
    if f=='emergent_curvature':
     aux[float(o)].append({'power_law':scores['family_oracle'],'concave_spline':rmse(concave_spline(t[obs],y[obs],t[tail]),truth),'constrained_neural_basis':rmse(neural_basis(t[obs],y[obs],t[tail]),truth)})
 group=defaultdict(list)
 for z in rec: group[(z['family'],z['level'])].append(z)
 summary=[]
 for (f,l),zs in group.items(): summary.append({'family':f,'level':l,'observability':zs[0]['observability'],**{k:float(np.mean([z[k] for z in zs])) for k in ('no_prior','family_oracle','parameter_oracle','full_information_oracle')}})
 auxsum=[{'observability':o,**{k:float(np.mean([z[k] for z in zs])) for k in ('power_law','concave_spline','constrained_neural_basis')}} for o,zs in aux.items()]
 OUT.mkdir(parents=True,exist_ok=True); result={'experiment_id':'oracle_decomposition_v1','status':'development','n_tasks':len(rec),'terms':{'family_oracle':'generative-family oracle; correct family only, parameters fitted from prefix','parameter_oracle':'bottleneck realization parameters supplied as prespecified in protocol','full_information_oracle':'all generator parameters supplied'},'summary':sorted(summary,key=lambda z:(z['family'],z['level'])),'acceleration_realization_auxiliary':sorted(auxsum,key=lambda z:z['observability'])}; (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
 FIG.mkdir(exist_ok=True); fig,axs=plt.subplots(1,3,figsize=(14,4),constrained_layout=True); names={'regime_change':'Regime change','emergent_curvature':'Emergent curvature','asymptotic_bound':'Asymptotic bound'}
 for ax,f in zip(axs,F):
  z=sorted([q for q in summary if q['family']==f],key=lambda q:q['observability']); x=[q['observability'] for q in z]
  for k,c in [('no_prior','#777'),('family_oracle','#cc4c4c'),('parameter_oracle','#3978b8'),('full_information_oracle','#43a86b')]: ax.plot(x,[q[k] for q in z],'o-',label=k.replace('_',' '),color=c)
  ax.set(title=names[f],xlabel='observability',ylabel='far-OOD RMSE'); ax.legend(fontsize=7)
 fig.suptitle('Oracle decomposition: family truth is not realization knowledge'); fig.savefig(FIG/'fig09_oracle_decomposition.png',dpi=220); plt.close(fig)
 fig,ax=plt.subplots(figsize=(6.5,4.2),constrained_layout=True)
 for k,c in [('power_law','#cc4c4c'),('concave_spline','#3978b8'),('constrained_neural_basis','#43a86b')]: ax.plot([z['observability'] for z in auxsum],[z[k] for z in auxsum],'o-',label=k.replace('_',' '),color=c)
 ax.set(title='Auxiliary: acceleration realizations',xlabel='observability',ylabel='far-OOD RMSE'); ax.legend(); fig.savefig(FIG/'fig10_acceleration_realization_robustness.png',dpi=220)
 print(json.dumps(summary[:2],indent=2))
if __name__=='__main__': main()
