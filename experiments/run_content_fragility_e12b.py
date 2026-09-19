#!/usr/bin/env python3
"""Frozen E12-B structural content/composition fragility runner."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from run_prior_completeness_e11 import (
    GENS, M, OMEGA, PMIN, XP, Task, atom_mask, bank, sd, truth, valid_atoms,
)


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "E12B_OPERATION_CATALOG_V1.json"
OUT = ROOT / "results/content_fragility_e12b"
DELTA = 0.10


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_task(intent_name: str, intent: tuple[str, ...], generator: str, draw: int):
    """Generate one task with a task-level, fixed prefix and ambient bank."""
    x = np.linspace(0, 1, 401)
    clean = truth(intent, generator, np.random.default_rng(sd("truth", intent_name, generator, draw)), x)
    valid = valid_atoms(clean, intent, x)
    if not set(intent) <= set(valid):
        return None, "checker_reject"
    yclean = np.interp(XP, x, clean)
    rref = max(float(np.ptp(yclean)), 1e-8)
    rng_noise = np.random.default_rng(sd("noise", intent_name, generator, draw))
    yobs = yclean + rng_noise.normal(0, 0.01 * rref, len(XP))
    rng_bank = np.random.default_rng(sd("bank", intent_name, generator, draw))
    z = rng_bank.normal(0, 1, (M, 5))
    regime = rng_bank.random(M) < 0.5
    task = Task(
        f"{intent_name}:{generator}:{draw}", intent_name, intent, generator, draw,
        XP, yobs, rref, z, regime, valid, frozenset(intent), {},
    )
    fobs = bank(task, XP)
    loss = np.mean(((fobs - yobs[None, :]) / rref) ** 2, axis=1)
    logw = -(loss - loss.min()) / (2 * 0.02)
    weights = np.exp(np.clip(logw, -745, 0))
    # Preserve M total mass so the frozen pseudo-count has the intended scale.
    weights *= M / weights.sum()
    return (task, x, clean, weights), "accepted"


def scores(task: Task, weights: np.ndarray):
    fg = bank(task, OMEGA)
    masks = atom_mask(task, fg)
    ess = float(weights.sum() ** 2 / np.sum(weights ** 2))

    def score(atoms: list[str]) -> dict:
        ok = np.ones(M, dtype=bool)
        for atom in atoms:
            ok &= masks[atom]
        p_weighted = float(np.sum(weights * ok) / np.sum(weights))
        smoothed = (float(np.sum(weights * ok)) + 0.5) / (float(np.sum(weights)) + 1.0)
        floor = int(smoothed <= PMIN)
        return {
            "S": -math.log(max(smoothed, PMIN)),
            "ESS": ess,
            "N_survive": int(ok.sum()),
            "p_weighted": p_weighted,
            "floor_hit": floor,
        }

    return score


def floor_status(operation: str, full: dict, candidate: dict) -> str:
    ff, cf = bool(full["floor_hit"]), bool(candidate["floor_hit"])
    if operation == "omission":
        if cf and not ff:
            return "integrity_violation"
        if ff and cf:
            return "unresolved"
        return "lower_bound" if ff else "exact"
    if operation == "false_addition":
        if ff and not cf:
            return "integrity_violation"
        if ff and cf:
            return "unresolved"
        return "lower_bound" if cf else "exact"
    if not ff and not cf:
        return "exact"
    if cf and not ff:
        return "lower_bound"
    if ff and not cf:
        return "upper_bound"
    return "unresolved"


def violation_for_false_atom(atom: str, clean: np.ndarray, x: np.ndarray) -> tuple[float, str]:
    """Return a family-local oracle violation, never for cross-family ranking."""
    y = np.interp(OMEGA, x, clean)
    dx = OMEGA[1] - OMEGA[0]
    d1 = np.gradient(y, dx)
    d2 = np.gradient(d1, dx)
    scale = max(float(np.ptp(y)), 1e-8)
    if atom == "direction_increasing":
        return float(np.mean(d1 < -0.01 * scale)), "wrong_sign_derivative_fraction"
    if atom == "direction_decreasing":
        return float(np.mean(d1 > 0.01 * scale)), "wrong_sign_derivative_fraction"
    if atom == "curvature_concave":
        return float(np.mean(d2 > 0.04 * scale)), "wrong_sign_second_derivative_fraction"
    if atom == "curvature_convex":
        return float(np.mean(d2 < -0.04 * scale)), "wrong_sign_second_derivative_fraction"
    if atom == "lower_bound_0":
        return float(max(-np.min(y), 0.0) / scale), "normalized_boundary_violation"
    if atom == "upper_bound_0":
        return float(max(np.max(y), 0.0) / scale), "normalized_boundary_violation"
    if atom.startswith("inflection_"):
        return 1.0, "event_pattern_mismatch_indicator"
    if atom.startswith("turning_"):
        return 1.0, "event_pattern_mismatch_indicator"
    if atom == "regime_postchange":
        return 1.0, "latent_mechanism_mismatch_indicator"
    if atom.startswith("asymptote_"):
        return 1.0, "latent_mechanism_mismatch_indicator"
    raise ValueError(f"no frozen violation semantic for {atom}")


def task_rows(task: Task, weights: np.ndarray, valid: frozenset, cell: dict, clean: np.ndarray, x: np.ndarray) -> tuple[list[dict], list[dict]]:
    evaluate = scores(task, weights)
    full_atoms = cell["supplied_atoms"]
    full = evaluate(full_atoms)
    rows = [{
        "task_id": task.id, "intent_name": task.intent_name, "generator": task.gen,
        "row_role": "baseline", "operation_id": "P_full", "operation_type": "baseline",
        "source_atom": "", "target_atom": "", "candidate_atoms": "|".join(full_atoms),
        "coverage": int(set(full_atoms) <= set(valid)), "D_violation": 0.0,
        "D_violation_semantics": "not_applicable_valid_baseline",
        **full, "delta_S": 0.0, "floor_status": "baseline", "sharpness_class": "valid_baseline",
    }]
    audit = []
    for op in cell["operations"]:
        atoms = op["candidate_atoms"]
        candidate = evaluate(atoms)
        coverage = int(set(atoms) <= set(valid))
        expected = op["expected_coverage"]
        if coverage != expected:
            raise ValueError(f"coverage invariant failure {task.id} {op['id']}")
        if op["type"] == "omission":
            delta = full["S"] - candidate["S"]
            sharp_class = "coverage_preserving_omission"
            violation, violation_semantics = 0.0, "not_applicable_coverage_preserving_omission"
        else:
            delta = candidate["S"] - full["S"]
            sharp_class = (
                "inherited_sharp_wrong" if full["S"] >= DELTA and candidate["S"] >= DELTA else
                "induced_sharp_wrong" if full["S"] < DELTA and candidate["S"] >= DELTA else
                "attenuated_wrong" if full["S"] >= DELTA else "false_but_weak"
            )
            target = op.get("target_atom", op.get("added_atom", ""))
            violation, violation_semantics = violation_for_false_atom(target, clean, x)
        rows.append({
            "task_id": task.id, "intent_name": task.intent_name, "generator": task.gen,
            "row_role": "operation", "operation_id": op["id"], "operation_type": op["type"],
            "source_atom": op.get("source_atom", ""), "target_atom": op.get("target_atom", op.get("added_atom", "")),
            "candidate_atoms": "|".join(atoms), "coverage": coverage,
            "D_violation": violation, "D_violation_semantics": violation_semantics,
            **candidate, "delta_S": delta,
            "floor_status": floor_status(op["type"], full, candidate), "sharpness_class": sharp_class,
        })
        audit.append({"task_id": task.id, "operation_id": op["id"], "coverage": coverage,
                      "expected_coverage": expected, "same_ESS": int(abs(candidate["ESS"] - full["ESS"]) < 1e-10),
                      "finite_support_audit": int(np.isfinite(candidate["p_weighted"]) and candidate["N_survive"] >= 0)})
    return rows, audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("sanity", "full"), default="sanity")
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text())
    requested = 1 if args.mode == "sanity" else catalog["accepted_tasks_per_intended_triple_generator"]
    maximum = catalog["max_generation_attempts_per_cell"]
    rows, audits, accounting = [], [], []
    for cell in catalog["cells"]:
        intent = tuple(cell["supplied_atoms"])
        for generator in GENS:
            accepted = attempts = accidental = checker = 0
            for draw in range(maximum):
                if accepted >= requested:
                    break
                attempts += 1
                built, reason = make_task(cell["intent_name"], intent, generator, draw)
                if built is None:
                    checker += 1
                    continue
                task, x, clean, weights = built
                # Every false catalog operation must be actually false here.
                if any((op["expected_coverage"] == 0 and set(op["candidate_atoms"]) <= set(task.valid_atoms)) for op in cell["operations"]):
                    accidental += 1
                    continue
                rr, aa = task_rows(task, weights, task.valid_atoms, cell, clean, x)
                rows.extend(rr); audits.extend(aa); accepted += 1
            accounting.append({"intent_name": cell["intent_name"], "generator": generator,
                               "requested": requested, "attempts": attempts, "accepted": accepted,
                               "accidental_valid_rejects": accidental, "compatibility_rejects": 0,
                               "checker_rejects": checker, "catalog_operation_exclusions": 0,
                               "exhaustion": int(accepted < requested)})
    base = OUT / args.mode
    write_csv(base / "rows.csv", rows); write_csv(base / "operation_audit.csv", audits); write_csv(base / "accounting.csv", accounting)
    expected = ((sum(len(c["operations"]) for c in catalog["cells"]) + len(catalog["cells"])) * len(GENS) * requested)
    failures = [a for a in accounting if a["exhaustion"]]
    integrity = {"mode": args.mode, "catalog_sha256": sha256(CATALOG), "expected_rows": expected,
                 "actual_rows": len(rows), "exhausted_cells": len(failures),
                 "all_audits_pass": bool(all(a["same_ESS"] and a["finite_support_audit"] for a in audits))}
    (base / "integrity.json").write_text(json.dumps(integrity, indent=2) + "\n")
    if failures or len(rows) != expected or not integrity["all_audits_pass"]:
        raise SystemExit(f"integrity failure: {integrity}")
    print(json.dumps(integrity))


if __name__ == "__main__":
    main()
