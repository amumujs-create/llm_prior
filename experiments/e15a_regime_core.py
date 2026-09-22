"""Well-specified smooth regime family for E15-A / E15-A0.

The sole event parameter is the onset ``tau``.  Transition width ``s`` and the
relative slope change ``kappa`` are frozen constants.  The post-onset slope
change is structurally tied to the pre-onset slope, ``c=kappa*b``; it is not a
separately unidentified nuisance parameter in a low-exposure prefix.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SmoothRegimeParams:
    """Parameters of a continuous, differentiable slope-change trajectory."""

    a: float  # baseline level
    b: float  # pre-onset slope
    tau: float  # regime onset
    s: float  # fixed transition width
    kappa: float = 1.0  # fixed relative slope change; c = kappa * b

    def __post_init__(self) -> None:
        if not np.all(np.isfinite((self.a, self.b, self.tau, self.s, self.kappa))):
            raise ValueError("smooth-regime parameters must be finite")
        if self.s <= 0:
            raise ValueError("transition width s must be positive")

    @property
    def c(self) -> float:
        """Derived slope-change magnitude, never independently profiled."""
        return self.kappa * self.b


def _softplus(x: np.ndarray) -> np.ndarray:
    """Stable log(1 + exp(x)), including far from the transition."""
    return np.maximum(x, 0.0) + np.log1p(np.exp(-np.abs(x)))


def smooth_regime(t: np.ndarray, params: SmoothRegimeParams) -> np.ndarray:
    """``a+b[t+kappa*s*softplus((t-tau)/s)]`` evaluated stably."""
    time = np.asarray(t, dtype=float)
    if time.ndim != 1 or not np.all(np.isfinite(time)):
        raise ValueError("t must be a finite one-dimensional grid")
    basis = time + params.kappa * params.s * _softplus((time - params.tau) / params.s)
    return params.a + params.b * basis


def smooth_regime_slope(t: np.ndarray, params: SmoothRegimeParams) -> np.ndarray:
    """Derivative, used only for generator/horizon admissibility checks."""
    time = np.asarray(t, dtype=float)
    x = (time - params.tau) / params.s
    logistic = np.empty_like(x)
    positive = x >= 0.0
    logistic[positive] = 1.0 / (1.0 + np.exp(-x[positive]))
    exp_negative = np.exp(x[~positive])
    logistic[~positive] = exp_negative / (1.0 + exp_negative)
    return params.b * (1.0 + params.kappa * logistic)


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
