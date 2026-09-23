"""Protected E15-C0 v1.1 quota run; bounded profile, no outcome disclosure."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

if __package__:
    from .e15b_a0_contract import BlindedContrastAccumulator, max_attempts_from_acceptance
    from .run_e15c_c0 import EXPOSURES, task_draws, y_invariant, z_bases
    from .run_e15c_c0_v1_1 import BoundedContract, bounded_profile_all_q
else:  # pragma: no cover
    from e15b_a0_contract import BlindedContrastAccumulator, max_attempts_from_acceptance
    from run_e15c_c0 import EXPOSURES, task_draws, y_invariant, z_bases
    from run_e15c_c0_v1_1 import BoundedContract, bounded_profile_all_q


@dataclass(frozen=True)
class ProtectedQuotaV11:
    contract_id: str = "e15-c0-v1.1-protected-quota"
    pilot_seed: int = 151504
    pilot_tasks: int = 240
    grid_step: float = .05
    rho: float = .10
    x_far: float = 1.00
    amplitude_bound_ratio: float = 1.5
    epsilon: float = .025
    minimum_quota: int = 125


def weights(losses: np.ndarray) -> np.ndarray:
    log_w = -(losses - losses.min(axis=1, keepdims=True))
    log_w -= np.logaddexp.reduce(log_w, axis=1, keepdims=True)
    return np.exp(log_w)


def run(contract: ProtectedQuotaV11) -> dict:
    base = BoundedContract(seed=contract.pilot_seed, n_tasks=contract.pilot_tasks, amplitude_bound_ratio=contract.amplitude_bound_ratio)
    q_true, amplitude, master_noise = task_draws(base)
    q_grid = np.linspace(0.0, 1.0, int(round(1.0 / contract.grid_step)) + 1)
    x_full = np.linspace(0.0, 1.0, base.n_observation_points)
    z1_full, z3_full = z_bases(x_full, base.kappa0)
    z_true = (1.0-q_true[:, None])*z1_full[None, :] + q_true[:, None]*z3_full[None, :]
    clean = y_invariant(x_full, base)[None, :] + amplitude[:, None]*z_true
    sigma = contract.rho*base.r_inv
    noisy = clean + sigma*master_noise
    x_forecast = np.linspace(.75, contract.x_far, base.n_forecast_points)
    future = x_forecast > .75
    z1_forecast, z3_forecast = z_bases(x_forecast, base.kappa0)
    zq_forecast = (1.0-q_grid[:, None])*z1_forecast[None, :] + q_grid[:, None]*z3_forecast[None, :]
    inv_forecast = y_invariant(x_forecast, base)
    z_truth = (1.0-q_true[:, None])*z1_forecast[None, :] + q_true[:, None]*z3_forecast[None, :]
    truth = inv_forecast[None, :] + amplitude[:, None]*z_truth
    accumulators = {(name, exposure): BlindedContrastAccumulator() for name in ("C1_C", "C2_C") for exposure in EXPOSURES}

    for exposure, endpoint in EXPOSURES.items():
        observed = x_full <= endpoint + 1e-12
        a_hat, losses, _ = bounded_profile_all_q(noisy[:, observed], x_full[observed], q_grid, sigma, base)
        predictions = inv_forecast[None, None, :] + a_hat[:, :, None]*zq_forecast[None, :, :]
        map_prediction = predictions[np.arange(base.n_tasks), np.argmin(losses, axis=1)]
        uniform_prediction = predictions.mean(axis=1)
        weighted_prediction = np.einsum("tq,tqf->tf", weights(losses), predictions, optimize=True)
        if not all(np.all(np.isfinite(item)) for item in (map_prediction, uniform_prediction, weighted_prediction)):
            raise RuntimeError("non-finite prediction in protected quota pilot")
        map_nrmse = np.sqrt(np.mean((map_prediction[:, future]-truth[:, future])**2, axis=1))/base.r_inv
        uniform_nrmse = np.sqrt(np.mean((uniform_prediction[:, future]-truth[:, future])**2, axis=1))/base.r_inv
        weighted_nrmse = np.sqrt(np.mean((weighted_prediction[:, future]-truth[:, future])**2, axis=1))/base.r_inv
        for value in weighted_nrmse-map_nrmse:
            accumulators[("C1_C", exposure)].update(float(value))
        for value in weighted_nrmse-uniform_nrmse:
            accumulators[("C2_C", exposure)].update(float(value))

    cells=[]
    for name in ("C1_C", "C2_C"):
        for exposure in EXPOSURES:
            cells.append({"contrast": name, "prefix_exposure": exposure, **accumulators[(name, exposure)].summary(contract.epsilon, contract.minimum_quota)})
    quota=max(row["required_quota"] for row in cells)
    return {
        "contract": contract.__dict__,
        "contract_sha256": hashlib.sha256(json.dumps(contract.__dict__, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "estimator_amendment": "bounded amplitude profile only",
        "policy_outcomes_inspected": False,
        "raw_contrasts_persisted": False,
        "pilot_acceptance": {"accepted_tasks": base.n_tasks, "proposals": base.n_tasks, "rejection_count": 0},
        "protected_primary_cells": cells,
        "confirmatory_quota": quota,
        "max_attempts": max_attempts_from_acceptance(base.n_tasks, base.n_tasks, quota),
        "note": "Variance-derived quantities only; contrast means, signs, rankings, and winners are absent.",
    }


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--out",type=Path,required=True); args=parser.parse_args()
    result=run(ProtectedQuotaV11())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")


if __name__ == "__main__":
    main()
