"""Frozen E16-B train-only capacity fit and post-fit realization audit.

Only frozen train-row target cells are used. Validation, guard, and test
targets are never stored, summarized, or passed to numerical routines.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from itertools import product
from pathlib import Path

import numpy as np
import openpyxl


FEATURES = ("AT", "V", "AP", "RH")
LAMBDAS = tuple(10.0**power for power in range(-6, 3))
EPSILON = 1e-12
DISTINCTNESS_TOLERANCE = 1e-10


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_indices(indices: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(indices, dtype=">u4").tobytes()).hexdigest()


def candidate_sha256(candidates: np.ndarray) -> str:
    digest = hashlib.sha256()
    for index, row in enumerate(candidates):
        digest.update(struct.pack(">I5d", index, *row))
    return digest.hexdigest()


def read_x_and_train_target_only(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Read all X rows; append the fifth-column value only for frozen train rows."""
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Sheet1"]
    rows = sheet.iter_rows(max_col=5, values_only=True)
    header = next(rows)
    if tuple(header[:4]) != FEATURES:
        raise ValueError("Canonical Sheet1 feature header mismatch")
    x_rows: list[tuple[float, ...]] = []
    train_indices: list[int] = []
    train_target: list[float] = []
    for index, row in enumerate(rows):
        feature_row = tuple(float(value) for value in row[:4])
        x_rows.append(feature_row)
        if feature_row[0] <= 24.79:
            train_indices.append(index)
            train_target.append(float(row[4]))
    x = np.asarray(x_rows, dtype=float)
    indices = np.asarray(train_indices, dtype=np.uint32)
    target = np.asarray(train_target, dtype=float)
    if x.shape != (9568, 4) or target.shape != (6699,) or not np.isfinite(x).all() or not np.isfinite(target).all():
        raise ValueError("Train-only source read failed shape or finiteness checks")
    return x, indices, target


def build_background(z: np.ndarray) -> np.ndarray:
    zv, zap, zrh = z.T
    return np.column_stack((np.ones(z.shape[0]), zv, zap, zrh, zv**2, zap**2, zrh**2, zv * zap, zv * zrh, zap * zrh))


def build_candidates(d0: dict) -> np.ndarray:
    amplitudes = tuple(d0["amplitude_reference_measure"]["nodes"])
    rc = tuple(d0["shape_levels"]["r_c"])
    interactions = tuple(d0["shape_levels"]["r_interaction"])
    return np.asarray([(a, c, rv, rap, rh) for a, c, rv, rap, rh in product(amplitudes, rc, interactions, interactions, interactions)], dtype=float)


def continuation(candidates: np.ndarray, u: np.ndarray, z: np.ndarray) -> np.ndarray:
    output = np.empty((u.size, candidates.shape[0]), dtype=float)
    for column, (amplitude, rcurv, rv, rap, rh) in enumerate(candidates):
        output[:, column] = amplitude * (-u + rcurv * u**2 + u * (z[:, 0] * rv + z[:, 1] * rap + z[:, 2] * rh))
    return output


def ridge_coefficients(design: np.ndarray, response: np.ndarray, ridge: float) -> np.ndarray:
    n_rows = design.shape[0]
    penalty = np.eye(design.shape[1])
    penalty[0, 0] = 0.0
    lhs = (design.T @ design) / n_rows + ridge * penalty
    rhs = (design.T @ response) / n_rows
    return np.linalg.solve(lhs, rhs)


def fold_hash(indices: np.ndarray) -> tuple[np.ndarray, str]:
    folds = (indices % 5).astype(np.uint8)
    digest = hashlib.sha256()
    for index, fold in zip(np.asarray(indices, dtype=">u4"), folds):
        digest.update(index.tobytes())
        digest.update(fold.tobytes())
    return folds, digest.hexdigest()


def quantile_summary(values: np.ndarray) -> dict:
    return {
        "min": float(np.min(values)),
        "q05": float(np.quantile(values, 0.05, method="linear")),
        "median": float(np.median(values)),
        "q95": float(np.quantile(values, 0.95, method="linear")),
        "max": float(np.max(values)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--d0", type=Path, required=True)
    parser.add_argument("--split-replay", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    d0 = json.loads(args.d0.read_text(encoding="utf-8"))
    replay = json.loads(args.split_replay.read_text(encoding="utf-8"))
    x, train_indices, y_train = read_x_and_train_target_only(args.xlsx)
    source_hash = sha256(args.xlsx)
    candidates = build_candidates(d0)
    d0_replay_checks = {
        "source_workbook_sha256_match": source_hash == d0["source_hashes"]["workbook_sha256"],
        "train_index_hash_match": hash_indices(train_indices) == replay["partition_index_sha256"]["train"],
        "candidate_table_sha256_match": candidate_sha256(candidates) == d0["candidate_table_sha256"],
        "candidate_count_405": candidates.shape[0] == 405,
    }
    if not all(d0_replay_checks.values()):
        raise ValueError(f"Frozen D0 replay mismatch: {d0_replay_checks}")

    train_mask = np.zeros(x.shape[0], dtype=bool)
    train_mask[train_indices] = True
    train_x = x[train_mask]
    train_median = np.asarray(d0["coordinate_convention"]["train_x_median"], dtype=float)
    train_iqr = np.asarray(d0["coordinate_convention"]["train_x_iqr"], dtype=float)
    z_all = (x[:, 1:] - train_median) / train_iqr
    u_all = (x[:, 0] - 24.79) / 4.45
    z_train, u_train = z_all[train_mask], u_all[train_mask]
    background_train = build_background(z_train)
    target_median = float(np.median(y_train))
    target_q25, target_q75 = np.quantile(y_train, (0.25, 0.75), method="linear")
    target_iqr = float(target_q75 - target_q25)
    if not np.isfinite(target_iqr) or target_iqr <= 0:
        raise ValueError("Train target IQR is nonpositive or nonfinite")
    y = (y_train - target_median) / target_iqr
    t_train = continuation(candidates, u_train, z_train)
    residual = y[:, None] - t_train
    folds, folds_sha = fold_hash(train_indices)
    expected_fold_sha = "41607f07db26c966c1525ad1ae37b68c5a72a2c20017d0b293bf9ae01d37e1b6"
    if folds_sha != expected_fold_sha:
        raise ValueError("Frozen train-fold assignment hash mismatch")

    cv_scores: dict[float, float] = {}
    for ridge in LAMBDAS:
        fold_errors = []
        for fold in range(5):
            fit_mask, holdout_mask = folds != fold, folds == fold
            beta = ridge_coefficients(background_train[fit_mask], residual[fit_mask], ridge)
            error = residual[holdout_mask] - background_train[holdout_mask] @ beta
            fold_errors.append(np.mean(error**2, axis=0))
        cv_scores[ridge] = float(np.mean(np.vstack(fold_errors)))
    minimum_cv = min(cv_scores.values())
    tied = [ridge for ridge, score in cv_scores.items() if abs(score - minimum_cv) <= EPSILON * max(1.0, abs(minimum_cv))]
    ridge_spec = max(tied)

    oof_error = np.empty_like(residual)
    for fold in range(5):
        fit_mask, holdout_mask = folds != fold, folds == fold
        beta = ridge_coefficients(background_train[fit_mask], residual[fit_mask], ridge_spec)
        oof_error[holdout_mask] = residual[holdout_mask] - background_train[holdout_mask] @ beta
    oof_rmse = np.sqrt(np.mean(oof_error**2, axis=0))
    sigma_ref = float(np.median(oof_rmse))
    if not np.isfinite(sigma_ref) or sigma_ref <= 0:
        raise ValueError("Frozen working-likelihood scale is nonpositive or nonfinite")

    beta_full = ridge_coefficients(background_train, residual, ridge_spec)
    shell_mask = x[:, 0] > 27.96
    background_shell = build_background(z_all[shell_mask])
    t_shell = continuation(candidates, u_all[shell_mask], z_all[shell_mask])
    predictions = background_shell @ beta_full + t_shell
    if not np.isfinite(predictions).all():
        raise ValueError("Nonfinite post-fit candidate prediction")
    gram = np.einsum("ik,ij->kj", predictions, predictions)
    norms = np.sum(predictions**2, axis=0)
    squared = np.maximum((norms[:, None] + norms[None, :] - 2.0 * gram) / predictions.shape[0], 0.0)
    pairwise = np.sqrt(squared[np.triu_indices(candidates.shape[0], k=1)])
    exact_pairs = int(np.sum(pairwise <= DISTINCTNESS_TOLERANCE))
    centered = predictions - np.mean(predictions, axis=1, keepdims=True)
    singular_values = np.linalg.svd(centered, compute_uv=False)
    rank = int(np.linalg.matrix_rank(centered))
    nonzero = singular_values[:rank]
    condition_number = float(nonzero[0] / nonzero[-1]) if rank else float("inf")
    postfit_checks = {
        "all_prediction_values_finite": bool(np.isfinite(predictions).all()),
        "no_realized_exact_equivalent_pair": exact_pairs == 0,
        "positive_finite_sigma_ref": np.isfinite(sigma_ref) and sigma_ref > 0,
    }
    final_status = "PASS" if all(postfit_checks.values()) else "STOP_IMPLEMENTATION_REALIZATION_FAILURE"
    artifact = {
        "protocol": "E16-B CCPP train-only capacity and realized-distinctness audit v1",
        "final_status": final_status,
        "source_hashes": {
            "workbook_sha256": source_hash,
            "d0_artifact_sha256": sha256(args.d0),
            "split_replay_artifact_sha256": sha256(args.split_replay),
        },
        "target_access": {
            "train_target_rows_read": int(y_train.size),
            "validation_target_access": "prohibited",
            "guard_target_access": "prohibited",
            "confirmatory_target_access": "prohibited",
        },
        "train_target_normalization": {"median": target_median, "iqr": target_iqr},
        "background_basis": ["1", "z_V", "z_AP", "z_RH", "z_V^2", "z_AP^2", "z_RH^2", "z_V*z_AP", "z_V*z_RH", "z_AP*z_RH"],
        "ridge_contract": {
            "grid": list(LAMBDAS),
            "intercept_penalized": False,
            "fold_rule": "zero-based canonical Sheet1 train-row index modulo 5",
            "fold_sizes": [int(np.sum(folds == fold)) for fold in range(5)],
            "fold_assignment_sha256": folds_sha,
            "aggregate_cv_mse_by_lambda": {str(key): value for key, value in cv_scores.items()},
            "selected_lambda": ridge_spec,
            "tie_rule": "within relative 1e-12, choose largest lambda",
        },
        "working_likelihood": {"sigma_ref": sigma_ref, "sigma_ref_definition": "median candidate train OOF RMSE", "evidence_temperature": "none"},
        "train_oof_rmse_summary": quantile_summary(oof_rmse),
        "postfit_prediction_shell": {"definition": "AT > q85 = 27.96; validation plus guard plus confirmatory X rows", "row_count": int(predictions.shape[0])},
        "postfit_pairwise_distinctness": {**quantile_summary(pairwise), "pair_count": int(pairwise.size), "pairs_at_or_below_1e-10": exact_pairs},
        "centered_prediction_matrix": {"numerical_rank": rank, "condition_number": condition_number, "singular_values": singular_values.tolist()},
        "d0_replay_checks": d0_replay_checks,
        "postfit_checks": postfit_checks,
        "scope": "train-target capacity only; no validation, guard, or confirmatory target values used",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final_status": final_status, "selected_lambda": ridge_spec, "sigma_ref": sigma_ref, "postfit_min_distance": artifact["postfit_pairwise_distinctness"]["min"]}, indent=2))
    if final_status != "PASS":
        raise SystemExit("E16-B v1 implementation realization failure")


if __name__ == "__main__":
    main()
