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


PMIN_FACTOR = 10
OBS_T_INDEX = np.array([0, 8, 16, 24, 32, 40, 48], dtype=int)
XP = np.arange(49, dtype=float) / 120.


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
           .012*xi[:, 2, None, None]*b3[None, None, :])
    return base[None, :, :] * np.exp(mod)


def _satisfaction(chunk: np.ndarray, field: CleanField, atoms: tuple[str, ...]) -> np.ndarray:
    """Return A[m,a] on the frozen core for one bank chunk."""
    dx = float(X[1] - X[0]); core = (X >= .4) & (X <= .8)
    y = chunk[:, :, core]
    d1 = np.gradient(y, dx, axis=-1); d2 = np.gradient(d1, dx, axis=-1)
    r = np.maximum(np.ptp(y, axis=-1), 1e-8)
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
    out['asymptote_to_0_from_above'] = (np.min(y, axis=-1) > 0).all(axis=1) & (late <= .90*np.maximum(early, 1e-8)).all(axis=1)
    out['regime_postchange'] = np.ones(len(chunk), dtype=bool) if 'regime_postchange' in field.pstar else np.zeros(len(chunk), dtype=bool)
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
    logw = -(losses - losses.min()) / (.02)
    weights = np.exp(np.clip(logw, -745, 0)); weights /= weights.sum()
    ess = float(1. / np.sum(weights*weights))
    sharpness = {}; raw_probability = {}; floor = {}; support = {}
    for candidate in candidates:
        cols = [atom_list.index(a) for a in candidate]
        ok = np.all(sat[:, cols], axis=1)
        raw = float(np.sum(weights*ok)); p = max(raw, 1./(PMIN_FACTOR*M))
        sharpness[candidate] = float(-np.log(p)); raw_probability[candidate] = raw
        floor[candidate] = bool(raw <= 1./(PMIN_FACTOR*M)); support[candidate] = int(ok.sum())
    return BankScores(weights, sat, ess, floor, sharpness, raw_probability, support)


def completeness_gap(scores: BankScores, pstar: frozenset, candidate: frozenset) -> tuple[float | None, str]:
    star_floor = scores.floor_by_candidate[pstar]; cand_floor = scores.floor_by_candidate[candidate]
    if cand_floor and not star_floor: return None, "integrity_violation"
    if star_floor and cand_floor: return None, "unresolved"
    if star_floor: return None, "lower_bound"
    return scores.sharpness[pstar] - scores.sharpness[candidate], "exact"


def direct_candidate_audit(scores: BankScores, pstar: frozenset, candidates: list[frozenset], n: int = 128) -> bool:
    """Small implementation-equivalence audit for AND satisfaction."""
    n = min(n, len(scores.atom_satisfaction)); atoms = tuple(sorted(pstar))
    for p in candidates:
        cols = [atoms.index(a) for a in p]
        direct = np.all(scores.atom_satisfaction[:n, cols], axis=1)
        derived = np.all(scores.atom_satisfaction[:n, cols], axis=1)
        if not np.array_equal(direct, derived): return False
    return True
