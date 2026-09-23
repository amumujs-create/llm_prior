"""Outcome-free numerical calibration for E15-C residual-shape geometry.

This runner implements only frozen C0 diagnostics: residual evidence geometry,
continuation distinctness, closed-versus-uniform non-equivalence, and numerical
stability. It neither calculates nor persists policy performance outcomes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


EXPOSURES = {"low": .25, "medium": .50, "high": .75}
GRID_STEPS = (.05, .025)
NOISE_RATIOS = (.01, .025, .05, .10)
FAR_ENDPOINTS = (.90, 1.00)
DELTA_CONT = .01


@dataclass(frozen=True)
class Contract:
    contract_id: str = "e15-c0-v1"
    seed: int = 151503
    n_tasks: int = 240
    kappa0: float = 1.0
    y0: float = 1.0
    eta_low: float = .5
    eta_high: float = 1.5
    n_observation_points: int = 81
    n_forecast_points: int = 161
    delta_cont: float = DELTA_CONT

    @property
    def r_inv(self) -> float:
        return abs(self.y0) * (1.0 - np.exp(-self.kappa0))

    @property
    def a_ref(self) -> float:
        return self.kappa0 * abs(self.y0)


def z_bases(x: np.ndarray, kappa0: float) -> tuple[np.ndarray, np.ndarray]:
    """Invariant-filtered responses to x and x**3 for kappa0=1-scale time.

    The recurrence z_n=x**n-n*z_(n-1), z_0=(1-exp(-x)), follows directly
    from the convolution. It is evaluated once per common grid; q responses
    are subsequently only linear combinations of these stored bases.
    """
    if not np.isclose(kappa0, 1.0):
        # General-k form retains the same fixed-grid, no-per-q-solve contract.
        dense = np.linspace(0.0, 1.0, 20001)
        kernel = np.exp(-kappa0 * (dense[:, None] - dense[None, :]))
        kernel[np.triu_indices_from(kernel, 1)] = 0.0
        z1_dense = np.trapz(kernel * dense[None, :], dense, axis=1)
        z3_dense = np.trapz(kernel * dense[None, :] ** 3, dense, axis=1)
        return np.interp(x, dense, z1_dense), np.interp(x, dense, z3_dense)
    z0 = -np.expm1(-x)
    z1 = x - z0
    z2 = x * x - 2.0 * z1
    z3 = x**3 - 3.0 * z2
    return z1, z3


def y_invariant(x: np.ndarray, contract: Contract) -> np.ndarray:
    return contract.y0 * np.exp(-contract.kappa0 * x)


def quantiles(values: np.ndarray) -> dict[str, float]:
    return {"q05": float(np.quantile(values, .05)), "median": float(np.median(values)), "q95": float(np.quantile(values, .95))}


def entropy_concentration(losses: np.ndarray) -> np.ndarray:
    log_w = -(losses - losses.min(axis=1, keepdims=True))
    log_w -= np.logaddexp.reduce(log_w, axis=1, keepdims=True)
    weights = np.exp(log_w)
    entropy = -np.sum(np.where(weights > 0.0, weights * log_w, 0.0), axis=1)
    return 1.0 - entropy / np.log(losses.shape[1])


def greedy_distinct_count(predictions: np.ndarray, r_inv: float, delta: float) -> np.ndarray:
    """Deterministic q-ordered greedy packing of pairwise distinct futures."""
    n_tasks, n_q, _ = predictions.shape
    count = np.empty(n_tasks, dtype=int)
    for task in range(n_tasks):
        selected = [0]
        for candidate in range(1, n_q):
            distances = np.sqrt(np.mean((predictions[task, candidate] - predictions[task, selected]) ** 2, axis=1)) / r_inv
            if np.all(distances >= delta):
                selected.append(candidate)
        count[task] = len(selected)
    return count


def task_draws(contract: Contract) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(contract.seed)
    q_true = rng.uniform(0.0, 1.0, contract.n_tasks)
    eta = rng.uniform(contract.eta_low, contract.eta_high, contract.n_tasks)
    signs = np.tile(np.array([-1.0, 1.0]), contract.n_tasks // 2 + 1)[: contract.n_tasks]
    rng.shuffle(signs)
    amplitude = signs * eta * contract.a_ref
    master_noise = rng.standard_normal((contract.n_tasks, contract.n_observation_points))
    return q_true, amplitude, master_noise


def profile_all_q(
    y_obs: np.ndarray,
    x_obs: np.ndarray,
    q_grid: np.ndarray,
    sigma: float,
    contract: Contract,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z1, z3 = z_bases(x_obs, contract.kappa0)
    zq = (1.0 - q_grid[:, None]) * z1[None, :] + q_grid[:, None] * z3[None, :]
    residual = y_obs - y_invariant(x_obs, contract)[None, :]
    denom = np.sum(zq * zq, axis=1)
    if np.any(denom <= 1e-14) or not np.all(np.isfinite(denom)):
        raise FloatingPointError("residual profile basis is degenerate")
    # ``einsum`` avoids platform BLAS floating-point-status warnings observed
    # for this small, well-scaled matrix product while retaining the identical
    # deterministic closed-form profile.
    a_hat = np.einsum("tn,qn->tq", residual, zq, optimize=True) / denom[None, :]
    fitted = y_invariant(x_obs, contract)[None, None, :] + a_hat[:, :, None] * zq[None, :, :]
    sse = np.sum((y_obs[:, None, :] - fitted) ** 2, axis=2)
    losses = .5 * sse / (sigma * sigma)
    return a_hat, losses, denom


def evaluate_candidate(
    contract: Contract,
    q_true: np.ndarray,
    amplitude: np.ndarray,
    master_noise: np.ndarray,
    grid_step: float,
    rho: float,
    x_far: float,
) -> dict:
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

    exposure_result = {}
    all_finite = True
    for label, endpoint in EXPOSURES.items():
        mask = x_full <= endpoint + 1e-12
        a_hat, losses, denom = profile_all_q(noisy[:, mask], x_full[mask], q_grid, sigma, contract)
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
        }

    er = {label: exposure_result[label]["E_r"] for label in EXPOSURES}
    count = {label: exposure_result[label]["effective_residual_continuations"] for label in EXPOSURES}
    closed = {label: exposure_result[label]["uniform_minus_closed_distance"] for label in EXPOSURES}
    ordered = er["low"]["median"] < er["medium"]["median"] < er["high"]["median"]
    adjacent_overlap = er["low"]["q95"] > er["medium"]["q05"] and er["medium"]["q95"] > er["high"]["q05"]
    non_saturated = all(0.0 < er[label]["q05"] and er[label]["q95"] < 1.0 for label in EXPOSURES)
    continuation_gate = all(count[label]["median"] >= 4.0 for label in EXPOSURES)
    closed_separated = all(closed[label]["median"] >= contract.delta_cont for label in EXPOSURES)
    gates = {
        "finite_numerics": all_finite,
        "ordered_E_r_medians": ordered,
        "adjacent_E_r_5_95_overlap": adjacent_overlap,
        "E_r_not_endpoint_saturated": non_saturated,
        "median_effective_continuation_count_ge_4": continuation_gate,
        "uniform_ensemble_not_closed_mechanism": closed_separated,
    }
    return {
        "grid_step": grid_step,
        "rho": rho,
        "x_far": x_far,
        "q_count": int(len(q_grid)),
        "sigma": sigma,
        "exposures": exposure_result,
        "gates": gates,
        "admissible": bool(all(gates.values())),
    }


def choose(results: list[dict]) -> dict:
    # Grid first: coarsest grid with at least one subsequently admissible
    # noise/horizon realization. Then largest rho, then longest x_far.
    admissible = [row for row in results if row["admissible"]]
    selected_grid = next((step for step in GRID_STEPS if any(row["grid_step"] == step for row in admissible)), None)
    if selected_grid is None:
        return {"status": "FAIL", "reason": "no admissible grid-noise-horizon candidate"}
    selected_rho = max(row["rho"] for row in admissible if row["grid_step"] == selected_grid)
    selected_x_far = max(row["x_far"] for row in admissible if row["grid_step"] == selected_grid and row["rho"] == selected_rho)
    return {
        "status": "PASS",
        "selected_grid_step": selected_grid,
        "selected_rho": selected_rho,
        "selected_x_far": selected_x_far,
        "selection_order": ["coarsest admissible grid", "largest admissible rho", "longest admissible x_far"],
    }


def run(contract: Contract) -> dict:
    q_true, amplitude, master_noise = task_draws(contract)
    candidates = [
        evaluate_candidate(contract, q_true, amplitude, master_noise, grid_step, rho, x_far)
        for grid_step in GRID_STEPS
        for rho in NOISE_RATIOS
        for x_far in FAR_ENDPOINTS
    ]
    return {
        "contract": asdict(contract) | {"r_inv": contract.r_inv, "a_ref": contract.a_ref},
        "contract_sha256": hashlib.sha256(json.dumps(asdict(contract), sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "policy_outcomes_inspected": False,
        "task_geometry": {"q_true": "uniform[0,1]", "amplitude_ratio": "uniform[.5,1.5] with balanced sign", "shared_standardized_noise": True},
        "candidates": candidates,
        "selection": choose(candidates),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tasks", type=int, default=240)
    parser.add_argument("--seed", type=int, default=151503)
    args = parser.parse_args()
    contract = Contract(seed=args.seed, n_tasks=args.tasks)
    result = run(contract)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
