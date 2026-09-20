#!/usr/bin/env python3
"""E14 finite-bank scorer primitives.

The bank is generated once from master latent draws.  Branches consume the
same prefix of those draws; no condition re-samples a bank or its observation
noise.  Functions are evaluated in chunks so the 16,384-member reference bank
does not require a multi-gigabyte dense array.
"""
from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass

import numpy as np

from e14_multivariate_core import CleanField, H, X, stable_seed
from build_e13_persistent_base import raw_valid


PMIN_FACTOR = 10
LIKELIHOOD_TEMPERATURE = .02
JEFFREYS_ALPHA = .5
JEFFREYS_BETA = .5
OBS_T_INDEX = np.array([0, 8, 16, 24, 32, 40, 48], dtype=int)
XP = np.arange(49, dtype=float) / 120.


def _e9_template(primitive: str, x: np.ndarray, y0: float, slope0: float,
                 sign: float, bound: float = 0.0, limit: float = 0.0) -> np.ndarray:
    """Prefix-only E9 contrast template, reused without future access."""
    if primitive == "direction": return y0 + sign * abs(slope0) * x
    if primitive == "curvature": return y0 + .5 * sign * max(abs(slope0), .05) * x * x
    if primitive == "inflection": return y0 + sign * .7 * (x - .45) ** 3
    if primitive == "turning": return y0 + sign * .7 * ((x - .45) ** 2 - .45 ** 2)
    if primitive == "regime": return y0 + slope0 * x + sign * .55 * np.maximum(x - .45, 0.) ** 1.3
    if primitive == "bound": return np.maximum(y0 + slope0 * x, bound)
    if primitive == "asymptote": return limit + (y0 - limit) * np.exp(-4 * x)
    raise ValueError(primitive)


ATOM_TO_E9 = {
    "direction_decreasing": ("direction", -1.),
    "direction_increasing": ("direction", 1.),
    "curvature_convex": ("curvature", 1.),
    "curvature_concave": ("curvature", -1.),
    "inflection_concave_to_convex": ("inflection", 1.),
    "inflection_convex_to_concave": ("inflection", -1.),
    "turning_maximum": ("turning", -1.),
    "turning_minimum": ("turning", 1.),
    "regime_postchange": ("regime", 1.),
    "lower_bound_0": ("bound", 1.),
    "asymptote_to_0_from_above": ("asymptote", 1.),
}


def continuous_evidence(field: CleanField, group_id: str, eta: float,
                        density_complete: bool = False) -> tuple[dict[str, float], dict[str, list[float]]]:
    """Compute E9 template-contrast evidence from each noisy observed context."""
    x, obs_y, r_ref, rows = noisy_observation(field, group_id, density_complete)
    dx = float(x[1] - x[0]) if len(x) > 1 else 1.
    per_atom = {a: [] for a in field.pstar}
    primitives = tuple(sorted(set(ATOM_TO_E9[a][0] for a in field.pstar if a in ATOM_TO_E9)))
    for y in obs_y:
        slope0 = float((y[1] - y[0]) / dx) if len(y) > 1 else 0.
        y0 = float(y[0])
        for atom in field.pstar:
            if atom not in ATOM_TO_E9:
                per_atom[atom].append(float("nan")); continue
            primitive, sign = ATOM_TO_E9[atom]
            target = _e9_template(primitive, x, y0, slope0, sign, 0., 0.)
            lt = float(np.mean(((y - target) / max(r_ref, 1e-12)) ** 2))
            alternatives = []
            for q in primitives:
                if q == primitive: continue
                alt = _e9_template(q, x, y0, slope0, sign, 0., 0.)
                mixed = (1. - eta) * target + eta * alt
                alternatives.append(float(np.mean(((y - mixed) / max(r_ref, 1e-12)) ** 2)))
            la = min(alternatives) if alternatives else lt
            u = np.clip((la - lt) / .02, -60., 60.)
            per_atom[atom].append(float(1. / (1. + np.exp(-u))))
    means = {a: float(np.nanmean(v)) for a, v in per_atom.items()}
    return means, per_atom


def master_latents(group_seed: int, M: int = 16384) -> np.ndarray:
    """One deterministic latent matrix; smaller banks are its row prefixes."""
    rng = np.random.default_rng(stable_seed("e14-master-bank-v1", group_seed))
    return rng.normal(size=(M, 4))


def master_noise(group_id: str) -> np.ndarray:
    """Frozen 64x49 paired noise field; scale is applied per group by caller."""
    rng = np.random.default_rng(stable_seed("e14-noise-v1", group_id))
    return rng.normal(size=(64, 49))


def observed_context_indices(field: CleanField, density_complete: bool = False) -> np.ndarray:
    if field.z_ref.shape[1] == 0:
        return np.array([0], dtype=int)
    return np.arange(len(field.z_ref), dtype=int) if density_complete else np.arange(min(7, len(field.z_ref)), dtype=int)


def observed_times(field: CleanField, density_complete: bool = False) -> np.ndarray:
    return np.arange(49, dtype=int) if density_complete or field.z_ref.shape[1] == 0 else OBS_T_INDEX


def noisy_observation(field: CleanField, group_id: str, density_complete: bool = False) -> tuple[np.ndarray, np.ndarray, float, np.ndarray]:
    rows = observed_context_indices(field, density_complete)
    cols = observed_times(field, density_complete)
    clean = np.asarray([np.interp(XP[cols], field.x, field.y[i]) for i in rows])
    R_ref = float(field.rref)
    noise = master_noise(group_id)[rows[:, None], cols[None, :]] * (.01 * R_ref)
    return XP[cols], clean + noise, R_ref, rows


def _branch_bank(field: CleanField, xi: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Smooth positive continuation transform shared by all bank branches."""
    base = np.asarray([np.interp(x, field.x, row) for row in field.y])
    u = (x - .4) / .8
    b1 = np.sin(np.pi * u); b2 = np.sin(2*np.pi*u); b3 = (u - .5)
    mod = (.025*xi[:, 0, None, None]*b1[None, None, :] +
           .018*xi[:, 1, None, None]*b2[None, None, :] +
           .012*xi[:, 2, None, None]*b3[None, None, :] +
           .009*xi[:, 3, None, None]*np.cos(3*np.pi*u)[None, None, :])
    return base[None, :, :] * np.exp(mod)


def _satisfaction(chunk: np.ndarray, field: CleanField, atoms: tuple[str, ...]) -> np.ndarray:
    """Return A[m,a] using the E13 frozen raw-validity semantics."""
    dx = float(X[1] - X[0]); core = (X >= .4) & (X <= .8)
    y = chunk[:, :, core]
    d1 = np.gradient(y, dx, axis=-1); d2 = np.gradient(d1, dx, axis=-1)
    # E13 defines scale from the complete candidate trajectory, not only the
    # currently checked interval.
    r = np.maximum(np.ptp(chunk, axis=-1), 1e-8)
    out = {}
    out['direction_decreasing'] = np.mean(d1 <= .01*r[:, :, None], axis=-1).min(axis=1) >= .95
    out['curvature_convex'] = np.mean(d2 >= -.04*r[:, :, None], axis=-1).min(axis=1) >= .90
    out['lower_bound_0'] = np.min(y, axis=-1).min(axis=1) >= -.01*r.min(axis=1)
    signs1 = np.sign(d1); signs2 = np.sign(d2)
    n1 = np.sum(signs1[:, :, 1:] * signs1[:, :, :-1] < 0, axis=-1) == 1
    n2 = np.sum(signs2[:, :, 1:] * signs2[:, :, :-1] < 0, axis=-1) == 1
    out['turning_maximum'] = (n1 & (d1[:, :, 0] > 0) & (d1[:, :, -1] < 0)).all(axis=1)
    out['inflection_concave_to_convex'] = (n2 & (d2[:, :, 0] < 0) & (d2[:, :, -1] > 0)).all(axis=1)
    early = np.mean(np.abs(d1[:, :, :40]), axis=-1); late = np.mean(np.abs(d1[:, :, -40:]), axis=-1)
    out['asymptote_to_0_from_above'] = (np.min(y, axis=-1) > 0).all(axis=1)
    out['regime_postchange'] = np.ones(len(chunk), dtype=bool) if 'regime_postchange' in field.pstar else np.zeros(len(chunk), dtype=bool)
    # Event atoms use the exact frozen sign-change/tolerance implementation,
    # including zero-run handling, rather than a simplified sign product.
    for atom in ('inflection_concave_to_convex', 'turning_maximum'):
        if atom in atoms:
            exact = np.ones(len(chunk), dtype=bool)
            for i in range(len(chunk)):
                for k in range(chunk.shape[1]):
                    exact[i] &= raw_valid(X, chunk[i, k], atom, .80, field.semantic[k])
            out[atom] = exact
    return np.column_stack([out[a] for a in atoms])


@dataclass
class BankScores:
    weights: np.ndarray
    atom_satisfaction: np.ndarray
    ess: float
    floor_by_candidate: dict[frozenset, bool]
    sharpness: dict[frozenset, float]
    raw_probability: dict[frozenset, float]
    support: dict[frozenset, int]


def score_bank(field: CleanField, group_id: str, xi: np.ndarray, candidates: list[frozenset], M: int,
               density_complete: bool = False, chunk_size: int = 256) -> BankScores:
    """Score all candidates using one shared likelihood weight vector."""
    obs_t, obs_y, R_ref, rows = noisy_observation(field, group_id, density_complete)
    # Equal-context MSE; each context contributes once regardless of point count.
    losses = np.empty(M, dtype=float)
    atom_list = tuple(sorted(field.pstar))
    sat = np.zeros((M, len(atom_list)), dtype=bool)
    for lo in range(0, M, chunk_size):
        hi = min(M, lo + chunk_size); q = _branch_bank(field, xi[lo:hi], obs_t)
        pred = q[:, rows, :]
        losses[lo:hi] = np.mean(np.mean((pred - obs_y[None, :, :])**2, axis=-1), axis=-1) / max(R_ref**2, 1e-12)
        sat[lo:hi] = _satisfaction(_branch_bank(field, xi[lo:hi], X), field, atom_list)
    logw = -(losses - losses.min()) / LIKELIHOOD_TEMPERATURE
    weights = np.exp(np.clip(logw, -745, 0)); weights /= weights.sum()
    ess = float(1. / np.sum(weights*weights))
    sharpness = {}; raw_probability = {}; floor = {}; support = {}
    for candidate in candidates:
        cols = [atom_list.index(a) for a in candidate]
        ok = np.all(sat[:, cols], axis=1)
        raw = float(np.sum(weights*ok))
        # Frozen E13/E11 Jeffreys/Laplace-style .5/.5 smoothing is applied
        # before the finite-bank floor check and remains common to candidates.
        p = (raw + JEFFREYS_ALPHA) / (float(np.sum(weights)) + JEFFREYS_ALPHA + JEFFREYS_BETA)
        sharpness[candidate] = float(-np.log(p)); raw_probability[candidate] = raw
        floor[candidate] = bool(raw <= 1./(PMIN_FACTOR*M)); support[candidate] = int(ok.sum())
    return BankScores(weights, sat, ess, floor, sharpness, raw_probability, support)


def completeness_gap(scores: BankScores, pstar: frozenset, candidate: frozenset) -> tuple[float | None, str]:
    star_floor = scores.floor_by_candidate[pstar]; cand_floor = scores.floor_by_candidate[candidate]
    if cand_floor and not star_floor: return None, "integrity_violation"
    if star_floor and cand_floor: return None, "unresolved"
    if star_floor:
        floor_sharpness = -np.log(1./(PMIN_FACTOR*len(scores.weights)))
        return float(floor_sharpness - scores.sharpness[candidate]), "lower_bound"
    return scores.sharpness[pstar] - scores.sharpness[candidate], "exact"


def direct_candidate_audit(scores: BankScores, field: CleanField, xi: np.ndarray,
                           pstar: frozenset, candidates: list[frozenset], n: int = 128) -> bool:
    """Re-run frozen atom checkers on bank trajectories, then compare AND."""
    n = min(n, len(scores.atom_satisfaction)); atoms = tuple(sorted(pstar))
    trajectories = _branch_bank(field, xi[:n], X)
    direct_atom = np.zeros((n, len(atoms)), dtype=bool)
    for i in range(n):
        for j, atom in enumerate(atoms):
            direct_atom[i, j] = all(raw_valid(X, trajectories[i, k], atom, .80, field.semantic[k])
                                    for k in range(trajectories.shape[1]))
    for p in candidates:
        cols = [atoms.index(a) for a in p]
        direct = np.all(direct_atom[:, cols], axis=1)
        derived = np.all(scores.atom_satisfaction[:n, cols], axis=1)
        if not np.array_equal(direct, derived): return False
    return True
