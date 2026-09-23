"""Outcome-free integrity sanity for frozen E15-C v1.1 implementation."""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import numpy as np

from e15c_confirmatory_core import (MANIFEST, MANIFEST_SHA, c_grid, free_prediction, invariant_base, invariant_predictions, load_manifest, make_tasks, profile_matched_free, q_grid, responses_for_c, weights, z_bases)


def main() -> None:
    manifest=load_manifest()
    raw=MANIFEST.read_bytes()
    qs=q_grid(manifest); cs=c_grid(manifest); bound=1.5
    x=np.linspace(0,1,81); z1,z3=z_bases(x,1.0); f1,f3=responses_for_c(x,-1.0)
    response_error=float(max(np.max(np.abs(z1-f1)),np.max(np.abs(z3-f3)),np.max(np.abs(invariant_base(x)-np.exp(-x)))))

    tasks=make_tasks(151599,10,manifest)
    x_forecast=np.linspace(.75,1,161); sigma=.1*manifest["scales"]["R_inv_value_under_manifest"]
    checks=[]
    for endpoint in (.25,.5,.75):
        observed=tasks["x"]<=endpoint+1e-12
        obs=tasks["clean"][:,observed]+sigma*tasks["master_noise"][:,observed]
        inv1=invariant_predictions(obs,tasks["x"][observed],x_forecast,qs,sigma,bound)
        inv2=invariant_predictions(obs,tasks["x"][observed],x_forecast,qs,sigma,bound)
        free1=free_prediction(obs,tasks["x"][observed],x_forecast,qs,cs,sigma,bound)
        free2=free_prediction(obs,tasks["x"][observed],x_forecast,qs,cs,sigma,bound)
        singleton=np.array([.4])
        one=invariant_predictions(obs,tasks["x"][observed],x_forecast,singleton,sigma,bound)
        singleton_error=float(max(
            np.max(np.abs(one["invariant_residual_MAP"]-one["invariant_residual_ensemble"])),
            np.max(np.abs(one["invariant_residual_MAP"]-one["evidence_weighted_residual_mixture"])),
        ))
        checks.append({"endpoint":endpoint,"invariant_replay_max_abs_error":float(np.max(np.abs(inv1["invariant_residual_MAP"]-inv2["invariant_residual_MAP"]))),"free_replay_max_abs_error":float(np.max(np.abs(free1-free2))),"singleton_equivalence_max_abs_error":singleton_error,"all_finite":bool(np.all(np.isfinite(free1)))})

    # Profile-bound audit uses deliberately extreme prefix values; no outcomes.
    y_extreme=np.full((2,21),1e6); a,_,_=profile_matched_free(y_extreme,np.linspace(0,.25,21),qs,cs,sigma,bound)
    source=inspect.getsource(invariant_predictions)+inspect.getsource(free_prediction)+inspect.getsource(profile_matched_free)
    result={
        "manifest_sha256":hashlib.sha256(raw).hexdigest(),
        "manifest_sha_assertion":hashlib.sha256(raw).hexdigest()==MANIFEST_SHA,
        "response_c_minus_k0_equivalence_max_abs_error":response_error,
        "matched_free_c_grid_contains_minus_k0":bool(np.any(np.isclose(cs,-1.0))),
        "matched_free_amplitude_bound_max_abs":float(np.max(np.abs(a))),
        "amplitude_bound":bound,
        "replay_and_singleton_checks":checks,
        "future_label_names_absent_from_prediction_functions":all(token not in source for token in ("q_true","truth","future_label","h_viol")),
        "policy_outcomes_inspected":False,
    }
    result["status"]="PASS" if (
        result["manifest_sha_assertion"] and response_error<=1e-12 and result["matched_free_c_grid_contains_minus_k0"] and result["matched_free_amplitude_bound_max_abs"]<=bound+1e-12 and result["future_label_names_absent_from_prediction_functions"] and all(c["all_finite"] and c["invariant_replay_max_abs_error"]<=1e-12 and c["free_replay_max_abs_error"]<=1e-12 and c["singleton_equivalence_max_abs_error"]<=1e-12 for c in checks)
    ) else "FAIL"
    out=Path("results/prior_utilization_e15c/confirmatory_v1_1/e15c_confirmatory_sanity.json")
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if result["status"]!="PASS": raise SystemExit("E15-C sanity failed")


if __name__=="__main__": main()
