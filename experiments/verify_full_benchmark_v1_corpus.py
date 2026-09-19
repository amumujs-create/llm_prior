#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"full_benchmark_v1"/"corpus"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rows=list(csv.DictReader((OUT/"task_manifest.csv").open()))
    reg=json.loads((OUT/"composition_registry.json").read_text())
    errors=[]
    def need(x,msg):
        if not x: errors.append(msg)
    need(len(rows)==3375,"total")
    need(len({r['task_id'] for r in rows})==3375,"unique ids")
    non=[r for r in rows if r['null_type']=='none']; null=[r for r in rows if r['null_type']!='none']
    need(len(non)==2700 and len(null)==675,"nonnull/null")
    counts=Counter(r['cell_id'] for r in non); need(len(counts)==27 and set(counts.values())=={100},"cell balance")
    need(Counter(r['null_type'] for r in null)==Counter({'structural':338,'informational':337}),"null split")
    need(Counter(r['generator'] for r in rows)==Counter({'spline':1125,'basis':1125,'ode':1125}),"generator balance")
    need(len(reg)==27 and Counter(r['size'] for r in reg)==Counter({1:7,2:12,3:8}),"registry sizes")
    for r in rows:
        need(.35<=float(r['support_fraction'])<=.70,"support range")
        need(24<=int(r['sample_count'])<=120,"sample range")
        need(.001<=float(r['noise_ratio'])<=.05,"noise range")
        need(0<=float(r['exposure'])<=.90,"exposure range")
        need(.05<=float(r['ood_distance'])<=1,"distance range")
        need(0<=float(r['heterogeneity_cv'])<=.25,"heterogeneity range")
        need(.05<=float(r['effect_strength'])<=1,"effect range")
    summary=json.loads((OUT/"corpus_summary.json").read_text())
    need(summary['manifest_sha256']==sha(OUT/"task_manifest.csv"),"manifest hash")
    need(summary['registry_sha256']==sha(OUT/"composition_registry.json"),"registry hash")
    result={"passed":not errors,"n_errors":len(errors),"errors":sorted(set(errors)),
            "manifest_sha256":sha(OUT/"task_manifest.csv"),"registry_sha256":sha(OUT/"composition_registry.json")}
    (OUT/"verification.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2)); raise SystemExit(0 if result['passed'] else 1)
if __name__=='__main__': main()
