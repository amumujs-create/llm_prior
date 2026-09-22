"""E15-B support geometry and protected quota-calibration helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log
from typing import Iterable

import numpy as np
from scipy.stats import binom, chi2


GRID_STEP_RATIO = 0.025
NARROW_HALF_WIDTH_RATIO = 0.10
BROAD_HALF_WIDTH_RATIO = 0.30
COVERED_BIAS_RATIO = 0.05
UNCOVERED_BIAS_RATIO = 0.15
PRIMARY_STATES = ("narrow", "broad", "existence_only", "covered_biased")
EXPOSURES = ("low", "medium", "high")


@dataclass(frozen=True)
class ScopeSupport:
    h_min: float
    h_max: float
    grid_step_ratio: float = GRID_STEP_RATIO

    @property
    def width(self) -> float:
        return self.h_max - self.h_min

    @property
    def grid_step(self) -> float:
        return self.grid_step_ratio * self.width

    def interval(self, h_star: float, state: str, bias_sign: int | None = None) -> tuple[float, float]:
        if state == "exact":
            interval = (h_star, h_star)
        elif state == "narrow":
            interval = (h_star - NARROW_HALF_WIDTH_RATIO * self.width, h_star + NARROW_HALF_WIDTH_RATIO * self.width)
        elif state == "broad":
            interval = (h_star - BROAD_HALF_WIDTH_RATIO * self.width, h_star + BROAD_HALF_WIDTH_RATIO * self.width)
        elif state == "existence_only":
            interval = (self.h_min, self.h_max)
        elif state in {"covered_biased", "uncovered_biased"}:
            if bias_sign not in {-1, 1}:
                raise ValueError("biased scope support needs a sign")
            shift = (COVERED_BIAS_RATIO if state == "covered_biased" else UNCOVERED_BIAS_RATIO) * self.width
            center = h_star + bias_sign * shift
            interval = (center - NARROW_HALF_WIDTH_RATIO * self.width, center + NARROW_HALF_WIDTH_RATIO * self.width)
        else:
            raise ValueError(f"unknown scope knowledge state: {state}")
        lo, hi = interval
        if not self.h_min <= lo <= hi <= self.h_max:
            raise ValueError("scope support would require clipping; reject the task")
        return float(lo), float(hi)

    def frozen_grid(self, interval: tuple[float, float]) -> np.ndarray:
        lo, hi = interval
        if lo == hi:
            return np.array([lo], dtype=float)
        count = int(round((hi - lo) / self.grid_step))
        if not np.isclose(count * self.grid_step, hi - lo, rtol=0.0, atol=1e-12):
            raise ValueError("scope support incompatible with frozen .025 W_h grid")
        return np.linspace(lo, hi, count + 1)


def profile_weights(losses: Iterable[float]) -> np.ndarray:
    losses = np.asarray(list(losses), dtype=float)
    if losses.ndim != 1 or len(losses) == 0 or not np.all(np.isfinite(losses)):
        raise ValueError("profile losses must be nonempty and finite")
    log_weights = -(losses - np.min(losses))
    log_weights -= np.logaddexp.reduce(log_weights)
    return np.exp(log_weights)


@dataclass
class BlindedContrastAccumulator:
    """Streaming variance only: never exposes a contrast mean or sign."""

    count: int = 0
    _mean: float = 0.0
    _m2: float = 0.0

    def update(self, value: float) -> None:
        self.count += 1
        delta = value - self._mean
        self._mean += delta / self.count
        self._m2 += delta * (value - self._mean)

    def summary(self, epsilon: float, minimum_quota: int) -> dict[str, float | int]:
        if self.count < 2:
            raise ValueError("at least two discarded tasks are required")
        sd = float(np.sqrt(self._m2 / (self.count - 1)))
        upper = float(sd * np.sqrt((self.count - 1) / chi2.ppf(.05, self.count - 1)))
        quota = max(minimum_quota, ceil((1.96 * upper / epsilon) ** 2))
        return {"n_tasks": self.count, "paired_sd": sd, "paired_sd_upper_95": upper, "required_quota": quota}


def wilson_lower(accepted: int, proposals: int, z: float = 1.6448536269514722) -> float:
    if not 0 < accepted <= proposals:
        raise ValueError("need 0 < accepted <= proposals")
    p = accepted / proposals
    denom = 1 + z**2 / proposals
    center = p + z**2 / (2 * proposals)
    margin = z * np.sqrt(p * (1 - p) / proposals + z**2 / (4 * proposals**2))
    return float((center - margin) / denom)


def max_attempts_from_acceptance(accepted: int, proposals: int, quota: int, failure_probability: float = 1e-4) -> dict[str, float | int]:
    p_lower = wilson_lower(accepted, proposals)
    attempts = quota
    while binom.cdf(quota - 1, attempts, p_lower) >= failure_probability:
        attempts += 1
    return {"accepted": accepted, "proposals": proposals, "wilson_lower_probability": p_lower, "max_attempts": attempts, "failure_probability_target": failure_probability}
