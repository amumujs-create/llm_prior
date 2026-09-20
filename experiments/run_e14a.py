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
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from e14_multivariate_core import H, INTENTS, build_clean, apply_c2_intervention, exact_envelope_match, stable_seed, persistent_scope_table, measured_stratum
from e14_master_scorer import (
    direct_candidate_audit, master_latents, score_bank, completeness_gap,
    continuous_evidence, score_bank_ladder,
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


MAX_GROUP_PROPOSALS = 2000


def group_seed(axis: str, cell_id: str, proposal_index: int) -> int:
    return stable_seed("e14-a-v1", axis, cell_id, proposal_index)


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
    if not exact_envelope_match(*[q[0] for q in hs]):
        raise ValueError("pstar_mismatch")
    out = []
    for field, name in hs:
        base = field
        _, base_cont = persistent_scope_table(base)
        if any(v != 1 for atom in field.pstar for v in base_cont[atom]):
            raise ValueError("base_not_persistent")
        intervention = apply_c2_intervention(base, scope)
        _, int_cont = persistent_scope_table(intervention)
        measured = measured_stratum(int_cont, intervention.pstar)
        if measured != scope:
            raise ValueError("scope_mismatch")
        out.append((name, base, intervention))
    return out


def rejection_category(reason: str) -> str:
    """Map frozen generator/checker failures into predeclared accounting bins."""
    if reason in {"pstar_mismatch", "base_not_persistent", "scope_mismatch"}:
        return reason
    if "admissible range" in reason or "numeric" in reason:
        return "numeric_field_rejection"
    if "envelope" in reason or "semantic" in reason or "checker" in reason:
        return "semantic_failure"
    return "exceptions_other"


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
    # V_f remains function-space dispersion, evaluated on the frozen
    # continuation domain [.40, 1.20] at the inherited 49-point resolution.
    # Accumulate first and second weighted moments in chunks so M=16384 never
    # materializes a large bank-by-context-by-time cube.
    x_eval = np.linspace(.40, 1.20, 49)
    mu = np.zeros((len(field.z_ref), len(x_eval)), dtype=float)
    second = np.zeros_like(mu)
    chunk = 256
    for lo in range(0, len(xi), chunk):
        hi = min(len(xi), lo + chunk)
        f = _branch_bank(field, xi[lo:hi], x_eval)
        w = scores.weights[lo:hi]
        mu += np.sum(w[:, None, None] * f, axis=0)
        second += np.sum(w[:, None, None] * f * f, axis=0)
    vf = float(np.mean(second - mu * mu))
    return d_eff, vf, vf / max(field.rref ** 2, 1e-12)


def _write_progress(completed_cells, total_cells, cell_id, integrity, rejection_counts, groups_per_cell):
    """Persist operational status without changing corpus membership or scoring."""
    payload = {
        "completed_cells": completed_cells,
        "total_cells": total_cells,
        "last_completed_cell": cell_id,
        "accepted_groups": integrity["groups"],
        "expected_accepted_groups": total_cells * len(BRANCHES) * groups_per_cell,
        "direct_audit_failures": integrity["direct_audit_failures"],
        "rejection_counts": rejection_counts,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "e14a_progress.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"[E14-A] {completed_cells}/{total_cells} cells complete; "
        f"accepted groups={integrity['groups']}",
        flush=True,
    )


def run(args):
    OUT.mkdir(parents=True, exist_ok=True)
    cell_rows = []
    accounting_rows = []
    manifest_rows = []
    integrity = {"cells": 0, "groups": 0, "branch_conditions": 0,
                 "direct_audit_failures": 0, "pstar_mismatch": 0,
                 "scope_or_base_failures": 0, "exceptions": 0}
    rejection_counts = {"pstar_mismatch": 0, "base_not_persistent": 0,
                        "scope_mismatch": 0, "semantic_failure": 0,
                        "numeric_field_rejection": 0, "exceptions_other": 0,
                        "exhaustion": 0}
    run_levels = (SMOKE_M,) if args.max_M == SMOKE_M else tuple(m for m in M_LEVELS if m <= args.max_M)
    cells = [(intent, gen, eta_name, eta, scope)
             for intent in INTENT_NAMES for gen in GENS
             for eta_name, eta in ETAS for scope in SCOPES]
    cells = cells[args.offset: args.offset + args.cell_limit if args.cell_limit else None]
    for cell_index, (intent, gen, eta_name, eta, scope) in enumerate(cells, start=1):
        cell_id = f"{intent}|{gen}|{eta_name}|{scope}"
        integrity["cells"] += 1
        vals = {axis: [] for axis in BRANCHES}
        for axis in BRANCHES:
            accepted = 0; proposal = 0
            local_rejections = {k: 0 for k in rejection_counts if k != "exhaustion"}
            while accepted < args.groups and proposal < MAX_GROUP_PROPOSALS:
                seed = group_seed(axis, cell_id, proposal)
                try:
                    members = branch_fields(intent, gen, axis, seed, scope)
                except Exception as exc:
                    reason = str(exc)
                    category = rejection_category(reason)
                    rejection_counts[category] += 1; local_rejections[category] += 1
                    proposal += 1
                    continue
                group_index = accepted
                accepted += 1; proposal += 1; integrity["groups"] += 1
                pstar = members[0][1].pstar
                cands = subsets(pstar)
                for branch_name, base, field in members:
                    integrity["branch_conditions"] += 1
                    # Ensure scope is measured from the field; no proposal
                    # metadata is used in scoring.
                    xi = master_latents(seed, M=max(M_LEVELS))
                    group_id = f"{axis}|{cell_id}|proposal{proposal-1}"
                    e_mean, e_raw = continuous_evidence(field, group_id, eta)
                    audit_ok = direct_candidate_audit(
                        score_bank(field, group_id, xi[:min(args.audit_n, max(M_LEVELS))], cands,
                                   min(args.audit_n, max(M_LEVELS))),
                        field, xi[:min(args.audit_n, max(M_LEVELS))], pstar, cands, n=min(args.audit_n, max(M_LEVELS)))
                    if not audit_ok:
                        integrity["direct_audit_failures"] += 1
                    row_by_m = {}
                    ladder_scores = score_bank_ladder(field, group_id, xi, cands, run_levels)
                    for M in run_levels:
                        if M > args.max_M:
                            continue
                        scores = ladder_scores[M]
                        d_eff, vf, vf_norm = _metrics(scores, field, xi[:M], cands)
                        gaps = {"|".join(sorted(c)): completeness_gap(scores, pstar, c) for c in cands}
                        row_by_m[M] = (scores, gaps, d_eff, vf, vf_norm)
                        for c in cands:
                            gap, status = gaps["|".join(sorted(c))]
                            manifest_rows.append({"cell_id": cell_id, "axis": axis, "group_index": group_index, "proposal_index": proposal-1,
                                "branch": branch_name, "M": M, "candidate": "|".join(sorted(c)),
                                "pstar": "|".join(sorted(pstar)), "S": scores.sharpness[c],
                                "ESS": scores.ess, "N_survive": scores.support[c],
                                "floor": int(scores.floor_by_candidate[c]), "delta_S_miss": gap,
                                "gap_status": status, "d_eff": d_eff, "V_f": vf, "V_f_norm": vf_norm,
                                "E_a": json.dumps({a: e_mean.get(a) for a in sorted(c)}, sort_keys=True),
                                "E_a_raw": json.dumps({a: e_raw.get(a) for a in sorted(c)}, sort_keys=True),
                                "E_min": float(min(e_mean.get(a, float("nan")) for a in c)),
                                "direct_audit": int(audit_ok), "eta": eta, "requested_scope": scope})
                    vals[axis].append({"branch": branch_name, "rows": row_by_m,
                                       "pstar": pstar, "cands": cands,
                                       "group_index": group_index})
            if accepted < args.groups:
                rejection_counts["exhaustion"] += 1
                cell_rows.append({"cell_id": cell_id, "axis": axis, "status": "exhaustion",
                                  "accepted": accepted, "proposals": proposal})
            accounting_rows.append({"cell_id": cell_id, "axis": axis, "requested_groups": args.groups,
                                    "accepted_groups": accepted, "proposals": proposal,
                                    **local_rejections, "exhausted": int(accepted < args.groups)})
        for axis, records in vals.items():
            if not records:
                continue
            # Convergence cells are base-cell x primary axis x realized branch
            # condition. Never pool d=1/d=3/d=8 (or add/pair/ent) here.
            by_branch = {}
            for rec in records:
                by_branch.setdefault(rec["branch"], []).append(rec)
            for branch_name, branch_records in by_branch.items():
                ref_records = [rec for rec in branch_records if 16384 in rec["rows"]]
                for M in (4096, 8192):
                    if M > args.max_M or not ref_records:
                        continue
                    sdiff = []; gdiff = []; floor_agree = []; ranks = []; exact_n = 0
                    for rec in ref_records:
                        rb = rec["rows"]; group_cands = rec["cands"]; group_pstar = rec["pstar"]
                        a_s, a_g, _, _, _ = rb[M]; b_s, b_g, _, _, _ = rb[16384]
                        keys = [c for c in group_cands if c in a_s.sharpness and c in b_s.sharpness]
                        sdiff.extend(abs(a_s.sharpness[c] - b_s.sharpness[c]) for c in keys)
                        floor_agree.extend(a_s.floor_by_candidate[c] == b_s.floor_by_candidate[c] for c in keys)
                        proper = [c for c in keys if c != group_pstar]
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
        _write_progress(cell_index, len(cells), cell_id, integrity, rejection_counts, args.groups)
    with (OUT / "e14a_manifest.json").open("w") as f: json.dump({"config":{"M_levels":run_levels,"primary_M_levels":M_LEVELS,"max_M":args.max_M,"groups":args.groups,"cell_limit":args.cell_limit,"offset":args.offset},"rows":manifest_rows}, f, indent=2)
    fields = sorted({k for r in cell_rows for k in r})
    with (OUT / "e14a_convergence_by_cell.csv").open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(cell_rows)
    diagnostics = [r for r in cell_rows if r.get("status") == "diagnostic"]
    common_selected = None; selection_basis = "not_evaluated"
    if args.max_M >= 4096 and diagnostics and all(r.get("M") == 4096 and r.get("pass") for r in diagnostics if r.get("M") == 4096) and sum(r.get("M") == 4096 for r in diagnostics) == len({(r.get("cell_id"), r.get("axis"), r.get("branch")) for r in diagnostics}):
        common_selected = 4096; selection_basis = "all_convergence_cells_pass_4096"
    elif args.max_M >= 8192 and diagnostics and all(r.get("M") == 8192 and r.get("pass") for r in diagnostics if r.get("M") == 8192) and sum(r.get("M") == 8192 for r in diagnostics) == len({(r.get("cell_id"), r.get("axis"), r.get("branch")) for r in diagnostics}):
        common_selected = 8192; selection_basis = "all_convergence_cells_pass_8192"
    elif args.max_M >= 16384 and diagnostics:
        common_selected = 16384; selection_basis = "largest_frozen_reference_after_any_lower_M_failure"
    integrity["rejection_counts"] = rejection_counts
    integrity["pstar_mismatch"] = rejection_counts["pstar_mismatch"]
    integrity["scope_or_base_failures"] = rejection_counts["scope_mismatch"] + rejection_counts["base_not_persistent"]
    integrity["exceptions"] = rejection_counts["exceptions_other"]
    integrity["common_selected_M"] = common_selected
    integrity["common_selection_basis"] = selection_basis
    integrity["expected_accepted_groups"] = len(cells) * len(BRANCHES) * args.groups
    integrity["accepted_groups_complete"] = integrity["groups"] == integrity["expected_accepted_groups"]
    integrity["global_sanity_pass"] = bool(integrity["accepted_groups_complete"] and integrity["direct_audit_failures"] == 0 and rejection_counts["exhaustion"] == 0 and rejection_counts["exceptions_other"] == 0)
    with (OUT / "e14a_integrity_summary.json").open("w") as f: json.dump(integrity, f, indent=2)
    accounting_fields = ["cell_id", "axis", "requested_groups", "accepted_groups", "proposals",
                         "pstar_mismatch", "base_not_persistent", "scope_mismatch", "semantic_failure",
                         "numeric_field_rejection", "exceptions_other", "exhausted"]
    with (OUT / "e14a_rejection_accounting.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=accounting_fields); w.writeheader(); w.writerows(accounting_rows)
    chosen_m = common_selected if common_selected is not None else (max(run_levels) if run_levels else None)
    support = {}
    if chosen_m is not None:
        for row in manifest_rows:
            if row["M"] != chosen_m:
                continue
            key = (row["axis"], row["branch"])
            s = support.setdefault(key, {"axis": row["axis"], "branch": row["branch"], "M": chosen_m,
                                         "rows": 0, "reliable": 0, "floor": 0, "exact_gap": 0,
                                         "E_min": [], "d_eff": [], "V_f_norm": []})
            s["rows"] += 1; s["reliable"] += int(row["ESS"] >= 100); s["floor"] += int(row["floor"])
            s["exact_gap"] += int(row["gap_status"] == "exact")
            s["E_min"].append(row["E_min"]); s["d_eff"].append(row["d_eff"]); s["V_f_norm"].append(row["V_f_norm"])
    support_rows = []
    for s in support.values():
        n = max(s.pop("rows"), 1)
        support_rows.append({"axis": s["axis"], "branch": s["branch"], "M": s["M"], "candidate_rows": n,
                             "reliable_rate": s.pop("reliable") / n, "floor_rate": s.pop("floor") / n,
                             "exact_gap_rate": s.pop("exact_gap") / n,
                             "mean_E_min": float(np.nanmean(s.pop("E_min"))),
                             "mean_d_eff": float(np.nanmean(s.pop("d_eff"))),
                             "mean_V_f_norm": float(np.nanmean(s.pop("V_f_norm")))})
    with (OUT / "e14a_measurement_support.csv").open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=["axis","branch","M","candidate_rows","reliable_rate","floor_rate","exact_gap_rate","mean_E_min","mean_d_eff","mean_V_f_norm"])
        w.writeheader(); w.writerows(support_rows)
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
