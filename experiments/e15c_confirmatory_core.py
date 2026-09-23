"""Frozen E15-C v1.1 generative and policy machinery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from run_e15c_c0_v1_1 import BoundedContract, bounded_profile_all_q
from run_e15c_c0 import z_bases


MANIFEST = Path(__file__).with_name("e15c_confirmatory_manifest_v1_1.json")
MANIFEST_SHA = "1d6da0e4984be39d92dfcfd1fec82e248a68d4f9919e2ddda014fe65e3d2f18f"


def load_manifest() -> dict:
    raw = MANIFEST.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA:
        raise RuntimeError("E15-C confirmatory manifest SHA mismatch")
    return json.loads(raw)


def invariant_base(x: np.ndarray) -> np.ndarray:
    return np.exp(-x)


def q_grid(manifest: dict) -> np.ndarray:
    cfg = manifest["estimator"]["residual_q_grid"]
    return np.arange(cfg["min"], cfg["max"] + cfg["step"] / 2, cfg["step"])


def c_grid(manifest: dict) -> np.ndarray:
    cfg = manifest["matched_free"]["c_grid_dimensionless_cT"]
    return np.arange(cfg["min"], cfg["max"] + cfg["step"] / 2, cfg["step"])


def responses_for_c(x: np.ndarray, c: float) -> tuple[np.ndarray, np.ndarray]:
    """Convolution responses to x and x**3 for y'=c*y+A*g_q(x)."""
    if np.isclose(c, 0.0, rtol=0.0, atol=1e-14):
        return x**2 / 2.0, x**4 / 4.0
    z0 = np.expm1(c * x) / c
    z1 = -x / c + z0 / c
    z2 = -(x**2) / c + 2.0 * z1 / c
    z3 = -(x**3) / c + 3.0 * z2 / c
    return z1, z3


def profile_matched_free(y_obs: np.ndarray, x_obs: np.ndarray, qs: np.ndarray, cs: np.ndarray, sigma: float, bound: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For each task,q choose c then bounded A by fixed-grid enumeration."""
    n_tasks, n_obs = y_obs.shape
    best_loss = np.full((n_tasks, len(qs)), np.inf)
    best_a = np.zeros_like(best_loss)
    best_c_index = np.zeros((n_tasks, len(qs)), dtype=int)
    for ci, c in enumerate(cs):
        baseline = np.exp(c * x_obs)
        z1, z3 = responses_for_c(x_obs, float(c))
        zq = (1.0 - qs[:, None]) * z1[None, :] + qs[:, None] * z3[None, :]
        denom = np.sum(zq*zq, axis=1)
        if np.any(denom <= 1e-14):
            raise FloatingPointError("matched-free profile basis is degenerate")
        a = np.einsum("tn,qn->tq", y_obs-baseline[None, :], zq, optimize=True) / denom[None, :]
        a = np.clip(a, -bound, bound)
        fitted = baseline[None, None, :] + a[:, :, None]*zq[None, :, :]
        loss = .5*np.sum((y_obs[:, None, :]-fitted)**2,axis=2)/(sigma*sigma)
        # c grid is ascending; strict improvement preserves smaller-c ties.
        update = loss < best_loss - 1e-12
        best_loss[update] = loss[update]
        best_a[update] = a[update]
        best_c_index[update] = ci
    return best_a, best_loss, best_c_index


def weights(losses: np.ndarray) -> np.ndarray:
    lw = -(losses-losses.min(axis=1,keepdims=True))
    lw -= np.logaddexp.reduce(lw,axis=1,keepdims=True)
    return np.exp(lw)


def invariant_predictions(y_obs: np.ndarray, x_obs: np.ndarray, x_forecast: np.ndarray, qs: np.ndarray, sigma: float, bound: float) -> dict[str, np.ndarray]:
    base = BoundedContract(amplitude_bound_ratio=bound)
    a, losses, _ = bounded_profile_all_q(y_obs,x_obs,qs,sigma,base)
    z1,z3=z_bases(x_forecast,1.0)
    zq=(1-qs[:,None])*z1[None,:]+qs[:,None]*z3[None,:]
    all_predictions=invariant_base(x_forecast)[None,None,:]+a[:,:,None]*zq[None,:,:]
    map_index=np.argmin(losses,axis=1)
    return {
        "invariant_residual_MAP": all_predictions[np.arange(len(y_obs)),map_index],
        "invariant_residual_ensemble": all_predictions.mean(axis=1),
        "evidence_weighted_residual_mixture": np.einsum("tq,tqf->tf",weights(losses),all_predictions,optimize=True),
        "closed_mechanism": np.broadcast_to(invariant_base(x_forecast),(len(y_obs),len(x_forecast))).copy(),
        "losses": losses,
    }


def free_prediction(y_obs: np.ndarray, x_obs: np.ndarray, x_forecast: np.ndarray, qs: np.ndarray, cs: np.ndarray, sigma: float, bound: float) -> np.ndarray:
    a, _, c_index = profile_matched_free(y_obs,x_obs,qs,cs,sigma,bound)
    all_predictions=np.empty((len(y_obs),len(qs),len(x_forecast)))
    for ci,c in enumerate(cs):
        tasks, q_indices=np.where(c_index==ci)
        if not len(tasks):
            continue
        z1,z3=responses_for_c(x_forecast,float(c))
        zq=(1-qs[:,None])*z1[None,:]+qs[:,None]*z3[None,:]
        all_predictions[tasks,q_indices]=np.exp(c*x_forecast)[None,:]+a[tasks,q_indices,None]*zq[q_indices]
    return all_predictions.mean(axis=1)


def make_tasks(seed: int, n_tasks: int, manifest: dict) -> dict:
    rng=np.random.default_rng(seed)
    q_true=rng.uniform(0,1,n_tasks)
    eta=rng.uniform(.5,1.5,n_tasks)
    signs=np.tile(np.array([-1.,1.]), n_tasks//2+1)[:n_tasks]; rng.shuffle(signs)
    amplitude=signs*eta
    x=np.linspace(0,1,manifest["sampling"]["full_observation_grid_points"])
    z1,z3=z_bases(x,1.0)
    z=(1-q_true[:,None])*z1[None,:]+q_true[:,None]*z3[None,:]
    clean=invariant_base(x)[None,:]+amplitude[:,None]*z
    master_noise=rng.standard_normal(clean.shape)
    return {"task_id":np.arange(n_tasks),"q_true":q_true,"amplitude":amplitude,"x":x,"clean":clean,"master_noise":master_noise}


def proposal_seed(namespace: str, proposal_index: int) -> int:
    payload=f"{namespace}:proposal:{proposal_index}".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8],"big") % (2**63)


def make_proposal(seed: int, sign: float, manifest: dict) -> dict:
    rng=np.random.default_rng(seed)
    q_true=float(rng.uniform(0,1)); amplitude=float(sign*rng.uniform(.5,1.5))
    x=np.linspace(0,1,manifest["sampling"]["full_observation_grid_points"])
    z1,z3=z_bases(x,1.0); z=(1-q_true)*z1+q_true*z3
    clean=invariant_base(x)+amplitude*z
    return {"q_true":q_true,"amplitude":amplitude,"x":x,"clean":clean,"master_noise":rng.standard_normal(len(x))}
