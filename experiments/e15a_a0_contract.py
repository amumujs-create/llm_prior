"""Non-outcome E15-A0 design-calibration contracts.

This module deliberately contains no regime generator, predictive policy, RMSE,
CRPS, winner, or contrast-mean reporting.  Those belong to confirmatory E15-A.
E15-A0 may use it only to freeze support geometry, exposure acceptance,
deterministic quadrature, full-domain onset evidence concentration, and blinded
paired-contrast *variance* for a discarded pilot.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log
from typing import Iterable

import numpy as np


N_QUAD = 201
GRID_STEP_RATIO = 0.025
NARROW_HALF_WIDTH_RATIO = 0.10
BROAD_HALF_WIDTH_RATIO = 0.30
EXPOSURE_ENDPOINT_RATIOS = {"low": -0.20, "medium": -0.05, "high": 0.10}


@dataclass(frozen=True)
class A0SupportContract:
    """Frozen geometry shared by A0 and the eventual confirmatory manifest."""

    tau_min: float
    tau_max: float
    observation_min: float
    observation_max: float
    grid_step_ratio: float = GRID_STEP_RATIO
    n_quad: int = N_QUAD

    def __post_init__(self) -> None:
        if not self.tau_min < self.tau_max:
            raise ValueError("tau_min must be less than tau_max")
        if not self.observation_min < self.observation_max:
            raise ValueError("invalid observation domain")
        if self.grid_step_ratio <= 0:
            raise ValueError("grid_step_ratio must be positive")
        if self.n_quad < 2:
            raise ValueError("n_quad must be at least two")

    @property
    def width(self) -> float:
        return self.tau_max - self.tau_min

    @property
    def broad_half_width(self) -> float:
        return BROAD_HALF_WIDTH_RATIO * self.width

    @property
    def grid_step(self) -> float:
        return self.grid_step_ratio * self.width

    def accepts_true_onset(self, tau_star: float) -> bool:
        """Reject rather than clip any support or exposure boundary violation."""
        broad_ok = (
            self.tau_min <= tau_star - self.broad_half_width
            and tau_star + self.broad_half_width <= self.tau_max
        )
        exposure_ok = (
            self.observation_min
            <= tau_star + EXPOSURE_ENDPOINT_RATIOS["low"] * self.width
            and tau_star + EXPOSURE_ENDPOINT_RATIOS["high"] * self.width
            <= self.observation_max
        )
        return broad_ok and exposure_ok

    def exposure_endpoint(self, tau_star: float, level: str) -> float:
        try:
            ratio = EXPOSURE_ENDPOINT_RATIOS[level]
        except KeyError as exc:
            raise ValueError(f"unknown prefix exposure level: {level}") from exc
        endpoint = tau_star + ratio * self.width
        if not self.observation_min <= endpoint <= self.observation_max:
            raise ValueError("exposure endpoint outside frozen observation domain")
        return endpoint

    def frozen_grid(self, interval: tuple[float, float]) -> np.ndarray:
        """Endpoint-inclusive grid on an already valid, unclipped interval."""
        lo, hi = interval
        if not self.tau_min <= lo <= hi <= self.tau_max:
            raise ValueError("onset support is outside admissible domain; do not clip")
        if lo == hi:
            return np.array([lo], dtype=float)
        n_steps = int(round((hi - lo) / self.grid_step))
        if not np.isclose(n_steps * self.grid_step, hi - lo, rtol=0, atol=1e-12):
            raise ValueError("interval width must be compatible with frozen grid step")
        return np.linspace(lo, hi, n_steps + 1, dtype=float)

    def quadrature(self, interval: tuple[float, float]) -> tuple[np.ndarray, np.ndarray]:
        """Frozen Gauss--Legendre rule; exact support is a point mass."""
        lo, hi = interval
        if not self.tau_min <= lo <= hi <= self.tau_max:
            raise ValueError("onset support is outside admissible domain; do not clip")
        if lo == hi:
            return np.array([lo], dtype=float), np.array([1.0], dtype=float)
        base_nodes, base_weights = np.polynomial.legendre.leggauss(self.n_quad)
        nodes = (hi - lo) * (base_nodes + 1.0) / 2.0 + lo
        weights = base_weights / base_weights.sum()
        return nodes, weights


def profile_weights(profile_nll: Iterable[float]) -> np.ndarray:
    """Un-tempered (T=1) stable likelihood weights for a shared profile score."""
    ell = np.asarray(list(profile_nll), dtype=float)
    if ell.ndim != 1 or ell.size == 0 or not np.all(np.isfinite(ell)):
        raise ValueError("profile_nll must be a nonempty finite vector")
    unnormalized = np.exp(-(ell - ell.min()))
    return unnormalized / unnormalized.sum()


def onset_evidence_concentration(full_domain_profile_nll: Iterable[float]) -> float:
    """Full-domain E_tau, deliberately independent of the supplied support I."""
    weights = profile_weights(full_domain_profile_nll)
    if weights.size < 2:
        raise ValueError("full admissible onset grid must contain at least two hypotheses")
    entropy = -float(np.sum(weights * np.log(weights)))
    return float(1.0 - entropy / log(weights.size))


@dataclass(frozen=True)
class BlindedVarianceSummary:
    """A0-safe quota information: no contrast mean, sign, or policy ranking."""

    n_tasks: int
    paired_sd: float
    target_half_width: float
    normal_approx_required_tasks: int


def blinded_paired_variance_summary(
    paired_loss_contrasts: Iterable[float], target_half_width: float
) -> BlindedVarianceSummary:
    """Return only dispersion and a conservative normal-approximation quota."""
    contrast = np.asarray(list(paired_loss_contrasts), dtype=float)
    if contrast.ndim != 1 or contrast.size < 2 or not np.all(np.isfinite(contrast)):
        raise ValueError("need at least two finite paired contrasts")
    if target_half_width <= 0:
        raise ValueError("target_half_width must be positive")
    paired_sd = float(np.std(contrast, ddof=1))
    required = int(ceil((1.96 * paired_sd / target_half_width) ** 2))
    return BlindedVarianceSummary(
        n_tasks=int(contrast.size),
        paired_sd=paired_sd,
        target_half_width=float(target_half_width),
        normal_approx_required_tasks=required,
    )
