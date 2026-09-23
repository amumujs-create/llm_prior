"""Freeze the E16-B AT-tail geometry without loading the workbook target column.

This audit intentionally reads only the first four feature columns of the
canonical Sheet1 workbook.  It produces no target-derived summaries, models,
or policy quantities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import openpyxl


FEATURES = ("AT", "V", "AP", "RH")
CO_SHIFT_FEATURES = ("V", "AP", "RH")
QUANTILES = (0.70, 0.85, 0.90)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_features_only(path: Path) -> np.ndarray:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Sheet1"]
    # max_col is deliberate: the target column is never materialized in this
    # X-only audit.
    rows = sheet.iter_rows(max_col=len(FEATURES), values_only=True)
    header = tuple(next(rows)[: len(FEATURES)])
    if header != FEATURES:
        raise ValueError(f"Sheet1 feature header mismatch: {header!r}")
    values = [tuple(float(value) for value in row[: len(FEATURES)]) for row in rows]
    array = np.asarray(values, dtype=float)
    if array.shape != (9568, len(FEATURES)) or not np.isfinite(array).all():
        raise ValueError("Feature-only source audit failed shape or finiteness checks")
    return array


def wasserstein_1d(left: np.ndarray, right: np.ndarray) -> float:
    """Exact empirical 1-Wasserstein distance for equally weighted samples."""
    left = np.sort(left)
    right = np.sort(right)
    knots = np.unique(np.concatenate((left, right)))
    if knots.size < 2:
        return 0.0
    left_cdf = np.searchsorted(left, knots[:-1], side="right") / left.size
    right_cdf = np.searchsorted(right, knots[:-1], side="right") / right.size
    return float(np.sum(np.abs(left_cdf - right_cdf) * np.diff(knots)))


def minimum_distances(query: np.ndarray, reference: np.ndarray, exclude_self: bool) -> np.ndarray:
    """Euclidean nearest-neighbour distances without retaining an all-pairs matrix."""
    result = np.empty(query.shape[0], dtype=float)
    chunk_size = 256
    for start in range(0, query.shape[0], chunk_size):
        stop = min(start + chunk_size, query.shape[0])
        delta = query[start:stop, None, :] - reference[None, :, :]
        squared = np.einsum("ijk,ijk->ij", delta, delta)
        if exclude_self:
            indices = np.arange(start, stop)
            squared[np.arange(stop - start), indices] = np.inf
        result[start:stop] = np.sqrt(np.min(squared, axis=1))
    return result


def feature_summary(train: np.ndarray, test: np.ndarray, feature_index: int) -> dict:
    train_values = train[:, feature_index]
    test_values = test[:, feature_index]
    q25, q75 = np.quantile(train_values, (0.25, 0.75), method="linear")
    iqr = float(q75 - q25)
    if iqr <= 0:
        raise ValueError(f"Train IQR is nonpositive for {FEATURES[feature_index]}")
    lower, upper = float(np.min(train_values)), float(np.max(train_values))
    return {
        "feature": FEATURES[feature_index],
        "train_min": lower,
        "train_max": upper,
        "test_min": float(np.min(test_values)),
        "test_max": float(np.max(test_values)),
        "test_within_train_minmax_count": int(np.sum((test_values >= lower) & (test_values <= upper))),
        "test_within_train_minmax_fraction": float(np.mean((test_values >= lower) & (test_values <= upper))),
        "train_median": float(np.median(train_values)),
        "test_median": float(np.median(test_values)),
        "median_shift_over_train_iqr": float((np.median(test_values) - np.median(train_values)) / iqr),
        "wasserstein_over_train_iqr": float(wasserstein_1d(train_values, test_values) / iqr),
        "train_iqr": iqr,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    features = read_features_only(args.xlsx)
    at = features[:, 0]
    q70, q85, q90 = (float(np.quantile(at, q, method="linear")) for q in QUANTILES)
    train_mask = at <= q70
    validation_mask = (at > q70) & (at <= q85)
    guard_mask = (at > q85) & (at <= q90)
    test_mask = at > q90
    if not np.all(train_mask | validation_mask | guard_mask | test_mask):
        raise ValueError("Split masks are not exhaustive")
    if np.sum(train_mask) + np.sum(validation_mask) + np.sum(guard_mask) + np.sum(test_mask) != at.size:
        raise ValueError("Split masks are not disjoint")
    if np.max(at[train_mask]) >= np.min(at[validation_mask]) or np.max(at[validation_mask]) >= np.min(at[guard_mask]) or np.max(at[guard_mask]) >= np.min(at[test_mask]):
        raise ValueError("AT support separation failed")

    train = features[train_mask]
    test = features[test_mask]
    co_shift_indices = tuple(FEATURES.index(name) for name in CO_SHIFT_FEATURES)
    train_co_shift = train[:, co_shift_indices]
    test_co_shift = test[:, co_shift_indices]
    median = np.median(train_co_shift, axis=0)
    q25, q75 = np.quantile(train_co_shift, (0.25, 0.75), axis=0, method="linear")
    iqr = q75 - q25
    if np.any(iqr <= 0):
        raise ValueError("Nonpositive train IQR in co-shift features")
    train_z = (train_co_shift - median) / iqr
    test_z = (test_co_shift - median) / iqr
    loo_train_nn = minimum_distances(train_z, train_z, exclude_self=True)
    test_to_train_nn = minimum_distances(test_z, train_z, exclude_self=False)
    train_nn_q95 = float(np.quantile(loo_train_nn, 0.95, method="linear"))
    c_overlap = float(np.mean(test_to_train_nn <= train_nn_q95))

    # The 95th percentile is a frozen reference distribution.  A test set with
    # less than 95% coverage is labelled compound covariate shift; it does not
    # authorize changing the already fixed quantile split.
    compound_label = (
        "high-AT extrapolation under compound covariate shift"
        if c_overlap < 0.95
        else "high-AT extrapolation with substantial remaining-covariate overlap"
    )
    source = json.loads(args.source_manifest.read_text(encoding="utf-8"))
    artifact = {
        "protocol": "E16-B CCPP AT-tail X-only geometry audit v1",
        "status": "PASS",
        "source_identity": {
            "source_manifest_sha256": sha256(args.source_manifest),
            "workbook_sha256": sha256(args.xlsx),
            "canonical_sheet": source["workbook_audit"]["canonical_sheet"],
        },
        "x_only_contract": {
            "loaded_columns": list(FEATURES),
            "target_column_access": "prohibited; not loaded into this audit",
            "quantile_method": "numpy.quantile(method='linear')",
            "support_coordinate": "AT",
            "extrapolation_direction": "high-temperature tail",
            "split_definition": {
                "train": "AT <= q70",
                "validation": "q70 < AT <= q85",
                "guard_band": "q85 < AT <= q90; excluded from fitting and tuning",
                "confirmatory_test": "AT > q90",
                "final_training_rule": "train region only; validation is never merged into training",
            },
        },
        "at_quantiles": {
            "q70": q70,
            "q85": q85,
            "q90": q90,
            "ties_at_q70": int(np.sum(at == q70)),
            "ties_at_q85": int(np.sum(at == q85)),
            "ties_at_q90": int(np.sum(at == q90)),
        },
        "split_counts": {
            "train": int(np.sum(train_mask)),
            "validation": int(np.sum(validation_mask)),
            "guard_band": int(np.sum(guard_mask)),
            "confirmatory_test": int(np.sum(test_mask)),
            "total": int(at.size),
        },
        "at_support": {
            "train_max": float(np.max(at[train_mask])),
            "validation_min": float(np.min(at[validation_mask])),
            "guard_band_min": float(np.min(at[guard_mask])),
            "confirmatory_test_min": float(np.min(at[test_mask])),
            "strict_train_to_test_gap": float(np.min(at[test_mask]) - np.max(at[train_mask])),
        },
        "remaining_covariate_diagnostics": [
            feature_summary(train, test, FEATURES.index(name)) for name in CO_SHIFT_FEATURES
        ],
        "nearest_neighbor_diagnostic": {
            "features": list(CO_SHIFT_FEATURES),
            "standardization": "train median and train IQR",
            "train_leave_one_out_nn_q95": train_nn_q95,
            "test_to_train_nn_median": float(np.median(test_to_train_nn)),
            "test_to_train_nn_q95": float(np.quantile(test_to_train_nn, 0.95, method="linear")),
            "c_overlap": c_overlap,
            "classification_rule": "compound covariate shift iff C_overlap < 0.95",
            "classification": compound_label,
        },
        "scope": "X-only geometry; no target-derived summaries, split optimization, model, policy, or predictive outcome",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "classification": compound_label}, indent=2))


if __name__ == "__main__":
    main()
