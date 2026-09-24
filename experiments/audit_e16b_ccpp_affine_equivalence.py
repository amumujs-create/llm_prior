"""Train-only audit of E16-B affine point-mixture equivalence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from run_e16b_ccpp_train_capacity import (
    build_background,
    build_candidates,
    candidate_sha256,
    continuation,
    read_x_and_train_target_only,
    ridge_coefficients,
    sha256,
)


TOLERANCE = 1e-12


def raw_theta(candidates: np.ndarray) -> np.ndarray:
    amplitude = candidates[:, 0]
    return np.column_stack((-amplitude, amplitude * candidates[:, 1], amplitude[:, None] * candidates[:, 2:]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--d0", type=Path, required=True)
    parser.add_argument("--capacity", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    d0 = json.loads(args.d0.read_text(encoding="utf-8"))
    capacity = json.loads(args.capacity.read_text(encoding="utf-8"))
    x, train_indices, y_train = read_x_and_train_target_only(args.xlsx)
    candidates = build_candidates(d0)
    if candidate_sha256(candidates) != d0["candidate_table_sha256"]:
        raise ValueError("D0 candidate-table replay mismatch")
    if sha256(args.xlsx) != capacity["source_hashes"]["workbook_sha256"]:
        raise ValueError("Source workbook hash mismatch")
    target = capacity["train_target_normalization"]
    y = (y_train - target["median"]) / target["iqr"]
    train_mask = np.zeros(x.shape[0], dtype=bool)
    train_mask[train_indices] = True
    train_median = np.asarray(d0["coordinate_convention"]["train_x_median"], dtype=float)
    train_iqr = np.asarray(d0["coordinate_convention"]["train_x_iqr"], dtype=float)
    z_all = (x[:, 1:] - train_median) / train_iqr
    u_all = (x[:, 0] - 24.79) / 4.45
    background_train = build_background(z_all[train_mask])
    background_all = build_background(z_all)
    ridge = capacity["ridge_contract"]["selected_lambda"]
    candidate_t_train = continuation(candidates, u_all[train_mask], z_all[train_mask])
    # Some local BLAS builds leave floating-point warning flags set after a
    # prior operation.  The audit therefore asserts finiteness explicitly
    # instead of treating those stale flags as numerical evidence.
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        candidate_beta = ridge_coefficients(background_train, y[:, None] - candidate_t_train, ridge)
        candidate_prediction = background_all @ candidate_beta + continuation(candidates, u_all, z_all)
    if not np.isfinite(candidate_beta).all() or not np.isfinite(candidate_prediction).all():
        raise ValueError("Nonfinite candidate fit or prediction in affine-equivalence audit")
    uniform_point_mean = np.mean(candidate_prediction, axis=1)

    theta_bar = np.mean(raw_theta(candidates), axis=0)
    s_bar, c_bar, *gamma_bar = theta_bar.tolist()
    # Elementwise reduction avoids a platform BLAS warning-flag artifact for
    # the zero-centered interaction mean while preserving the same formula.
    gamma = np.asarray(gamma_bar)
    gamma_term_train = np.sum(z_all[train_mask] * gamma, axis=1)
    t_bar_train = s_bar * u_all[train_mask] + c_bar * u_all[train_mask] ** 2 + u_all[train_mask] * gamma_term_train
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        beta_bar = ridge_coefficients(background_train, (y - t_bar_train)[:, None], ridge)[:, 0]
        gamma_term_all = np.sum(z_all * gamma, axis=1)
        t_bar_all = s_bar * u_all + c_bar * u_all**2 + u_all * gamma_term_all
        mean_specification_prediction = background_all @ beta_bar + t_bar_all
    if not np.isfinite(beta_bar).all() or not np.isfinite(mean_specification_prediction).all():
        raise ValueError("Nonfinite mean-specification fit or prediction in affine-equivalence audit")
    difference = uniform_point_mean - mean_specification_prediction
    max_abs = float(np.max(np.abs(difference)))
    rms = float(np.sqrt(np.mean(difference**2)))
    status = "PASS" if max_abs <= TOLERANCE else "FAIL"
    artifact = {
        "protocol": "E16-B affine point-mixture equivalence audit v1",
        "final_status": status,
        "source_hashes": {
            "workbook_sha256": sha256(args.xlsx),
            "d0_artifact_sha256": sha256(args.d0),
            "capacity_artifact_sha256": sha256(args.capacity),
        },
        "target_access": {"train_target_rows_read": int(y_train.size), "validation_guard_confirmatory_target_access": "prohibited"},
        "candidate_count": int(candidates.shape[0]),
        "common_ridge": ridge,
        "numerical_checks": {
            "candidate_fit_and_predictions_finite": True,
            "mean_specification_fit_and_prediction_finite": True,
        },
        "mean_raw_specification": {"s": s_bar, "c": c_bar, "gamma_V": gamma_bar[0], "gamma_AP": gamma_bar[1], "gamma_RH": gamma_bar[2]},
        "evaluation_domain": "all 9,568 canonical X rows",
        "max_abs_uniform_point_mean_minus_mean_specification": max_abs,
        "rms_uniform_point_mean_minus_mean_specification": rms,
        "tolerance": TOLERANCE,
        "interpretation": "uniform candidate point mean is affinely equivalent to the point prediction at the uniform mean raw specification",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final_status": status, "max_abs_difference": max_abs}, indent=2))
    if status != "PASS":
        raise SystemExit("Affine-equivalence audit failure")


if __name__ == "__main__":
    main()
