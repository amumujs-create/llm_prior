"""In-memory A0 producer of protected paired far-OOD NRMSE contrasts.

Raw signed contrasts exist only as local scalars yielded directly to the quota
accumulator. This module never writes them, their means, policy-level losses,
or policy rankings to disk.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

import numpy as np

try:
    from .e15a_a0_contract import A0SupportContract, profile_weights
    from .e15a_regime_core import numerically_admissible, reference_range, smooth_regime
    from .run_e15a_a0 import _draw_task, _stable_softplus
except ImportError:  # pragma: no cover - direct script execution
    from e15a_a0_contract import A0SupportContract, profile_weights
    from e15a_regime_core import numerically_admissible, reference_range, smooth_regime
    from run_e15a_a0 import _draw_task, _stable_softplus


RCOND = 1e-12
PRIMARY_STATES = ("narrow", "broad", "existence_only", "covered_biased")
EXPOSURES = ("low", "medium", "high")


def _pair(value: list[float]) -> tuple[float, float]:
    return float(value[0]), float(value[1])


def _accepted_tasks(config: dict) -> Iterator:
    support = A0SupportContract(*_pair(config["onset_domain"]), *_pair(config["observation_domain"]))
    rng = np.random.default_rng(int(config["seed"]))
    ranges = {
        "a": _pair(config["parameter_ranges"]["a"]),
        "b_magnitude": _pair(config["parameter_ranges"]["b_magnitude"]),
        "kappa": float(config["kappa"]),
    }
    s0 = float(config["s0"])
    horizon = float(config["noise_reference_horizon_after_onset_ratio"]) * support.width
    grid_points = int(config["eval_points"])
    accepted = 0
    attempts = 0
    while accepted < int(config["pilot_tasks"]) and attempts < int(config["max_attempts"]):
        attempts += 1
        tau = float(rng.uniform(support.tau_min, support.tau_max))
        if not support.accepts_true_onset(tau):
            continue
        b_sign = 1.0 if accepted % 2 else -1.0
        task = _draw_task(rng, ranges, tau, s0, int(rng.integers(0, 2**32 - 1)), b_sign)
        if abs(task.params.c) / float(config["slope_scale"]) <= float(config["min_c_ratio"]):
            continue
        t_eval = np.linspace(support.observation_min, task.params.tau + horizon, grid_points)
        if not numerically_admissible(t_eval, task.params, float(config["min_reference_range"])):
            continue
        accepted += 1
        yield task
    if accepted != int(config["pilot_tasks"]):
        raise RuntimeError("A0 protected producer could not reproduce accepted pilot quota")


def _profile_predictions(
    t_prefix: np.ndarray,
    y_prefix: np.ndarray,
    tau_grid: np.ndarray,
    s0: float,
    kappa: float,
    sigma: float,
    t_eval: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    losses = []
    predictions = []
    for tau in tau_grid:
        basis_prefix = t_prefix + kappa * s0 * _stable_softplus((t_prefix - tau) / s0)
        design = np.column_stack((np.ones_like(t_prefix), basis_prefix))
        coef, *_ = np.linalg.lstsq(design, y_prefix, rcond=RCOND)
        residual = (design @ coef - y_prefix) / sigma
        losses.append(.5 * float(np.sum(residual**2)) + len(t_prefix) * np.log(sigma * np.sqrt(2.0 * np.pi)))
        basis_eval = t_eval + kappa * s0 * _stable_softplus((t_eval - tau) / s0)
        predictions.append(coef[0] + coef[1] * basis_eval)
    return np.asarray(losses), np.asarray(predictions)


def produce(config_path: str | Path) -> Iterator[tuple[str, str, str, float]]:
    """Yield `(knowledge_state, exposure, C#, signed contrast)` in memory only."""
    config = json.loads(Path(config_path).read_text())
    support = A0SupportContract(*_pair(config["onset_domain"]), *_pair(config["observation_domain"]))
    noise_ratio = float(config["selected_noise_ratio"])
    horizon = float(config["selected_horizon_after_onset_ratio"]) * support.width
    far_start = float(config["far_ood_start_after_onset_ratio"]) * support.width
    if noise_ratio not in [float(v) for v in config["noise_ratios"]]:
        raise ValueError("selected_noise_ratio was not an A0 candidate")
    if horizon not in [float(v) * support.width for v in config["horizon_after_onset_ratios"]]:
        raise ValueError("selected_horizon_after_onset_ratio was not an A0 candidate")
    if not 0.0 <= far_start < horizon:
        raise ValueError("far_ood_start_after_onset_ratio must precede the selected horizon")
    for task_index, task in enumerate(_accepted_tasks(config)):
        t_reference = np.linspace(
            task.params.tau + far_start, task.params.tau + horizon, int(config["eval_points"]) + 1
        )[1:]
        r_ref = reference_range(t_reference, task.params)
        sigma = noise_ratio * r_ref
        # Reuse one standardized noise realization for every exposure of this
        # discarded task.  Prefix grids have equal cardinality, so this makes
        # low/mid/high differ only by their endpoint and clean signal.
        standardized_noise = np.random.default_rng(task.seed).normal(
            0.0, 1.0, int(config["prefix_points"])
        )
        for exposure in EXPOSURES:
            endpoint = support.exposure_endpoint(task.params.tau, exposure)
            t_prefix = np.linspace(support.observation_min, endpoint, int(config["prefix_points"]))
            y_prefix = smooth_regime(t_prefix, task.params) + sigma * standardized_noise
            t_far = t_reference
            y_far = smooth_regime(t_far, task.params)
            for state in PRIMARY_STATES:
                # Bias sign is deterministically balanced across discarded tasks.
                sign = 1 if task_index % 2 else -1
                interval = support.knowledge_interval(task.params.tau, state, sign if state == "covered_biased" else None)
                grid = support.frozen_grid(interval)
                losses, predictions = _profile_predictions(
                    t_prefix, y_prefix, grid, task.params.s, task.params.kappa, sigma, t_far
                )
                map_prediction = predictions[int(np.argmin(losses))]
                uniform_prediction = predictions.mean(axis=0)
                mixture_prediction = np.average(predictions, axis=0, weights=profile_weights(losses))
                midpoint_grid = np.array([np.mean(interval)])
                _, midpoint_prediction = _profile_predictions(
                    t_prefix, y_prefix, midpoint_grid, task.params.s, task.params.kappa, sigma, t_far
                )
                midpoint_prediction = midpoint_prediction[0]
                nrmse = lambda prediction: float(np.sqrt(np.mean((prediction - y_far) ** 2)) / r_ref)
                mixture = nrmse(mixture_prediction)
                map_point = nrmse(map_prediction)
                uniform = nrmse(uniform_prediction)
                midpoint = nrmse(midpoint_prediction)
                yield state, exposure, "C1", mixture - map_point
                yield state, exposure, "C2", mixture - uniform
                yield state, exposure, "C3", map_point - midpoint
