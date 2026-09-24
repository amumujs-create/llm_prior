"""Integrity audit for the sealed E16-B test-X predictive distributions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from run_e16b_ccpp_train_capacity import sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--components", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    with np.load(args.components, allow_pickle=False) as data:
        expected = {"test_indices", "component_means", "uniform_weights", "weighted_weights", "map_index", "sigma_ref"}
        keys = set(data.files)
        means = data["component_means"]
        test_indices = data["test_indices"]
        uniform = data["uniform_weights"]
        weighted = data["weighted_weights"]
        map_index = int(data["map_index"])
        sigma = float(data["sigma_ref"])
    checks = {
        "allowed_npz_keys_only": keys == expected,
        "component_means_shape": means.shape == (956, 405),
        "test_indices_shape": test_indices.shape == (956,),
        "all_component_means_finite": bool(np.isfinite(means).all()),
        "uniform_weights_exact": bool(np.array_equal(uniform, np.full(405, 1.0 / 405.0))),
        "weighted_weights_sum_to_one": bool(np.isclose(weighted.sum(), 1.0, atol=1e-15, rtol=0.0)),
        "weights_finite_nonnegative": bool(np.isfinite(weighted).all() and np.all(weighted >= 0.0)),
        "MAP_index_in_range": 0 <= map_index < 405,
        "sigma_matches_manifest": sigma == float(manifest["sigma_ref"]),
        "component_sha_matches_manifest": sha256(args.components) == manifest["component_artifact"]["sha256"],
        "no_target_named_arrays": all("target" not in key.lower() and "pe" != key.lower() for key in keys),
    }
    artifact = {
        "protocol": "E16-B CCPP sealed test-X predictive-distribution integrity audit v1",
        "final_status": "PASS" if all(checks.values()) else "FAIL",
        "source_hashes": {"prediction_manifest_sha256": sha256(args.manifest), "components_sha256": sha256(args.components)},
        "checks": checks,
        "target_access": "none; audit reads only already-frozen prediction arrays",
        "scope": "test predictive distributions are structurally complete and contain no target array",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final_status": artifact["final_status"], "check_count": len(checks)}, indent=2))
    if artifact["final_status"] != "PASS":
        raise SystemExit("Test prediction-freeze integrity audit failure")


if __name__ == "__main__":
    main()
