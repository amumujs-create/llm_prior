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
from scipy.stats import binom, chi2


N_QUAD = 201
GRID_STEP_RATIO = 0.025
NARROW_HALF_WIDTH_RATIO = 0.10
BROAD_HALF_WIDTH_RATIO = 0.30
COVERED_BIAS_RATIO = 0.05
UNCOVERED_BIAS_RATIO = 0.15
WRONG_ONSET_TOLERANCE_RATIO = 0.05
ENTROPY_COLLAPSE_THRESHOLD = 0.25
EXPOSURE_ENDPOINT_RATIOS = {"low": -0.20, "medium": -0.05, "high": 0.10}
KNOWLEDGE_STATES = (
    "exact",
    "narrow",
    "broad",
    "existence_only",
    "covered_biased",
    "uncovered_biased",
)


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

    @property
    def narrow_half_width(self) -> float:
        return NARROW_HALF_WIDTH_RATIO * self.width

    @property
    def wrong_onset_tolerance(self) -> float:
        return WRONG_ONSET_TOLERANCE_RATIO * self.width

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

    def knowledge_interval(
        self, tau_star: float, state: str, bias_sign: int | None = None
    ) -> tuple[float, float]:
        """Single source of truth for all six declared onset-support states.

        Intervals are never clipped.  A caller must reject a task whose requested
        state cannot be represented within the frozen admissible domain.
        """
        if state not in KNOWLEDGE_STATES:
            raise ValueError(f"unknown knowledge state: {state}")
        if state == "exact":
            interval = (tau_star, tau_star)
        elif state == "narrow":
            interval = (tau_star - self.narrow_half_width, tau_star + self.narrow_half_width)
        elif state == "broad":
            interval = (tau_star - self.broad_half_width, tau_star + self.broad_half_width)
        elif state == "existence_only":
            interval = (self.tau_min, self.tau_max)
        else:
            if bias_sign not in {-1, 1}:
                raise ValueError("biased knowledge states require bias_sign in {-1, +1}")
            shift_ratio = COVERED_BIAS_RATIO if state == "covered_biased" else UNCOVERED_BIAS_RATIO
            center = tau_star + bias_sign * shift_ratio * self.width
            interval = (center - self.narrow_half_width, center + self.narrow_half_width)
        lo, hi = interval
        if not self.tau_min <= lo <= hi <= self.tau_max:
            raise ValueError("knowledge support would require clipping; reject this task")
        return float(lo), float(hi)


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
    positive = weights > 0.0  # avoid 0 * log(0) after legitimate underflow.
    entropy = -float(np.sum(weights[positive] * np.log(weights[positive])))
    return float(1.0 - entropy / log(weights.size))


@dataclass(frozen=True)
class BlindedVarianceSummary:
    """A0-safe quota information: no contrast mean, sign, or policy ranking."""

    n_tasks: int
    paired_sd: float
    paired_sd_upper_95: float
    target_half_width: float
    minimum_quota: int
    normal_approx_required_tasks: int


@dataclass(frozen=True)
class AttemptBudgetSummary:
    """Policy-free proposal budget derived from A0 acceptance feasibility."""

    accepted: int
    proposals: int
    wilson_lower_probability: float
    confirmatory_quota: int
    failure_probability_target: float
    minimum_attempts: int


class BlindedContrastAccumulator:
    """Streaming A0-only dispersion accumulator that never retains contrasts.

    The internal running mean is required by Welford's variance identity but is
    private and deliberately never exposed.  This object must be the sole sink
    for A0 paired losses; callers should not write raw contrasts to disk.
    """

    def __init__(self) -> None:
        self._n = 0
        self._mean = 0.0
        self._m2 = 0.0

    def update(self, paired_loss_contrast: float) -> None:
        if not np.isfinite(paired_loss_contrast):
            raise ValueError("paired loss contrast must be finite")
        self._n += 1
        delta = paired_loss_contrast - self._mean
        self._mean += delta / self._n
        self._m2 += delta * (paired_loss_contrast - self._mean)

    @property
    def count(self) -> int:
        """Number of absorbed contrasts; safe to disclose for support audits."""
        return self._n

    def summary(self, target_half_width: float, minimum_quota: int) -> BlindedVarianceSummary:
        if self._n < 2:
            raise ValueError("need at least two pilot tasks for a variance-only quota")
        if target_half_width <= 0 or minimum_quota < 1:
            raise ValueError("invalid quota calibration settings")
        paired_sd = float(np.sqrt(self._m2 / (self._n - 1)))
        if paired_sd == 0.0:
            # A zero pilot SD is a degeneracy, not evidence that zero tasks suffice.
            raise ValueError("zero paired pilot SD: treat as a degeneracy and investigate")
        # One-sided 95% upper confidence limit under the standard normal-variance
        # approximation: (n-1)s^2 / chi2_{0.05,n-1}.
        paired_sd_upper = float(
            np.sqrt((self._n - 1) * paired_sd**2 / chi2.ppf(0.05, self._n - 1))
        )
        required = max(
            minimum_quota,
            int(ceil((1.96 * paired_sd_upper / target_half_width) ** 2)),
        )
        return BlindedVarianceSummary(
            n_tasks=self._n,
            paired_sd=paired_sd,
            paired_sd_upper_95=paired_sd_upper,
            target_half_width=float(target_half_width),
            minimum_quota=int(minimum_quota),
            normal_approx_required_tasks=required,
        )


def conservative_wilson_lower_bound(
    accepted: int, proposals: int, z_value: float = 1.96
) -> float:
    """Conservative Wilson lower bound; `1.96` matches the frozen 95% convention."""
    if not 0 <= accepted <= proposals or proposals < 1 or z_value <= 0:
        raise ValueError("invalid accepted/proposals/z_value")
    p_hat = accepted / proposals
    denominator = 1.0 + z_value**2 / proposals
    center = p_hat + z_value**2 / (2.0 * proposals)
    radius = z_value * np.sqrt(p_hat * (1.0 - p_hat) / proposals + z_value**2 / (4.0 * proposals**2))
    return float((center - radius) / denominator)


def minimum_attempts_for_quota(
    confirmatory_quota: int,
    lower_acceptance_probability: float,
    failure_probability_target: float = 1e-4,
) -> int:
    """Smallest N satisfying P[Binomial(N,p_L) < quota] < target."""
    if confirmatory_quota < 1 or not 0 < lower_acceptance_probability <= 1:
        raise ValueError("invalid quota or lower acceptance probability")
    if not 0 < failure_probability_target < 1:
        raise ValueError("failure_probability_target must lie in (0,1)")
    lo = confirmatory_quota
    hi = max(confirmatory_quota, int(np.ceil(confirmatory_quota / lower_acceptance_probability)))
    while binom.cdf(confirmatory_quota - 1, hi, lower_acceptance_probability) >= failure_probability_target:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if binom.cdf(confirmatory_quota - 1, mid, lower_acceptance_probability) < failure_probability_target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def attempt_budget_from_a0(
    accepted: int,
    proposals: int,
    confirmatory_quota: int,
    failure_probability_target: float = 1e-4,
) -> AttemptBudgetSummary:
    """Freeze max attempts from feasibility, without reference to policy outcomes."""
    lower = conservative_wilson_lower_bound(accepted, proposals)
    return AttemptBudgetSummary(
        accepted=accepted,
        proposals=proposals,
        wilson_lower_probability=lower,
        confirmatory_quota=confirmatory_quota,
        failure_probability_target=failure_probability_target,
        minimum_attempts=minimum_attempts_for_quota(
            confirmatory_quota, lower, failure_probability_target
        ),
    )
