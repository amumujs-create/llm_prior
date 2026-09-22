"""Deterministically complete predeclared E15-A CRPS and distance outcomes.

This is an analysis-only completion: it reads the frozen manifest and checks
that regenerated NRMSE agrees with the original confirmatory rows. It does not
generate tasks, tune policies, or modify the original result artifact.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.special import ndtr

try:
    from .e15a_confirmatory_core import EXPOSURES, POLICIES, accepted_tasks, evaluate_prefix, load_manifest
    from .e15a_regime_core import smooth_regime
except ImportError:  # pragma: no cover
    from e15a_confirmatory_core import EXPOSURES, POLICIES, accepted_tasks, evaluate_prefix, load_manifest
    from e15a_regime_core import smooth_regime


STATES = ("exact", "narrow", "broad", "existence_only", "covered_biased", "uncovered_biased")


def _expected_absolute_normal(delta: np.ndarray, scale: float) -> np.ndarray:
    z = delta / scale
    return scale * (2.0 * np.exp(-.5 * z * z) / np.sqrt(2.0 * np.pi) + z * (2.0 * ndtr(z) - 1.0))


def normal_mixture_crps(means: np.ndarray, weights: np.ndarray, y: np.ndarray, sigma: float) -> float:
    """Exact Gaussian-mixture CRPS, streamed in time chunks for bounded memory."""
    first = np.sum(weights[:, None] * _expected_absolute_normal(means - y, sigma), axis=0)
    second = np.zeros(y.size)
    pair_scale = np.sqrt(2.0) * sigma
    for start in range(0, y.size, 32):
        stop = min(start + 32, y.size)
        difference = means[:, None, start:stop] - means[None, :, start:stop]
        expected = _expected_absolute_normal(difference, pair_scale)
        second[start:stop] = np.einsum("i,j,ijt->t", weights, weights, expected, optimize=True)
    return float(np.mean(first - .5 * second))


def _source_rows(path: Path) -> dict[tuple[int, str, str, str], float]:
    out = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = (int(row["task_id"]), row["policy"], row["knowledge_state"], row["prefix_exposure"])
            out[key] = float(row["far_nrmse"])
    return out


def run(manifest_path: Path, source_rows_path: Path, out_dir: Path) -> dict:
    manifest = load_manifest(manifest_path)
    source = _source_rows(source_rows_path)
    rows = []
    mismatch_count = 0
    tasks = accepted_tasks(manifest)
    total = len(tasks)
    out_dir.mkdir(parents=True, exist_ok=True)
    progress_path = out_dir / "e15a_outcome_completion_progress.json"
    for task_index, task in enumerate(tasks, start=1):
        for exposure in EXPOSURES:
            for state in STATES:
                evaluated = evaluate_prefix(manifest, task, exposure, state)
                y_far = smooth_regime(evaluated["t_far"], task.params)
                bin_edges = np.linspace(0, y_far.size, 4, dtype=int)
                for policy in POLICIES:
                    prediction = evaluated["policy_predictions"][policy]
                    nrmse = float(np.sqrt(np.mean((prediction - y_far) ** 2)) / evaluated["r_ref"])
                    key = (task.task_id, policy, state, exposure)
                    if not np.isclose(nrmse, source[key], rtol=0.0, atol=1e-14):
                        mismatch_count += 1
                    components, weights = evaluated["policy_components"][policy]
                    crps = normal_mixture_crps(components, weights, y_far, evaluated["sigma"])
                    row = {
                        "task_id": task.task_id,
                        "policy": policy,
                        "knowledge_state": state,
                        "prefix_exposure": exposure,
                        "far_crps": crps,
                        "far_ncrps": crps / evaluated["r_ref"],
                    }
                    for bin_index in range(3):
                        lo, hi = bin_edges[bin_index], bin_edges[bin_index + 1]
                        row[f"distance_bin_{bin_index + 1}_nrmse"] = float(
                            np.sqrt(np.mean((prediction[lo:hi] - y_far[lo:hi]) ** 2)) / evaluated["r_ref"]
                        )
                    rows.append(row)
        if task_index % 5 == 0 or task_index == total:
            progress_path.write_text(json.dumps({"completed_tasks": task_index, "total_tasks": total}, indent=2) + "\n")
    if mismatch_count:
        raise RuntimeError(f"{mismatch_count} regenerated NRMSE values differ from frozen confirmatory rows")
    path = out_dir / "e15a_outcome_completion_rows.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "status": "PASS",
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "source_rows_sha256": hashlib.sha256(source_rows_path.read_bytes()).hexdigest(),
        "source_row_count": len(source),
        "completion_row_count": len(rows),
        "nrmse_regeneration_mismatch_count": mismatch_count,
        "CRPS": "exact Gaussian-mixture energy form",
        "distance_bins": "three equal-index thirds of the frozen common far-OOD grid",
    }
    (out_dir / "e15a_outcome_completion_integrity.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-rows", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.manifest, args.source_rows, args.out_dir)


if __name__ == "__main__":
    main()
