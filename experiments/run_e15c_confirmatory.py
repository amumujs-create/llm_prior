"""Generate frozen E15-C v1.1 confirmatory corpus without opening outcomes."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from e15c_confirmatory_core import (MANIFEST, MANIFEST_SHA, c_grid, free_prediction, invariant_predictions, load_manifest, make_proposal, proposal_seed, q_grid)


OUTDIR=Path("results/prior_utilization_e15c/confirmatory_v1_1")
POLICIES=("closed_mechanism","invariant_residual_MAP","invariant_residual_ensemble","evidence_weighted_residual_mixture","free_baseline")


def main() -> None:
    manifest=load_manifest(); raw=MANIFEST.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==MANIFEST_SHA
    quota=manifest["quota"]["accepted_latent_tasks"]; max_attempts=manifest["quota"]["max_attempts"]
    qs=q_grid(manifest); cs=c_grid(manifest); bound=manifest["estimator"]["amplitude_profile_bound_ratio"]
    rho=manifest["noise"]["rho"]; r_inv=manifest["scales"]["R_inv_value_under_manifest"]; sigma=rho*r_inv
    x_forecast=np.linspace(.75,1.0,manifest["evaluation"]["forecast_points_including_left_endpoint"]); future=x_forecast>.75
    rows=[]; rejections=[]; accepted=0; proposals_used=0
    for proposal_index in range(max_attempts):
        if accepted>=quota: break
        sign=-1.0 if accepted%2==0 else 1.0
        try:
            proposals_used+=1
            task=make_proposal(proposal_seed(manifest["sampling"]["confirmatory_seed_namespace"],proposal_index),sign,manifest)
            truth_x=x_forecast
            # Truth uses only generator latent state and is accessed after all
            # policy predictions for the prefix have been fixed.
            from e15c_confirmatory_core import z_bases, invariant_base
            z1,z3=z_bases(truth_x,1.0); truth=invariant_base(truth_x)+task["amplitude"]*((1-task["q_true"])*z1+task["q_true"]*z3)
            task_rows=[]
            for exposure, endpoint in manifest["sampling"]["prefix_exposures"].items():
                observed=task["x"]<=endpoint+1e-12
                y_obs=(task["clean"]+sigma*task["master_noise"])[observed][None,:]
                inv=invariant_predictions(y_obs,task["x"][observed],x_forecast,qs,sigma,bound)
                free=free_prediction(y_obs,task["x"][observed],x_forecast,qs,cs,sigma,bound)
                predictions={name:inv[name][0] for name in POLICIES if name!="free_baseline"} | {"free_baseline":free[0]}
                for policy,prediction in predictions.items():
                    if not np.all(np.isfinite(prediction)): raise FloatingPointError(f"nonfinite {policy}")
                    nrmse=float(np.sqrt(np.mean((prediction[future]-truth[future])**2))/r_inv)
                    task_rows.append({"task_id":accepted,"proposal_index":proposal_index,"prefix_exposure":exposure,"policy":policy,"nrmse":nrmse})
            rows.extend(task_rows); accepted+=1
        except (FloatingPointError, ValueError) as error:
            rejections.append({"proposal_index":proposal_index,"reason":type(error).__name__})
    if accepted!=quota: raise RuntimeError(f"accepted {accepted}, required {quota}")
    OUTDIR.mkdir(parents=True,exist_ok=True)
    csv_path=OUTDIR/"e15c_confirmatory_rows.csv"
    with csv_path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["task_id","proposal_index","prefix_exposure","policy","nrmse"]); writer.writeheader(); writer.writerows(rows)
    expected=quota*len(manifest["sampling"]["prefix_exposures"])*len(POLICIES)
    duplicate=len(rows)-len({(r["task_id"],r["prefix_exposure"],r["policy"]) for r in rows})
    integrity={
        "status":"PASS" if len(rows)==expected and duplicate==0 and not rejections else "FAIL",
        "manifest_sha256":hashlib.sha256(raw).hexdigest(),
        "accepted_tasks":accepted,"max_attempts":max_attempts,"proposals_used":proposals_used,"rejection_count":len(rejections),
        "expected_rows":expected,"actual_rows":len(rows),"duplicate_rows":duplicate,"missing_rows":expected-len(rows),
        "policies":list(POLICIES),"exposures":list(manifest["sampling"]["prefix_exposures"]),
        "row_sha256":hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "outcomes_opened":False,
        "note":"Corpus rows contain scores for later preregistered analysis; this run emits no aggregate score, contrast, sign, rank, or winner.",
        "rejections":rejections,
    }
    (OUTDIR/"e15c_confirmatory_integrity.json").write_text(json.dumps(integrity,indent=2,sort_keys=True)+"\n")
    if integrity["status"]!="PASS": raise SystemExit("integrity failure")


if __name__=="__main__": main()
