#!/usr/bin/env python3
"""Frozen E14-v1 multivariate persistent-base and clean-scope primitives.

This module contains no scorer and no task selection.  It constructs clean
paired fields, applies the frozen post-.80 C2 intervention, and exposes only
checker-derived core envelopes and contiguous scope tables.
"""
from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass

import numpy as np
from scipy.stats import qmc

from build_e13_persistent_base import H, X, raw_valid
from run_prior_completeness_e11 import INTENTS, envelope, valid_atoms


Z_SEED = 20261014
SIGMA_CONTEXT = .20
KAPPA = {"none": 0., "moderate": .25, "strong": .50}
SCALE_SIGMA = {"none": 0., "moderate": .10, "strong": .20}
HET_FIELD = {
    "direction+curvature+bound": "beta",
    "direction+curvature+asymptote": "beta",
    "direction+inflection+bound": "iota",
    "direction+inflection+asymptote": "iota",
    "curvature+bound+asymptote": "beta",
    "inflection+bound+asymptote": "iota",
    "turning+bound+asymptote": "tau",
    "regime+bound+asymptote": "rho",
}


def stable_seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "little") % (2**32 - 1)


def smooth5(u: np.ndarray) -> np.ndarray:
    u = np.clip(u, 0., 1.)
    return u**3 * (10. - 15. * u + 6. * u*u)


def z_ref_max() -> np.ndarray:
    """Frozen 64-point scrambled Sobol design in [-1,1]^7."""
    return 2. * qmc.Sobol(d=7, scramble=True, seed=Z_SEED).random_base2(m=6) - 1.


def z_ref(d: int) -> np.ndarray:
    if d not in (1, 3, 8):
        raise ValueError(f"unsupported total dimension: {d}")
    if d == 1:
        return np.zeros((1, 0))
    z = z_ref_max()[:, :d - 1]
    return np.unique(z, axis=0)


def _raw_context_field(z: np.ndarray, family: str) -> np.ndarray:
    q = z.shape[1]
    if q == 0:
        return np.zeros(len(z))
    if family == "additive":
        return np.sum(z, axis=1) / np.sqrt(q)
    if family == "pairwise":
        if q < 2:
            raise ValueError("pairwise field requires q>=2")
        return np.sqrt(2. / (q * (q - 1))) * sum(z[:, i] * z[:, j] for i in range(q) for j in range(i + 1, q))
    if family == "entangled":
        return np.sin(np.pi * np.sum(z, axis=1) / np.sqrt(q))
    raise ValueError(family)


def _standardized(z: np.ndarray, family: str) -> np.ndarray:
    raw = _raw_context_field(z, family)
    centered = raw - raw.mean()
    rms = np.sqrt(np.mean(centered*centered))
    if rms <= 1e-12:
        raise ValueError("degenerate context field")
    return centered / rms


def modulation(z: np.ndarray, family: str, sigma: float) -> np.ndarray:
    if z.shape[1] == 0:
        return np.ones(len(z))
    s = _standardized(z, family)
    a = np.exp(sigma*s)
    return a / a.mean()


def _native_field(intent_name: str, generator: str, x: np.ndarray, theta: np.ndarray | None = None) -> np.ndarray:
    """Analytic E13 persistent families with one optional native field."""
    k = {"spline": 1., "basis": 1.03, "ode": .97}[generator]
    intent = set(INTENTS[intent_name])
    theta = {} if theta is None else theta
    n = len(next(iter(theta.values()))) if theta else 1
    def value(name: str, default: float) -> np.ndarray:
        v = np.asarray(theta.get(name, default), dtype=float)
        return np.full(n, float(v)) if v.ndim == 0 else v
    if "turning_maximum" in intent:
        # The E13 asymptote checker loses its core-domain tail criterion above
        # tau=.55.  Use the predeclared atom-preserving interior [.53,.55].
        tau, lam, beta = value("tau", .54), value("lambda", 3.2*k), value("beta", 7.0*k)
        u = x[None, :] - tau[:, None]
        return np.exp(-lam[:, None]*u - (lam/beta)[:, None]*(np.exp(-beta[:, None]*u)-1.))
    if "inflection_concave_to_convex" in intent:
        iota, beta = value("iota", .55), value("beta", 7.0*k)
        return 1. / (1. + np.exp(beta[:, None]*(x[None, :] - iota[:, None])))
    if "regime_postchange" in intent:
        rho = value("rho", 1.2)
        u = np.clip((x - .28) / .10, 0., 1.); gate = smooth5(u)
        return np.exp(-1.1*k*x[None, :] - rho[:, None]*gate[None, :])
    if "asymptote_to_0_from_above" in intent:
        lam = value("lambda", 2.1*k)
        return np.exp(-lam[:, None]*x[None, :])
    beta = value("beta", .01)
    return 1.5 - .80*x[None, :] + beta[:, None]*x[None, :]**2


def _theta_values(intent_name: str, generator: str, z: np.ndarray, level: str) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    """Use one packet-frozen field and reject rather than clip unsafe values."""
    n = len(z); field = HET_FIELD[intent_name]; k = {"spline": 1., "basis": 1.03, "ode": .97}[generator]
    s = _standardized(z, "additive") if z.shape[1] else np.zeros(n)
    unit = s / max(float(np.max(np.abs(s))), 1e-12)
    if field == "tau":
        base, lo, hi = .54, .53, .55
    elif field == "iota":
        base, lo, hi = .55, .50, .60
    elif field == "rho":
        base, lo, hi = 1.2, .90, 1.50
    elif field == "beta" and "turning_maximum" in INTENTS[intent_name]:
        base, lo, hi = 7.*k, 5.*k, 9.*k
    elif field == "beta" and "inflection_concave_to_convex" in INTENTS[intent_name]:
        base, lo, hi = 7.*k, 5.*k, 9.*k
    else:  # convex quadratic coefficient
        base, lo, hi = .01, .005, .020
    margin = min(base-lo, hi-base)
    values = base + KAPPA[level]*margin*unit
    if not np.all(np.isfinite(values)) or np.any(values <= lo) or np.any(values >= hi):
        raise ValueError("native heterogeneity field out of admissible range")
    return {field: values}, {"field": field, "rms": float(np.sqrt(np.mean((values-values.mean())**2))), "max_displacement": float(np.max(np.abs(values-base)))}


@dataclass(frozen=True)
class CleanField:
    intent_name: str
    generator: str
    branch: str
    x: np.ndarray
    z_ref: np.ndarray
    y: np.ndarray
    semantic: tuple[dict, ...]
    field_audit: dict
    pstar: frozenset
    rref: float


def _core_envelope(intent_name: str, x: np.ndarray, y: np.ndarray) -> frozenset:
    per_context = [set(valid_atoms(row, INTENTS[intent_name], x)) for row in y]
    shared = frozenset.intersection(*(frozenset(q) for q in per_context))
    pstar, _ = envelope(shared, INTENTS[intent_name])
    if pstar is None or not set(INTENTS[intent_name]) <= set(pstar):
        raise ValueError("core_envelope_failure")
    return pstar


def build_clean(intent_name: str, generator: str, branch: str, heterogeneity: str = "none") -> CleanField:
    """Build a persistent multivariate base with checker-derived core envelope."""
    if branch == "dimension_d1": d, family, heterogeneity = 1, "additive", "none"
    elif branch == "dimension_d3": d, family, heterogeneity = 3, "additive", "none"
    elif branch == "dimension_d8": d, family, heterogeneity = 8, "additive", "none"
    elif branch in ("interaction_additive", "interaction_pairwise", "interaction_entangled"):
        d, family, heterogeneity = 8, branch.removeprefix("interaction_"), "none"
    elif branch == "heterogeneity": d, family = 8, "additive"
    else: raise ValueError(branch)
    if heterogeneity not in KAPPA: raise ValueError(heterogeneity)
    z = z_ref(d); n = len(z)
    theta, native_audit = _theta_values(intent_name, generator, z, heterogeneity) if heterogeneity != "none" else ({}, {"field": None, "rms": 0., "max_displacement": 0.})
    native = _native_field(intent_name, generator, X, theta)
    amp = modulation(z, family, SIGMA_CONTEXT) if d > 1 else np.ones(n)
    y = amp[:, None] * native
    pstar = _core_envelope(intent_name, X, y)
    semantic = tuple({"regime_active": "regime_postchange" in pstar, "asymptote_active": "asymptote_to_0_from_above" in pstar,
                      "asymptote_active_through": np.inf, "turning_type": "maximum" if "turning_maximum" in pstar else None}
                     for _ in range(n))
    core = (X >= .40) & (X <= .80)
    # Paired-group R_ref is always the unmodulated f0 reference, not a branch
    # or heterogeneity-specific value.
    rref = float(np.ptp(_native_field(intent_name, generator, X)[0, core]))
    return CleanField(intent_name, generator, branch, X.copy(), z, y, semantic,
                      {"amplitude_centered_log_rms": float(np.sqrt(np.mean((np.log(amp)-np.log(amp).mean())**2))), **native_audit},
                      pstar, max(rref, 1e-8))


def persistent_scope_table(field: CleanField) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    raw = {a: [] for a in field.pstar}
    for atom in field.pstar:
        for h in H:
            raw[atom].append(int(all(raw_valid(field.x, field.y[k], atom, float(h), field.semantic[k]) for k in range(len(field.z_ref)))))
    cont = {}
    for atom, values in raw.items():
        alive = 1; cont[atom] = []
        for value in values:
            alive *= value; cont[atom].append(alive)
    return raw, cont


def apply_c2_intervention(field: CleanField, requested: str) -> CleanField:
    """Frozen post-.80 negative level excursion; no proposal metadata enters scoring."""
    if requested not in ("limited", "intermediate", "persistent_within_tested_domain"):
        raise ValueError(requested)
    y = field.y.copy(); semantic = [dict(v) for v in field.semantic]
    if requested == "persistent_within_tested_domain":
        return CleanField(field.intent_name, field.generator, field.branch, field.x, field.z_ref, y, tuple(semantic), field.field_audit, field.pstar, field.rref)
    target = .85 if requested == "limited" else 1.10
    onset = target-.04; gate = smooth5((field.x-onset)/(target-onset))
    amp = np.asarray([np.interp(target, field.x, row) for row in field.y]) + .10
    y -= amp[:, None]*gate[None, :]
    if not np.array_equal(field.y[:, field.x <= .80], y[:, field.x <= .80]):
        raise RuntimeError("C2 intervention changed core")
    for state in semantic:
        state["asymptote_active_through"] = target
    return CleanField(field.intent_name, field.generator, field.branch, field.x, field.z_ref, y, tuple(semantic), field.field_audit, field.pstar, field.rref)


def candidate_cp(cont: dict[str, list[int]], candidate: frozenset) -> list[int]:
    return [int(np.prod([cont[a][j] for a in candidate])) for j in range(len(H))]


def measured_stratum(cont: dict[str, list[int]], pstar: frozenset) -> str:
    cp = candidate_cp(cont, pstar)
    if all(cp): return "persistent_within_tested_domain"
    last = .80 if cp[0] == 0 else float(H[np.where(np.asarray(cp) == 0)[0][0]-1])
    if last <= .90: return "limited"
    if last in (1.00, 1.10): return "intermediate"
    return "out_of_quota"


def exact_envelope_match(*fields: CleanField) -> bool:
    return len({tuple(sorted(f.pstar)) for f in fields}) == 1
