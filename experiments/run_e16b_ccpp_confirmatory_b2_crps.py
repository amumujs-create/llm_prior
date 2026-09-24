"""Release predeclared secondary E16-B B2 CRPS after frozen B1."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from run_e16b_ccpp_final_b1_crps import SEED, SIGMA, bootstrap_interval, mixture_crps, read_confirmatory_target_only
from run_e16b_ccpp_train_capacity import sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--prediction-manifest", type=Path, required=True)
    parser.add_argument("--components", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--b1", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    b1 = json.loads(args.b1.read_text(encoding="utf-8"))
    if b1["primary_estimand"]["disposition"] not in {"Supported", "Direction-compatible, inconclusive", "Direction-incompatible, inconclusive", "Prospective failure", "Numerical boundary case"}:
        raise ValueError("B1 artifact is not a frozen disposition")
    manifest = json.loads(args.prediction_manifest.read_text(encoding="utf-8"))
    with np.load(args.components, allow_pickle=False) as data:
        indices = data["test_indices"]
        means = data["component_means"]
        uniform = data["uniform_weights"]
        weighted = data["weighted_weights"]
        sigma = float(data["sigma_ref"])
    if sha256(args.components) != manifest["component_artifact"]["sha256"] or means.shape != (956, 405) or sigma != SIGMA:
        raise ValueError("Frozen component artifact mismatch")
    target_indices, target = read_confirmatory_target_only(args.xlsx)
    if not np.array_equal(indices, target_indices):
        raise ValueError("Confirmatory index mismatch")
    capacity = json.loads(Path("results/prior_utilization_e16b/train_capacity_v1/E16B_CCPP_TRAIN_CAPACITY_V1.json").read_text(encoding="utf-8"))
    y = (target - capacity["train_target_normalization"]["median"]) / capacity["train_target_normalization"]["iqr"]
    crps_weighted = mixture_crps(y, means, weighted, sigma)
    crps_uniform = mixture_crps(y, means, uniform, sigma)
    delta = crps_weighted - crps_uniform
    if not np.isfinite(crps_weighted).all() or not np.isfinite(crps_uniform).all() or not np.isfinite(delta).all() or np.any(crps_weighted < 0.0) or np.any(crps_uniform < 0.0):
        raise ValueError("Nonfinite or negative B2 CRPS")
    lower, upper = bootstrap_interval(delta)
    artifact = {
        "protocol": "E16-B CCPP confirmatory secondary B2 exact CRPS v1",
        "final_status": "PASS",
        "source_hashes": {"workbook_sha256": sha256(args.xlsx), "prediction_manifest_sha256": sha256(args.prediction_manifest), "components_sha256": sha256(args.components), "final_scoring_contract_sha256": sha256(args.contract), "frozen_B1_sha256": sha256(args.b1)},
        "target_access": {"confirmatory_target_rows_read": int(target.size), "validation_target_access": "none", "guard_target_access": "prohibited"},
        "scoring": {"metric": "exact finite Gaussian-mixture CRPS", "sigma_ref": sigma, "component_counts": {"weighted": 405, "uniform": 405}},
        "bootstrap": {"unit": "empirical confirmatory row", "replicates": 5000, "generator": "NumPy PCG64", "seed": SEED, "ci": "percentile 95%, linear quantiles"},
        "secondary_estimand": {"name": "B2_CRPS = CRPS_weighted - CRPS_uniform", "n_rows": int(target.size), "mean": float(np.mean(delta)), "ci_2_5": lower, "ci_97_5": upper, "direction": "non-directional; no success/failure disposition"},
        "row_delta_sha256": hashlib.sha256(np.asarray(delta, dtype=">f8").tobytes()).hexdigest(),
        "scope": "B2 only after frozen B1; NRMSE was not computed or persisted in this run",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final_status": "PASS", "mean_B2_CRPS": artifact["secondary_estimand"]["mean"], "ci": [lower, upper]}, indent=2))


if __name__ == "__main__":
    main()
