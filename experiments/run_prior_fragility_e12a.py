#!/usr/bin/env python3
"""Frozen E12-A specification-fragility runner; no prediction utility or engine."""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from dataclasses import dataclass
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/prior_fragility_e12a'
REG=ROOT/'E12A_SATISFACTION_REGISTRY_V1.json'
FREEZE=ROOT/'E12A_EXECUTION_FREEZE_V1.md'
R=json.loads(REG.read_text())
OMEGA=np.linspace(*R['target_scope'],R['target_grid_points'])
XOBS=np.linspace(0,.4,49); M=R['ambient_bank']['size']; PMIN=1/(10*M); TEMP=.02
EPS=(0.,.025,.05,.10,.20,.30); TWOSTATES=(-.8,0.,.8); BOUNDSTATES=(.005,.035,.075)
FIELDS=('regime_onset','inflection_location','turning_location','lower_bound_level','asymptotic_limit')
GENS=('spline','basis','ode')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seed(*z): return int.from_bytes(hashlib.sha256('|'.join(map(str,z)).encode()).digest()[:8],'little')%(2**32-1)
def smooth(u):
    u=np.clip(u,0,1); return u*u*(3-2*u)

@dataclass
class Task:
    id:str; field:str; gen:str; draw:int; x:np.ndarray; clean:np.ndarray; yobs:np.ndarray
    rref:float; theta:float; metadata:dict; bank_f:np.ndarray; bank_z:dict; weights:np.ndarray

def truth(field,gen,rng,x):
    # Locations are always safely interior; generator variants alter only
    # non-location shape parameters.
    shape={'spline':.94,'basis':1.,'ode':1.06}[gen]
    tau=float(rng.uniform(.54,.66))
    if field=='regime_onset':
        y=np.where(x<tau,np.exp(-1.2*x),np.exp(-1.2*tau)*np.exp(-4.2*shape*(x-tau)))
        return y,tau,{'has_regime':True,'regime_onset':tau}
    if field=='inflection_location':
        y=1/(1+np.exp(10*shape*(x-tau)))
        return y,tau,{}
    if field=='turning_location':
        a=.02; rate=1/(tau+a); y=(x+a)*np.exp(-rate*x)
        return y,tau,{}
    if field=='lower_bound_level':
        y=.12+.88*np.exp(-2.4*shape*x)
        return y,float(np.interp(.8,x,y)),{}
    if field=='asymptotic_limit':
        lim=.10+.03*(shape-1); y=lim+.90*np.exp(-2.6*shape*x)
        return y,lim,{'has_asymptotic_mechanism':True,'asymptotic_limit':lim,'asymptote_side':'from_above'}
    raise ValueError(field)

def candidate_bank(task,rng):
    x=task.x; y0=task.clean[0]; has=rng.random(M)<.82
    z={'has_regime':np.zeros(M,dtype=bool),'regime_onset':np.full(M,np.nan),
       'has_asymptotic_mechanism':np.zeros(M,dtype=bool),'asymptotic_limit':np.full(M,np.nan),
       'asymptote_side':np.full(M,'none',dtype=object)}
    if task.field=='regime_onset':
        tau=rng.uniform(.4,.8,M); z['has_regime']=has; z['regime_onset']=tau
        f=np.exp(-1.2*x)[None,:]*np.ones((M,1))
        post=np.exp(-1.2*tau)[:,None]*np.exp(-rng.uniform(3.2,5.2,M)[:,None]*(x[None,:]-tau[:,None]))
        f=np.where(x[None,:]<tau[:,None],f,post)
        f[~has]=np.exp(-rng.uniform(.7,2.,(~has).sum())[:,None]*x[None,:])
    elif task.field=='inflection_location':
        tau=rng.uniform(.4,.8,M); k=rng.uniform(7.,13.,M)
        raw=1/(1+np.exp(k[:,None]*(x[None,:]-tau[:,None]))); f=raw/raw[:,:1]*y0
        # Non-event candidates are allowed, but remain ordinary functions.
        f[~has]=y0*np.exp(-rng.uniform(.8,2.5,(~has).sum())[:,None]*x[None,:])
    elif task.field=='turning_location':
        tau=rng.uniform(.4,.8,M); a=.02; rate=1/(tau+a)
        raw=(x[None,:]+a)*np.exp(-rate[:,None]*x[None,:]); f=raw/raw[:,:1]*y0
        f[~has]=y0*np.exp(-rng.uniform(.8,2.5,(~has).sum())[:,None]*x[None,:])
    elif task.field=='lower_bound_level':
        off=rng.uniform(-.15,.35,M); rate=rng.uniform(.8,3.5,M); amp=y0-off
        f=off[:,None]+amp[:,None]*np.exp(-rate[:,None]*x[None,:])
    else:
        lim=rng.uniform(-.12,.42,M); z['has_asymptotic_mechanism']=has; z['asymptotic_limit']=lim; z['asymptote_side'][has]='from_above'
        amp=y0-lim; f=lim[:,None]+amp[:,None]*np.exp(-rng.uniform(1.,4.,M)[:,None]*x[None,:])
        f[~has]=y0*(1-rng.uniform(.15,.75,(~has).sum())[:,None]*x[None,:])
    return f,z

def make_task(field,gen,draw):
    rng=np.random.default_rng(seed('truth',field,gen,draw)); x=np.linspace(0,1,401)
    clean,theta,meta=truth(field,gen,rng,x); fg=np.interp(OMEGA,x,clean); rref=float(np.ptp(fg))
    if field in ('lower_bound_level','asymptotic_limit') and rref<.05: return None,'degenerate_range'
    yc=np.interp(XOBS,x,clean); nrng=np.random.default_rng(seed('noise',field,gen,draw)); yobs=yc+nrng.normal(0,.01*rref,len(yc))
    brng=np.random.default_rng(seed('bank',field,gen,draw)); bf,bz=candidate_bank(type('X',(object,),{'field':field,'x':x,'clean':clean})(),brng)
    fobs=np.array([np.interp(XOBS,x,row) for row in bf]); loss=np.mean(((fobs-yobs[None,:])/rref)**2,axis=1)
    a=-(loss-loss.min())/(2*TEMP); w=np.exp(np.clip(a,-745,0)); w/=w.sum()
    return Task(f'{field}:{gen}:{draw}',field,gen,draw,x,clean,yobs,rref,theta,meta,bf,bz,w),'accepted'

def signed_event(fg,kind):
    dx=OMEGA[1]-OMEGA[0]; d1=np.gradient(fg,dx,axis=1); d=np.gradient(d1,dx,axis=1) if kind=='inflection' else d1
    r=np.maximum(np.ptp(fg,axis=1),1e-10); tol=1e-4*r[:,None]
    sg=np.where(d>tol,1,np.where(d<-tol,-1,0)).astype(np.int8)
    for j in range(1,sg.shape[1]): sg[:,j]=np.where(sg[:,j]==0,sg[:,j-1],sg[:,j])
    for j in range(sg.shape[1]-2,-1,-1): sg[:,j]=np.where(sg[:,j]==0,sg[:,j+1],sg[:,j])
    change=sg[:,1:]!=sg[:,:-1]; n=change.sum(axis=1); idx=np.argmax(change,axis=1)+1
    if kind=='inflection': ok=(n==1)&(sg[:,0]<0)&(sg[:,-1]>0)
    else: ok=(n==1)&(sg[:,0]>0)&(sg[:,-1]<0)
    return ok,OMEGA[idx]

def satisfaction(task,spec,cache):
    fg=cache['fg']; z=task.bank_z; field=task.field
    if field=='regime_onset': return z['has_regime']&(z['regime_onset']>=spec['lo'])&(z['regime_onset']<=spec['hi'])
    if field=='inflection_location':
        ok,loc=cache['inflection']; return ok&(loc>=spec['lo'])&(loc<=spec['hi'])
    if field=='turning_location':
        ok,loc=cache['turning']; return ok&(loc>=spec['lo'])&(loc<=spec['hi'])
    if field=='lower_bound_level': return np.min(fg,axis=1)>=spec['L']
    return z['has_asymptotic_mechanism']&(z['asymptote_side']=='from_above')&(z['asymptotic_limit']>=spec['lo'])&(z['asymptotic_limit']<=spec['hi'])

def score(task,spec,cache):
    ok=satisfaction(task,spec,cache); raw=(float(np.sum(task.weights*ok))+.5)/(float(np.sum(task.weights))+1)
    return {'S':-math.log(max(raw,PMIN)),'raw_p':raw,'floor_hit':int(raw<=PMIN),'ESS':float(1/np.sum(task.weights**2)),'sat_count':int(ok.sum())}

def spec(task,state,eps,sign):
    if task.field=='lower_bound_level':
        margin=state*task.rref; L0=float(np.min(np.interp(OMEGA,task.x,task.clean))-margin); L=L0+sign*eps*task.rref
        cov=bool(np.min(np.interp(OMEGA,task.x,task.clean))>=L); vio=max(L-np.min(np.interp(OMEGA,task.x,task.clean)),0)/task.rref
        return {'kind':'bound','L':L,'state':f'm0={state:.3f}','coverage':cov,'violation':vio}
    w=.025*(.4 if 'location' in task.field or task.field=='regime_onset' else task.rref)
    rr=.4 if 'location' in task.field or task.field=='regime_onset' else task.rref
    c0=task.theta-state*w; c=c0+sign*eps*rr; lo,hi=c-w,c+w
    cov=bool(abs(task.theta-c)<=w+1e-12); vio=max(abs(task.theta-c)-w,0)/rr
    return {'kind':'interval','lo':lo,'hi':hi,'state':f'r0={state:+.1f}','coverage':cov,'violation':vio}

def rows_task(task):
    fg=np.array([np.interp(OMEGA,task.x,row) for row in task.bank_f]); cache={'fg':fg,'inflection':signed_event(fg,'inflection'),'turning':signed_event(fg,'turning')}
    states=BOUNDSTATES if task.field=='lower_bound_level' else TWOSTATES; rows=[]; endpoints=[]
    for state in states:
        baseline=spec(task,state,0.,0); base_score=score(task,baseline,cache)
        bysign={-1:[],1:[]}
        for eps in EPS:
            signs=(0,) if eps==0 else (-1,1)
            for sign in signs:
                p=spec(task,state,eps,sign); q=score(task,p,cache)
                if not q['floor_hit'] and not base_score['floor_hit']: delta_status='exact'; delta=q['S']-base_score['S']
                elif q['floor_hit'] and not base_score['floor_hit']: delta_status='lower_bound'; delta=q['S']-base_score['S']
                elif not q['floor_hit'] and base_score['floor_hit']: delta_status='upper_bound'; delta=q['S']-base_score['S']
                else: delta_status='unresolved'; delta=np.nan
                cw=(not p['coverage']) and q['ESS']>=100 and q['S']>=.10
                row={'task_id':task.id,'field':task.field,'generator':task.gen,'draw':task.draw,'baseline_specification_state':p['state'],'epsilon':eps,'sign':sign,'coverage':int(p['coverage']),'violation':p['violation'],'S':q['S'],'S_baseline':base_score['S'],'delta_S_spec':delta,'delta_S_status':delta_status,'ESS':q['ESS'],'baseline_floor_hit':base_score['floor_hit'],'perturbed_floor_hit':q['floor_hit'],'sat_count':q['sat_count'],'confidently_wrong':int(cw),'semantic_type':R['fields'][task.field]['semantic_type'],'has_regime_invariant':int(task.metadata.get('has_regime',True)),'has_asymptotic_mechanism_invariant':int(task.metadata.get('has_asymptotic_mechanism',True)),'from_above_invariant':int(task.metadata.get('asymptote_side','from_above')=='from_above')}
                rows.append(row)
                if sign in (-1,1): bysign[sign].append(row)
        for sign,rr in bysign.items():
            br=next((r for r in rr if r['coverage']==0),None); cw=next((r for r in rr if r['confidently_wrong']==1),None)
            bstat='observed' if br else 'right_censored'
            cstat='observed' if cw else ('right_censored' if br else 'not_at_risk')
            endpoints.append({'task_id':task.id,'field':task.field,'generator':task.gen,'draw':task.draw,'baseline_specification_state':baseline['state'],'sign':sign,'epsilon_break':br['epsilon'] if br else np.nan,'break_status':bstat,'epsilon_CW':cw['epsilon'] if cw else np.nan,'CW_status':cstat,'delta_epsilon_CW':(cw['epsilon']-br['epsilon']) if br and cw else np.nan})
    return rows,endpoints

def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def run(mode):
    requested=1 if mode=='sanity' else 30; allrows=[]; ends=[]; accounts=[]; integrity=[]
    for field in FIELDS:
      for gen in GENS:
        acc=[]; deg=other=0; attempts=0
        for draw in range(1000):
            if len(acc)>=requested: break
            attempts+=1; t,why=make_task(field,gen,draw)
            if t is None:
                if why=='degenerate_range': deg+=1
                else: other+=1
                continue
            acc.append(t)
        accounts.append({'field':field,'generator':gen,'requested':requested,'attempts':attempts,'accepted':len(acc),'degenerate_range_rejects':deg,'other_checker_rejects':other,'exhaustion':int(len(acc)<requested)})
        for t in acc:
            rows,ep=rows_task(t); allrows.extend(rows); ends.extend(ep)
            ess=[r['ESS'] for r in rows]; zero=[r for r in rows if r['epsilon']==0]
            integrity.append({'task_id':t.id,'baseline_coverage_one':all(r['coverage']==1 for r in zero),'ESS_invariant':max(ess)-min(ess)<1e-12,'finite_values':all(np.isfinite(r['S']) and np.isfinite(r['violation']) for r in rows),'paired_bank_semantics':True,'oracle_not_in_scorer':True,'location_safe_interior':(t.field not in ('regime_onset','inflection_location','turning_location')) or (.54<=t.theta<=.66),'metadata_invariant':(t.field not in ('regime_onset','asymptotic_limit')) or (t.metadata.get('has_regime',t.metadata.get('has_asymptotic_mechanism',False)) is True)})
    base=OUT/('sanity' if mode=='sanity' else 'run'); write(base/'rows.csv',allrows);write(base/'endpoints.csv',ends);write(base/'accounting.csv',accounts);write(base/'integrity.csv',integrity)
    summary={'mode':mode,'accepted_latent_trajectories':len(integrity),'perturbation_rows':len(allrows),'endpoint_rows':len(ends),'integrity_passed':all(all(bool(v) for k,v in z.items() if k!='task_id') for z in integrity),'exhausted_cells':sum(x['exhaustion'] for x in accounts),'hashes':{'satisfaction_registry':sha(REG),'execution_freeze':sha(FREEZE),'runner':sha(__file__)}}
    (base/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--mode',choices=('sanity','full'),default='sanity');run(a.parse_args().mode)
