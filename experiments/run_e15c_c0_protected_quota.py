"""Protected variance-only quota calibration for frozen E15-C0 geometry.

Individual C1/C2 contrasts, means, signs, predictions, and scores stay inside
this process. The persisted artifact exposes only variance-derived quotas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

if __package__:
    from .e15b_a0_contract import BlindedContrastAccumulator, max_attempts_from_acceptance
    from .run_e15c_c0 import Contract, EXPOSURES, profile_all_q, task_draws, y_invariant, z_bases
else:  # pragma: no cover - direct script invocation
    from e15b_a0_contract import BlindedContrastAccumulator, max_attempts_from_acceptance
    from run_e15c_c0 import Contract, EXPOSURES, profile_all_q, task_draws, y_invariant, z_bases


@dataclass(frozen=True)
class ProtectedQuotaContract:
    contract_id: str = "e15-c0-protected-quota-v1"
    pilot_seed: int = 151504
    pilot_tasks: int = 240
    grid_step: float = .05
    rho: float = .10
    x_far: float = 1.00
    epsilon: float = .025
    minimum_quota: int = 125


def _weights(losses: np.ndarray) -> np.ndarray:
    log_w = -(losses - losses.min(axis=1, keepdims=True))
    log_w -= np.logaddexp.reduce(log_w, axis=1, keepdims=True)
    return np.exp(log_w)


def run(contract: ProtectedQuotaContract) -> dict:
    base = Contract(seed=contract.pilot_seed, n_tasks=contract.pilot_tasks)
    q_true, amplitude, master_noise = task_draws(base)
    q_grid = np.linspace(0.0, 1.0, int(round(1.0 / contract.grid_step)) + 1)
    x_full = np.linspace(0.0, 1.0, base.n_observation_points)
    z1_full, z3_full = z_bases(x_full, base.kappa0)
    z_true = (1.0 - q_true[:, None]) * z1_full[None, :] + q_true[:, None] * z3_full[None, :]
    clean = y_invariant(x_full, base)[None, :] + amplitude[:, None] * z_true
    sigma = contract.rho * base.r_inv
    noisy = clean + sigma * master_noise
    x_forecast = np.linspace(.75, contract.x_far, base.n_forecast_points)
    future_mask = x_forecast > .75
    z1_forecast, z3_forecast = z_bases(x_forecast, base.kappa0)
    zq_forecast = (1.0 - q_grid[:, None]) * z1_forecast[None, :] + q_grid[:, None] * z3_forecast[None, :]
    inv_forecast = y_invariant(x_forecast, base)
    z_true_forecast = (1.0 - q_true[:, None]) * z1_forecast[None, :] + q_true[:, None] * z3_forecast[None, :]
    truth = inv_forecast[None, :] + amplitude[:, None] * z_true_forecast

    accumulators = {(contrast, exposure): BlindedContrastAccumulator() for contrast in ("C1_C", "C2_C") for exposure in EXPOSURES}
    accepted = 0
    rejected = 0
    for exposure, endpoint in EXPOSURES.items():
        obs_mask = x_full <= endpoint + 1e-12
        a_hat, losses, _ = profile_all_q(noisy[:, obs_mask], x_full[obs_mask], q_grid, sigma, base)
        predictions = inv_forecast[None, None, :] + a_hat[:, :, None] * zq_forecast[None, :, :]
        map_prediction = predictions[np.arange(base.n_tasks), np.argmin(losses, axis=1)]
        uniform_prediction = predictions.mean(axis=1)
        weighted_prediction = np.einsum("tq,tqf->tf", _weights(losses), predictions, optimize=True)
        if not (np.all(np.isfinite(map_prediction)) and np.all(np.isfinite(uniform_prediction)) and np.all(np.isfinite(weighted_prediction))):
            rejected += base.n_tasks
            continue
        map_nrmse = np.sqrt(np.mean((map_prediction[:, future_mask] - truth[:, future_mask]) ** 2, axis=1)) / base.r_inv
        uniform_nrmse = np.sqrt(np.mean((uniform_prediction[:, future_mask] - truth[:, future_mask]) ** 2, axis=1)) / base.r_inv
        weighted_nrmse = np.sqrt(np.mean((weighted_prediction[:, future_mask] - truth[:, future_mask]) ** 2, axis=1)) / base.r_inv
        # Values are deliberately streamed and then discarded; no raw contrast
        # array, mean, or sign is persisted or returned.
        for value in weighted_nrmse - map_nrmse:
            accumulators[("C1_C", exposure)].update(float(value))
        for value in weighted_nrmse - uniform_nrmse:
            accumulators[("C2_C", exposure)].update(float(value))
        accepted = base.n_tasks

    if rejected:
        raise RuntimeError("protected quota pilot encountered non-finite predictions")
    cells = []
    for contrast in ("C1_C", "C2_C"):
        for exposure in EXPOSURES:
            summary = accumulators[(contrast, exposure)].summary(contract.epsilon, contract.minimum_quota)
            cells.append({"contrast": contrast, "prefix_exposure": exposure, **summary})
    quota = max(cell["required_quota"] for cell in cells)
    attempt = max_attempts_from_acceptance(accepted, base.n_tasks, quota)
    return {
        "contract": contract.__dict__,
        "contract_sha256": hashlib.sha256(json.dumps(contract.__dict__, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "policy_outcomes_inspected": False,
        "raw_contrasts_persisted": False,
        "pilot_acceptance": {"accepted_tasks": accepted, "proposals": base.n_tasks, "rejection_count": rejected},
        "protected_primary_cells": cells,
        "confirmatory_quota": quota,
        "max_attempts": attempt,
        "note": "Only variance-derived quota quantities are exposed. No contrast mean, sign, policy outcome, score, ranking, or winner is present in this artifact.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(ProtectedQuotaContract())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
