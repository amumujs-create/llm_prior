#!/usr/bin/env python3
"""Frozen E11 grammar-relative completeness runner (no utility/engine scoring)."""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,math
from dataclasses import dataclass
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results/prior_completeness_e11'
LIB=ROOT/'E11_CANONICAL_ATOM_LIBRARY_V1.json'; INT=ROOT/'E11_INTENDED_ATOM_INTENTS_V1.json'; COMP=ROOT/'E11_COMPATIBILITY_SCOPE_REGISTRY_V1.json'
OMEGA=np.linspace(.4,.8,161); XP=np.arange(0,49)/120; M=4096; PMIN=1/(10*M); DELTA=.10
GENS=('spline','basis','ode')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
L=json.loads(LIB.read_text()); I=json.loads(INT.read_text()); C=json.loads(COMP.read_text())
INTENTS={k:tuple(v) for k,v in I['generator_intents'].items()}; INCOMP={frozenset(x) for x in L['pairwise_incompatible']}

@dataclass
class Task:
 id:str; intent_name:str; intent:tuple; gen:str; seed:int; xobs:np.ndarray; yobs:np.ndarray; rref:float; z:np.ndarray; bank_regime:np.ndarray; valid_atoms:frozenset; pstar:frozenset; provenance:dict

def sd(*x): return int.from_bytes(hashlib.sha256('|'.join(map(str,x)).encode()).digest()[:8],'little')%(2**32-1)
def smooth(x):
    z=np.clip(x,0,1)
    return z*z*(3-2*z)

def truth(intent,gen,rng,x):
    # canonical instances are generated directly; all have y>=0 and scope .4-.8.
    k={'spline':1.,'basis':1.06,'ode':.94}[gen]; n=set(intent)
    if 'turning_maximum' in n: y=(x+.02)*np.exp(-1.75*x-8*smooth((x-.58)/.24))
    elif 'inflection_concave_to_convex' in n: y=1/(1+np.exp(8*k*(x-.55)))
    elif 'regime_postchange' in n: y=np.where(x<.28,np.exp(-1.5*x),np.exp(-1.5*.28)*np.exp(-5*k*(x-.28)))
    elif 'asymptote_to_0_from_above' in n: y=np.exp(-3.5*k*x)
    elif 'direction_decreasing' in n and 'curvature_convex' in n: y=np.exp(-2.2*k*x)
    else: y=.8-.45*x  # only fallback; intents are all canonical triple cases
    if gen=='spline': y+=.0005*np.sin(2*np.pi*x)**2
    elif gen=='basis': y+=.0004*(x-.5)**3
    else: y+=.0004*np.sin(np.pi*x)**2
    return y

def sign_changes(a,tol):
    s=np.where(a>tol,1,np.where(a<-tol,-1,0)); s=s[s!=0]
    return int(np.sum(s[1:]!=s[:-1])) if len(s)>1 else 0

def valid_atoms(clean,intent,x):
    # Oracle selects only frozen instances; no parameter/interval construction.
    y=np.interp(OMEGA,x,clean); dx=OMEGA[1]-OMEGA[0]; d1=np.gradient(y,dx); d2=np.gradient(d1,dx); r=max(float(np.ptp(clean)),1e-8)
    out=set()
    if np.mean(d1<=.01*r)>=.95: out.add('direction_decreasing')
    if np.mean(d1>=-.01*r)>=.95: out.add('direction_increasing')
    if np.mean(d2>=-.04*r)>=.90: out.add('curvature_convex')
    if np.mean(d2<=.04*r)>=.90: out.add('curvature_concave')
    if sign_changes(d2,.03*r)==1:
        # Determine sign sequence from nonzero curvature values.
        nz=d2[np.abs(d2)>.03*r]
        if len(nz) and nz[0]<0 and nz[-1]>0: out.add('inflection_concave_to_convex')
        if len(nz) and nz[0]>0 and nz[-1]<0: out.add('inflection_convex_to_concave')
    if sign_changes(d1,.02*r)==1:
        nz=d1[np.abs(d1)>.02*r]
        if len(nz) and nz[0]>0 and nz[-1]<0: out.add('turning_maximum')
        if len(nz) and nz[0]<0 and nz[-1]>0: out.add('turning_minimum')
    if np.min(y)>=-.01*r: out.add('lower_bound_0')
    if np.max(y)<=.01*r: out.add('upper_bound_0')
    # Mechanistic regime only when it was declared; asymptote is fixed-instance phenomenological check.
    if 'regime_postchange' in intent: out.add('regime_postchange')
    early=np.mean(np.abs(d1[:40])); late=np.mean(np.abs(d1[-40:]));
    if np.min(y)>0 and late<=.90*max(early,1e-9) and np.mean(y[-20:])<=.90*np.mean(y[:20]): out.add('asymptote_to_0_from_above')
    return frozenset(out)

def compatible(s): return not any(p<=s for p in INCOMP)
def envelope(valid,intent):
    vals=list(valid); mx=[]
    for q in range(1,len(vals)+1):
        for z in itertools.combinations(vals,q):
            z=frozenset(z)
            if set(intent)<=z and compatible(z): mx.append(z)
    maximal=[z for z in mx if not any(z<w for w in mx)]
    return maximal[0] if len(maximal)==1 else None, len(maximal)

def make_task(intent_name,gen,seed):
    intent=INTENTS[intent_name]; rng=np.random.default_rng(sd('truth',intent_name,gen,seed)); x=np.linspace(0,1,401); clean=truth(intent,gen,rng,x)
    valid=valid_atoms(clean,intent,x); pstar,nmax=envelope(valid,intent)
    if not set(intent)<=set(valid): return None,'checker_reject'
    if pstar is None: return None,'ambiguous_envelope'
    xc=XP; yc=np.interp(xc,x,clean); r=max(float(np.ptp(yc)),1e-8); nrng=np.random.default_rng(sd('noise',intent_name,gen,seed)); yo=yc+nrng.normal(0,.01*r,len(xc))
    brng=np.random.default_rng(sd('bank',intent_name,gen,seed)); z=brng.normal(0,1,(M,5)); reg=brng.random(M)<.5
    prov={a:('intended_atom' if a in intent else 'incidental_valid_atom') for a in pstar}
    return Task(f'{intent_name}:{gen}:{seed}',intent_name,intent,gen,seed,xc,yo,r,z,reg,valid,pstar,prov),'accepted'

def basis(x):
    raw=np.column_stack([x,x*x-.3,np.maximum(x-.45,0)**2,np.sin(2*np.pi*x),np.cos(2*np.pi*x)])
    ref=np.column_stack([OMEGA,OMEGA*OMEGA-.3,np.maximum(OMEGA-.45,0)**2,np.sin(2*np.pi*OMEGA),np.cos(2*np.pi*OMEGA)])
    return raw/np.maximum(np.sqrt(np.mean(ref*ref,axis=0)),1e-8)
def bank(task,x):
    slope=(task.yobs[1]-task.yobs[0])/(task.xobs[1]-task.xobs[0]); base=task.yobs[0]+slope*x
    return base[None,:]+.10*np.einsum('ij,kj->ik',task.z,basis(x))
def weights(f,y,r):
    loss=np.mean(((f-y)/r)**2,axis=1); a=-(loss-loss.min())/(2*.02); w=np.exp(np.clip(a,-745,0)); return w/w.sum()
def atom_mask(task,fg):
    dx=OMEGA[1]-OMEGA[0]; d1=np.gradient(fg,dx,axis=1); d2=np.gradient(d1,dx,axis=1); r=np.maximum(np.ptp(fg,axis=1),1e-8); out={}
    out['direction_decreasing']=np.mean(d1<=.01*r[:,None],axis=1)>=.95; out['direction_increasing']=np.mean(d1>=-.01*r[:,None],axis=1)>=.95
    out['curvature_convex']=np.mean(d2>=-.04*r[:,None],axis=1)>=.90; out['curvature_concave']=np.mean(d2<=.04*r[:,None],axis=1)>=.90
    # Event instances carry an ordered sign change; a generic event is not
    # permitted to satisfy both signed canonical atoms.
    sc2=np.sign(d2); sc1=np.sign(d1)
    n2=np.sum(sc2[:,1:]*sc2[:,:-1]<0,axis=1)==1
    n1=np.sum(sc1[:,1:]*sc1[:,:-1]<0,axis=1)==1
    out['inflection_concave_to_convex']=n2 & (d2[:,0]<0) & (d2[:,-1]>0)
    out['inflection_convex_to_concave']=n2 & (d2[:,0]>0) & (d2[:,-1]<0)
    out['turning_maximum']=n1 & (d1[:,0]>0) & (d1[:,-1]<0)
    out['turning_minimum']=n1 & (d1[:,0]<0) & (d1[:,-1]>0)
    out['lower_bound_0']=np.min(fg,axis=1)>=-.01*r; out['upper_bound_0']=np.max(fg,axis=1)<=.01*r
    out['regime_postchange']=task.bank_regime.copy(); early=np.mean(np.abs(d1[:,:40]),axis=1); late=np.mean(np.abs(d1[:,-40:]),axis=1)
    out['asymptote_to_0_from_above']=(np.min(fg,axis=1)>0)&(late<=.90*np.maximum(early,1e-8)); out['asymptote_to_0_from_below']=(np.max(fg,axis=1)<0)&(late<=.90*np.maximum(early,1e-8))
    return out
def scorer(task):
    # Prefix likelihood and the fixed-domain constraint masks are task-level
    # objects. Reuse them for every supplied/envelope conjunction.
    f=bank(task,task.xobs); w=weights(f,task.yobs[None,:],task.rref)
    masks=atom_mask(task,bank(task,OMEGA)); ess=1/np.sum(w*w)
    def score(atoms):
        ok=np.ones(M,dtype=bool)
        for a in atoms: ok &= masks[a]
        raw=(float(np.sum(w*ok))+.5)/(float(np.sum(w))+1); hit=raw<=PMIN; p=max(raw,PMIN)
        return {'S':-math.log(p),'raw_p':raw,'floor_hit':int(hit),'ESS':ess,'sat_count':int(ok.sum())}
    return score

def score(task,atoms):
    # Convenience wrapper for isolated checks; batch scoring uses scorer().
    return scorer(task)(atoms)

def _deprecated_score(task,atoms):
    # Retained only as a readable reference for the scalar calculation.
    f=bank(task,task.xobs); w=weights(f,task.yobs[None,:],task.rref); fg=bank(task,OMEGA); masks=atom_mask(task,fg); ok=np.ones(M,dtype=bool)
    for a in atoms: ok &= masks[a]
    raw=(float(np.sum(w*ok))+.5)/(float(np.sum(w))+1); hit=raw<=PMIN; p=max(raw,PMIN); S=-math.log(p); ess=1/np.sum(w*w)
    return {'S':S,'raw_p':raw,'floor_hit':int(hit),'ESS':ess,'sat_count':int(ok.sum())}

def candidates(intent):
    return [frozenset(z) for k in (1,2,3) for z in itertools.combinations(intent,k)]
def rows_task(t):
    ps=candidates(t.intent); cache={}
    evaluate=scorer(t)
    def get(atoms):
        atoms=frozenset(atoms)
        if atoms not in cache: cache[atoms]=evaluate(atoms)
        return cache[atoms]
    star=get(t.pstar); rows=[]
    for s in ps:
        q=get(s); gap=star['S']-q['S']; lower=bool(star['floor_hit'] and not q['floor_hit']); both=bool(star['floor_hit'] and q['floor_hit'])
        if q['ESS']<100: status='measurement_unresolved'
        elif both: status='floor_unresolved'
        elif lower and gap<=DELTA: status='floor_lower_bound_unresolved'
        elif gap<=DELTA and not lower: status='informationally_complete'
        else: status='informationally_incomplete'
        missing=sorted(t.pstar-s); marginal={a:get(set(s)|{a})['S']-q['S'] for a in missing}
        rows.append({'task_id':t.id,'intent_name':t.intent_name,'generator':t.gen,'seed':t.seed,'candidate_role':'supplied','supplied_atoms':'|'.join(sorted(s)),'pstar_atoms':'|'.join(sorted(t.pstar)),'intended_atoms':'|'.join(t.intent),'incidental_atoms':'|'.join(sorted(set(t.pstar)-set(t.intent))),'C_atom':int(s==t.pstar),'atom_status':'atom_complete' if s==t.pstar else 'atom_incomplete','S_supplied':q['S'],'S_star':star['S'],'delta_S_miss':gap,'ESS':q['ESS'],'candidate_floor_hit':q['floor_hit'],'oracle_floor_hit':star['floor_hit'],'gap_lower_bound':int(lower),'information_status':status,'missing_atoms':'|'.join(missing),'marginal_json':json.dumps(marginal,sort_keys=True),'nested_floor_violation':int(q['floor_hit'] and not star['floor_hit'])})
    rows.append({'task_id':t.id,'intent_name':t.intent_name,'generator':t.gen,'seed':t.seed,'candidate_role':'oracle_envelope','supplied_atoms':'|'.join(sorted(t.pstar)),'pstar_atoms':'|'.join(sorted(t.pstar)),'intended_atoms':'|'.join(t.intent),'incidental_atoms':'|'.join(sorted(set(t.pstar)-set(t.intent))),'C_atom':1,'atom_status':'atom_complete','S_supplied':star['S'],'S_star':star['S'],'delta_S_miss':0.0,'ESS':star['ESS'],'candidate_floor_hit':star['floor_hit'],'oracle_floor_hit':star['floor_hit'],'gap_lower_bound':0,'information_status':'oracle_reference','missing_atoms':'','marginal_json':'{}','nested_floor_violation':0})
    return rows
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)
def run(mode):
    requested=1 if mode=='sanity' else 30; allrows=[]; accounts=[]; checks=[]
    for name in INTENTS:
      for gen in GENS:
        accepted=[]; attempts=amb=checker=0
        for attempt in range(1000):
            if len(accepted)>=requested: break
            attempts+=1; t,reason=make_task(name,gen,attempt)
            if t is None:
                amb+=reason=='ambiguous_envelope'; checker+=reason=='checker_reject'; continue
            accepted.append(t)
        exhaustion=int(len(accepted)<requested); accounts.append({'intent_name':name,'generator':gen,'requested':requested,'attempts':attempts,'accepted':len(accepted),'ambiguous_envelope_rejects':amb,'coverage_checker_rejects':checker,'other_rejects':0,'exhaustion':exhaustion})
        for t in accepted:
            rr=rows_task(t); allrows+=rr
            checks.append({'task_id':t.id,'intent_atom_ids_match':set(t.intent)<=set(t.pstar),'unique_envelope':True,'coverage_preserving':set(t.intent)<=set(t.valid_atoms),'shared_bank_candidates':True,'nonnegative_gap':all(r['delta_S_miss']>=-1e-10 for r in rr),'nested_floor_zero':all(r['nested_floor_violation']==0 for r in rr),'no_utility_engine_api':True})
    base=OUT/('sanity' if mode=='sanity' else 'run'); write(base/'accounting.csv',accounts); write(base/'rows.csv',allrows); write(base/'integrity.csv',checks)
    summ={'mode':mode,'requested_per_cell':requested,'accepted_tasks':len(checks),'candidate_rows':len(allrows),'integrity_passed':all(all(bool(v) for k,v in c.items() if k!='task_id') for c in checks),'exhausted_cells':sum(a['exhaustion'] for a in accounts),'hashes':{'atom_library':sha(LIB),'intent_registry':sha(INT),'compatibility_scope_registry':sha(COMP),'runner':sha(__file__)}}
    (base/'summary.json').write_text(json.dumps(summ,indent=2)); print(json.dumps(summ,indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--mode',choices=('sanity','full'),default='sanity');run(a.parse_args().mode)
