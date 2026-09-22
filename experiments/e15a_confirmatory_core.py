"""Frozen E15-A policy implementation shared by sanity and confirmatory runs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

try:
    from .e15a_a0_contract import A0SupportContract, onset_evidence_concentration, profile_weights
    from .e15a_regime_core import SmoothRegimeParams, reference_range, smooth_regime
    from .run_e15a_a0 import _draw_task, _stable_softplus
except ImportError:  # pragma: no cover
    from e15a_a0_contract import A0SupportContract, onset_evidence_concentration, profile_weights
    from e15a_regime_core import SmoothRegimeParams, reference_range, smooth_regime
    from run_e15a_a0 import _draw_task, _stable_softplus


RCOND = 1e-12
POLICIES = (
    "free_onset_baseline", "hard_midpoint", "evidence_MAP_point", "soft_constraint",
    "distributional_prior", "uniform_hypothesis_ensemble", "evidence_weighted_mixture",
)
EXPOSURES = ("low", "medium", "high")


@dataclass(frozen=True)
class ConfirmatoryTask:
    task_id: int
    params: SmoothRegimeParams
    standardized_noise: np.ndarray
    bias_sign: int


def load_manifest(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def support_from_manifest(manifest: dict) -> A0SupportContract:
    generator = manifest["generator"]
    return A0SupportContract(*generator["normalized_onset_domain"], *generator["observation_domain"])


def _profile(
    t_prefix: np.ndarray, y_prefix: np.ndarray, taus: np.ndarray, params: SmoothRegimeParams,
    sigma: float, t_eval: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    losses, predictions = [], []
    for tau in taus:
        basis = t_prefix + params.kappa * params.s * _stable_softplus((t_prefix - tau) / params.s)
        design = np.column_stack((np.ones_like(t_prefix), basis))
        coefficients, *_ = np.linalg.lstsq(design, y_prefix, rcond=RCOND)
        residual = (design @ coefficients - y_prefix) / sigma
        losses.append(.5 * float(np.sum(residual ** 2)) + len(t_prefix) * np.log(sigma * np.sqrt(2.0 * np.pi)))
        eval_basis = t_eval + params.kappa * params.s * _stable_softplus((t_eval - tau) / params.s)
        predictions.append(coefficients[0] + coefficients[1] * eval_basis)
    return np.asarray(losses), np.asarray(predictions)


def accepted_tasks(manifest: dict) -> list[ConfirmatoryTask]:
    """Generate exactly the frozen quota; sign balance is exact up to one task."""
    support = support_from_manifest(manifest)
    generator = manifest["generator"]
    gates = manifest["acceptance_gates"]
    obs = manifest["observation_and_evaluation"]
    rng = np.random.default_rng(int(manifest["seed"]))
    quota = int(manifest["precision_and_feasibility"]["confirmatory_quota"])
    max_attempts = int(manifest["precision_and_feasibility"]["max_attempts"])
    ranges = {"a": tuple(generator["a_uniform"]), "b_magnitude": tuple(generator["abs_b_uniform"]), "kappa": generator["kappa"]}
    out: list[ConfirmatoryTask] = []
    attempts = 0
    far = obs["far_ood_window_after_onset_over_W_tau"]
    while len(out) < quota and attempts < max_attempts:
        attempts += 1
        tau = float(rng.uniform(support.tau_min, support.tau_max))
        if not support.accepts_true_onset(tau):
            continue
        b_sign = 1.0 if len(out) % 2 else -1.0
        seed = int(rng.integers(0, 2**32 - 1))
        draw = _draw_task(rng, ranges, tau, float(generator["s0_over_W_tau"]) * support.width, seed, b_sign)
        t_far = np.linspace(tau + far["open_start"] * support.width, tau + far["closed_end"] * support.width, int(obs["evaluation_points"]) + 1)[1:]
        if reference_range(t_far, draw.params) < float(gates["min_reference_range"]):
            continue
        noise = np.random.default_rng(seed).normal(0.0, 1.0, int(obs["prefix_points"]))
        out.append(ConfirmatoryTask(len(out), draw.params, noise, 1 if len(out) % 2 else -1))
    if len(out) != quota:
        raise RuntimeError(f"only {len(out)}/{quota} tasks accepted within {max_attempts} proposals")
    return out


def evaluate_prefix(manifest: dict, task: ConfirmatoryTask, exposure: str, state: str) -> dict:
    """Evaluate all policies using only one noisy prefix; never receives future labels."""
    support = support_from_manifest(manifest)
    obs = manifest["observation_and_evaluation"]
    params = task.params
    endpoint = support.exposure_endpoint(params.tau, exposure)
    t_prefix = np.linspace(support.observation_min, endpoint, int(obs["prefix_points"]))
    far = obs["far_ood_window_after_onset_over_W_tau"]
    t_far = np.linspace(
        params.tau + far["open_start"] * support.width,
        params.tau + far["closed_end"] * support.width,
        int(obs["evaluation_points"]) + 1,
    )[1:]
    r_ref = reference_range(t_far, params)
    sigma = float(obs["noise_ratio_sigma_over_R_ref"]) * r_ref
    y_prefix = smooth_regime(t_prefix, params) + sigma * task.standardized_noise
    interval = support.knowledge_interval(params.tau, state, task.bias_sign if "biased" in state else None)
    grid = support.frozen_grid(interval)
    losses, predictions = _profile(t_prefix, y_prefix, grid, params, sigma, t_far)
    full_grid = support.frozen_grid((support.tau_min, support.tau_max))
    full_losses, full_predictions = _profile(t_prefix, y_prefix, full_grid, params, sigma, t_far)
    midpoint = np.array([np.mean(interval)])
    _, midpoint_predictions = _profile(t_prefix, y_prefix, midpoint, params, sigma, t_far)
    quad_nodes, quad_weights = support.quadrature(interval)
    _, quadrature_predictions = _profile(t_prefix, y_prefix, quad_nodes, params, sigma, t_far)
    weights = profile_weights(losses)
    h_n = support.narrow_half_width
    soft_penalty = ((np.maximum(interval[0] - full_grid, 0.0) / h_n) ** 2
                    + (np.maximum(full_grid - interval[1], 0.0) / h_n) ** 2)
    soft_index = int(np.argmin(full_losses + soft_penalty))
    policy_predictions = {
        "free_onset_baseline": full_predictions[int(np.argmin(full_losses))],
        "hard_midpoint": midpoint_predictions[0],
        "evidence_MAP_point": predictions[int(np.argmin(losses))],
        "soft_constraint": full_predictions[soft_index],
        "distributional_prior": np.average(quadrature_predictions, axis=0, weights=quad_weights),
        "uniform_hypothesis_ensemble": predictions.mean(axis=0),
        "evidence_weighted_mixture": np.average(predictions, axis=0, weights=weights),
    }
    map_index = int(np.argmin(losses))
    return {
        "task_id": task.task_id, "exposure": exposure, "knowledge_state": state,
        "tau_star": params.tau, "interval": interval, "t_prefix": t_prefix, "t_far": t_far,
        "r_ref": r_ref, "sigma": sigma, "profile_losses": losses, "mixture_weights": weights,
        "full_profile_losses": full_losses, "policy_predictions": policy_predictions,
        "grid": grid, "quadrature_nodes": quad_nodes, "quadrature_weights": quad_weights,
        "map_tau": float(grid[map_index]),
        "E_tau": onset_evidence_concentration(full_losses),
    }
