"""Well-specified smooth regime family for E15-A / E15-A0.

The sole event parameter is the onset ``tau``.  Transition width ``s`` is a
task-level fixed nuisance parameter: it is never optimized alongside tau in an
onset-profile fit, preventing a tau--s uncertainty trade-off from entering the
E15-A utilization estimand.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SmoothRegimeParams:
    """Parameters of a continuous, differentiable slope-change trajectory."""

    a: float  # baseline level
    b: float  # pre-onset slope
    c: float  # slope-change magnitude
    tau: float  # regime onset
    s: float  # fixed transition width

    def __post_init__(self) -> None:
        if not np.all(np.isfinite((self.a, self.b, self.c, self.tau, self.s))):
            raise ValueError("smooth-regime parameters must be finite")
        if self.s <= 0:
            raise ValueError("transition width s must be positive")


def _softplus(x: np.ndarray) -> np.ndarray:
    """Stable log(1 + exp(x)), including far from the transition."""
    return np.maximum(x, 0.0) + np.log1p(np.exp(-np.abs(x)))


def smooth_regime(t: np.ndarray, params: SmoothRegimeParams) -> np.ndarray:
    """``a + b t + c s log(1 + exp((t-tau)/s))`` evaluated stably."""
    time = np.asarray(t, dtype=float)
    if time.ndim != 1 or not np.all(np.isfinite(time)):
        raise ValueError("t must be a finite one-dimensional grid")
    return params.a + params.b * time + params.c * params.s * _softplus(
        (time - params.tau) / params.s
    )


def smooth_regime_slope(t: np.ndarray, params: SmoothRegimeParams) -> np.ndarray:
    """Derivative, used only for generator/horizon admissibility checks."""
    time = np.asarray(t, dtype=float)
    x = (time - params.tau) / params.s
    logistic = np.empty_like(x)
    positive = x >= 0.0
    logistic[positive] = 1.0 / (1.0 + np.exp(-x[positive]))
    exp_negative = np.exp(x[~positive])
    logistic[~positive] = exp_negative / (1.0 + exp_negative)
    return params.b + params.c * logistic


def reference_range(t_eval: np.ndarray, params: SmoothRegimeParams) -> float:
    """E15-A's synthetic scale only; never an input to a fitted policy."""
    y = smooth_regime(t_eval, params)
    value = float(y.max() - y.min())
    if not np.isfinite(value) or value <= 0.0:
        raise ValueError("degenerate or non-finite reference trajectory range")
    return value


def post_onset_fraction(t_eval: np.ndarray, tau: float) -> float:
    """Fraction of an evaluation grid lying weakly after the event onset."""
    time = np.asarray(t_eval, dtype=float)
    if time.ndim != 1 or time.size == 0:
        raise ValueError("t_eval must be a nonempty one-dimensional grid")
    return float(np.mean(time >= tau))


def numerically_admissible(
    t_eval: np.ndarray, params: SmoothRegimeParams, min_reference_range: float
) -> bool:
    """Generator-only gate: nondegenerate finite trajectory without clipping."""
    if min_reference_range <= 0.0:
        raise ValueError("min_reference_range must be positive")
    y = smooth_regime(t_eval, params)
    return bool(np.all(np.isfinite(y)) and (float(y.max() - y.min()) >= min_reference_range))
