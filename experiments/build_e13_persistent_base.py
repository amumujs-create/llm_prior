#!/usr/bin/env python3
"""Dedicated E13 persistent-base generator; no E11 trajectory reuse."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from run_prior_completeness_e11 import INTENTS, GENS, valid_atoms, envelope

ROOT=Path(__file__).resolve().parents[1]; X=np.linspace(0,1.20,601); H=(.85,.90,1.00,1.10,1.20)

def _hash(a): return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def _changes(v,tol):
 s=np.where(v>tol,1,np.where(v<-tol,-1,0));s=s[s!=0];return int(np.sum(s[1:]!=s[:-1])) if len(s)>1 else 0

def persistent_base(intent,generator,seed):
 """Atom-compatible parameterization; final acceptance remains checker-based."""
 x=X; k={'spline':1.0,'basis':1.03,'ode':.97}[generator]; n=set(INTENTS[intent]); rng=np.random.default_rng(seed)
 if 'turning_maximum' in n:
  # Analytic asymmetric hump: one maximum at tau, positive lower bound,
  # and an explicit exponential tail to zero from above.
  tau=.55; lam=3.2*k; beta=7.0*k; u=x-tau
  y=1.0*np.exp(-lam*u-(lam/beta)*(np.exp(-beta*u)-1.0))
 elif 'inflection_concave_to_convex' in n:
  y=1/(1+np.exp(7.0*k*(x-.55)))
 elif 'regime_postchange' in n:
  u=np.clip((x-.28)/.10,0,1); gate=u**3*(10-15*u+6*u*u)
  y=np.exp(-1.1*k*x-1.2*gate)
 elif 'asymptote_to_0_from_above' in n:
  y=np.exp(-2.1*k*x)
 else:
  # Near-linear decreasing convex positive trajectory avoids an accidental
  # operational asymptote while retaining the requested core atoms.
  y=1.5-.80*x+.01*x*x
 # Tiny family variation is bounded to preserve the persistent parameterization.
 y+=rng.uniform(-2e-5,2e-5)*(x-.6)**3
 return x,y

def raw_valid(x,y,atom,h,z):
 m=(x>=.40)&(x<=h); xx=x[m]; yy=y[m];r=max(float(np.ptp(y)),1e-8);d1=np.gradient(yy,xx);d2=np.gradient(d1,xx)
 if atom=='direction_decreasing': return np.mean(d1<=.01*r)>=.95
 if atom=='curvature_convex': return np.mean(d2>=-.04*r)>=.90
 if atom=='lower_bound_0': return np.min(yy)>=-.01*r
 if atom=='inflection_concave_to_convex':
  nz=d2[np.abs(d2)>.03*r];return _changes(d2,.03*r)==1 and len(nz)>1 and nz[0]<0 and nz[-1]>0
 if atom=='turning_maximum':
  nz=d1[np.abs(d1)>.02*r];return _changes(d1,.02*r)==1 and len(nz)>1 and nz[0]>0 and nz[-1]<0
 if atom=='regime_postchange': return bool(z['regime_active'])
 if atom=='asymptote_to_0_from_above': return bool(z['asymptote_active'] and h<=z.get('asymptote_active_through',np.inf) and np.min(yy)>0)
 raise ValueError(atom)

def contiguous_table(x,y,pstar,z):
 raw={a:[int(raw_valid(x,y,a,h,z)) for h in H] for a in pstar}; cont={}
 for a,v in raw.items():
  alive=1;cont[a]=[]
  for q in v: alive*=q;cont[a].append(alive)
 return raw,cont

def build(intent,generator,seed):
 x,y=persistent_base(intent,generator,seed)
 core=valid_atoms(y,INTENTS[intent],x); pstar,nmax=envelope(core,INTENTS[intent])
 if pstar is None or not set(INTENTS[intent])<=set(pstar): return None,'core_envelope_failure'
 z={'regime_active':'regime_postchange' in pstar,
    'asymptote_active':'asymptote_to_0_from_above' in pstar,
    'asymptote_active_through':np.inf,
    'asymptotic_limit':0.0 if 'asymptote_to_0_from_above' in pstar else None,
    'approach_side':'from_above' if 'asymptote_to_0_from_above' in pstar else None,
    'turning_type':'maximum' if 'turning_maximum' in pstar else None,
    'turning_location':.55 if 'turning_maximum' in pstar else None}
 raw,cont=contiguous_table(x,y,pstar,z)
 if not all(all(v) for v in cont.values()): return None,'base_not_persistent'
 return {'x':x,'y':y,'intent':INTENTS[intent],'pstar':pstar,'z':z,'raw':raw,'contiguous':cont,'base_hash':_hash(y)},'accepted'

def main():
 rows=[]
 for intent in INTENTS:
  for gen in GENS:
   task,reason=build(intent,gen,0);rows.append({'intent':intent,'generator':gen,'status':reason,'pstar':'' if task is None else '|'.join(sorted(task['pstar'])),'base_hash':'' if task is None else task['base_hash']})
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
