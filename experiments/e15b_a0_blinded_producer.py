"""In-memory protected E15-B0 D1/D2 producer; raw contrasts never persist."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterator

import numpy as np

try:
    from .e15b_a0_contract import EXPOSURES, PRIMARY_STATES, ScopeSupport, profile_weights
    from .e15b_scope_core import (
        clean_scope_slope, clean_scope_trajectory, fit_quadratic_with_direction_constraint,
        profile_scope_precursor, quadratic_prediction,
    )
    from .run_e15b_a0 import _draw_task, _reference_range, _reference_window_grid
except ImportError:  # pragma: no cover
    from e15b_a0_contract import EXPOSURES, PRIMARY_STATES, ScopeSupport, profile_weights
    from e15b_scope_core import clean_scope_slope, clean_scope_trajectory, fit_quadratic_with_direction_constraint, profile_scope_precursor, quadratic_prediction
    from run_e15b_a0 import _draw_task, _reference_range, _reference_window_grid


def _accepted_tasks(config: dict) -> Iterator:
    support = ScopeSupport(*map(float, config["scope_domain"]))
    width = float(config["scope_width"])
    rng = np.random.default_rng(int(config["seed"]))
    margin = float(config["support_margin_ratio"]) * width
    modes = tuple(float(value) for value in config["post_scope_modes"])
    horizon = float(config["noise_reference_horizon_ratio"]) * width
    start_ratio = float(config["reference_window_start_before_scope_ratio"])
    attempts = accepted = 0
    while accepted < int(config["pilot_tasks"]) and attempts < int(config["max_attempts"]):
        attempts += 1
        h_star = float(rng.uniform(support.h_min + margin, support.h_max - margin))
        mode = modes[(attempts - 1) % len(modes)]
        task = _draw_task(rng, config, h_star, mode)
        ref = _reference_window_grid(h_star, width, start_ratio, horizon / width, int(config["eval_points"]))
        r_ref = _reference_range(ref, task.params)
        if r_ref < float(config["min_reference_range"]):
            continue
        slope = width * float(np.max(np.abs(clean_scope_slope(ref, task.params)))) / r_ref
        if slope > float(config["max_normalized_slope"]):
            continue
        accepted += 1
        yield accepted - 1, task
    if accepted != int(config["pilot_tasks"]):
        raise RuntimeError("protected producer could not reproduce E15-B0 accepted quota")


def produce(contract_path: str | Path) -> Iterator[tuple[str, str, str, float]]:
    """Yield only in-memory `(state, exposure, D#, signed_scalar)` values."""
    config = json.loads(Path(contract_path).read_text())
    support = ScopeSupport(*map(float, config["scope_domain"]))
    width = support.width
    gamma = float(config["gamma0_times_scope_width"]) / width
    h_full = support.frozen_grid((support.h_min, support.h_max))
    rho = float(config["noise_ratios"][0])
    horizon = float(config["noise_reference_horizon_ratio"]) * width
    reference_start = float(config["reference_window_start_before_scope_ratio"])
    constraint_tolerance = float(config["constraint_tolerance"])
    for task_index, task in _accepted_tasks(config):
        params = task.params
        ref_grid = _reference_window_grid(params.h_star, width, reference_start, horizon / width, int(config["eval_points"]))
        r_ref = _reference_range(ref_grid, params)
        sigma = rho * r_ref
        t_far = np.linspace(params.h_star, params.h_star + horizon, int(config["eval_points"]) + 1)[1:]
        y_far = clean_scope_trajectory(t_far, params)
        standardized_noise = np.random.default_rng(task.seed).normal(0.0, 1.0, int(config["prefix_points"]))
        for exposure, ratio in config["exposure_offsets"].items():
            endpoint = params.h_star - float(ratio) * width
            t_prefix = np.linspace(float(config["observation_start"]), endpoint, int(config["prefix_points"]))
            y_prefix = clean_scope_trajectory(t_prefix, params) + sigma * standardized_noise
            bias_sign = 1 if task_index % 2 else -1
            for state in PRIMARY_STATES:
                interval = support.interval(params.h_star, state, bias_sign if state == "covered_biased" else None)
                grid = support.frozen_grid(interval)
                losses, _ = profile_scope_precursor(t_prefix, y_prefix, grid, gamma, sigma)
                # A warranted endpoint already behind the observed prefix adds no
                # future enforcement; it is represented by the prefix endpoint,
                # not rejected or allowed to impose a retroactive constraint.
                fits = [
                    fit_quadratic_with_direction_constraint(
                        t_prefix, y_prefix, max(float(h), endpoint), tolerance=constraint_tolerance
                    )
                    for h in grid
                ]
                predictions = np.asarray([quadratic_prediction(t_far, fit.coefficients) for fit in fits])
                map_prediction = predictions[int(np.argmin(losses))]
                uniform_prediction = predictions.mean(axis=0)
                mixture_prediction = np.average(predictions, axis=0, weights=profile_weights(losses))
                nrmse = lambda prediction: float(np.sqrt(np.mean((prediction - y_far) ** 2)) / r_ref)
                mixture = nrmse(mixture_prediction)
                yield state, exposure, "D1", mixture - nrmse(map_prediction)
                yield state, exposure, "D2", mixture - nrmse(uniform_prediction)
