"""Frozen E15-B policy paths, shared by integrity sanity and confirmation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

try:
    from .e15b_a0_contract import ScopeSupport, profile_weights
    from .e15b_scope_core import (
        ScopeTaskParams, clean_scope_slope, clean_scope_trajectory,
        fit_quadratic_soft_global, fit_quadratic_with_direction_constraint,
        fit_quadratic_with_direction_slack, normalized_entropy_concentration,
        profile_scope_precursor, quadratic_prediction,
    )
    from .run_e15b_a0 import _reference_range, _reference_window_grid
except ImportError:  # pragma: no cover
    from e15b_a0_contract import ScopeSupport, profile_weights
    from e15b_scope_core import ScopeTaskParams, clean_scope_slope, clean_scope_trajectory, fit_quadratic_soft_global, fit_quadratic_with_direction_constraint, fit_quadratic_with_direction_slack, normalized_entropy_concentration, profile_scope_precursor, quadratic_prediction
    from run_e15b_a0 import _reference_range, _reference_window_grid


POLICIES = ("free_baseline", "hard_global", "hard_local_MAP", "soft_global", "slack_distribution", "scope_hypothesis_ensemble", "evidence_weighted_scope_mixture")
STATES = ("exact", "narrow", "broad", "existence_only", "covered_biased", "uncovered_biased")
EXPOSURES = ("low", "medium", "high")


def load_frozen_manifest(path: str | Path) -> dict:
    path = Path(path)
    manifest = json.loads(path.read_text())
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = path.with_suffix(".sha256").read_text().strip()
    if actual != expected:
        raise RuntimeError(f"manifest SHA mismatch: {actual} != {expected}")
    return manifest


def support_from_manifest(manifest: dict) -> ScopeSupport:
    return ScopeSupport(*map(float, manifest["generator"]["normalized_scope_domain"]))


@dataclass(frozen=True)
class ConfirmatoryTask:
    task_id: int
    params: ScopeTaskParams
    standardized_noise: np.ndarray
    bias_sign: int


def _task_from_seed(manifest: dict, task_id: int) -> ConfirmatoryTask:
    generator, obs = manifest["generator"], manifest["observation_and_evaluation"]
    support = support_from_manifest(manifest)
    rng = np.random.default_rng(np.random.SeedSequence([int(manifest["seed"]), task_id]))
    # This interior range guarantees every predeclared support can be created
    # without clipping. It does not expose h* to any policy.
    h_star = float(rng.uniform(.45, .55))
    modes = tuple(generator["post_scope_modes_balanced"].values())
    mode = float(modes[task_id % len(modes)])
    params = ScopeTaskParams(
        a=float(rng.uniform(*generator["a_uniform"])),
        b=float(rng.uniform(*generator["b_uniform_positive"])),
        gamma=float(generator["gamma0_times_W_h"]) / support.width,
        h_star=h_star, width=support.width, post_scope_mode=mode,
    )
    noise = np.random.default_rng(np.random.SeedSequence([int(manifest["seed"]), task_id, 991])).normal(0., 1., int(obs["prefix_points"]))
    return ConfirmatoryTask(task_id, params, noise, 1 if task_id % 2 else -1)


def accepted_tasks(manifest: dict) -> list[ConfirmatoryTask]:
    quota = int(manifest["precision_and_feasibility"]["confirmatory_quota"])
    max_attempts = int(manifest["precision_and_feasibility"]["max_attempts"])
    gates, obs = manifest["acceptance_gates"], manifest["observation_and_evaluation"]
    out = []
    for proposal in range(max_attempts):
        task = _task_from_seed(manifest, proposal)
        p = task.params
        ref = _reference_window_grid(p.h_star, p.width, obs["common_reference_window_over_W_h"]["start_before_h_star"], obs["common_reference_window_over_W_h"]["end_after_h_star"], 321)
        r_ref = _reference_range(ref, p)
        slope = p.width * float(np.max(np.abs(clean_scope_slope(ref, p)))) / r_ref
        if r_ref < gates["min_reference_range"] or slope > gates["max_normalized_reference_window_slope"]:
            continue
        out.append(ConfirmatoryTask(len(out), p, task.standardized_noise, 1 if len(out) % 2 else -1))
        if len(out) == quota:
            return out
    raise RuntimeError("confirmatory quota exhausted")


def evaluate_prefix(manifest: dict, task: ConfirmatoryTask, exposure: str, state: str) -> dict:
    """Prefix-only policy fitting. Future truth is intentionally not accepted."""
    if exposure not in EXPOSURES or state not in STATES:
        raise ValueError("unknown frozen exposure/state")
    support = support_from_manifest(manifest)
    obs, policy = manifest["observation_and_evaluation"], manifest["secondary_policy_contract"]
    p = task.params
    endpoint = p.h_star - obs["exposure_end_before_h_star_over_W_h"][exposure] * p.width
    t_prefix = np.linspace(obs["observation_start"], endpoint, int(obs["prefix_points"]))
    # R_ref is only a synthetic scale for noise; it is not passed to policies.
    ref = _reference_window_grid(p.h_star, p.width, obs["common_reference_window_over_W_h"]["start_before_h_star"], obs["common_reference_window_over_W_h"]["end_after_h_star"], 321)
    r_ref = _reference_range(ref, p)
    sigma = obs["noise_ratio_sigma_over_R_ref"] * r_ref
    y = clean_scope_trajectory(t_prefix, p) + sigma * task.standardized_noise
    interval = support.interval(p.h_star, state, task.bias_sign if "biased" in state else None)
    grid = support.frozen_grid(interval)
    losses, conditions = profile_scope_precursor(t_prefix, y, grid, p.gamma, sigma)
    weights = profile_weights(losses)
    fits = [fit_quadratic_with_direction_constraint(t_prefix, y, max(float(h), endpoint), tolerance=manifest["acceptance_gates"]["constraint_tolerance"]) for h in grid]
    # This endpoint is public and shared.  It must not be derived from h*,
    # h_viol, an exposure offset, or any task-specific scoring endpoint.
    h_far = float(policy["global_enforcement_endpoint"])
    free = np.linalg.lstsq(np.column_stack((np.ones_like(t_prefix), t_prefix, t_prefix**2)), y, rcond=1e-12)[0]
    hard_global = fit_quadratic_with_direction_constraint(t_prefix, y, h_far, tolerance=manifest["acceptance_gates"]["constraint_tolerance"])
    soft_fit, learned_slack = fit_quadratic_soft_global(t_prefix, y, h_far, reference_y_scale=float(policy["reference_y_scale"]), reference_slope=float(policy["reference_slope"]), penalty_lambda=float(policy["soft_global_lambda"]), tolerance=manifest["acceptance_gates"]["constraint_tolerance"])
    slack_fits = [fit_quadratic_with_direction_slack(t_prefix, y, h_far, float(s), tolerance=manifest["acceptance_gates"]["constraint_tolerance"]) for s in policy["slack_values"]]
    return {"t_prefix": t_prefix, "y_prefix": y, "interval": interval, "grid": grid, "losses": losses, "weights": weights, "conditions": conditions, "fits": fits, "free": free, "hard_global": hard_global, "soft": soft_fit, "soft_learned_slack": learned_slack, "slack_fits": slack_fits, "r_ref_internal": r_ref, "E_h": normalized_entropy_concentration(profile_scope_precursor(t_prefix, y, support.frozen_grid((support.h_min, support.h_max)), p.gamma, sigma)[0])[1]}


def policy_predictions(evaluated: dict, t: np.ndarray) -> dict[str, np.ndarray]:
    local = np.asarray([quadratic_prediction(t, fit.coefficients) for fit in evaluated["fits"]])
    slack = np.asarray([quadratic_prediction(t, fit.coefficients) for fit in evaluated["slack_fits"]])
    return {
        "free_baseline": quadratic_prediction(t, evaluated["free"]),
        "hard_global": quadratic_prediction(t, evaluated["hard_global"].coefficients),
        "hard_local_MAP": local[int(np.argmin(evaluated["losses"]))],
        "soft_global": quadratic_prediction(t, evaluated["soft"].coefficients),
        "slack_distribution": slack.mean(axis=0),
        "scope_hypothesis_ensemble": local.mean(axis=0),
        "evidence_weighted_scope_mixture": np.average(local, axis=0, weights=evaluated["weights"]),
    }
