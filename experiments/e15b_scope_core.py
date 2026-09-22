"""Deterministic clean-field, evidence, and enforcement primitives for E15-B.

E15-B intentionally separates the scope-precursor likelihood used to measure
``E_h`` from the quadratic forecast engine used to enforce a direction prior.
Neither component uses post-prefix labels during fitting or selection.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np


LINEAR_LSTSQ_RCOND = 1e-12


@dataclass(frozen=True)
class ScopeTaskParams:
    """Clean task parameters; ``h_star`` is a warranted scope endpoint."""

    a: float
    b: float
    gamma: float
    h_star: float
    width: float
    post_scope_mode: float


def q_scope(t: np.ndarray, h: float, gamma: float) -> np.ndarray:
    """In-scope precursor basis, linear in the fitted coefficient ``b``."""
    t = np.asarray(t, dtype=float)
    return t + gamma * (h * t - 0.5 * t**2)


def clean_scope_trajectory(t: np.ndarray, params: ScopeTaskParams) -> np.ndarray:
    """Continuous truth with a separately generated post-scope derivative."""
    t = np.asarray(t, dtype=float)
    h = params.h_star
    pre = params.a + params.b * q_scope(t, h, params.gamma)
    at_h = params.a + params.b * q_scope(np.asarray([h]), h, params.gamma)[0]
    dt = t - h
    post = at_h + params.b * dt + 0.5 * params.post_scope_mode * params.b * dt**2 / params.width
    return np.where(t <= h, pre, post)


def clean_scope_slope(t: np.ndarray, params: ScopeTaskParams) -> np.ndarray:
    t = np.asarray(t, dtype=float)
    pre = params.b * (1.0 + params.gamma * (params.h_star - t))
    post = params.b * (1.0 + params.post_scope_mode * (t - params.h_star) / params.width)
    return np.where(t <= params.h_star, pre, post)


def actual_violation_horizon(
    params: ScopeTaskParams, h_far: float, *, tolerance: float = 0.0
) -> float | None:
    """First clean time after ``h*`` where direction is violated, if observed."""
    if params.post_scope_mode >= 0.0:
        return None
    candidate = params.h_star - params.width / params.post_scope_mode
    return float(candidate) if candidate <= h_far and candidate >= params.h_star else None


def profile_scope_precursor(
    t: np.ndarray, y: np.ndarray, h_grid: np.ndarray, gamma: float, sigma: float
) -> tuple[np.ndarray, np.ndarray]:
    """Prefix-only Gaussian profile NLL and design condition for each scope."""
    if sigma <= 0.0 or not np.isfinite(sigma):
        raise ValueError("sigma must be finite and positive")
    losses: list[float] = []
    conditions: list[float] = []
    for h in np.asarray(h_grid, dtype=float):
        design = np.column_stack((np.ones_like(t), q_scope(t, float(h), gamma)))
        coef, *_ = np.linalg.lstsq(design, y, rcond=LINEAR_LSTSQ_RCOND)
        residual = (design @ coef - y) / sigma
        losses.append(float(.5 * np.sum(residual**2) + len(t) * np.log(sigma * np.sqrt(2.0 * np.pi))))
        conditions.append(float(np.linalg.cond(design)))
    return np.asarray(losses), np.asarray(conditions)


def normalized_entropy_concentration(losses: np.ndarray) -> tuple[np.ndarray, float]:
    """Stable T=1 profile weights and full-domain concentration in ``[0,1]``."""
    losses = np.asarray(losses, dtype=float)
    if losses.ndim != 1 or len(losses) < 2 or not np.all(np.isfinite(losses)):
        raise ValueError("need at least two finite profile losses")
    log_weights = -(losses - np.min(losses))
    log_weights -= np.logaddexp.reduce(log_weights)
    weights = np.exp(log_weights)
    positive = weights > 0.0
    entropy = -float(np.sum(weights[positive] * log_weights[positive]))
    return weights, float(1.0 - entropy / np.log(len(weights)))


@dataclass(frozen=True)
class ConstrainedQuadraticFit:
    coefficients: np.ndarray
    objective: float
    active_constraints: tuple[int, ...]
    min_constraint: float
    stationarity_residual: float


def _equality_constrained_ls(design: np.ndarray, y: np.ndarray, active: tuple[int, ...], constraints: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    gram = design.T @ design
    rhs = design.T @ y
    if not active:
        coef, *_ = np.linalg.lstsq(design, y, rcond=LINEAR_LSTSQ_RCOND)
        return coef, np.empty(0)
    c_active = constraints[list(active)]
    kkt = np.block([[gram, c_active.T], [c_active, np.zeros((len(active), len(active)))]] )
    solution, *_ = np.linalg.lstsq(kkt, np.concatenate((rhs, np.zeros(len(active)))), rcond=LINEAR_LSTSQ_RCOND)
    return solution[:3], solution[3:]


def _active_set_qp(
    hessian: np.ndarray,
    linear: np.ndarray,
    constraints: np.ndarray,
    lower: np.ndarray,
    *,
    tolerance: float,
    slack_index: int | None = None,
) -> tuple[np.ndarray, float, tuple[int, ...], float, float]:
    """Solve a tiny deterministic convex QP by enumerating active sets.

    Constraints are ``C x >= lower``.  Objective ties within ``1e-12`` are
    resolved by smaller slack, then lexicographic active-set index, as frozen
    for E15-B's secondary relaxation policies.
    """
    n_constraints = len(constraints)
    feasible = []
    for size in range(n_constraints + 1):
        for active in combinations(tuple(range(n_constraints)), size):
            if active:
                c_active = constraints[list(active)]
                kkt = np.block([[hessian, c_active.T], [c_active, np.zeros((size, size))]])
                rhs = np.concatenate((linear, lower[list(active)]))
                solution, *_ = np.linalg.lstsq(kkt, rhs, rcond=LINEAR_LSTSQ_RCOND)
                x, multipliers = solution[: len(linear)], solution[len(linear):]
            else:
                x, *_ = np.linalg.lstsq(hessian, linear, rcond=LINEAR_LSTSQ_RCOND)
                multipliers = np.empty(0)
            values = constraints @ x - lower
            if np.min(values) < -tolerance:
                continue
            # KKT form is Hx + C'lambda = linear.  For Cx>=lower, lambda must
            # be non-positive in this convention.
            if len(multipliers) and np.max(multipliers) > tolerance:
                continue
            stationarity = hessian @ x - linear
            if active:
                stationarity += constraints[list(active)].T @ multipliers
            objective = float(.5 * x @ hessian @ x - linear @ x)
            feasible.append((x, objective, active, float(np.min(values)), float(np.max(np.abs(stationarity)))))
    if not feasible:
        raise RuntimeError("no feasible active-set QP solution")
    best_objective = min(item[1] for item in feasible)
    tied = [item for item in feasible if abs(item[1] - best_objective) <= 1e-12]
    return min(tied, key=lambda item: (float(item[0][slack_index]) if slack_index is not None else 0.0, item[2]))


def fit_quadratic_with_direction_constraint(
    t: np.ndarray, y: np.ndarray, endpoint: float, *, tolerance: float = 1e-10
) -> ConstrainedQuadraticFit:
    """Deterministic active-set solution for ``f'(t)>=0`` through endpoint.

    The derivative is affine, so enforcing it at the prefix endpoint and at the
    requested scope endpoint is sufficient for the entire interval.
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(t) != len(y) or len(t) < 3:
        raise ValueError("quadratic fit needs matching t/y arrays of length at least three")
    t_prefix = float(np.max(t))
    if endpoint < t_prefix - tolerance:
        raise ValueError("scope endpoint precedes prefix endpoint")
    design = np.column_stack((np.ones_like(t), t, t**2))
    constraints = np.asarray(((0.0, 1.0, 2.0 * t_prefix), (0.0, 1.0, 2.0 * endpoint)))
    feasible: list[ConstrainedQuadraticFit] = []
    for size in range(3):
        for active in combinations((0, 1), size):
            coef, multipliers = _equality_constrained_ls(design, y, active, constraints)
            values = constraints @ coef
            if np.min(values) < -tolerance:
                continue
            # KKT uses X'X beta + C'lambda=X'y. For C beta>=0, lambda is the
            # negative of the conventional nonnegative inequality multiplier.
            if len(multipliers) and np.max(multipliers) > tolerance:
                continue
            residual = design @ coef - y
            stationarity = design.T @ residual
            if active:
                stationarity += constraints[list(active)].T @ multipliers
            feasible.append(ConstrainedQuadraticFit(
                coefficients=coef,
                objective=float(residual @ residual),
                active_constraints=active,
                min_constraint=float(np.min(values)),
                stationarity_residual=float(np.max(np.abs(stationarity))),
            ))
    if not feasible:
        raise RuntimeError("no feasible active-set solution")
    return min(feasible, key=lambda fit: fit.objective)


def quadratic_prediction(t: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    t = np.asarray(t, dtype=float)
    return coefficients[0] + coefficients[1] * t + coefficients[2] * t**2


def fit_quadratic_with_direction_slack(
    t: np.ndarray, y: np.ndarray, endpoint: float, slack: float, *, tolerance: float = 1e-10
) -> ConstrainedQuadraticFit:
    """Least-squares quadratic with fixed global directional slack ``s``."""
    if slack < 0.0:
        raise ValueError("slack must be nonnegative")
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    t_prefix = float(np.max(t))
    design = np.column_stack((np.ones_like(t), t, t**2))
    constraints = np.asarray(((0.0, 1.0, 2.0 * t_prefix), (0.0, 1.0, 2.0 * endpoint)))
    hessian, linear = design.T @ design, design.T @ y
    coef, _, active, min_value, stationarity = _active_set_qp(
        hessian, linear, constraints, np.full(2, -float(slack)), tolerance=tolerance
    )
    residual = design @ coef - y
    return ConstrainedQuadraticFit(coef, float(residual @ residual), active, min_value, stationarity)


def fit_quadratic_soft_global(
    t: np.ndarray,
    y: np.ndarray,
    endpoint: float,
    *,
    reference_y_scale: float,
    reference_slope: float,
    penalty_lambda: float = 1.0,
    tolerance: float = 1e-10,
) -> tuple[ConstrainedQuadraticFit, float]:
    """Frozen E15-B soft-global QP with learned nonnegative violation slack."""
    if reference_y_scale <= 0 or reference_slope <= 0 or penalty_lambda < 0:
        raise ValueError("reference scales must be positive and penalty nonnegative")
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    t_prefix = float(np.max(t))
    design = np.column_stack((np.ones_like(t), t, t**2))
    n = len(t)
    # Objective is mean normalized SSE plus lambda*(xi/b_ref)^2.  The common
    # factor 1/2 leaves its minimizer unchanged and gives a standard QP form.
    h_beta = design.T @ design / (n * reference_y_scale**2)
    hessian = np.zeros((4, 4))
    hessian[:3, :3] = h_beta
    hessian[3, 3] = penalty_lambda / reference_slope**2
    linear = np.zeros(4)
    linear[:3] = design.T @ y / (n * reference_y_scale**2)
    constraints = np.asarray(((0.0, 1.0, 2.0 * t_prefix, 1.0), (0.0, 1.0, 2.0 * endpoint, 1.0), (0.0, 0.0, 0.0, 1.0)))
    x, _, active, min_value, stationarity = _active_set_qp(
        hessian, linear, constraints, np.zeros(3), tolerance=tolerance, slack_index=3
    )
    residual = design @ x[:3] - y
    return ConstrainedQuadraticFit(x[:3], float(residual @ residual), active, min_value, stationarity), float(x[3])
