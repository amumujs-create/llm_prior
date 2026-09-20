#!/usr/bin/env python3
"""Quota preflight for E13's persistent-base, C2-intervention corpus."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
import numpy as np
from build_e13_persistent_base import H, INTENTS, GENS, build, contiguous_table

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results/joint_prior_anatomy_e13/corrected_preflight'
ETAS=('low','mid','high'); STRATA=('limited','intermediate','persistent_within_tested_domain'); QUOTA=10; MAX=2000
def smooth5(t):
 t=np.clip(t,0.,1.);return t**3*(10-15*t+6*t*t)
def hashv(y):return hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest()
def intervention(x,y,z,requested,seed):
 """Frozen C2 family. Proposal parameters are not passed to the oracle."""
 yi=y.copy(); zi=dict(z); params={'family':'c2_negative_level_excursion','seed':seed}
 if requested=='persistent_within_tested_domain':
  params.update({'onset':None,'width':None,'amplitude':0.});return yi,zi,params
 target=.85 if requested=='limited' else 1.10; onset=target-.04
 amp=float(np.interp(target,x,y)+.10); gate=smooth5((x-onset)/(target-onset)); yi-=amp*gate
 # This is generated semantic state, not a requested-label input to scoring.
 zi['asymptote_active_through']=target
 params.update({'onset':onset,'width':target-onset,'amplitude':amp});return yi,zi,params
def h_from(cont):
 full=[int(np.prod([cont[a][j] for a in cont])) for j in range(len(H))]
 if all(full):return '>1.20',True,full
 return (.80 if full[0]==0 else float(H[np.where(np.array(full)==0)[0][0]-1])),False,full
def label(h,c):
 if c:return 'persistent_within_tested_domain'
 if h<=.90:return 'limited'
 return 'intermediate' if h in (1.,1.1) else 'out_of_quota'
def write(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 rows=[];acct=[]
 for intent in INTENTS:
  for gen in GENS:
   for eta in ETAS:
    for requested in STRATA:
     accepted=attempts=mismatch=basefail=corechange=0
     for q in range(QUOTA):
      for attempt in range(MAX):
       attempts+=1;seed=int.from_bytes(hashlib.sha256(f'{intent}|{gen}|{eta}|{requested}|{q}|{attempt}'.encode()).digest()[:4],'little')
       task,reason=build(intent,gen,seed)
       if task is None:basefail+=1;continue
       y,z,params=intervention(task['x'],task['y'],task['z'],requested,seed)
       core=(task['x']<=.80)
       if not np.array_equal(task['y'][core],y[core]):corechange+=1;continue
       raw,cont=contiguous_table(task['x'],y,task['pstar'],z);hv,cens,cp=h_from(cont);measured=label(hv,cens)
       if measured!=requested:mismatch+=1;continue
       size=len(task['pstar']); rows.append({'task_id':f'{intent}:{gen}:{eta}:{requested}:{q}','generator_family':gen,'eta':eta,'intended_atoms':'|'.join(task['intent']),'realized_P_star_atoms':'|'.join(sorted(task['pstar'])),'P_star_size':size,'base_hash':task['base_hash'],'intervened_core_hash':hashv(y[core]),'core_equal':1,'intervention_family':params['family'],'intervention_seed':seed,'intervention_parameters':json.dumps(params,sort_keys=True),'requested_scope_stratum':requested,'measured_scope_stratum':measured,'atom_Va_json':json.dumps(raw,sort_keys=True),'atom_Ca_json':json.dumps(cont,sort_keys=True),'full_CP_star':'|'.join(map(str,cp)),'measured_H_valid':hv,'censored':int(cens),'candidate_count':2**size-1,'accepted_attempt':attempt+1,'acceptance':'accepted','rejection_reason':''});accepted+=1;break
     acct.append({'intent':intent,'generator':gen,'eta':eta,'requested_scope_stratum':requested,'requested':QUOTA,'accepted':accepted,'attempts':attempts,'requested_measured_scope_mismatch':mismatch,'base_not_persistent':basefail,'core_changed':corechange,'exhaustion':int(accepted!=QUOTA)})
 write(OUT/'accepted_manifest.csv',rows);write(OUT/'accounting.csv',acct)
 s={'protocol':'E13_scope_aware_preflight_v1','latent_tasks':len(rows),'expected_candidate_rows':sum(r['candidate_count'] for r in rows),'exhausted_cells':sum(r['exhaustion'] for r in acct),'manifest_sha256':hashlib.sha256((OUT/'accepted_manifest.csv').read_bytes()).hexdigest(),'accounting_sha256':hashlib.sha256((OUT/'accounting.csv').read_bytes()).hexdigest()}
 (OUT/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
if __name__=='__main__':main()
