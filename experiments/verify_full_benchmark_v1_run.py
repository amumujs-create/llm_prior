#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"results"/"full_benchmark_v1"/"run"
ACTIONS={"abstain","true-subset","true-full","biased-specific","mixed-true-false","fully-wrong"};ENGINES={"spline","neural"}
def sha(p):h=hashlib.sha256();h.update(p.read_bytes());return h.hexdigest()
def main():
 rows=list(csv.DictReader((OUT/"task_candidate_engine.csv").open())); errors=[]
 def need(v,m):
  if not v:errors.append(m)
 need(len(rows)==40500,"record count");need(len({r['task_id'] for r in rows})==3375,"task count")
 groups=defaultdict(list)
 for r in rows:groups[(r['task_id'],r['engine'])].append(r)
 need(len(groups)==6750,"task-engine groups")
 for k,z in groups.items():
  need(len(z)==6 and {r['action'] for r in z}==ACTIONS,"action pairing")
  need(len({r['baseline_rmse'] for r in z})==1,"baseline consistency")
  a=next(r for r in z if r['action']=='abstain');need(abs(float(a['utility']))<1e-12,"abstain utility")
 for r in rows:
  for f in ("sharpness","baseline_rmse","prior_rmse","utility","normalized_utility","ess"):
   need(math.isfinite(float(r[f])),f"nonfinite {f}")
  need(int(r['solver_failure'])==0,"solver failure")
 for a,c in (("true-subset",1),("true-full",1),("biased-specific",0),("mixed-true-false",0),("fully-wrong",0)):
  z=[r for r in rows if r['action']==a and r['null_type']=='none'];need(set(float(r['coverage']) for r in z)=={float(c)},f"coverage {a}")
 result={"passed":not errors,"n_records":len(rows),"n_tasks":len({r['task_id'] for r in rows}),"errors":sorted(set(errors)),
  "output_sha256":sha(OUT/"task_candidate_engine.csv"),"diagnostics_sha256":sha(OUT/"task_diagnostics.csv")}
 (OUT/"verification.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
if __name__=='__main__':main()
