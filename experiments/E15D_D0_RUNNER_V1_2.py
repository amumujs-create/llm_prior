#!/usr/bin/env python3
"""Outcome-free E15-D0 v1.2 calibration adapter.

Version 1.2 inherits all v1.1 numerical machinery but removes only the two
cross-sectional adjacent-overlap construct gates. It contains no predictive
policy or outcome-analysis path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import E15D_D0_RUNNER_V1_1 as base


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "experiments" / "E15D_D0_RUNTIME_CONFIG_V1_2_PROPOSED.json"
DEFAULT_SCHEMA = ROOT / "experiments" / "E15D_D0_ARTIFACT_SCHEMA_V1_2.json"
DEFAULT_OUTPUT = ROOT / "results" / "prior_utilization_e15d" / "d0_v1_2" / "E15D_D0_ARTIFACT_V1_2.json"
DEFAULT_SANITY_OUTPUT = ROOT / "results" / "prior_utilization_e15d" / "d0_v1_2" / "E15D_D0_SANITY_V1_2.json"


def construct_failures_without_overlap(evidence: dict[str, Any], distinctness: dict[str, Any], finite: bool, max_weight_error: float) -> list[str]:
    med = lambda regime, dimension: evidence[regime][dimension]["median"]
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
        "distinctness_clique_absent": distinctness["status"] == "PASS",
        "nonfinite_numerics": finite,
        "weight_normalization_failure": max_weight_error <= 1e-12,
    }
    for name, passed in checks.items():
        if not passed:
            failures.append(name)
    return failures


# The frozen v1.1 candidate evaluator resolves this name in its own module at
# runtime. The adapter changes only the versioned failure predicate.
base.construct_failures = construct_failures_without_overlap


def source_hashes(config: dict[str, Any], config_path: Path, schema_path: Path) -> dict[str, Any]:
    return {
        "runner_sha256": base.sha256_file(Path(__file__)),
        "foundation_runner_sha256": base.sha256_file(Path(base.__file__)),
        "config_sha256": base.sha256_file(config_path),
        "schema_sha256": base.sha256_file(schema_path),
        "implementation_addendum_sha256": config["implementation_addendum_sha256"],
        "inherited_implementation_addendum_sha256": config["inherited_implementation_addendum_sha256"],
        "contract_sha256": config["source_contract_sha256"],
    }


def schema_probe(config: dict[str, Any]) -> dict[str, Any]:
    record = base.candidate_record(base.candidate_ladder(config)[0], config)
    return {
        "protocol": "E15-D0-v1.2",
        "discarded_calibration": {"seed_namespace": config["rng"]["seed_namespace"]},
        "source_hashes": source_hashes(config, DEFAULT_CONFIG, DEFAULT_SCHEMA),
        "selection_rule": config["selection_priority"],
        "candidate_count": 144,
        "candidates": [record] * 144,
        "selected_candidate": record,
        "final_status": "PASS",
    }


def sanity_checks(config: dict[str, Any], schema_path: Path) -> dict[str, Any]:
    inherited = base.sanity_checks(config)
    try:
        base.validate_artifact_schema(schema_probe(config), schema_path)
        schema_validation = True
    except ValueError:
        schema_validation = False
    first_record = base.candidate_record(base.candidate_ladder(config)[0], config)
    removed_overlap_absent = not any(
        reason in first_record["failure_reasons"]
        for reason in ("kappa_adjacent_overlap_absent", "lambda_adjacent_overlap_absent")
    )
    checks = dict(inherited["checks"])
    checks["v1_2_schema_validation"] = schema_validation
    checks["adjacent_overlap_gates_removed"] = removed_overlap_absent
    return {
        "protocol": "E15-D0-v1.2",
        "checks": checks,
        "dependence_equivalence_audit": inherited["dependence_equivalence_audit"],
        "forbidden_function_audit": inherited["forbidden_function_audit"],
        "final_status": "PASS" if all(checks.values()) else "FAIL",
    }


def build_artifact(config: dict[str, Any], config_path: Path, schema_path: Path) -> dict[str, Any]:
    records = [base.candidate_record(candidate, config) for candidate in base.candidate_ladder(config)]
    selected = next((record for record in records if record["construct_gate"] == "PASS"), None)
    artifact = {
        "protocol": "E15-D0-v1.2",
        "discarded_calibration": {"seed_namespace": config["rng"]["seed_namespace"], "task_id_start": 0, "task_id_end": 399, "task_count": 400, "no_replacement": True},
        "source_hashes": source_hashes(config, config_path, schema_path),
        "selection_rule": config["selection_priority"],
        "candidate_count": len(records),
        "candidates": records,
        "selected_candidate": selected,
        "final_status": "PASS" if selected is not None else "FAIL",
    }
    base.reject_outcome_keys(artifact)
    base.validate_artifact_schema(artifact, schema_path)
    return artifact


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
    config = base.load_config(args.config)
    if config["protocol"] != "E15-D0-v1.2":
        raise SystemExit("v1.2 runner requires an E15-D0-v1.2 runtime config")
    if args.sanity:
        result = sanity_checks(config, args.schema)
        args.sanity_out.parent.mkdir(parents=True, exist_ok=True)
        args.sanity_out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if result["final_status"] != "PASS":
            raise SystemExit("E15-D0 v1.2 sanity failed")
        return
    if config.get("status") != "FROZEN":
        raise SystemExit("formal D0 requires runtime config status FROZEN")
    artifact = build_artifact(config, args.config, args.schema)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
