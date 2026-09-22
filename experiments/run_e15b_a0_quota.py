"""Protected E15-B0 quota calibration with no persisted raw policy contrasts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .e15b_a0_blinded_producer import produce
    from .e15b_a0_contract import BlindedContrastAccumulator, max_attempts_from_acceptance
except ImportError:  # pragma: no cover
    from e15b_a0_blinded_producer import produce
    from e15b_a0_contract import BlindedContrastAccumulator, max_attempts_from_acceptance


def run(contract: Path, epsilon: float, minimum_quota: int, failure_probability: float = 1e-4) -> dict:
    if epsilon <= 0.0 or minimum_quota < 1:
        raise ValueError("epsilon and minimum_quota must be positive")
    states = ("narrow", "broad", "existence_only", "covered_biased")
    exposures = ("low", "medium", "high")
    contrasts = ("D1", "D2")
    cells = [f"{state}::{exposure}::{contrast}" for state in states for exposure in exposures for contrast in contrasts]
    accumulators = {cell: BlindedContrastAccumulator() for cell in cells}
    for state, exposure, contrast, scalar in produce(contract):
        accumulators[f"{state}::{exposure}::{contrast}"].update(scalar)
    summaries = {cell: accumulator.summary(epsilon, minimum_quota) for cell, accumulator in accumulators.items()}
    quota = max(int(summary["required_quota"]) for summary in summaries.values())
    config = json.loads(contract.read_text())
    feasibility = max_attempts_from_acceptance(
        int(config["pilot_tasks"]), int(config["pilot_tasks"]), quota, failure_probability
    )
    return {
        "metric": "paired_post_scope_nrmse_contrast",
        "target_ci_half_width": epsilon,
        "minimum_quota": minimum_quota,
        "primary_cell_count": len(cells),
        "by_primary_cell": {
            cell: {
                "n_discarded_pilot_tasks": int(summary["n_tasks"]),
                "paired_sd": summary["paired_sd"],
                "paired_sd_upper_95": summary["paired_sd_upper_95"],
                "required_confirmatory_quota": int(summary["required_quota"]),
            }
            for cell, summary in summaries.items()
        },
        "confirmatory_quota": quota,
        "acceptance_feasibility": feasibility,
        "protected": True,
        "note": "Only variance-derived summaries are persisted; no raw contrast, mean, sign, policy-specific loss, ranking, or winner is exposed.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--epsilon", type=float, required=True)
    parser.add_argument("--minimum-quota", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.contract, args.epsilon, args.minimum_quota)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
