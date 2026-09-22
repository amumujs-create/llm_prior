#!/usr/bin/env python3
"""Read-only paired E14-B/C/D analysis of the frozen full corpus."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from e14_multivariate_core import H, candidate_cp, persistent_scope_table, stable_seed
from run_e14a import branch_fields

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results" / "complexity_scaling_e14" / "e14bcd"
OUT = RUN / "analysis"
B = 5000
SEED = 20261014

CONTRASTS = {
    "E14-B_dimension": [("dimension_d8", "dimension_d3", "d8_minus_d3"),
                          ("dimension_d1", "dimension_d3", "d1_minus_d3_anchor")],
    "E14-C_interaction": [("interaction_pairwise", "interaction_additive", "pairwise_minus_additive"),
                            ("interaction_entangled", "interaction_additive", "entangled_minus_additive")],
    "E14-D_heterogeneity": [("heterogeneity_moderate", "heterogeneity_none", "moderate_minus_none"),
                              ("heterogeneity_strong", "heterogeneity_none", "strong_minus_none")],
}


def mean(values):
    return float(np.mean(values)) if values else float("nan")


def candidate_evidence(row):
    values = list(json.loads(row["E_a"]).values())
    return mean(values)


def atom_set(value):
    return frozenset(a for a in value.split("|") if a)


def group_metrics(rows):
    """Within-group equal-candidate summaries; subsets are never bootstrap units."""
    proper = [r for r in rows if r["candidate"] != r["pstar"]]
    exact = [r for r in proper if r["gap_status"] == "exact" and float(r["ESS"]) >= 100]
    result = {
        "S": mean([float(r["S"]) for r in rows]),
        "E_a_mean": mean([candidate_evidence(r) for r in rows]),
        "E_a_min": mean([float(r["E_min"]) for r in rows]),
        "d_eff": mean([float(r["d_eff"]) for r in rows]),
        "V_f_norm": mean([float(r["V_f_norm"]) for r in rows]),
        "delta_S_miss": mean([float(r["delta_S_miss"]) for r in exact]),
        "info_complete_rate": mean([float(r["delta_S_miss"]) <= .10 for r in exact]),
        "exact_gap_rate": len(exact) / len(proper) if proper else float("nan"),
    }
    full = next(r for r in rows if r["candidate"] == r["pstar"])
    for j, horizon in enumerate(H):
        result[f"scope_survival_{horizon:.2f}"] = mean([r["scope_cp"][j] for r in rows])
        result[f"scope_extension_{horizon:.2f}"] = mean(
            [r["scope_cp"][j] - full["scope_cp"][j] for r in proper]
        )
    return result


def bootstrap_by_generator(values_by_generator, rng):
    """5,000 paired-group bootstrap, preserving equal generator weighting."""
    draws = np.zeros(B)
    used = 0
    for values in values_by_generator.values():
        a = np.asarray(values, dtype=float)
        a = a[np.isfinite(a)]
        if not len(a):
            continue
        ix = rng.integers(0, len(a), size=(B, len(a)))
        draws += a[ix].mean(axis=1)
        used += 1
    if not used:
        return float("nan"), float("nan"), float("nan")
    draws /= used
    return float(draws.mean()), float(np.quantile(draws, .025)), float(np.quantile(draws, .975))


def write_csv(name, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    manifest = json.loads((RUN / "e14a_manifest.json").read_text())
    assert manifest["config"]["seed_namespace"] == "e14-full-v1"
    assert manifest["config"]["groups"] == 6
    assert manifest["config"]["M_levels"] == [16384]
    rows = [r for r in manifest["rows"] if r["M"] == 16384]
    grouped = defaultdict(list)
    for r in rows:
        key = (r["axis"], r["cell_id"], r["group_index"], r["proposal_index"], r["branch"])
        grouped[key].append(r)
    # Scope is re-evaluated deterministically from the frozen clean field, not
    # inferred from the requested-stratum label. It remains censoring-aware as
    # a horizon survival profile rather than a numeric censored horizon mean.
    group_branches = defaultdict(set)
    for axis, cell, group, proposal, branch in grouped:
        group_branches[(axis, cell, group, proposal)].add(branch)
    for (axis, cell, group, proposal), expected_branches in group_branches.items():
        intent, generator, _eta, requested_scope = cell.split("|")
        seed = stable_seed("e14-full-v1", axis, cell, proposal)
        fields = {name: field for name, _base, field in branch_fields(intent, generator, axis, seed, requested_scope)}
        if set(fields) != expected_branches:
            raise ValueError(f"branch pairing mismatch for {axis}|{cell}|{proposal}")
        for branch, field in fields.items():
            _raw, cont = persistent_scope_table(field)
            for row in grouped[(axis, cell, group, proposal, branch)]:
                row["scope_cp"] = candidate_cp(cont, atom_set(row["candidate"]))
    summaries = {key: group_metrics(value) for key, value in grouped.items()}
    out = []
    metrics = ("S", "E_a_mean", "E_a_min", "delta_S_miss", "info_complete_rate", "exact_gap_rate", "d_eff", "V_f_norm") + tuple(
        f"scope_survival_{h:.2f}" for h in H
    ) + tuple(f"scope_extension_{h:.2f}" for h in H)
    for analysis, contrasts in CONTRASTS.items():
        axis = {"E14-B_dimension": "dimension", "E14-C_interaction": "interaction", "E14-D_heterogeneity": "heterogeneity"}[analysis]
        paired = defaultdict(dict)
        for (a, cell, group, proposal, branch), values in summaries.items():
            if a == axis:
                paired[(cell, group, proposal)][branch] = values
        for target, base, label in contrasts:
            units = [(key, values[target], values[base]) for key, values in paired.items()
                     if target in values and base in values]
            for metric_index, metric in enumerate(metrics):
                by_gen = defaultdict(list)
                for (cell, _, _), target_values, base_values in units:
                    generator = cell.split("|")[1]
                    by_gen[generator].append(target_values[metric] - base_values[metric])
                rng = np.random.default_rng(SEED + metric_index + 100 * len(out))
                estimate, lo, hi = bootstrap_by_generator(by_gen, rng)
                out.append({"analysis": analysis, "contrast": label, "metric": metric,
                            "paired_groups": sum(len(v) for v in by_gen.values()),
                            "generators": len(by_gen), "estimate": estimate,
                            "cluster_bootstrap_95ci_low": lo, "cluster_bootstrap_95ci_high": hi,
                            "bootstrap_replicates": B})
    write_csv("paired_effects.csv", out)
    result = {
        "manifest_sha256": hashlib.sha256((RUN / "e14a_manifest.json").read_bytes()).hexdigest(),
        "seed_namespace": "e14-full-v1", "M_common": 16384,
        "bootstrap": {"replicates": B, "seed": SEED, "unit": "paired latent group", "generator_weighting": "equal"},
        "pairing": {"dimension_primary": "d8-d3", "dimension_anchor": "d1-d3", "interaction": ["pairwise-additive", "entangled-additive"], "heterogeneity": ["moderate-none", "strong-none"]},
        "scope_note": "Candidate scope profiles were deterministically re-evaluated from frozen clean fields using Va->Ca->CP; requested scope labels were not used as candidate scope outcomes.",
    }
    (OUT / "analysis_manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
