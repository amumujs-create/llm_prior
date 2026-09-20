#!/usr/bin/env python3
"""Micro integrity check for E14's frozen multivariate clean-field contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from e14_multivariate_core import (HET_FIELD, INTENTS, apply_c2_intervention,
                                   build_clean, candidate_cp, exact_envelope_match,
                                   measured_stratum, persistent_scope_table)
from build_e13_persistent_base import H

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "complexity_scaling_e14" / "micro_sanity"
PRIMARY = ("dimension_d1", "dimension_d3", "dimension_d8", "interaction_additive", "interaction_pairwise", "interaction_entangled")


def check(intent: str, generator: str, requested: str) -> dict:
    fields = [build_clean(intent, generator, branch) for branch in PRIMARY]
    fields += [build_clean(intent, generator, "heterogeneity", level) for level in ("none", "moderate", "strong")]
    base_raw_cont = [persistent_scope_table(f) for f in fields]
    pstars_equal = exact_envelope_match(*fields)
    persistent = all(all(all(v) for v in cont.values()) for _, cont in base_raw_cont)
    scoped = [apply_c2_intervention(f, requested) for f in fields]
    core_equal = all((s.y[:, s.x <= .80] == f.y[:, f.x <= .80]).all() for f, s in zip(fields, scoped))
    measured = []
    nesting = True
    for f in scoped:
        _, cont = persistent_scope_table(f); measured.append(measured_stratum(cont, f.pstar))
        full = candidate_cp(cont, f.pstar)
        for atom in f.pstar:
            nesting &= all((not full[j]) or candidate_cp(cont, frozenset((atom,)))[j] for j in range(len(H)))
    return {"intent": intent, "generator": generator, "requested": requested,
            "heterogeneity_target": HET_FIELD[intent], "pstar_equal": pstars_equal,
            "base_persistent": persistent, "core_bit_identical": core_equal,
            "scope_nesting": nesting, "requested_equals_measured": all(m == requested for m in measured),
            "pstar": "|".join(sorted(fields[0].pstar)), "measured": measured,
            "rref_shared": len({f.rref for f in fields}) == 1}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--limit", type=int, default=0); parser.add_argument("--offset", type=int, default=0); args = parser.parse_args()
    rows = []
    triples = [(i, g, s) for i in INTENTS for g in ("spline", "basis", "ode") for s in ("limited", "intermediate", "persistent_within_tested_domain")]
    stop = args.offset + args.limit if args.limit else None
    for item in triples[args.offset:stop]:
        try: rows.append(check(*item))
        except Exception as exc: rows.append({"intent": item[0], "generator": item[1], "requested": item[2], "error": repr(exc)})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps({"rows": rows, "all_pass": all(not r.get("error") and all(bool(v) for k, v in r.items() if k not in {"intent", "generator", "requested", "heterogeneity_target", "pstar", "measured"}) for r in rows)}, indent=2) + "\n")
    print((OUT / "summary.json").read_text())


if __name__ == "__main__": main()
