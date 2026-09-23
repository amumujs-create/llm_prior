"""E15-C0 v1.1 outcome-free sweep with bounded amplitude profiling only."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

if __package__:
    from .run_e15c_c0 import (DELTA_CONT, EXPOSURES, FAR_ENDPOINTS, GRID_STEPS, NOISE_RATIOS, Contract, entropy_concentration, greedy_distinct_count, quantiles, task_draws, y_invariant, z_bases)
else:  # pragma: no cover - direct script invocation
    from run_e15c_c0 import (DELTA_CONT, EXPOSURES, FAR_ENDPOINTS, GRID_STEPS, NOISE_RATIOS, Contract, entropy_concentration, greedy_distinct_count, quantiles, task_draws, y_invariant, z_bases)


@dataclass(frozen=True)
class BoundedContract(Contract):
    contract_id: str = "e15-c0-v1.1"
    amplitude_bound_ratio: float = 1.5


def bounded_profile_all_q(y_obs: np.ndarray, x_obs: np.ndarray, q_grid: np.ndarray, sigma: float, contract: BoundedContract) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z1, z3 = z_bases(x_obs, contract.kappa0)
    zq = (1.0 - q_grid[:, None]) * z1[None, :] + q_grid[:, None] * z3[None, :]
    residual = y_obs - y_invariant(x_obs, contract)[None, :]
    denom = np.sum(zq * zq, axis=1)
    if np.any(denom <= 1e-14) or not np.all(np.isfinite(denom)):
        raise FloatingPointError("residual profile basis is degenerate")
    a_ls = np.einsum("tn,qn->tq", residual, zq, optimize=True) / denom[None, :]
    bound = contract.amplitude_bound_ratio * contract.a_ref
    a_hat = np.clip(a_ls, -bound, bound)
    fitted = y_invariant(x_obs, contract)[None, None, :] + a_hat[:, :, None] * zq[None, :, :]
    losses = .5 * np.sum((y_obs[:, None, :] - fitted) ** 2, axis=2) / (sigma * sigma)
    return a_hat, losses, denom


def evaluate_candidate(contract: BoundedContract, q_true: np.ndarray, amplitude: np.ndarray, master_noise: np.ndarray, grid_step: float, rho: float, x_far: float) -> dict:
    q_grid = np.linspace(0.0, 1.0, int(round(1.0 / grid_step)) + 1)
    x_full = np.linspace(0.0, 1.0, contract.n_observation_points)
    z1_full, z3_full = z_bases(x_full, contract.kappa0)
    z_true = (1.0 - q_true[:, None]) * z1_full[None, :] + q_true[:, None] * z3_full[None, :]
    clean = y_invariant(x_full, contract)[None, :] + amplitude[:, None] * z_true
    sigma = rho * contract.r_inv
    noisy = clean + sigma * master_noise
    x_forecast = np.linspace(.75, x_far, contract.n_forecast_points)
    z1_forecast, z3_forecast = z_bases(x_forecast, contract.kappa0)
    zq_forecast = (1.0 - q_grid[:, None]) * z1_forecast[None, :] + q_grid[:, None] * z3_forecast[None, :]
    inv_forecast = y_invariant(x_forecast, contract)
    exposure_result, all_finite = {}, True
    for label, endpoint in EXPOSURES.items():
        mask = x_full <= endpoint + 1e-12
        a_hat, losses, denom = bounded_profile_all_q(noisy[:, mask], x_full[mask], q_grid, sigma, contract)
        e_r = entropy_concentration(losses)
        predictions = inv_forecast[None, None, :] + a_hat[:, :, None] * zq_forecast[None, :, :]
        counts = greedy_distinct_count(predictions, contract.r_inv, contract.delta_cont)
        uniform = predictions.mean(axis=1)
        uniform_closed_distance = np.sqrt(np.mean((uniform - inv_forecast[None, :]) ** 2, axis=1)) / contract.r_inv
        all_finite &= bool(np.all(np.isfinite(a_hat)) and np.all(np.isfinite(losses)) and np.all(np.isfinite(predictions)))
        exposure_result[label] = {
            "E_r": quantiles(e_r),
            "effective_residual_continuations": quantiles(counts.astype(float)),
            "uniform_minus_closed_distance": quantiles(uniform_closed_distance),
            "uniform_closed_distance_fraction_ge_delta": float(np.mean(uniform_closed_distance >= contract.delta_cont)),
            "profile_basis_minimum": float(denom.min()),
            "bounded_amplitude_fraction": float(np.mean(np.isclose(np.abs(a_hat), contract.amplitude_bound_ratio * contract.a_ref))),
        }
    er = {label: exposure_result[label]["E_r"] for label in EXPOSURES}
    count = {label: exposure_result[label]["effective_residual_continuations"] for label in EXPOSURES}
    closed = {label: exposure_result[label]["uniform_minus_closed_distance"] for label in EXPOSURES}
    gates = {
        "finite_numerics": all_finite,
        "ordered_E_r_medians": er["low"]["median"] < er["medium"]["median"] < er["high"]["median"],
        "adjacent_E_r_5_95_overlap": er["low"]["q95"] > er["medium"]["q05"] and er["medium"]["q95"] > er["high"]["q05"],
        "E_r_not_endpoint_saturated": all(0.0 < er[label]["q05"] and er[label]["q95"] < 1.0 for label in EXPOSURES),
        "median_effective_continuation_count_ge_4": all(count[label]["median"] >= 4.0 for label in EXPOSURES),
        "uniform_ensemble_not_closed_mechanism": all(closed[label]["median"] >= contract.delta_cont for label in EXPOSURES),
    }
    return {"grid_step": grid_step, "rho": rho, "x_far": x_far, "q_count": int(len(q_grid)), "sigma": sigma, "exposures": exposure_result, "gates": gates, "admissible": bool(all(gates.values()))}


def choose(results: list[dict]) -> dict:
    admissible = [row for row in results if row["admissible"]]
    selected_grid = next((step for step in GRID_STEPS if any(row["grid_step"] == step for row in admissible)), None)
    if selected_grid is None:
        return {"status": "FAIL", "reason": "no admissible grid-noise-horizon candidate"}
    selected_rho = max(row["rho"] for row in admissible if row["grid_step"] == selected_grid)
    selected_x_far = max(row["x_far"] for row in admissible if row["grid_step"] == selected_grid and row["rho"] == selected_rho)
    return {"status": "PASS", "selected_grid_step": selected_grid, "selected_rho": selected_rho, "selected_x_far": selected_x_far, "selection_order": ["coarsest admissible grid", "largest admissible rho", "longest admissible x_far"]}


def run(contract: BoundedContract) -> dict:
    q_true, amplitude, master_noise = task_draws(contract)
    candidates = [evaluate_candidate(contract, q_true, amplitude, master_noise, grid_step, rho, x_far) for grid_step in GRID_STEPS for rho in NOISE_RATIOS for x_far in FAR_ENDPOINTS]
    return {
        "contract": asdict(contract) | {"r_inv": contract.r_inv, "a_ref": contract.a_ref},
        "contract_sha256": hashlib.sha256(json.dumps(asdict(contract), sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "estimator_amendment": "bounded amplitude profile only: clip A_LS to [-1.5 A_ref, +1.5 A_ref]",
        "policy_outcomes_inspected": False,
        "candidates": candidates,
        "selection": choose(candidates),
    }


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(BoundedContract())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
