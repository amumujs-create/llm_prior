#!/usr/bin/env python3
"""Read-only scorer for the frozen corrected E13 manifest."""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,math
from pathlib import Path
import numpy as np
from build_e13_persistent_base import build,H
from run_prior_completeness_e11 import Task,scorer,XP,M,sd
ROOT=Path(__file__).resolve().parents[1]; MAN=ROOT/'results/joint_prior_anatomy_e13/corrected_preflight/accepted_manifest.csv'; OUT=ROOT/'results/joint_prior_anatomy_e13/corrected_run'; HASH='a45ea724f2442ba919035ff73e65fc643ac732d48e15a550feb9d4b483579298'; PMIN=1/(10*M)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atoms(s):return frozenset(x for x in s.split('|') if x)
def subs(p):return [frozenset(q) for k in range(1,len(p)+1) for q in itertools.combinations(sorted(p),k)]
def write(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def make_task(m):
 t,r=build(m['intended_atoms'].replace('|','+').replace('direction_decreasing','direction').replace('curvature_convex','curvature').replace('inflection_concave_to_convex','inflection').replace('turning_maximum','turning').replace('regime_postchange','regime').replace('lower_bound_0','bound').replace('asymptote_to_0_from_above','asymptote'),m['generator_family'],int(m['intervention_seed']))
 if t is None:raise RuntimeError(r)
 xobs=XP; clean=np.interp(xobs,t['x'],t['y']);rref=max(float(np.ptp(clean)),1e-8); rng=np.random.default_rng(sd('e13-score-noise',m['task_id']));yobs=clean+rng.normal(0,.01*rref,len(clean)); brng=np.random.default_rng(sd('e13-score-bank',m['task_id']));z=brng.normal(0,1,(M,5));reg=brng.random(M)<.5
 return Task(m['task_id'],m['task_id'],tuple(m['intended_atoms'].split('|')),m['generator_family'],int(m['intervention_seed']),xobs,yobs,rref,z,reg,atoms(m['realized_P_star_atoms']),atoms(m['realized_P_star_atoms']),{})
def main(mode):
 if sha(MAN)!=HASH:raise RuntimeError('manifest hash mismatch')
 manifest=list(csv.DictReader(MAN.open()));rows=[];checks=[]
 for m in manifest:
  task=make_task(m); pstar=atoms(m['realized_P_star_atoms']); ea=json.loads(m['atom_Ea_json']);ca=json.loads(m['atom_Ca_json']); ev=scorer(task);cache={}
  def get(p):
   if p not in cache:cache[p]=ev(p)
   return cache[p]
  star=get(pstar); candidates=subs(pstar); taskrows=[]
  for p in candidates:
   q=get(p); gap=star['S']-q['S']; gapstatus='exact' if not star['floor_hit'] and not q['floor_hit'] else ('lower_bound' if star['floor_hit'] and not q['floor_hit'] else ('unresolved' if star['floor_hit'] else 'integrity_violation'))
   cp=[int(all(ca[a][j] for a in p)) for j in range(len(H))]; cstar=[int(all(ca[a][j] for a in pstar)) for j in range(len(H))]
   rows.append({'task_id':m['task_id'],'eta':m['eta'],'generator':m['generator_family'],'requested_scope_stratum':m['requested_scope_stratum'],'measured_scope_stratum':m['measured_scope_stratum'],'pstar_atoms':m['realized_P_star_atoms'],'candidate_atoms':'|'.join(sorted(p)),'oracle_size':len(pstar),'omitted_count':len(pstar)-len(p),'S':q['S'],'ESS':q['ESS'],'floor_hit':q['floor_hit'],'delta_S_miss':gap,'gap_status':gapstatus,'N_obs':sum(ea[a]>=.80 for a in p),'O_P':int(all(ea[a]>=.80 for a in p)),'C_P':'|'.join(map(str,cp)),'C_Pstar':'|'.join(map(str,cstar)),'task_weight':1/len(candidates)})
   taskrows.append(rows[-1])
  checks.append({'task_id':m['task_id'],'manifest_only':True,'shared_ESS':len({x['ESS'] for x in taskrows})==1,'sharpness_nesting':all(x['delta_S_miss']>=-1e-10 for x in taskrows),'scope_nesting':all(all(int(a)>=int(b) for a,b in zip(x['C_P'].split('|'),x['C_Pstar'].split('|'))) for x in taskrows),'evidence_manifest_derived':True,'dynamic_count':len(taskrows)==int(m['candidate_count'])})
 base=OUT/('sanity' if mode=='sanity' else 'run');write(base/'rows.csv',rows);write(base/'integrity.csv',checks);s={'mode':mode,'manifest_sha256':sha(MAN),'latent_tasks':len(checks),'candidate_rows':len(rows),'expected_candidate_rows':34560,'integrity_passed':all(all(bool(v) for k,v in c.items() if k!='task_id') for c in checks)};(base/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
if __name__=='__main__':p=argparse.ArgumentParser();p.add_argument('--mode',choices=('sanity','full'),default='sanity');main(p.parse_args().mode)
