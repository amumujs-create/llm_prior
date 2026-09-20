#!/usr/bin/env python3
"""Predeclared descriptive analysis for frozen corrected E13 outputs."""
from __future__ import annotations
import csv,json,random
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; IN=ROOT/'results/joint_prior_anatomy_e13/corrected_run/run'; OUT=ROOT/'results/joint_prior_anatomy_e13/corrected_analysis'
def read(p):
 with p.open() as f:return list(csv.DictReader(f))
def write(name,rows):
 OUT.mkdir(parents=True,exist_ok=True)
 with (OUT/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def mean(x):return sum(x)/len(x) if x else None
def atoms(s):return frozenset(x for x in s.split('|') if x)
def q50(x):return sorted(x)[len(x)//2] if x else None
def boot_rate(rows, key, n=1000):
 by=defaultdict(list)
 for r in rows:by[r['task_id']].append(r)
 ids=list(by); vals=[]; rng=random.Random(20260920)
 for _ in range(n):
  sample=[r for _id in [rng.choice(ids) for _ in ids] for r in by[_id]]
  vals.append(mean([key(r) for r in sample]))
 vals.sort();return vals[25],vals[974]
def main():
 r=read(IN/'rows.csv');
 for x in r:
  x['reliable']=float(x['ESS'])>=100; x['informative']=float(x['S'])>=.10; x['observable']=x['O_P']=='1';x['incomplete']=int(x['omitted_count'])>0;x['exact']=x['gap_status']=='exact';x['info_complete']=x['incomplete'] and x['reliable'] and x['exact'] and float(x['delta_S_miss'])<=.10
 # Reliability audit by predeclared fine strata.
 groups=defaultdict(list)
 for x in r:groups[(x['oracle_size'],x['omitted_count'],x['eta'],x['measured_scope_stratum'],x['generator'])].append(x)
 audit=[]
 for k,v in groups.items():audit.append({'oracle_size':k[0],'omitted_count':k[1],'eta':k[2],'scope':k[3],'generator':k[4],'n':len(v),'reliable_rate':mean([z['reliable'] for z in v]),'floor_rate':mean([int(z['floor_hit']) for z in v])})
 write('reliability_by_stratum.csv',audit)
 # Joint states with explicit denominators.
 state_defs={'informative_unobservable':lambda x:x['reliable'] and x['informative'] and not x['observable'],'atom_incomplete_info_complete':lambda x:x['info_complete'],'informative_limited_scope':lambda x:x['reliable'] and x['informative'] and x['C_P'].split('|')[1]=='0','weak_persistent':lambda x:x['reliable'] and not x['informative'] and x['C_P'].split('|')[-1]=='1','observable_info_redundant':lambda x:x['incomplete'] and x['reliable'] and x['exact'] and x['observable'] and float(x['delta_S_miss'])<=.10}
 states=[]
 reliable=[x for x in r if x['reliable']]
 for n,f in state_defs.items():states.append({'state':n,'count':sum(f(x) for x in r),'all_rows':len(r),'reliable_denominator':len(reliable),'rate_all':mean([f(x) for x in r]),'rate_reliable':mean([f(x) for x in reliable])})
 states+= [{'state':'observable_any','count':sum(x['observable'] for x in r),'all_rows':len(r),'reliable_denominator':len(reliable),'rate_all':mean([x['observable'] for x in r]),'rate_reliable':mean([x['observable'] for x in reliable])}]
 write('joint_states.csv',states)
 # Scope profile and completeness audit.
 prof=[]
 for i,h in enumerate(('085','090','100','110','120')):
  prof.append({'horizon':'.'+h,'all_candidate_survival':mean([int(x['C_P'].split('|')[i]) for x in r]),'full_survival':mean([int(x['C_P'].split('|')[i]) for x in r if int(x['omitted_count'])==0])})
 write('scope_profile.csv',prof)
 inc=[x for x in r if x['incomplete'] and x['reliable']]; exact=[x for x in inc if x['exact']]
 comp=[{'incomplete_reliable_rows':len(inc),'exact_gap_rows':len(exact),'exact_gap_rate':len(exact)/len(inc) if inc else None,'info_complete_exact_rows':sum(float(x['delta_S_miss'])<=.10 for x in exact),'info_complete_rate_given_exact':mean([float(x['delta_S_miss'])<=.10 for x in exact])}]
 write('completeness_audit.csv',comp)
 # Omission decomposition: implied atom redundancy vs conditional redundancy.
 manifest={x['task_id']:x for x in read(ROOT/'results/joint_prior_anatomy_e13/corrected_preflight/accepted_manifest.csv')}
 dec=defaultdict(list)
 for x in exact:
  p=atoms(x['candidate_atoms']); star=atoms(x['pstar_atoms']); omitted=star-p; implied=atoms(manifest[x['task_id']]['realized_P_star_atoms'])-atoms(manifest[x['task_id']]['intended_atoms'])
  for a in omitted: dec[(a,int(a in implied),x['oracle_size'],x['omitted_count'])].append(float(x['delta_S_miss']))
 out=[]
 for k,v in dec.items():out.append({'omitted_atom':k[0],'is_implied_atom':k[1],'oracle_size':k[2],'omitted_count':k[3],'n':len(v),'mean_delta_S_miss':mean(v),'median_delta_S_miss':q50(v),'info_complete_rate':mean([z<=.10 for z in v])})
 write('completeness_by_omitted_atom.csv',out)
 # Mutually exclusive all-implied / mixed / no-implied omission classes.
 coarse=[]
 for klass in ('all_implied','mixed','no_implied'):
  rr=[]
  for x in exact:
   p=atoms(x['candidate_atoms']);star=atoms(x['pstar_atoms']); implied=atoms(manifest[x['task_id']]['realized_P_star_atoms'])-atoms(manifest[x['task_id']]['intended_atoms'])
   omitted=star-p; flags=[a in implied for a in omitted]
   if (klass=='all_implied' and all(flags)) or (klass=='no_implied' and not any(flags)) or (klass=='mixed' and any(flags) and not all(flags)):rr.append(x)
  lo,hi=boot_rate(rr,lambda z:float(z['delta_S_miss'])<=.10)
  vv=[float(z['delta_S_miss']) for z in rr];coarse.append({'omission_class':klass,'rows':len(rr),'latent_tasks':len({z['task_id'] for z in rr}),'mean_delta_S_miss':mean(vv),'median_delta_S_miss':q50(vv),'info_complete_rate':mean([z<=.10 for z in vv]),'cluster_bootstrap_95ci_low':lo,'cluster_bootstrap_95ci_high':hi})
 write('completeness_by_implied_status.csv',coarse)
 summary={'rows':len(r),'reliable_rate':mean([x['reliable'] for x in r]),'observable_rate':mean([x['observable'] for x in r]),'states':{x['state']:x['count'] for x in states},'completeness':comp[0],'association_boundary':'Observability associations are descriptive-only because O_P is degenerate in this corpus; primary empirical decomposition is omitted-atom delta_S_miss by scope profile.'}
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
