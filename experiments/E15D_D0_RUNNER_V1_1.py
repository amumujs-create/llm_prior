#!/usr/bin/env python3
"""Outcome-free E15-D0 v1.1 numerical-geometry calibration.

This module deliberately contains no policy-prediction or outcome-analysis
path. It is limited to prefix likelihood, posterior marginal entropy,
continuous continuation distinctness, and frozen construct gates.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "experiments" / "E15D_D0_RUNTIME_CONFIG_PROPOSED.json"
DEFAULT_SCHEMA = ROOT / "experiments" / "E15D_D0_ARTIFACT_SCHEMA_V1_1.json"
DEFAULT_OUTPUT = ROOT / "results" / "prior_utilization_e15d" / "d0_v1_1" / "E15D_D0_ARTIFACT_V1_1.json"
DEFAULT_SANITY_OUTPUT = ROOT / "results" / "prior_utilization_e15d" / "d0_v1_1" / "E15D_D0_SANITY_V1_1.json"
FORBIDDEN_FUNCTION_NAMES = {
    "rmse", "nrmse", "crps", "d1", "d2", "d_dep", "d3",
    "joint_uniform", "kappa_selective", "factorized_joint_weighted",
    "joint_weighted", "joint_map",
}


@dataclass(frozen=True)
class Support:
    name: str
    lower: float
    upper: float


@dataclass(frozen=True)
class ExposureTriple:
    name: str
    L: float
    S: float
    J: float


@dataclass(frozen=True)
class Candidate:
    support: Support
    grid_spacing: float
    rho: float
    exposure: ExposureTriple
    far_horizon: float

    @property
    def candidate_id(self) -> str:
        return (
            f"{self.support.name}_dq{self.grid_spacing:g}_rho{self.rho:g}_"
            f"{self.exposure.name}_far{self.far_horizon:g}"
        )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_seed(namespace: str, task_id: int) -> int:
    payload = f"{namespace}:task:{task_id}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False) % (2**63)


def task_latents(namespace: str, task_id: int, points: int) -> tuple[float, float, np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(task_seed(namespace, task_id)))
    return float(rng.random()), float(rng.random()), rng.standard_normal(points)


def public_grid(config: dict[str, Any]) -> np.ndarray:
    grid = config["public_observation_grid"]
    expected = int(grid["points"])
    values = np.arange(expected, dtype=float) * float(grid["step"]) + float(grid["start"])
    if not np.isclose(values[-1], float(grid["stop"]), atol=0.0, rtol=0.0):
        raise ValueError("public observation grid does not include the frozen endpoint")
    return values


def coefficient_grid(support: Support, spacing: float) -> np.ndarray:
    count = int(round((support.upper - support.lower) / spacing))
    values = support.lower + spacing * np.arange(count + 1, dtype=float)
    if not np.isclose(values[-1], support.upper, atol=1e-12, rtol=0.0):
        raise ValueError("support is not exactly represented by frozen coefficient grid")
    return values


def exact_continuous_rms(delta_kappa: float, delta_lambda: float, x_j: float, x_far: float) -> float:
    if not x_far > x_j:
        raise ValueError("far horizon must exceed J exposure")
    width = x_far - x_j
    term_kappa = delta_kappa**2 * (x_far**5 - x_j**5) / (5.0 * width)
    term_cross = 2.0 * delta_kappa * delta_lambda * (x_far**9 - x_j**9) / (9.0 * width)
    term_lambda = delta_lambda**2 * (x_far**13 - x_j**13) / (13.0 * width)
    return math.sqrt(max(0.0, term_kappa + term_cross + term_lambda))


def dense_rms(delta_kappa: float, delta_lambda: float, x_j: float, x_far: float) -> float:
    x = np.linspace(x_j, x_far, 2_000_001, dtype=float)
    delta = delta_kappa * x**2 + delta_lambda * x**6
    return float(math.sqrt(np.trapezoid(delta**2, x) / (x_far - x_j)))


def find_four_clique(kappas: np.ndarray, lambdas: np.ndarray, x_j: float, x_far: float, threshold: float) -> dict[str, Any]:
    vertices = [(float(kappa), float(lam)) for kappa in kappas for lam in lambdas]
    adjacency: list[set[int]] = [set() for _ in vertices]
    for i, (ki, li) in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            kj, lj = vertices[j]
            if exact_continuous_rms(ki - kj, li - lj, x_j, x_far) >= threshold:
                adjacency[i].add(j)
                adjacency[j].add(i)

    def extend(chosen: list[int], available: list[int]) -> list[int] | None:
        if len(chosen) == 4:
            return chosen
        if len(chosen) + len(available) < 4:
            return None
        for offset, vertex in enumerate(available):
            future = [other for other in available[offset + 1:] if other in adjacency[vertex]]
            result = extend(chosen + [vertex], future)
            if result is not None:
                return result
        return None

    witness_indices = extend([], list(range(len(vertices))))
    if witness_indices is None:
        return {"status": "FAIL", "clique_size": 0, "witness": [], "minimum_pairwise_distance": None}
    witness = [vertices[index] for index in witness_indices]
    distances = [
        exact_continuous_rms(ki - kj, li - lj, x_j, x_far)
        for (ki, li), (kj, lj) in itertools.combinations(witness, 2)
    ]
    return {
        "status": "PASS",
        "clique_size": 4,
        "witness": [{"kappa": kappa, "lambda": lam} for kappa, lam in witness],
        "minimum_pairwise_distance": float(min(distances)),
    }


def stable_weights(loss: np.ndarray) -> np.ndarray:
    shifted = -(loss - np.min(loss))
    mass = np.exp(shifted)
    return mass / np.sum(mass)


def normalized_entropy(weights: np.ndarray) -> float:
    positive = weights[weights > 0.0]
    entropy = -float(np.sum(positive * np.log(positive)))
    value = 1.0 - entropy / math.log(len(weights))
    return min(1.0, max(0.0, value))


def prefix_loss_grid(y: np.ndarray, x: np.ndarray, mask: np.ndarray, kappas: np.ndarray, lambdas: np.ndarray, rho: float) -> np.ndarray:
    residual = y[mask] - x[mask]
    x2 = x[mask] ** 2
    x6 = x[mask] ** 6
    syy = float(residual @ residual)
    syk = float(residual @ x2)
    syl = float(residual @ x6)
    skk = float(x2 @ x2)
    skl = float(x2 @ x6)
    sll = float(x6 @ x6)
    k = kappas[:, None]
    lam = lambdas[None, :]
    sse = syy - 2.0 * k * syk - 2.0 * lam * syl + k**2 * skk + 2.0 * k * lam * skl + lam**2 * sll
    return np.maximum(sse, 0.0) / (2.0 * rho**2)


def evidence_for_prefix(y: np.ndarray, x: np.ndarray, exposure: float, kappas: np.ndarray, lambdas: np.ndarray, rho: float) -> tuple[float, float, dict[str, float]]:
    mask = x <= exposure
    loss = prefix_loss_grid(y, x, mask, kappas, lambdas, rho)
    weights = stable_weights(loss)
    marginal_kappa = np.sum(weights, axis=1)
    marginal_lambda = np.sum(weights, axis=0)
    diagnostics = {
        "joint_weight_sum": float(np.sum(weights)),
        "kappa_weight_sum": float(np.sum(marginal_kappa)),
        "lambda_weight_sum": float(np.sum(marginal_lambda)),
        "finite": bool(np.all(np.isfinite(loss)) and np.all(np.isfinite(weights))),
    }
    return normalized_entropy(marginal_kappa), normalized_entropy(marginal_lambda), diagnostics


def quantile_summary(values: list[float]) -> dict[str, float]:
    q05, median, q95 = np.quantile(np.asarray(values, dtype=float), [0.05, 0.5, 0.95], method="linear")
    return {"q05": float(q05), "median": float(median), "q95": float(q95)}


def candidate_from_dict(support_item: dict[str, Any], spacing: float, rho: float, triple_item: dict[str, Any], horizon: float) -> Candidate:
    return Candidate(
        support=Support(str(support_item["name"]), float(support_item["lower"]), float(support_item["upper"])),
        grid_spacing=float(spacing), rho=float(rho),
        exposure=ExposureTriple(str(triple_item["name"]), float(triple_item["L"]), float(triple_item["S"]), float(triple_item["J"])),
        far_horizon=float(horizon),
    )


def candidate_ladder(config: dict[str, Any], reverse: bool = False) -> list[Candidate]:
    ladder = config["candidate_ladders"]
    candidates = [
        candidate_from_dict(support, spacing, rho, triple, horizon)
        for support in ladder["supports"]
        for spacing in ladder["grid_spacings"]
        for rho in ladder["rhos"]
        for triple in ladder["exposure_triples"]
        for horizon in ladder["far_horizons"]
    ]
    if len(candidates) != 144:
        raise ValueError("frozen candidate ladder must contain exactly 144 candidates")
    return list(reversed(candidates)) if reverse else candidates


def candidate_record(candidate: Candidate, config: dict[str, Any]) -> dict[str, Any]:
    x = public_grid(config)
    kappas = coefficient_grid(candidate.support, candidate.grid_spacing)
    lambdas = coefficient_grid(candidate.support, candidate.grid_spacing)
    namespace = config["rng"]["seed_namespace"]
    evidence_values = {regime: {"E_kappa": [], "E_lambda": []} for regime in ("L", "S", "J")}
    all_finite = True
    maximum_weight_error = 0.0
    for task_id in range(config["discarded_calibration"]["task_count"]):
        u_kappa, u_lambda, epsilon = task_latents(namespace, task_id, len(x))
        kappa_truth = candidate.support.lower + (candidate.support.upper - candidate.support.lower) * u_kappa
        lambda_truth = candidate.support.lower + (candidate.support.upper - candidate.support.lower) * u_lambda
        y = x + kappa_truth * x**2 + lambda_truth * x**6 + candidate.rho * epsilon
        for regime in ("L", "S", "J"):
            e_kappa, e_lambda, diagnostic = evidence_for_prefix(y, x, getattr(candidate.exposure, regime), kappas, lambdas, candidate.rho)
            evidence_values[regime]["E_kappa"].append(e_kappa)
            evidence_values[regime]["E_lambda"].append(e_lambda)
            all_finite = all_finite and bool(diagnostic["finite"])
            maximum_weight_error = max(maximum_weight_error, *(abs(diagnostic[key] - 1.0) for key in ("joint_weight_sum", "kappa_weight_sum", "lambda_weight_sum")))
    evidence = {
        regime: {dimension: quantile_summary(values) for dimension, values in dimensions.items()}
        for regime, dimensions in evidence_values.items()
    }
    distinctness = find_four_clique(
        kappas, lambdas, candidate.exposure.J, candidate.far_horizon,
        float(config["continuation_distinctness"]["threshold"]),
    )
    failures = construct_failures(evidence, distinctness, all_finite, maximum_weight_error)
    return {
        "candidate_id": candidate.candidate_id,
        "support": {"name": candidate.support.name, "lower": candidate.support.lower, "upper": candidate.support.upper},
        "grid_spacing": candidate.grid_spacing,
        "rho": candidate.rho,
        "exposure_triple": {"name": candidate.exposure.name, "L": candidate.exposure.L, "S": candidate.exposure.S, "J": candidate.exposure.J},
        "far_horizon": candidate.far_horizon,
        "evidence": evidence,
        "distinctness": distinctness,
        "numerical_stability": {"finite": all_finite, "maximum_weight_sum_error": maximum_weight_error},
        "construct_gate": "PASS" if not failures else "FAIL",
        "failure_reasons": failures,
    }


def construct_failures(evidence: dict[str, Any], distinctness: dict[str, Any], finite: bool, max_weight_error: float) -> list[str]:
    med = lambda regime, dimension: evidence[regime][dimension]["median"]
    q = lambda regime, dimension, quantile: evidence[regime][dimension][quantile]
    failures: list[str] = []
    checks = {
        "L_kappa_not_weak": med("L", "E_kappa") <= 0.05,
        "L_lambda_not_weak": med("L", "E_lambda") <= 0.05,
        "S_kappa_increment_below_gate": med("S", "E_kappa") - med("L", "E_kappa") >= 0.10,
        "S_lambda_not_weak": med("S", "E_lambda") <= 0.05,
        "S_dimension_separation_below_gate": med("S", "E_kappa") - med("S", "E_lambda") >= 0.10,
        "J_lambda_increment_below_gate": med("J", "E_lambda") - med("S", "E_lambda") >= 0.10,
        "J_lambda_below_gate": med("J", "E_lambda") >= 0.10,
        "J_kappa_regresses": med("J", "E_kappa") >= med("S", "E_kappa"),
        "kappa_adjacent_overlap_absent": q("L", "E_kappa", "q95") > q("S", "E_kappa", "q05"),
        "lambda_adjacent_overlap_absent": q("S", "E_lambda", "q95") > q("J", "E_lambda", "q05"),
        "distinctness_clique_absent": distinctness["status"] == "PASS",
        "nonfinite_numerics": finite,
        "weight_normalization_failure": max_weight_error <= 1e-12,
    }
    for name, passed in checks.items():
        if not passed:
            failures.append(name)
    return failures


def forbidden_function_audit() -> dict[str, Any]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    defined = {node.name.lower() for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return {"defined_functions": sorted(defined), "forbidden_present": sorted(defined & FORBIDDEN_FUNCTION_NAMES), "passed": not bool(defined & FORBIDDEN_FUNCTION_NAMES)}


def dependence_equivalence_audit(x: np.ndarray) -> dict[str, float | bool]:
    """Audit the additive identity with fixed, non-factorized normalized weights."""
    kappas = np.array([0.10, 0.55, 0.90], dtype=float)
    lambdas = np.array([0.10, 0.60, 0.90], dtype=float)
    weights = np.array([[0.03, 0.12, 0.05], [0.16, 0.07, 0.18], [0.11, 0.22, 0.06]], dtype=float)
    weights /= np.sum(weights)
    marginal_kappa = np.sum(weights, axis=1)
    marginal_lambda = np.sum(weights, axis=0)
    continuations = x[None, None, :] + kappas[:, None, None] * x[None, None, :] ** 2 + lambdas[None, :, None] * x[None, None, :] ** 6
    full_mixture = np.einsum("ij,ijm->m", weights, continuations)
    factorized_mixture = np.einsum("ij,ijm->m", marginal_kappa[:, None] * marginal_lambda[None, :], continuations)
    grid_maximum = float(np.max(np.abs(full_mixture - factorized_mixture)))
    full_kappa = float(np.sum(kappas[:, None] * weights))
    full_lambda = float(np.sum(lambdas[None, :] * weights))
    factor_kappa = float(np.sum(kappas * marginal_kappa))
    factor_lambda = float(np.sum(lambdas * marginal_lambda))
    continuous_supremum_bound = abs(full_kappa - factor_kappa) + abs(full_lambda - factor_lambda)
    return {
        "maximum_absolute_difference_on_public_grid": grid_maximum,
        "continuous_supremum_bound": continuous_supremum_bound,
        "tolerance": 1e-12,
        "passed": max(grid_maximum, continuous_supremum_bound) <= 1e-12,
    }


def validate_schema_instance(instance: Any, schema: dict[str, Any], root: dict[str, Any], path: str = "$") -> None:
    if "$ref" in schema:
        reference = schema["$ref"]
        if not reference.startswith("#/"):
            raise ValueError(f"unsupported schema reference at {path}: {reference}")
        target: Any = root
        for component in reference[2:].split("/"):
            target = target[component]
        validate_schema_instance(instance, target, root, path)
        return
    expected_type = schema.get("type")
    if expected_type is not None:
        allowed = expected_type if isinstance(expected_type, list) else [expected_type]
        types = {
            "object": lambda value: isinstance(value, dict),
            "array": lambda value: isinstance(value, list),
            "string": lambda value: isinstance(value, str),
            "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
            "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
            "null": lambda value: value is None,
        }
        if not any(types[name](instance) for name in allowed):
            raise ValueError(f"schema type mismatch at {path}: expected {allowed}")
    if "const" in schema and instance != schema["const"]:
        raise ValueError(f"schema const mismatch at {path}")
    if "enum" in schema and instance not in schema["enum"]:
        raise ValueError(f"schema enum mismatch at {path}")
    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for required in schema.get("required", []):
            if required not in instance:
                raise ValueError(f"schema required field missing at {path}: {required}")
        if schema.get("additionalProperties") is False:
            extra = set(instance) - set(properties)
            if extra:
                raise ValueError(f"schema additional properties at {path}: {sorted(extra)}")
        for key, value in instance.items():
            if key in properties:
                validate_schema_instance(value, properties[key], root, f"{path}.{key}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            raise ValueError(f"schema minItems mismatch at {path}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            raise ValueError(f"schema maxItems mismatch at {path}")
        if "items" in schema:
            for index, value in enumerate(instance):
                validate_schema_instance(value, schema["items"], root, f"{path}[{index}]")


def validate_artifact_schema(artifact: dict[str, Any], schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validate_schema_instance(artifact, schema, schema)


def sanity_checks(config: dict[str, Any]) -> dict[str, Any]:
    x = public_grid(config)
    namespace = config["rng"]["seed_namespace"]
    first = task_latents(namespace, 17, len(x))
    second = task_latents(namespace, 17, len(x))
    replay = bool(first[0] == second[0] and first[1] == second[1] and np.array_equal(first[2], second[2]))
    triple = ExposureTriple("T1", 0.25, 0.55, 0.80)
    nested = bool(np.all((x <= triple.L) <= (x <= triple.S)) and np.all((x <= triple.S) <= (x <= triple.J)))
    candidate = candidate_ladder(config)[0]
    record_one = candidate_record(candidate, config)
    record_two = candidate_record(candidate, config)
    repeated = record_one == record_two
    kappas = coefficient_grid(candidate.support, candidate.grid_spacing)
    lambdas = coefficient_grid(candidate.support, candidate.grid_spacing)
    u_kappa, u_lambda, epsilon = task_latents(namespace, 3, len(x))
    y = x + (candidate.support.lower + (candidate.support.upper - candidate.support.lower) * u_kappa) * x**2 + (candidate.support.lower + (candidate.support.upper - candidate.support.lower) * u_lambda) * x**6 + candidate.rho * epsilon
    baseline_evidence = evidence_for_prefix(y, x, candidate.exposure.S, kappas, lambdas, candidate.rho)[:2]
    y_future_changed = y.copy()
    y_future_changed[x > candidate.exposure.S] += 10_000.0
    leakage_invariant = baseline_evidence == evidence_for_prefix(y_future_changed, x, candidate.exposure.S, kappas, lambdas, candidate.rho)[:2]
    exact = exact_continuous_rms(0.37, -0.23, triple.J, 1.0)
    dense = dense_rms(0.37, -0.23, triple.J, 1.0)
    rms_ok = abs(exact - dense) <= 1e-8
    clique_pass = find_four_clique(np.array([0.0, 0.1]), np.array([0.0, 0.1]), 0.8, 1.0, 0.01)["status"] == "PASS"
    clique_fail = find_four_clique(np.array([0.0]), np.array([0.0, 0.001, 0.002]), 0.8, 1.0, 0.01)["status"] == "FAIL"
    forward_latents = [task_latents(namespace, task_id, len(x)) for task_id in range(8)]
    _ = candidate_ladder(config, reverse=True)
    reverse_latents = [task_latents(namespace, task_id, len(x)) for task_id in range(8)]
    order_invariant = all(
        left[0] == right[0] and left[1] == right[1] and np.array_equal(left[2], right[2])
        for left, right in zip(forward_latents, reverse_latents)
    )
    forbidden = forbidden_function_audit()
    dependence = dependence_equivalence_audit(x)
    schema_probe = {
        "protocol": "E15-D0-v1.1",
        "discarded_calibration": {"seed_namespace": namespace},
        "source_hashes": {"runner_sha256": "x", "config_sha256": "x", "schema_sha256": "x", "implementation_addendum_sha256": config["implementation_addendum_sha256"], "contract_sha256": config["source_contract_sha256"]},
        "selection_rule": config["selection_priority"],
        "candidate_count": 144,
        "candidates": [record_one] * 144,
        "selected_candidate": record_one,
        "final_status": "PASS",
    }
    try:
        validate_artifact_schema(schema_probe, DEFAULT_SCHEMA)
        schema_validation = True
    except ValueError:
        schema_validation = False
    checks = {
        "task_seed_replay_identical": replay,
        "candidate_order_does_not_change_latents": order_invariant,
        "nested_prefixes": nested,
        "same_candidate_repeats_identically": repeated,
        "weight_and_entropy_stability": record_one["numerical_stability"]["maximum_weight_sum_error"] <= 1e-12,
        "continuous_rms_matches_dense_integration": rms_ok,
        "synthetic_clique_pass": clique_pass,
        "synthetic_clique_fail": clique_fail,
        "future_label_leakage_absent": leakage_invariant,
        "forbidden_outcome_functions_absent": forbidden["passed"],
        "dependence_equivalence": bool(dependence["passed"]),
        "artifact_schema_validation": schema_validation,
    }
    return {"protocol": "E15-D0-v1.1", "checks": checks, "forbidden_function_audit": forbidden, "dependence_equivalence_audit": dependence, "final_status": "PASS" if all(checks.values()) else "FAIL"}


def build_artifact(config: dict[str, Any], config_path: Path, schema_path: Path) -> dict[str, Any]:
    records = [candidate_record(candidate, config) for candidate in candidate_ladder(config)]
    selected = next((record for record in records if record["construct_gate"] == "PASS"), None)
    artifact = {
        "protocol": "E15-D0-v1.1",
        "discarded_calibration": {"seed_namespace": config["rng"]["seed_namespace"], "task_id_start": 0, "task_id_end": 399, "task_count": 400, "no_replacement": True},
        "source_hashes": {"runner_sha256": sha256_file(Path(__file__)), "config_sha256": sha256_file(config_path), "schema_sha256": sha256_file(schema_path), "implementation_addendum_sha256": config["implementation_addendum_sha256"], "contract_sha256": config["source_contract_sha256"]},
        "selection_rule": config["selection_priority"],
        "candidate_count": len(records),
        "candidates": records,
        "selected_candidate": selected,
        "final_status": "PASS" if selected is not None else "FAIL",
    }
    reject_outcome_keys(artifact)
    validate_artifact_schema(artifact, schema_path)
    return artifact


def reject_outcome_keys(value: Any) -> None:
    forbidden_fragments = ("rmse", "crps", "d1", "d2", "d_dep", "d3", "winner", "ranking", "policy")
    if isinstance(value, dict):
        for key, item in value.items():
            if any(fragment in key.lower() for fragment in forbidden_fragments):
                raise ValueError(f"outcome-related key prohibited in D0 artifact: {key}")
            reject_outcome_keys(item)
    elif isinstance(value, list):
        for item in value:
            reject_outcome_keys(item)


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--sanity", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--sanity-out", type=Path, default=DEFAULT_SANITY_OUTPUT)
    args = parser.parse_args()
    if args.sanity == args.run:
        parser.error("specify exactly one of --sanity or --run")
    config = load_config(args.config)
    if args.sanity:
        result = sanity_checks(config)
        args.sanity_out.parent.mkdir(parents=True, exist_ok=True)
        args.sanity_out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if result["final_status"] != "PASS":
            raise SystemExit("E15-D0 sanity failed")
        return
    if config.get("status") != "FROZEN":
        raise SystemExit("formal D0 requires runtime config status FROZEN")
    artifact = build_artifact(config, args.config, args.schema)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
