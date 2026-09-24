"""Freeze E16-B test-X predictive distributions without reading test PE."""

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
    read_x_and_train_target_only,
    ridge_coefficients,
    sha256,
)


AT_TEST = 29.24


def read_test_x_only(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read exactly the four X columns; the PE column is never requested."""
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Sheet1"]
    rows = sheet.iter_rows(max_col=4, values_only=True)
    header = next(rows)
    if tuple(header) != FEATURES:
        raise ValueError("Canonical Sheet1 feature header mismatch")
    x = np.asarray([tuple(float(value) for value in row) for row in rows], dtype=float)
    indices = np.flatnonzero(x[:, 0] > AT_TEST).astype(np.uint32)
    if x.shape != (9568, 4) or indices.size != 956 or not np.isfinite(x).all():
        raise ValueError("Test-X-only read mismatch")
    return x[indices], indices


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--d0", type=Path, required=True)
    parser.add_argument("--capacity", type=Path, required=True)
    parser.add_argument("--validation-evidence", type=Path, required=True)
    parser.add_argument("--components-output", type=Path, required=True)
    parser.add_argument("--manifest-output", type=Path, required=True)
    args = parser.parse_args()
    d0 = json.loads(args.d0.read_text(encoding="utf-8"))
    capacity = json.loads(args.capacity.read_text(encoding="utf-8"))
    evidence = json.loads(args.validation_evidence.read_text(encoding="utf-8"))
    if evidence["final_status"] != "PASS":
        raise ValueError("Validation evidence is not frozen PASS")
    x_all, train_indices, y_train = read_x_and_train_target_only(args.xlsx)
    x_test, test_indices = read_test_x_only(args.xlsx)
    if sha256(args.xlsx) != capacity["source_hashes"]["workbook_sha256"]:
        raise ValueError("Workbook hash mismatch")
    candidates = build_candidates(d0)
    if candidate_sha256(candidates) != evidence["candidate_table_sha256"]:
        raise ValueError("Candidate-table mismatch")
    target = capacity["train_target_normalization"]
    y_train_norm = (y_train - target["median"]) / target["iqr"]
    median = np.asarray(d0["coordinate_convention"]["train_x_median"], dtype=float)
    iqr = np.asarray(d0["coordinate_convention"]["train_x_iqr"], dtype=float)
    z_all = (x_all[:, 1:] - median) / iqr
    z_test = (x_test[:, 1:] - median) / iqr
    u_all = (x_all[:, 0] - 24.79) / 4.45
    u_test = (x_test[:, 0] - 24.79) / 4.45
    ridge = float(capacity["ridge_contract"]["selected_lambda"])
    # Explicit finiteness checks below are authoritative; see the matching
    # validation implementation note for the local BLAS warning-flag artifact.
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        beta = ridge_coefficients(build_background(z_all[train_indices]), y_train_norm[:, None] - continuation(candidates, u_all[train_indices], z_all[train_indices]), ridge)
        component_means = build_background(z_test) @ beta + continuation(candidates, u_test, z_test)
    if not np.isfinite(beta).all() or component_means.shape != (956, 405) or not np.isfinite(component_means).all():
        raise ValueError("Nonfinite or malformed frozen test component means")
    uniform_weights = np.full(405, 1.0 / 405.0)
    weighted_weights = np.asarray(evidence["weights"], dtype=float)
    map_index = int(evidence["MAP"]["zero_based_candidate_index"])
    sigma = float(evidence["working_likelihood"]["sigma_ref"])
    if weighted_weights.shape != (405,) or not np.isclose(weighted_weights.sum(), 1.0, atol=1e-15, rtol=0.0):
        raise ValueError("Frozen validation weights malformed")
    args.components_output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.components_output, test_indices=test_indices, component_means=component_means, uniform_weights=uniform_weights, weighted_weights=weighted_weights, map_index=np.asarray(map_index), sigma_ref=np.asarray(sigma))
    manifest = {
        "protocol": "E16-B CCPP validation-selected test-X predictive-distribution freeze v1",
        "final_status": "PASS",
        "source_hashes": {"workbook_sha256": sha256(args.xlsx), "d0_artifact_sha256": sha256(args.d0), "capacity_artifact_sha256": sha256(args.capacity), "validation_evidence_sha256": sha256(args.validation_evidence)},
        "target_access": {"train_target_rows_read": int(y_train.size), "validation_target_access": "not read in this step", "guard_target_access": "prohibited", "confirmatory_target_access": "prohibited; workbook opened with max_col=4 for test X"},
        "component_artifact": {"path": str(args.components_output), "sha256": sha256(args.components_output), "component_means_shape": list(component_means.shape), "test_index_count": int(test_indices.size)},
        "policies": {"uniform": {"component_count": 405, "weights": "uniform_weights"}, "MAP": {"component_count": 1, "zero_based_candidate_index": map_index}, "weighted": {"component_count": 405, "weights": "weighted_weights"}},
        "sigma_ref": sigma,
        "scope": "prediction distributions fixed from train fit, validation evidence, and test X only; no guard or confirmatory PE was read",
    }
    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final_status": "PASS", "component_shape": list(component_means.shape), "MAP_index": map_index}, indent=2))


if __name__ == "__main__":
    main()
