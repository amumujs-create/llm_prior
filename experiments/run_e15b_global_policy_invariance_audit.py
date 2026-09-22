"""Outcome-free audit: global policies must ignore supplied scope support."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .e15b_confirmatory_core import EXPOSURES, STATES, accepted_tasks, evaluate_prefix, load_frozen_manifest, policy_predictions
except ImportError:  # pragma: no cover
    from e15b_confirmatory_core import EXPOSURES, STATES, accepted_tasks, evaluate_prefix, load_frozen_manifest, policy_predictions


GLOBAL_POLICIES = ("free_baseline", "hard_global", "soft_global", "slack_distribution")


def run(manifest_path: Path) -> dict:
    manifest = load_frozen_manifest(manifest_path)
    tasks = accepted_tasks(manifest)[:30]
    endpoint = float(manifest["secondary_policy_contract"]["global_enforcement_endpoint"])
    failures, comparisons = 0, 0
    for task in tasks:
        for exposure in EXPOSURES:
            anchor_eval = evaluate_prefix(manifest, task, exposure, "exact")
            t = np.linspace(anchor_eval["t_prefix"].max(), endpoint, 31)
            anchor = policy_predictions(anchor_eval, t)
            for state in STATES[1:]:
                predicted = policy_predictions(evaluate_prefix(manifest, task, exposure, state), t)
                for policy in GLOBAL_POLICIES:
                    comparisons += 1
                    if not np.array_equal(anchor[policy], predicted[policy]): failures += 1
    return {"status": "PASS" if failures == 0 else "FAIL", "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(), "sampled_tasks": len(tasks), "exposures": list(EXPOSURES), "states_compared_against_exact": list(STATES[1:]), "global_policies": list(GLOBAL_POLICIES), "prediction_comparisons": comparisons, "support_dependence_failures": failures, "note": "No outcome scores or policy rankings were calculated."}


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--manifest", type=Path, required=True); p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(); result = run(a.manifest); a.out.parent.mkdir(parents=True, exist_ok=True); a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if result["status"] != "PASS": raise SystemExit("global-policy support invariance failed")
