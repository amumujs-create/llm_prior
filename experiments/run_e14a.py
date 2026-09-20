#!/usr/bin/env python3
"""E14-A finite-bank measurement-scaling sanity runner.

This runner consumes the frozen E14 clean-field/scorer layers.  It never
redraws a 4096/8192 bank: every size is a prefix of one 16384 master bank.
The default invocation is the predeclared E14-A corpus; ``--cell-limit`` and
``--groups`` are deterministic smoke-test controls and are recorded as such.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import statistics
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from e14_multivariate_core import H, INTENTS, build_clean, apply_c2_intervention, exact_envelope_match, stable_seed
from e14_master_scorer import (
    direct_candidate_audit, master_latents, score_bank, completeness_gap,
    continuous_evidence,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "complexity_scaling_e14" / "e14a"
M_LEVELS = (4096, 8192, 16384)
SMOKE_M = 128
ETAS = (("low", .20), ("mid", .50), ("high", .80))
GENS = ("spline", "basis", "ode")
INTENT_NAMES = tuple(INTENTS)
SCOPES = ("limited", "intermediate", "persistent_within_tested_domain")
BRANCHES = {
    "dimension": ("dimension_d1", "dimension_d3", "dimension_d8"),
    "interaction": ("interaction_additive", "interaction_pairwise", "interaction_entangled"),
    "heterogeneity": ("heterogeneity_none", "heterogeneity_moderate", "heterogeneity_strong"),
}


def subsets(pstar: frozenset) -> list[frozenset]:
    atoms = tuple(sorted(pstar))
    return [frozenset(q) for n in range(1, len(atoms) + 1)
            for q in itertools.combinations(atoms, n)]


def group_seed(axis: str, cell_id: str, j: int) -> int:
    return stable_seed("e14-a-v1", axis, cell_id, j)


def branch_fields(intent: str, gen: str, axis: str, seed: int, scope: str):
    if axis == "dimension":
        names = BRANCHES[axis]
        hs = [(build_clean(intent, gen, b, group_seed=seed), b) for b in names]
    elif axis == "interaction":
        names = BRANCHES[axis]
        hs = [(build_clean(intent, gen, b, group_seed=seed), b) for b in names]
    else:
        names = BRANCHES[axis]
        levels = ("none", "moderate", "strong")
        hs = [(build_clean(intent, gen, "heterogeneity", heterogeneity=l, group_seed=seed), b)
              for l, b in zip(levels, names)]
    out = []
    for field, name in hs:
        base = field
        if not exact_envelope_match(*[q[0] for q in hs]):
            raise ValueError("pstar_mismatch")
        if any(v != 1 for atom in field.pstar for v in __import__("e14_multivariate_core", fromlist=["persistent_scope_table"]).persistent_scope_table(field)[1][atom]):
            raise ValueError("base_not_persistent")
        intervention = apply_c2_intervention(base, scope)
        # Measurement is recomputed by the clean scope layer; requested labels
        # are never passed to the scorer.
        out.append((name, base, intervention))
    return out


def _rank_agreement(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2:
        return 1.0
    if np.allclose(a, a[0]) and np.allclose(b, b[0]):
        return 1.0
    if np.allclose(a, a[0]) or np.allclose(b, b[0]):
        return 0.0
    r = spearmanr(a, b).statistic
    return 0.0 if not np.isfinite(r) else float(r)


def _metrics(scores, field, xi, candidates):
    # Reconstruct weighted continuation moments without changing score weights.
    from e14_master_scorer import _branch_bank
    # E9's d_eff is the participation ratio of weighted active coordinates.
    # In E14 the active bank coordinates are the four frozen master latent
    # draws xi[:, :4]; retaining this estimand avoids a giant 601x601 matrix.
    mu_xi = np.sum(scores.weights[:, None] * xi, axis=0)
    cen_xi = xi - mu_xi[None, :]
    cov_xi = np.einsum("m,mi,mj->ij", scores.weights, cen_xi, cen_xi)
    tr = float(np.trace(cov_xi))
    den = float(np.trace(cov_xi @ cov_xi))
    d_eff = 0.0 if den < 1e-12 or not np.isfinite(den) else tr * tr / den
    # V_f remains function-space dispersion on the inherited 49-point grid.
    x_eval = np.arange(49, dtype=float) / 120.
    f = _branch_bank(field, xi, x_eval)
    mu = np.sum(scores.weights[:, None, None] * f, axis=0)
    cen = f - mu[None, :, :]
    vf = float(np.mean(np.sum(scores.weights[:, None, None] * cen * cen, axis=0)))
    return d_eff, vf


def run(args):
    OUT.mkdir(parents=True, exist_ok=True)
    cell_rows = []
    measurement_rows = []
    manifest_rows = []
    integrity = {"cells": 0, "groups": 0, "branch_conditions": 0,
                 "direct_audit_failures": 0, "pstar_mismatch": 0,
                 "scope_or_base_failures": 0, "exceptions": 0}
    selections = []
    run_levels = (SMOKE_M,) if args.max_M == SMOKE_M else tuple(m for m in M_LEVELS if m <= args.max_M)
    cells = [(intent, gen, eta_name, eta, scope)
             for intent in INTENT_NAMES for gen in GENS
             for eta_name, eta in ETAS for scope in SCOPES]
    cells = cells[args.offset: args.offset + args.cell_limit if args.cell_limit else None]
    for intent, gen, eta_name, eta, scope in cells:
        cell_id = f"{intent}|{gen}|{eta_name}|{scope}"
        integrity["cells"] += 1
        vals = {axis: [] for axis in BRANCHES}
        for axis in BRANCHES:
            for j in range(args.groups):
                integrity["groups"] += 1
                seed = group_seed(axis, cell_id, j)
                try:
                    members = branch_fields(intent, gen, axis, seed, scope)
                except Exception as exc:
                    integrity["exceptions"] += 1
                    cell_rows.append({"cell_id": cell_id, "axis": axis, "status": "reject", "reason": str(exc), "group_index": j})
                    continue
                pstar = members[0][1].pstar
                cands = subsets(pstar)
                for branch_name, base, field in members:
                    integrity["branch_conditions"] += 1
                    # Ensure scope is measured from the field; no proposal
                    # metadata is used in scoring.
                    xi = master_latents(seed, M=max(M_LEVELS))
                    e_mean, e_raw = continuous_evidence(field, f"{axis}|{cell_id}|{j}", eta)
                    audit_ok = direct_candidate_audit(
                        score_bank(field, f"{axis}|{cell_id}|{j}", xi[:min(args.audit_n, max(M_LEVELS))], cands,
                                   min(args.audit_n, max(M_LEVELS))),
                        field, xi[:min(args.audit_n, max(M_LEVELS))], pstar, cands, n=min(args.audit_n, max(M_LEVELS)))
                    if not audit_ok:
                        integrity["direct_audit_failures"] += 1
                    row_by_m = {}
                    for M in run_levels:
                        if M > args.max_M:
                            continue
                        scores = score_bank(field, f"{axis}|{cell_id}|{j}", xi[:M], cands, M)
                        d_eff, vf = _metrics(scores, field, xi[:M], cands)
                        gaps = {"|".join(sorted(c)): completeness_gap(scores, pstar, c) for c in cands}
                        row_by_m[M] = (scores, gaps, d_eff, vf)
                        for c in cands:
                            gap, status = gaps["|".join(sorted(c))]
                            manifest_rows.append({"cell_id": cell_id, "axis": axis, "group_index": j,
                                "branch": branch_name, "M": M, "candidate": "|".join(sorted(c)),
                                "pstar": "|".join(sorted(pstar)), "S": scores.sharpness[c],
                                "ESS": scores.ess, "N_survive": scores.support[c],
                                "floor": int(scores.floor_by_candidate[c]), "delta_S_miss": gap,
                                "gap_status": status, "d_eff": d_eff, "V_f": vf,
                                "E_a": json.dumps({a: e_mean.get(a) for a in sorted(c)}, sort_keys=True),
                                "E_a_raw": json.dumps({a: e_raw.get(a) for a in sorted(c)}, sort_keys=True),
                                "E_min": float(min(e_mean.get(a, float("nan")) for a in c)),
                                "direct_audit": int(audit_ok), "eta": eta, "requested_scope": scope})
                    vals[axis].append((branch_name, row_by_m))
        for axis, records in vals.items():
            if not records:
                continue
            # Convergence cells are base-cell x primary axis x realized branch
            # condition. Never pool d=1/d=3/d=8 (or add/pair/ent) here.
            by_branch = {}
            for branch_name, rb in records:
                by_branch.setdefault(branch_name, []).append(rb)
            for branch_name, branch_records in by_branch.items():
                ref_records = [rb for rb in branch_records if 16384 in rb]
                for M in (4096, 8192):
                    if M > args.max_M or not ref_records:
                        continue
                    sdiff = []; gdiff = []; floor_agree = []; ranks = []; exact_n = 0
                    for rb in ref_records:
                        a_s, a_g, _, _ = rb[M]; b_s, b_g, _, _ = rb[16384]
                        keys = [c for c in cands if c in a_s.sharpness and c in b_s.sharpness]
                        sdiff.extend(abs(a_s.sharpness[c] - b_s.sharpness[c]) for c in keys)
                        floor_agree.extend(a_s.floor_by_candidate[c] == b_s.floor_by_candidate[c] for c in keys)
                        proper = [c for c in keys if c != pstar]
                        ex = [c for c in proper if a_g["|".join(sorted(c))][1] == "exact" and b_g["|".join(sorted(c))][1] == "exact"]
                        gdiff.extend(abs(a_g["|".join(sorted(c))][0] - b_g["|".join(sorted(c))][0]) for c in ex)
                        exact_n += len(ex)
                        ranks.append(_rank_agreement(np.array([a_s.sharpness[c] for c in keys]), np.array([b_s.sharpness[c] for c in keys])))
                    cell_rows.append({"cell_id": cell_id, "axis": axis, "branch": branch_name, "status": "diagnostic", "M": M,
                        "p95_S_abs_diff": float(np.quantile(sdiff, .95)) if sdiff else None,
                        "p95_gap_abs_diff": float(np.quantile(gdiff, .95)) if gdiff else None,
                        "floor_agreement": float(np.mean(floor_agree)) if floor_agree else None,
                        "min_spearman": float(min(ranks)) if ranks else None, "eligible_exact_gap_rows": exact_n,
                        "pass": bool(sdiff and gdiff and exact_n >= 20 and np.quantile(sdiff,.95) <= .02 and np.quantile(gdiff,.95) <= .02 and np.mean(floor_agree) == 1 and min(ranks) >= .99)})
                diagnostics = [r for r in cell_rows if r.get("cell_id") == cell_id and r.get("axis") == axis and r.get("branch") == branch_name and r.get("status") == "diagnostic"]
                selected = None
                if args.max_M >= 4096 and any(r.get("M") == 4096 and r.get("pass") for r in diagnostics):
                    selected = 4096
                elif args.max_M >= 8192 and any(r.get("M") == 8192 and r.get("pass") for r in diagnostics):
                    selected = 8192
                elif args.max_M >= 16384:
                    selected = 16384
                selections.append({"cell_id": cell_id, "axis": axis, "branch": branch_name, "selected_M": selected,
                                   "selection_basis": "first_predeclared_M_passing_all_rules" if selected in (4096,8192) else ("largest_frozen_reference_after_failure" if selected == 16384 else "not_evaluated")})
    with (OUT / "e14a_manifest.json").open("w") as f: json.dump({"config":{"M_levels":run_levels,"primary_M_levels":M_LEVELS,"max_M":args.max_M,"groups":args.groups,"cell_limit":args.cell_limit,"offset":args.offset},"rows":manifest_rows}, f, indent=2)
    fields = sorted({k for r in cell_rows for k in r})
    with (OUT / "e14a_convergence_by_cell.csv").open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(cell_rows)
    integrity["M_selection"] = selections
    with (OUT / "e14a_integrity_summary.json").open("w") as f: json.dump(integrity, f, indent=2)
    with (OUT / "e14a_measurement_support.csv").open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=["cell_id","axis","branch","status","M","p95_S_abs_diff","p95_gap_abs_diff","floor_agreement","min_spearman","eligible_exact_gap_rows","pass"])
        w.writeheader(); w.writerows([r for r in cell_rows if r.get("status")=="diagnostic"])
    (OUT / "E14A_MEASUREMENT_SCALING_SANITY_RESULT.md").write_text(
        "# E14-A measurement-scaling sanity\n\n"
        f"Cells processed: {integrity['cells']}\n\n"
        f"Paired groups: {integrity['groups']}\n\n"
        f"Branch conditions: {integrity['branch_conditions']}\n\n"
        "This file is a convergence/integrity diagnostic; no complexity effect is interpreted here.\n")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cell-limit", type=int, default=0)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--groups", type=int, default=4)
    p.add_argument("--max-M", type=int, default=16384, choices=(SMOKE_M,) + M_LEVELS)
    p.add_argument("--audit-n", type=int, default=128)
    args=p.parse_args(); run(args)


if __name__ == "__main__": main()
