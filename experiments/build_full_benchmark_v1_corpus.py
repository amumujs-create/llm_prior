#!/usr/bin/env python3
"""Build the immutable metadata corpus for full benchmark v1.

This script does not calculate outcomes. It freezes task identity, composition,
data conditions, generator assignment, candidate balance, and OOD views.
"""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.stats import qmc

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"full_benchmark_v1"/"corpus"
PRIMITIVES=("direction","curvature","inflection","turning","regime","bound","asymptote")
SINGLES=tuple((p,) for p in PRIMITIVES)
PAIRS=(
 ("direction","curvature"),("direction","inflection"),("direction","bound"),("direction","asymptote"),
 ("curvature","bound"),("curvature","asymptote"),("inflection","turning"),("inflection","bound"),
 ("inflection","asymptote"),("turning","bound"),("regime","bound"),("bound","asymptote"),
)
TRIPLES=(
 ("direction","curvature","bound"),("direction","curvature","asymptote"),
 ("direction","inflection","bound"),("direction","inflection","asymptote"),
 ("curvature","bound","asymptote"),("inflection","bound","asymptote"),
 ("turning","bound","asymptote"),("regime","bound","asymptote"),
)
COMPOSITIONS=SINGLES+PAIRS+TRIPLES
CANDIDATES=("abstain","true-subset","true-full","biased-specific","mixed-true-false","fully-wrong")

def canon(comp): return "+".join(comp)
def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()
def logmap(u,lo,hi): return math.exp(math.log(lo)+u*(math.log(hi)-math.log(lo)))
def band(u):
    if u<.10 or u>=.90: return "tail"
    if .20<=u<.80: return "central"
    return "guard"

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # Hash ordering defines the held-out composition view; four of 20 multi-label cells.
    multi=sorted(PAIRS+TRIPLES,key=lambda c:hashlib.sha256(canon(c).encode()).hexdigest())
    held=set(multi[-4:])
    registry=[]
    for i,c in enumerate(COMPOSITIONS):
        registry.append({"cell_id":f"cell_{i:02d}","composition":canon(c),"size":len(c),
                         "heldout_composition":c in held,"contains_heldout_primitive":"inflection" in c,
                         "registration_status":"pre-registered; constructor validation required" if len(c)==3 else "registered"})
    (OUT/"composition_registry.json").write_text(json.dumps(registry,indent=2)+"\n")

    n=3375; lhs=qmc.LatinHypercube(d=7,seed=42000).random(n)
    rows=[]; task_index=0
    generators=("spline","basis","ode")
    for ci,c in enumerate(COMPOSITIONS):
        local=[]
        for j in range(100):
            gen=generators[(j+ci)%3]
            local.append((j,gen))
        rng=np.random.default_rng(42001+ci%5); rng.shuffle(local)
        for j,gen in local:
            u=lhs[task_index]; seed=42001+(j//20)
            bands=[band(x) for x in u]
            rows.append({"task_id":f"v1_{task_index:04d}","cell_id":f"cell_{ci:02d}","composition":canon(c),
              "composition_size":len(c),"null_type":"none","generator":gen,"seed_block":seed,"within_cell":j,
              "support_fraction":.35+.35*u[0],"sample_count":int(round(logmap(u[1],24,120))),
              "noise_ratio":logmap(u[2],.001,.05),"exposure":.90*u[3],"ood_distance":logmap(u[4],.05,1),
              "heterogeneity_cv":.25*u[5],"effect_strength":logmap(u[6],.05,1),
              "parameter_bands":"|".join(bands),"parameter_joint_view":"train" if all(b=="central" for b in bands) else ("test" if any(b=="tail" for b in bands) else "guard"),
              "heldout_composition":int(c in held),"heldout_primitive":int("inflection" in c),"heldout_generator":int(gen=="ode"),
              "candidate_actions":"|".join(CANDIDATES)})
            task_index+=1
    # Null split is deterministic and balanced to one task: 338 structural, 337 informational.
    for k in range(675):
        u=lhs[task_index]; gen=generators[k%3]; bands=[band(x) for x in u]
        nt="structural" if k<338 else "informational"
        rows.append({"task_id":f"v1_{task_index:04d}","cell_id":"null","composition":"null","composition_size":0,
          "null_type":nt,"generator":gen,"seed_block":42001+(k%5),"within_cell":k,
          "support_fraction":.35+.35*u[0],"sample_count":int(round(logmap(u[1],24,120))),
          "noise_ratio":logmap(u[2],.001,.05),"exposure":.90*u[3],"ood_distance":logmap(u[4],.05,1),
          "heterogeneity_cv":.25*u[5],"effect_strength":logmap(u[6],.05,1),
          "parameter_bands":"|".join(bands),"parameter_joint_view":"train" if all(b=="central" for b in bands) else ("test" if any(b=="tail" for b in bands) else "guard"),
          "heldout_composition":0,"heldout_primitive":0,"heldout_generator":int(gen=="ode"),
          "candidate_actions":"|".join(CANDIDATES)})
        task_index+=1
    assert task_index==3375 and len(rows)==3375
    with (OUT/"task_manifest.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,rows[0].keys()); w.writeheader(); w.writerows(rows)
    summary={"n_total":len(rows),"n_nonnull":2700,"n_null":675,"null_counts":{"structural":338,"informational":337},
      "composition_counts":{"single":7,"pair":12,"triple":8},"candidate_actions":CANDIDATES,
      "generators":{g:sum(r["generator"]==g for r in rows) for g in generators},
      "heldout_compositions":[canon(c) for c in held],"lhs_seed":42000,
      "manifest_sha256":sha(OUT/"task_manifest.csv"),"registry_sha256":sha(OUT/"composition_registry.json")}
    (OUT/"corpus_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
