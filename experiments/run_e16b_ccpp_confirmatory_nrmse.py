"""Release secondary E16-B point-prediction NRMSE diagnostics after CRPS."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from run_e16b_ccpp_final_b1_crps import SEED, read_confirmatory_target_only
from run_e16b_ccpp_train_capacity import sha256


def bootstrap_difference(y: np.ndarray, left: np.ndarray, right: np.ndarray) -> tuple[float, float, float]:
    left_error = (y - left) ** 2
    right_error = (y - right) ** 2
    point = float(np.sqrt(np.mean(left_error)) - np.sqrt(np.mean(right_error)))
    generator = np.random.Generator(np.random.PCG64(SEED))
    indices = generator.integers(0, y.size, size=(5000, y.size), endpoint=False)
    boot = np.sqrt(np.mean(left_error[indices], axis=1)) - np.sqrt(np.mean(right_error[indices], axis=1))
    lower, upper = np.quantile(boot, [0.025, 0.975], method="linear")
    return point, float(lower), float(upper)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--prediction-manifest", type=Path, required=True)
    parser.add_argument("--components", type=Path, required=True)
    parser.add_argument("--b1", type=Path, required=True)
    parser.add_argument("--b2", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.prediction_manifest.read_text(encoding="utf-8"))
    with np.load(args.components, allow_pickle=False) as data:
        indices = data["test_indices"]
        means = data["component_means"]
        uniform = data["uniform_weights"]
        weighted = data["weighted_weights"]
        map_index = int(data["map_index"])
    target_indices, target = read_confirmatory_target_only(args.xlsx)
    if not np.array_equal(indices, target_indices) or means.shape != (956, 405):
        raise ValueError("Frozen test predictions do not match confirmatory rows")
    capacity = json.loads(Path("results/prior_utilization_e16b/train_capacity_v1/E16B_CCPP_TRAIN_CAPACITY_V1.json").read_text(encoding="utf-8"))
    y = (target - capacity["train_target_normalization"]["median"]) / capacity["train_target_normalization"]["iqr"]
    # Component finiteness is audited before this stage; avoid stale BLAS
    # warning flags and validate the resulting point summaries explicitly.
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        prediction_uniform = means @ uniform
        prediction_weighted = means @ weighted
    prediction_map = means[:, map_index]
    if not np.isfinite(prediction_uniform).all() or not np.isfinite(prediction_weighted).all() or not np.isfinite(prediction_map).all():
        raise ValueError("Nonfinite frozen point prediction")
    b1 = bootstrap_difference(y, prediction_uniform, prediction_map)
    b2 = bootstrap_difference(y, prediction_weighted, prediction_uniform)
    artifact = {
        "protocol": "E16-B CCPP confirmatory secondary point-prediction NRMSE diagnostics v1",
        "final_status": "PASS",
        "source_hashes": {"workbook_sha256": sha256(args.xlsx), "prediction_manifest_sha256": sha256(args.prediction_manifest), "components_sha256": sha256(args.components), "frozen_B1_CRPS_sha256": sha256(args.b1), "frozen_B2_CRPS_sha256": sha256(args.b2)},
        "target_access": {"confirmatory_target_rows_read": int(target.size), "validation_target_access": "none", "guard_target_access": "prohibited"},
        "metric_boundary": "NRMSE is a secondary point-specification diagnostic, not evidence that a predictive distribution retained diversity.",
        "bootstrap": {"unit": "empirical confirmatory row", "replicates": 5000, "generator": "NumPy PCG64", "seed": SEED, "ci": "percentile 95%, linear quantiles"},
        "secondary_diagnostics": {
            "B1_NRMSE = NRMSE_uniform - NRMSE_MAP": {"mean": b1[0], "ci_2_5": b1[1], "ci_97_5": b1[2]},
            "B2_NRMSE = NRMSE_weighted - NRMSE_uniform": {"mean": b2[0], "ci_2_5": b2[1], "ci_97_5": b2[2]},
        },
        "prediction_vector_sha256": {"uniform": hashlib.sha256(np.asarray(prediction_uniform, dtype=">f8").tobytes()).hexdigest(), "weighted": hashlib.sha256(np.asarray(prediction_weighted, dtype=">f8").tobytes()).hexdigest(), "MAP": hashlib.sha256(np.asarray(prediction_map, dtype=">f8").tobytes()).hexdigest()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final_status": "PASS", "B1_NRMSE": b1, "B2_NRMSE": b2}, indent=2))


if __name__ == "__main__":
    main()
