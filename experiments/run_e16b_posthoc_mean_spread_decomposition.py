"""Post-hoc mean-spread CRPS decomposition using frozen E16-B predictions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.special import ndtr

from run_e16b_ccpp_final_b1_crps import SEED, read_confirmatory_target_only
from run_e16b_ccpp_train_capacity import sha256


RHOS = (0.0, 0.25, 0.5, 0.75, 1.0)
BOOTSTRAP_REPLICATES = 5000
TOLERANCE = 1e-12


def a_function(difference: np.ndarray, scale: np.ndarray | float) -> np.ndarray:
    z = difference / scale
    return 2.0 * scale * np.exp(-0.5 * z**2) / np.sqrt(2.0 * np.pi) + difference * (2.0 * ndtr(z) - 1.0)


def gaussian_crps(y: np.ndarray, mean: np.ndarray, scale: np.ndarray | float) -> np.ndarray:
    return a_function(y - mean, scale) - 0.5 * a_function(np.zeros_like(y), np.sqrt(2.0) * scale)


def mixture_crps(y: np.ndarray, means: np.ndarray, weights: np.ndarray, sigma: float, batch_size: int = 8) -> np.ndarray:
    output = np.empty(y.size, dtype=float)
    pair_scale = np.sqrt(2.0) * sigma
    for start in range(0, y.size, batch_size):
        stop = min(start + batch_size, y.size)
        current = means[start:stop]
        first = np.sum(weights * a_function(y[start:stop, None] - current, sigma), axis=1)
        pair = a_function(current[:, :, None] - current[:, None, :], pair_scale)
        output[start:stop] = first - 0.5 * np.einsum("i,bij,j->b", weights, pair, weights, optimize=True)
    return output


def bootstrap_terms(terms: dict[str, np.ndarray]) -> tuple[dict[str, dict[str, float]], float]:
    keys = list(terms)
    values = np.column_stack([terms[key] for key in keys])
    generator = np.random.Generator(np.random.PCG64(SEED))
    indices = generator.integers(0, values.shape[0], size=(BOOTSTRAP_REPLICATES, values.shape[0]), endpoint=False)
    boot = np.mean(values[indices], axis=1)
    results = {}
    for column, key in enumerate(keys):
        lower, upper = np.quantile(boot[:, column], [0.025, 0.975], method="linear")
        results[key] = {"mean": float(np.mean(values[:, column])), "ci_2_5": float(lower), "ci_97_5": float(upper)}
    identity_error = float(np.max(np.abs(boot[:, keys.index("recovery_total")] - (boot[:, keys.index("center_change")] + boot[:, keys.index("variance_change")] + boot[:, keys.index("shape_change")]))) )
    return results, identity_error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--components", type=Path, required=True)
    parser.add_argument("--prediction-manifest", type=Path, required=True)
    parser.add_argument("--b1", type=Path, required=True)
    parser.add_argument("--b2", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.prediction_manifest.read_text())
    b1 = json.loads(args.b1.read_text())
    b2 = json.loads(args.b2.read_text())
    if sha256(args.components) != manifest["component_artifact"]["sha256"]:
        raise ValueError("Frozen component artifact hash mismatch")
    with np.load(args.components, allow_pickle=False) as data:
        indices = data["test_indices"]
        base_means = data["component_means"]
        uniform_weights = data["uniform_weights"]
        weighted_weights = data["weighted_weights"]
        sigma = float(data["sigma_ref"])
        map_index = int(data["map_index"])
    target_indices, target = read_confirmatory_target_only(args.xlsx)
    if not np.array_equal(indices, target_indices) or base_means.shape != (956, 405):
        raise ValueError("Frozen inputs do not match confirmatory rows")
    capacity = json.loads(Path("results/prior_utilization_e16b/train_capacity_v1/E16B_CCPP_TRAIN_CAPACITY_V1.json").read_text())
    y = (target - capacity["train_target_normalization"]["median"]) / capacity["train_target_normalization"]["iqr"]
    policies = {"uniform": uniform_weights, "weighted": weighted_weights}
    crps_f: dict[str, dict[float, np.ndarray]] = {name: {} for name in policies}
    crps_g: dict[str, dict[float, np.ndarray]] = {name: {} for name in policies}
    audit = {"mean_preservation_max_abs": {}, "variance_match_max_abs": {}, "rho_zero_single_gaussian_max_abs": {}}
    for name, weights in policies.items():
        # Explicit finite checks below are authoritative; avoid stale BLAS
        # floating-point warning flags observed in this local runtime.
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            mean = base_means @ weights
        if not np.isfinite(mean).all():
            raise ValueError("Nonfinite frozen mixture mean")
        centered = base_means - mean[:, None]
        variance = np.sum(weights * centered**2, axis=1)
        for rho in RHOS:
            transformed = mean[:, None] + rho * centered
            crps_f[name][rho] = mixture_crps(y, transformed, weights, sigma)
            scale = np.sqrt(sigma**2 + rho**2 * variance)
            crps_g[name][rho] = gaussian_crps(y, mean, scale)
            with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
                reconstructed_mean = transformed @ weights
            if not np.isfinite(reconstructed_mean).all():
                raise ValueError("Nonfinite mean-preservation reconstruction")
            audit["mean_preservation_max_abs"][str(rho)] = float(np.max(np.abs(reconstructed_mean - mean)))
            audit["variance_match_max_abs"][str(rho)] = float(np.max(np.abs((sigma**2 + np.sum(weights * (transformed - mean[:, None])**2, axis=1)) - scale**2)))
            if rho == 0.0:
                audit["rho_zero_single_gaussian_max_abs"][name] = float(np.max(np.abs(crps_f[name][rho] - crps_g[name][rho])))
    crps_map = gaussian_crps(y, base_means[:, map_index], sigma)
    reproduction = {
        "weighted_minus_uniform_mean": float(np.mean(crps_f["weighted"][1.0] - crps_f["uniform"][1.0])),
        "frozen_B2_mean": b2["secondary_estimand"]["mean"],
        "weighted_minus_uniform_abs_error": float(abs(np.mean(crps_f["weighted"][1.0] - crps_f["uniform"][1.0]) - b2["secondary_estimand"]["mean"])),
        "uniform_minus_MAP_mean": float(np.mean(crps_f["uniform"][1.0] - crps_map)),
        "frozen_B1_mean": b1["primary_estimand"]["mean"],
        "uniform_minus_MAP_abs_error": float(abs(np.mean(crps_f["uniform"][1.0] - crps_map) - b1["primary_estimand"]["mean"])),
    }
    terms = {
        "retention": crps_f["weighted"][1.0] - crps_f["weighted"][0.0],
        "variance": crps_g["weighted"][1.0] - crps_f["weighted"][0.0],
        "shape": crps_f["weighted"][1.0] - crps_g["weighted"][1.0],
        "center_change": crps_f["weighted"][0.0] - crps_f["uniform"][0.0],
        "variance_change": (crps_g["weighted"][1.0] - crps_f["weighted"][0.0]) - (crps_g["uniform"][1.0] - crps_f["uniform"][0.0]),
        "shape_change": (crps_f["weighted"][1.0] - crps_g["weighted"][1.0]) - (crps_f["uniform"][1.0] - crps_g["uniform"][1.0]),
        "recovery_total": crps_f["weighted"][1.0] - crps_f["uniform"][1.0],
    }
    terms["retention_identity_error"] = terms["retention"] - (terms["variance"] + terms["shape"])
    row_identity = float(np.max(np.abs(terms["retention_identity_error"])))
    summaries, bootstrap_identity_error = bootstrap_terms({key: value for key, value in terms.items() if key != "retention_identity_error"})
    curve = {
        name: {str(rho): {"mean_CRPS": float(np.mean(crps_f[name][rho])), "difference_from_rho_0": float(np.mean(crps_f[name][rho] - crps_f[name][0.0]))} for rho in RHOS}
        for name in policies
    }
    checks = {
        "all_CRPS_finite_nonnegative": bool(all(np.isfinite(values).all() and np.all(values >= 0.0) for policy in crps_f.values() for values in policy.values()) and all(np.isfinite(values).all() and np.all(values >= 0.0) for policy in crps_g.values() for values in policy.values())),
        "mean_preservation": max(audit["mean_preservation_max_abs"].values()) <= TOLERANCE,
        "variance_match": max(audit["variance_match_max_abs"].values()) <= TOLERANCE,
        "rho_zero_single_gaussian": max(audit["rho_zero_single_gaussian_max_abs"].values()) <= TOLERANCE,
        "original_B1_reproduced": reproduction["uniform_minus_MAP_abs_error"] <= TOLERANCE,
        "original_B2_reproduced": reproduction["weighted_minus_uniform_abs_error"] <= TOLERANCE,
        "row_level_decomposition_identity": row_identity <= TOLERANCE,
        "bootstrap_decomposition_identity": bootstrap_identity_error <= TOLERANCE,
    }
    artifact = {
        "protocol": "E16-B post-hoc mean-spread decomposition v1",
        "final_status": "PASS" if all(checks.values()) else "FAIL",
        "analysis_status": "post-hoc diagnostic; not an independent confirmatory result",
        "source_hashes": {"workbook_sha256": sha256(args.xlsx), "components_sha256": sha256(args.components), "prediction_manifest_sha256": sha256(args.prediction_manifest), "B1_sha256": sha256(args.b1), "B2_sha256": sha256(args.b2), "contract_sha256": sha256(args.contract)},
        "target_access": {"confirmatory_target_rows_read": int(target.size), "validation_target_access": "none", "guard_target_access": "prohibited"},
        "fixed_inputs": {"sigma_ref": sigma, "rhos": list(RHOS), "component_shape": list(base_means.shape), "no_refit": True},
        "bootstrap": {"unit": "shared empirical confirmatory row indices across all terms", "replicates": BOOTSTRAP_REPLICATES, "generator": "NumPy PCG64", "seed": SEED, "ci": "percentile 95%, linear quantiles"},
        "weighted_spread_table": {key: summaries[key] for key in ("retention", "variance", "shape")},
        "uniform_to_weighted_recovery_table": {key: summaries[key] for key in ("center_change", "variance_change", "shape_change", "recovery_total")},
        "response_curve": curve,
        "implementation_audit": {"tolerance_normalized_target_scale": TOLERANCE, **audit, "reproduction": reproduction, "row_identity_max_abs": row_identity, "bootstrap_identity_max_abs": bootstrap_identity_error, "checks": checks},
        "interpretation_boundary": "Score-path decomposition under frozen predictive distributions; its terms are not unique causal contributions or calibrated epistemic-uncertainty recovery.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n")
    print(json.dumps({"final_status": artifact["final_status"], "weighted_retention": artifact["weighted_spread_table"]["retention"], "recovery_total": artifact["uniform_to_weighted_recovery_table"]["recovery_total"]}, indent=2))
    if artifact["final_status"] != "PASS":
        raise SystemExit("Mean-spread decomposition implementation audit failure")


if __name__ == "__main__":
    main()
