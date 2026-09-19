#!/usr/bin/env python3
"""Build the frozen, future-independent E12-B structural-operation catalog."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "E11_CANONICAL_ATOM_LIBRARY_V1.json"
INTENTS = ROOT / "E11_INTENDED_ATOM_INTENTS_V1.json"
COMPAT = ROOT / "E11_COMPATIBILITY_SCOPE_REGISTRY_V1.json"
OUT = ROOT / "E12B_OPERATION_CATALOG_V1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    atom_library = json.loads(LIB.read_text())
    intents = json.loads(INTENTS.read_text())["generator_intents"]
    incompatible = {frozenset(pair) for pair in atom_library["pairwise_incompatible"]}
    atom_ids = [atom["id"] for atom in atom_library["atoms"]]

    # These are signed instance-level reversals. Regime and lower-bound
    # reversal are intentionally outside E12-B v1 (see protocol §Operations).
    reverse = {
        "direction_decreasing": "direction_increasing",
        "direction_increasing": "direction_decreasing",
        "curvature_convex": "curvature_concave",
        "curvature_concave": "curvature_convex",
        "inflection_concave_to_convex": "inflection_convex_to_concave",
        "inflection_convex_to_concave": "inflection_concave_to_convex",
        "turning_maximum": "turning_minimum",
        "turning_minimum": "turning_maximum",
        "asymptote_to_0_from_above": "asymptote_to_0_from_below",
        "asymptote_to_0_from_below": "asymptote_to_0_from_above",
    }

    # One deterministic false-addition family per intended triple. Every
    # candidate is selected without access to a realised future. Falsity is
    # verified separately by the clean-oracle acceptance stage.
    false_addition = {
        "direction+curvature+bound": "regime_postchange",
        "direction+curvature+asymptote": "regime_postchange",
        "direction+inflection+bound": "regime_postchange",
        "direction+inflection+asymptote": "regime_postchange",
        "curvature+bound+asymptote": "regime_postchange",
        "inflection+bound+asymptote": "regime_postchange",
        "turning+bound+asymptote": "regime_postchange",
        "regime+bound+asymptote": "turning_maximum",
    }

    def compatible(atoms: set[str]) -> bool:
        return not any(pair <= atoms for pair in incompatible)

    cells = []
    for intent_name, supplied_atoms in intents.items():
        supplied = set(supplied_atoms)
        addition = false_addition[intent_name]
        if addition in supplied or not compatible(supplied | {addition}):
            raise ValueError(f"invalid frozen addition: {intent_name} -> {addition}")
        operations = [
            {
                "id": f"omit:{atom}",
                "type": "omission",
                "source_atom": atom,
                "candidate_atoms": sorted(supplied - {atom}),
                "expected_coverage": 1,
            }
            for atom in sorted(supplied)
        ]
        operations.append(
            {
                "id": f"add:{addition}",
                "type": "false_addition",
                "added_atom": addition,
                "candidate_atoms": sorted(supplied | {addition}),
                "expected_coverage": 0,
                "future_oracle_rule": "must be clean-oracle false per accepted task",
            }
        )
        for source in sorted(supplied):
            target = reverse.get(source)
            if target is None:
                continue
            candidate = (supplied - {source}) | {target}
            if compatible(candidate):
                operations.append(
                    {
                        "id": f"reverse:{source}->{target}",
                        "type": "reversal",
                        "source_atom": source,
                        "target_atom": target,
                        "candidate_atoms": sorted(candidate),
                        "expected_coverage": 0,
                        "future_oracle_rule": "must be clean-oracle false per accepted task",
                    }
                )
        cells.append(
            {
                "intent_name": intent_name,
                "supplied_atoms": sorted(supplied),
                "operations": operations,
                "excluded_reversal_sources": sorted(supplied - set(reverse)),
            }
        )

    payload = {
        "name": "E12B_OPERATION_CATALOG_V1",
        "purpose": "future-independent structural operation declarations for E12-B",
        "scope": [0.4, 0.8],
        "accepted_tasks_per_intended_triple_generator": 30,
        "max_generation_attempts_per_cell": 1000,
        "source_hashes": {
            "canonical_atom_library": sha256(LIB),
            "intended_atom_intents": sha256(INTENTS),
            "compatibility_scope_registry": sha256(COMPAT),
        },
        "selection_rule": (
            "The catalog selects only frozen canonical atom instances. "
            "False coverage is checked on every realised task and is not inferred "
            "from the catalog declaration."
        ),
        "cells": cells,
        "canonical_atom_ids": atom_ids,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} sha256={sha256(OUT)}")


if __name__ == "__main__":
    main()
