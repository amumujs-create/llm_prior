#!/usr/bin/env python3
"""Deterministic E13 envelope preflight.

This preflight deliberately uses the unchanged E11 canonical-envelope oracle.
It freezes only the core-domain envelope size and candidate-row accounting;
future scope manipulation is not consulted while finding the envelope.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from run_prior_completeness_e11 import GENS, INTENTS, make_task, sd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "joint_prior_anatomy_e13" / "preflight"
ETAS = ("low", "mid", "high")
SCOPES = ("limited", "intermediate", "persistent_within_tested_domain")
SEEDS_PER_CELL = 10
MAX_ATTEMPTS = 2000


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run() -> None:
    accepted_rows: list[dict] = []
    accounting: list[dict] = []
    for intent_name in INTENTS:
        for generator in GENS:
            for eta in ETAS:
                for scope_stratum in SCOPES:
                    accepted = attempts = ambiguous = checker = 0
                    for target_seed in range(SEEDS_PER_CELL):
                        for attempt in range(MAX_ATTEMPTS):
                            attempts += 1
                            task_seed = sd(
                                "e13-envelope-preflight", intent_name, generator,
                                eta, scope_stratum, target_seed, attempt,
                            )
                            task, reason = make_task(intent_name, generator, task_seed)
                            if task is None:
                                ambiguous += int(reason == "ambiguous_envelope")
                                checker += int(reason == "checker_reject")
                                continue
                            envelope = tuple(sorted(task.pstar))
                            intended = tuple(sorted(task.intent))
                            size = len(envelope)
                            accepted_rows.append({
                                "intent_name": intent_name,
                                "generator": generator,
                                "eta": eta,
                                "scope_stratum": scope_stratum,
                                "target_seed": target_seed,
                                "accepted_attempt": attempt + 1,
                                "task_seed": task_seed,
                                "generator_intended_atoms": "|".join(intended),
                                "oracle_envelope_atoms": "|".join(envelope),
                                "oracle_envelope_size": size,
                                "implied_atoms": "|".join(sorted(set(envelope) - set(intended))),
                                "candidate_count": 2 ** size - 1,
                            })
                            accepted += 1
                            break
                    accounting.append({
                        "intent_name": intent_name,
                        "generator": generator,
                        "eta": eta,
                        "scope_stratum": scope_stratum,
                        "requested": SEEDS_PER_CELL,
                        "accepted": accepted,
                        "attempts": attempts,
                        "ambiguous_envelope_rejects": ambiguous,
                        "checker_rejects": checker,
                        "exhaustion": int(accepted != SEEDS_PER_CELL),
                    })
    write_csv(OUT / "accepted_tasks.csv", accepted_rows)
    write_csv(OUT / "accounting.csv", accounting)
    counts = Counter(int(row["oracle_envelope_size"]) for row in accepted_rows)
    summary = {
        "protocol": "E13_realized_oracle_envelope_preflight_v1",
        "latent_tasks": len(accepted_rows),
        "requested_latent_tasks": len(INTENTS) * len(GENS) * len(ETAS) * len(SCOPES) * SEEDS_PER_CELL,
        "expected_candidate_rows": sum(int(row["candidate_count"]) for row in accepted_rows),
        "envelope_size_distribution": {str(k): v for k, v in sorted(counts.items())},
        "exhausted_cells": sum(int(row["exhaustion"]) for row in accounting),
        "accepted_tasks_sha256": digest(OUT / "accepted_tasks.csv"),
        "accounting_sha256": digest(OUT / "accounting.csv"),
        "runner_sha256": digest(Path(__file__)),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    run()
