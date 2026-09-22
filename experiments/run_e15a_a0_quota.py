"""Protected E15-A0 quota calibration.

The input has one blinded paired far-OOD NRMSE contrast per discarded pilot
task.  This script streams those values into per-cell accumulators and emits
only SD, conservative SD upper bound, quota, and feasibility-derived maximum
attempts. It never writes a contrast, mean, sign, policy name, or winner.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

try:
    from .e15a_a0_contract import BlindedContrastAccumulator, attempt_budget_from_a0
except ImportError:  # pragma: no cover - direct script execution
    from e15a_a0_contract import BlindedContrastAccumulator, attempt_budget_from_a0


def run(
    contrast_csv: Path,
    primary_cells: list[str],
    target_half_width: float,
    minimum_quota: int,
    a0_result: dict,
    failure_probability_target: float = 1e-4,
) -> dict:
    if target_half_width <= 0 or minimum_quota < 1:
        raise ValueError("target_half_width and minimum_quota must be positive")
    accumulators: dict[str, BlindedContrastAccumulator] = defaultdict(BlindedContrastAccumulator)
    with contrast_csv.open(newline="") as handle:
        for row in csv.DictReader(handle):
            # The protected producer uses this canonical identifier.
            key = f"{row['knowledge_state']}::{row['prefix_exposure']}::{row['contrast_id']}"
            if key in primary_cells:
                accumulators[key].update(float(row["blinded_paired_nrmse_contrast"]))
    missing = sorted(set(primary_cells) - set(accumulators))
    if missing:
        raise ValueError(f"missing protected variance cells: {missing}")
    by_cell = {}
    for cell in primary_cells:
        summary = accumulators[cell].summary(target_half_width, minimum_quota)
        by_cell[cell] = {
            "n_discarded_pilot_tasks": summary.n_tasks,
            "paired_sd": summary.paired_sd,
            "paired_sd_upper_95": summary.paired_sd_upper_95,
            "required_confirmatory_quota": summary.normal_approx_required_tasks,
        }
    quota = max(item["required_confirmatory_quota"] for item in by_cell.values())
    attempts = attempt_budget_from_a0(
        accepted=int(a0_result["accepted_tasks"]),
        proposals=int(a0_result["generated_attempts"]),
        confirmatory_quota=quota,
        failure_probability_target=failure_probability_target,
    )
    return {
        "metric": "paired_far_ood_nrmse_contrast",
        "target_ci_half_width": target_half_width,
        "minimum_quota": minimum_quota,
        "primary_cell_count": len(primary_cells),
        "by_primary_cell": by_cell,
        "confirmatory_quota": quota,
        "acceptance_feasibility": {
            "accepted": attempts.accepted,
            "proposals": attempts.proposals,
            "wilson_lower_probability": attempts.wilson_lower_probability,
            "failure_probability_target": attempts.failure_probability_target,
            "max_attempts": attempts.minimum_attempts,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blinded-contrast-csv", type=Path, required=True)
    parser.add_argument("--primary-cells", type=Path, required=True)
    parser.add_argument("--a0-result", type=Path, required=True)
    parser.add_argument("--target-ci-half-width", type=float, required=True)
    parser.add_argument("--minimum-quota", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        args.blinded_contrast_csv,
        json.loads(args.primary_cells.read_text()),
        args.target_ci_half_width,
        args.minimum_quota,
        json.loads(args.a0_result.read_text()),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
