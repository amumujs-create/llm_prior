"""Target-free replay integrity audit for the frozen E16-B CCPP AT split."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import openpyxl


FEATURES = ("AT", "V", "AP", "RH")
PARTITIONS = ("train", "validation", "guard_band", "confirmatory_test")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_indices(indices: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(indices, dtype=">u4").tobytes()).hexdigest()


def read_features_only(path: Path) -> np.ndarray:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Sheet1"]
    rows = sheet.iter_rows(max_col=len(FEATURES), values_only=True)
    if tuple(next(rows)) != FEATURES:
        raise ValueError("Canonical Sheet1 feature header mismatch")
    values = np.asarray([tuple(float(value) for value in row) for row in rows], dtype=float)
    if values.shape != (9568, 4) or not np.isfinite(values).all():
        raise ValueError("Feature-only replay input failed shape or finiteness checks")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    geometry = json.loads(args.geometry.read_text(encoding="utf-8"))
    x = read_features_only(args.xlsx)
    at = x[:, 0]
    q70, q85, q90 = (float(np.quantile(at, q, method="linear")) for q in (0.70, 0.85, 0.90))
    frozen_q = geometry["at_quantiles"]
    quantiles_exact = (q70, q85, q90) == (frozen_q["q70"], frozen_q["q85"], frozen_q["q90"])
    masks = {
        "train": at <= q70,
        "validation": (at > q70) & (at <= q85),
        "guard_band": (at > q85) & (at <= q90),
        "confirmatory_test": at > q90,
    }
    counts = {name: int(mask.sum()) for name, mask in masks.items()}
    expected_counts = {name: geometry["split_counts"][name] for name in PARTITIONS}
    membership = np.full(at.size, 255, dtype=np.uint8)
    for code, name in enumerate(PARTITIONS):
        membership[masks[name]] = code
    gap = float(np.min(at[masks["confirmatory_test"]]) - np.max(at[masks["train"]]))
    checks = {
        "source_workbook_sha256_match": sha256(args.xlsx) == geometry["source_identity"]["workbook_sha256"],
        "quantiles_exact_replay": quantiles_exact,
        "counts_match": counts == expected_counts,
        "partition_exhaustive": bool(np.all(membership != 255)),
        "partition_disjoint": int(sum(counts.values())) == at.size,
        "strict_train_to_test_gap_match": gap == geometry["at_support"]["strict_train_to_test_gap"],
        "x_only_input": True,
    }
    if not all(checks.values()):
        raise ValueError(f"Split replay failed: {checks}")
    index_hashes = {name: hash_indices(np.flatnonzero(masks[name])) for name in PARTITIONS}
    artifact = {
        "protocol": "E16-B CCPP split replay integrity audit v1",
        "status": "PASS",
        "source_identity": {
            "workbook_sha256": sha256(args.xlsx),
            "geometry_artifact_sha256": sha256(args.geometry),
            "canonical_sheet": "Sheet1",
        },
        "data_access": {"loaded_columns": list(FEATURES), "target_column_access": "prohibited; not loaded"},
        "replayed_quantiles": {"q70": q70, "q85": q85, "q90": q90, "method": "numpy.quantile(method='linear')"},
        "replayed_counts": counts,
        "strict_train_to_test_gap": gap,
        "row_index_convention": "zero-based canonical Sheet1 data rows; header excluded; SHA-256 over big-endian uint32 bytes",
        "partition_index_sha256": index_hashes,
        "partition_membership_sha256": hashlib.sha256(membership.tobytes()).hexdigest(),
        "pass_checks": checks,
        "scope": "integrity replay only; no target, model, policy, likelihood, or predictive outcome",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "pass_checks": checks}, indent=2))


if __name__ == "__main__":
    main()
