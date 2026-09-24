"""Freeze E16-B validation-only MAP and Gaussian working-likelihood weights."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import openpyxl

from run_e16b_ccpp_train_capacity import (
    FEATURES,
    build_background,
    build_candidates,
    candidate_sha256,
    continuation,
    hash_indices,
    ridge_coefficients,
    sha256,
)


AT_TRAIN = 24.79
AT_VALIDATION = 27.96


def read_x_train_validation_targets(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Read all X; retain PE only for the authorized train and validation rows."""
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Sheet1"]
    rows = sheet.iter_rows(max_col=5, values_only=True)
    header = next(rows)
    if tuple(header[:4]) != FEATURES:
        raise ValueError("Canonical Sheet1 feature header mismatch")
    x_rows: list[tuple[float, ...]] = []
    train_indices: list[int] = []
    validation_indices: list[int] = []
    train_target: list[float] = []
    validation_target: list[float] = []
    for index, row in enumerate(rows):
        features = tuple(float(value) for value in row[:4])
        x_rows.append(features)
        if features[0] <= AT_TRAIN:
            train_indices.append(index)
            train_target.append(float(row[4]))
        elif features[0] <= AT_VALIDATION:
            validation_indices.append(index)
            validation_target.append(float(row[4]))
    x = np.asarray(x_rows, dtype=float)
    train = np.asarray(train_indices, dtype=np.uint32)
    validation = np.asarray(validation_indices, dtype=np.uint32)
    y_train = np.asarray(train_target, dtype=float)
    y_validation = np.asarray(validation_target, dtype=float)
    if x.shape != (9568, 4) or y_train.shape != (6699,) or y_validation.shape != (1436,):
        raise ValueError("Authorized source read shape mismatch")
    if not np.isfinite(x).all() or not np.isfinite(y_train).all() or not np.isfinite(y_validation).all():
        raise ValueError("Nonfinite authorized source values")
    return x, train, validation, y_train, y_validation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--d0", type=Path, required=True)
    parser.add_argument("--capacity", type=Path, required=True)
    parser.add_argument("--split-replay", type=Path, required=True)
    parser.add_argument("--amendment", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    d0 = json.loads(args.d0.read_text(encoding="utf-8"))
    capacity = json.loads(args.capacity.read_text(encoding="utf-8"))
    replay = json.loads(args.split_replay.read_text(encoding="utf-8"))
    x, train_indices, validation_indices, y_train, y_validation = read_x_train_validation_targets(args.xlsx)
    if sha256(args.xlsx) != capacity["source_hashes"]["workbook_sha256"]:
        raise ValueError("Workbook hash mismatch")
    if hash_indices(train_indices) != replay["partition_index_sha256"]["train"]:
        raise ValueError("Train index replay mismatch")
    if hash_indices(validation_indices) != replay["partition_index_sha256"]["validation"]:
        raise ValueError("Validation index replay mismatch")
    candidates = build_candidates(d0)
    if candidate_sha256(candidates) != d0["candidate_table_sha256"]:
        raise ValueError("Candidate-table replay mismatch")

    target = capacity["train_target_normalization"]
    y_train_norm = (y_train - target["median"]) / target["iqr"]
    y_validation_norm = (y_validation - target["median"]) / target["iqr"]
    median = np.asarray(d0["coordinate_convention"]["train_x_median"], dtype=float)
    iqr = np.asarray(d0["coordinate_convention"]["train_x_iqr"], dtype=float)
    z = (x[:, 1:] - median) / iqr
    u = (x[:, 0] - AT_TRAIN) / 4.45
    background_train = build_background(z[train_indices])
    background_validation = build_background(z[validation_indices])
    ridge = float(capacity["ridge_contract"]["selected_lambda"])
    # Explicit finiteness checks below are authoritative.  This environment's
    # BLAS backend can surface stale warning flags during finite matrix products.
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        beta = ridge_coefficients(
            background_train,
            y_train_norm[:, None] - continuation(candidates, u[train_indices], z[train_indices]),
            ridge,
        )
        validation_prediction = background_validation @ beta + continuation(candidates, u[validation_indices], z[validation_indices])
    if not np.isfinite(beta).all() or not np.isfinite(validation_prediction).all():
        raise ValueError("Nonfinite validation candidate prediction")
    sigma = float(capacity["working_likelihood"]["sigma_ref"])
    residual = y_validation_norm[:, None] - validation_prediction
    sse = np.sum(residual**2, axis=0)
    losses = sse / (2.0 * sigma**2)
    minimum = float(np.min(losses))
    map_index = int(np.flatnonzero(losses == minimum)[0])
    unnormalized = np.exp(-(losses - minimum))
    weights = unnormalized / np.sum(unnormalized)
    if not np.isfinite(losses).all() or not np.isfinite(weights).all() or not np.isclose(np.sum(weights), 1.0, atol=1e-15, rtol=0.0):
        raise ValueError("Invalid frozen validation likelihood or weights")
    positive_weights = weights[weights > 0.0]
    entropy = float(-np.sum(positive_weights * np.log(positive_weights)))
    ess = float(1.0 / np.sum(weights**2))
    artifact = {
        "protocol": "E16-B CCPP validation-only evidence freeze v1",
        "final_status": "PASS",
        "source_hashes": {
            "workbook_sha256": sha256(args.xlsx),
            "d0_artifact_sha256": sha256(args.d0),
            "capacity_artifact_sha256": sha256(args.capacity),
            "split_replay_artifact_sha256": sha256(args.split_replay),
            "affine_crps_amendment_sha256": sha256(args.amendment),
        },
        "target_access": {
            "train_target_rows_read": int(y_train.size),
            "validation_target_rows_read": int(y_validation.size),
            "guard_target_access": "prohibited",
            "confirmatory_target_access": "prohibited",
        },
        "index_hashes": {"train": hash_indices(train_indices), "validation": hash_indices(validation_indices)},
        "candidate_count": int(candidates.shape[0]),
        "candidate_table_sha256": candidate_sha256(candidates),
        "target_normalization": target,
        "working_likelihood": {
            "sigma_ref": sigma,
            "loss": "validation normalized-target SSE / (2 * sigma_ref^2)",
            "evidence_temperature": "none",
            "MAP_tie_rule": "smallest frozen candidate index among exact minimum losses",
        },
        "MAP": {"zero_based_candidate_index": map_index, "candidate_coordinates": candidates[map_index].tolist()},
        "weights": weights.tolist(),
        "weight_diagnostics": {"sum": float(np.sum(weights)), "entropy_natural_log": entropy, "effective_sample_size": ess, "minimum": float(np.min(weights)), "maximum": float(np.max(weights))},
        "validation_loss_sha256": __import__("hashlib").sha256(np.asarray(losses, dtype=">f8").tobytes()).hexdigest(),
        "scope": "validation evidence only; MAP and weights are frozen without guard or confirmatory PE access",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final_status": "PASS", "MAP_index": map_index, "entropy": entropy, "ESS": ess}, indent=2))


if __name__ == "__main__":
    main()
