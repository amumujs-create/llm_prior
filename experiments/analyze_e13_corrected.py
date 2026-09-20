#!/usr/bin/env python3
"""Predeclared descriptive analysis for frozen corrected E13 outputs."""
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; IN=ROOT/'results/joint_prior_anatomy_e13/corrected_run/run'; OUT=ROOT/'results/joint_prior_anatomy_e13/corrected_analysis'
def read(p):
 with p.open() as f:return list(csv.DictReader(f))
def write(name,rows):
 OUT.mkdir(parents=True,exist_ok=True)
 with (OUT/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def mean(x):return sum(x)/len(x) if x else None
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
 summary={'rows':len(r),'reliable_rate':mean([x['reliable'] for x in r]),'observable_rate':mean([x['observable'] for x in r]),'states':{x['state']:x['count'] for x in states},'completeness':comp[0]}
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
