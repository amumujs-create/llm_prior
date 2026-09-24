"""Open E16-B confirmatory PE once and freeze only primary B1 CRPS."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import openpyxl
from scipy.special import ndtr

from run_e16b_ccpp_train_capacity import FEATURES, sha256


SEED = 20260924
BOOTSTRAP_REPLICATES = 5000
SIGMA = 0.26536872271489265


def a_function(difference: np.ndarray, scale: float) -> np.ndarray:
    z = difference / scale
    return 2.0 * scale * np.exp(-0.5 * z**2) / np.sqrt(2.0 * np.pi) + difference * (2.0 * ndtr(z) - 1.0)


def mixture_crps(observation: np.ndarray, means: np.ndarray, weights: np.ndarray, sigma: float, batch_size: int = 8) -> np.ndarray:
    """Exact CRPS for one common-variance Gaussian mixture per row."""
    result = np.empty(observation.size, dtype=float)
    pair_scale = np.sqrt(2.0) * sigma
    for start in range(0, observation.size, batch_size):
        stop = min(start + batch_size, observation.size)
        current = means[start:stop]
        first = np.sum(weights * a_function(observation[start:stop, None] - current, sigma), axis=1)
        pair = a_function(current[:, :, None] - current[:, None, :], pair_scale)
        second = 0.5 * np.einsum("i,bij,j->b", weights, pair, weights, optimize=True)
        result[start:stop] = first - second
    return result


def single_gaussian_crps(observation: np.ndarray, means: np.ndarray, sigma: float) -> np.ndarray:
    return a_function(observation - means, sigma) - 0.5 * a_function(np.zeros_like(observation), np.sqrt(2.0) * sigma)


def read_confirmatory_target_only(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read PE only for the frozen confirmatory rows and retain their indices."""
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Sheet1"]
    rows = sheet.iter_rows(max_col=5, values_only=True)
    header = next(rows)
    if tuple(header[:4]) != FEATURES:
        raise ValueError("Canonical Sheet1 feature header mismatch")
    indices: list[int] = []
    targets: list[float] = []
    for index, row in enumerate(rows):
        if float(row[0]) > 29.24:
            indices.append(index)
            targets.append(float(row[4]))
    return np.asarray(indices, dtype=np.uint32), np.asarray(targets, dtype=float)


def bootstrap_interval(delta: np.ndarray) -> tuple[float, float]:
    generator = np.random.Generator(np.random.PCG64(SEED))
    indices = generator.integers(0, delta.size, size=(BOOTSTRAP_REPLICATES, delta.size), endpoint=False)
    means = np.mean(delta[indices], axis=1)
    return tuple(float(value) for value in np.quantile(means, [0.025, 0.975], method="linear"))


def disposition(mean: float, lower: float, upper: float) -> str:
    if mean < 0.0 and upper < 0.0:
        return "Supported"
    if mean < 0.0 and lower <= 0.0 <= upper:
        return "Direction-compatible, inconclusive"
    if mean > 0.0 and lower <= 0.0 <= upper:
        return "Direction-incompatible, inconclusive"
    if lower > 0.0:
        return "Prospective failure"
    return "Numerical boundary case"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--prediction-manifest", type=Path, required=True)
    parser.add_argument("--components", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.prediction_manifest.read_text(encoding="utf-8"))
    expected_component_hash = manifest["component_artifact"]["sha256"]
    if sha256(args.components) != expected_component_hash:
        raise ValueError("Frozen component artifact hash mismatch")
    with np.load(args.components, allow_pickle=False) as data:
        component_indices = data["test_indices"]
        means = data["component_means"]
        uniform_weights = data["uniform_weights"]
        map_index = int(data["map_index"])
        sigma = float(data["sigma_ref"])
    if sigma != SIGMA or means.shape != (956, 405) or uniform_weights.shape != (405,):
        raise ValueError("Frozen prediction distribution mismatch")
    target_indices, target = read_confirmatory_target_only(args.xlsx)
    if not np.array_equal(target_indices, component_indices) or target.shape != (956,) or not np.isfinite(target).all():
        raise ValueError("Confirmatory target indices or values mismatch")
    normalization = json.loads(args.prediction_manifest.read_text(encoding="utf-8"))["source_hashes"]
    # Recover frozen train normalization via the referenced capacity artifact.
    capacity_path = Path("results/prior_utilization_e16b/train_capacity_v1/E16B_CCPP_TRAIN_CAPACITY_V1.json")
    capacity = json.loads(capacity_path.read_text(encoding="utf-8"))
    y = (target - capacity["train_target_normalization"]["median"]) / capacity["train_target_normalization"]["iqr"]
    crps_uniform = mixture_crps(y, means, uniform_weights, sigma)
    crps_map = single_gaussian_crps(y, means[:, map_index], sigma)
    delta = crps_uniform - crps_map
    if not np.isfinite(crps_uniform).all() or not np.isfinite(crps_map).all() or not np.isfinite(delta).all() or np.any(crps_uniform < 0.0) or np.any(crps_map < 0.0):
        raise ValueError("Nonfinite or negative confirmatory CRPS")
    mean = float(np.mean(delta))
    lower, upper = bootstrap_interval(delta)
    artifact = {
        "protocol": "E16-B CCPP confirmatory primary B1 exact CRPS v1",
        "final_status": "PASS",
        "source_hashes": {"workbook_sha256": sha256(args.xlsx), "prediction_manifest_sha256": sha256(args.prediction_manifest), "components_sha256": sha256(args.components), "final_scoring_contract_sha256": sha256(args.contract), "capacity_artifact_sha256": sha256(capacity_path)},
        "target_access": {"confirmatory_target_rows_read": int(target.size), "train_target_access": "normalization values loaded only from frozen capacity artifact", "validation_target_access": "none", "guard_target_access": "prohibited"},
        "scoring": {"metric": "exact finite Gaussian-mixture CRPS", "normalized_target_scale": "frozen train median/IQR", "sigma_ref": sigma, "component_counts": {"uniform": 405, "MAP": 1}},
        "bootstrap": {"unit": "empirical confirmatory row", "replicates": BOOTSTRAP_REPLICATES, "generator": "NumPy PCG64", "seed": SEED, "ci": "percentile 95%, linear quantiles"},
        "primary_estimand": {"name": "B1_CRPS = CRPS_uniform - CRPS_MAP", "n_rows": int(target.size), "mean": mean, "ci_2_5": lower, "ci_97_5": upper, "prospective_prediction": "< 0", "disposition": disposition(mean, lower, upper)},
        "row_delta_sha256": hashlib.sha256(np.asarray(delta, dtype=">f8").tobytes()).hexdigest(),
        "scope": "B1 only; weighted mixture, B2, and NRMSE were not computed or persisted in this run",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final_status": "PASS", "mean_B1_CRPS": mean, "ci": [lower, upper], "disposition": artifact["primary_estimand"]["disposition"]}, indent=2))


if __name__ == "__main__":
    main()
