#!/usr/bin/env python3
"""Generate and integrity-audit the frozen E15-D v1.2 confirmatory corpus."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import run_e15d_protected_quota_v1_2 as core


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "experiments" / "E15D_CONFIRMATORY_MANIFEST_V1_2.json"
DEFAULT_ROWS = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2" / "E15D_CONFIRMATORY_ROWS_V1_2.csv"
DEFAULT_INTEGRITY = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2" / "E15D_CONFIRMATORY_INTEGRITY_V1_2.json"
DEFAULT_SANITY = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2" / "E15D_CONFIRMATORY_SANITY_V1_2.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coefficient_grid(manifest: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    x = np.arange(int(manifest["public_grid"]["points"]), dtype=float) * float(manifest["public_grid"]["step"])
    support = manifest["support"]
    coefficients = np.arange(float(support["lower"]), float(support["upper"]) + 1e-12, float(manifest["grid_spacing"]))
    return x, coefficients


def normalized_entropy(weights: np.ndarray) -> float:
    positive = weights[weights > 0]
    return float(1.0 - (-np.sum(positive * np.log(positive))) / math.log(len(weights)))


def evidence(weights: np.ndarray) -> tuple[float, float]:
    return normalized_entropy(np.sum(weights, axis=1)), normalized_entropy(np.sum(weights, axis=0))


def joint_curve(weights: np.ndarray, coefficients: np.ndarray, x: np.ndarray) -> np.ndarray:
    return np.einsum(
        "ij,ijm->m", weights,
        x[None, None, :] + coefficients[:, None, None] * x[None, None, :] ** 2 + coefficients[None, :, None] * x[None, None, :] ** 6,
    )


def task_rows(manifest: dict[str, Any], task_id: int) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    x, coefficients = coefficient_grid(manifest)
    u_kappa, u_lambda, epsilon = core.task_draws(manifest["seed_namespace"], task_id)
    low, high = float(manifest["support"]["lower"]), float(manifest["support"]["upper"])
    kappa_truth, lambda_truth = low + (high - low) * u_kappa, low + (high - low) * u_lambda
    truth = x + kappa_truth * x**2 + lambda_truth * x**6
    y = truth + float(manifest["rho"]) * epsilon
    far = (x > float(manifest["far_window"]["lower_open"])) & (x <= float(manifest["far_window"]["upper_closed"]))
    records: list[dict[str, Any]] = []
    audits = {"finite": True, "joint_factorized_equivalent": True, "prefix_only": True}
    for exposure_name, exposure in manifest["exposures"].items():
        weights, loss = core.prefix_likelihood(y, x, float(exposure), coefficients, float(manifest["rho"]))
        e_kappa, e_lambda = evidence(weights)
        uniform, selective, factorized, point_map = core.curves(weights, loss, coefficients, x)
        additive_joint = joint_curve(weights, coefficients, x)
        audits["joint_factorized_equivalent"] &= bool(np.max(np.abs(additive_joint - factorized)) <= float(manifest["joint_factorized_equivalence_tolerance"]))
        changed_future = y.copy()
        changed_future[x > float(exposure)] += 1_000.0
        changed_weights, _ = core.prefix_likelihood(changed_future, x, float(exposure), coefficients, float(manifest["rho"]))
        audits["prefix_only"] &= bool(np.array_equal(weights, changed_weights))
        for policy, curve in zip(manifest["forecast_policies"], (uniform, selective, factorized, point_map)):
            nrmse = core.score(curve, truth, far)
            audits["finite"] &= bool(np.isfinite(nrmse) and np.isfinite(e_kappa) and np.isfinite(e_lambda))
            records.append({"task_id": task_id, "prefix_exposure": exposure_name, "policy": policy, "e_kappa": e_kappa, "e_lambda": e_lambda, "nrmse_clean_far": nrmse})
    return records, audits


def write_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["task_id", "prefix_exposure", "policy", "e_kappa", "e_lambda", "nrmse_clean_far"])
        writer.writeheader()
        writer.writerows(rows)


def integrity(rows: list[dict[str, Any]], manifest: dict[str, Any], per_task_audits: list[dict[str, bool]], manifest_path: Path, rows_path: Path) -> dict[str, Any]:
    expected = int(manifest["task_count"]) * len(manifest["exposures"]) * len(manifest["forecast_policies"])
    keys = {(row["task_id"], row["prefix_exposure"], row["policy"]) for row in rows}
    return {
        "protocol": manifest["protocol"],
        "manifest_sha256": sha256_file(manifest_path),
        "rows_sha256": sha256_file(rows_path),
        "accepted_task_count": int(manifest["task_count"]),
        "expected_row_count": expected,
        "actual_row_count": len(rows),
        "duplicate_or_missing_rows": len(keys) != expected or len(rows) != expected,
        "all_finite": all(audit["finite"] for audit in per_task_audits),
        "all_prefix_only": all(audit["prefix_only"] for audit in per_task_audits),
        "all_joint_factorized_equivalent": all(audit["joint_factorized_equivalent"] for audit in per_task_audits),
        "clean_target_scoring": manifest["far_window"]["target"] == "latent_clean_continuation",
        "final_status": "PASS" if len(keys) == expected and len(rows) == expected and all(all(audit.values()) for audit in per_task_audits) else "FAIL",
    }


def sanity(manifest: dict[str, Any]) -> dict[str, Any]:
    rows_one, audits_one = task_rows(manifest, 7)
    rows_two, audits_two = task_rows(manifest, 7)
    checks = {
        "task_seed_replay_identical": rows_one == rows_two and audits_one == audits_two,
        "nested_prefixes": float(manifest["exposures"]["L"]) < float(manifest["exposures"]["S"]) < float(manifest["exposures"]["J"]),
        "common_far_window_after_all_prefixes": float(manifest["far_window"]["lower_open"]) >= float(manifest["exposures"]["J"]),
        "clean_target_scoring": manifest["far_window"]["target"] == "latent_clean_continuation",
        "prefix_only_weights": audits_one["prefix_only"],
        "joint_factorized_equivalence": audits_one["joint_factorized_equivalent"],
        "finite_policy_rows": audits_one["finite"],
        "expected_policy_count": len(rows_one) == len(manifest["exposures"]) * len(manifest["forecast_policies"]),
        "no_acceptance_filter": manifest["no_replacement"] is True,
    }
    return {"protocol": manifest["protocol"], "checks": checks, "final_status": "PASS" if all(checks.values()) else "FAIL"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--sanity", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--integrity", type=Path, default=DEFAULT_INTEGRITY)
    parser.add_argument("--sanity-out", type=Path, default=DEFAULT_SANITY)
    args = parser.parse_args()
    if args.sanity == args.run:
        parser.error("specify exactly one of --sanity or --run")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("status") != "FROZEN":
        raise SystemExit("confirmatory run requires a frozen manifest")
    if args.sanity:
        result = sanity(manifest)
        args.sanity_out.parent.mkdir(parents=True, exist_ok=True)
        args.sanity_out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if result["final_status"] != "PASS":
            raise SystemExit("confirmatory sanity failed")
        return
    rows: list[dict[str, Any]] = []
    audits: list[dict[str, bool]] = []
    for task_id in range(int(manifest["task_count"])):
        task_records, task_audits = task_rows(manifest, task_id)
        rows.extend(task_records)
        audits.append(task_audits)
    write_rows(rows, args.rows)
    result = integrity(rows, manifest, audits, args.manifest, args.rows)
    args.integrity.parent.mkdir(parents=True, exist_ok=True)
    args.integrity.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["final_status"] != "PASS":
        raise SystemExit("confirmatory integrity failed")


if __name__ == "__main__":
    main()
