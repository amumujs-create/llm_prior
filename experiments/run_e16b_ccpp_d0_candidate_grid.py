"""Build and audit the frozen E16-B target-free 405-candidate reference grid."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from itertools import product
from pathlib import Path

import numpy as np
import openpyxl


FEATURES = ("AT", "V", "AP", "RH")
AMPLITUDES = (0.1, 0.3, 0.5, 0.7, 0.9)
EPSILON = 1e-12
DISTINCTNESS_TOLERANCE = 1e-10


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_indices(indices: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(indices, dtype=">u4").tobytes()).hexdigest()


def read_x_only(path: Path) -> np.ndarray:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Sheet1"]
    rows = sheet.iter_rows(max_col=len(FEATURES), values_only=True)
    if tuple(next(rows)) != FEATURES:
        raise ValueError("Canonical Sheet1 feature header mismatch")
    x = np.asarray([tuple(float(value) for value in row) for row in rows], dtype=float)
    if x.shape != (9568, 4) or not np.isfinite(x).all():
        raise ValueError("X-only source failed shape or finiteness checks")
    return x


def partition_masks(at: np.ndarray, geometry: dict) -> dict[str, np.ndarray]:
    q = geometry["at_quantiles"]
    return {
        "train": at <= q["q70"],
        "validation": (at > q["q70"]) & (at <= q["q85"]),
        "guard_band": (at > q["q85"]) & (at <= q["q90"]),
        "confirmatory_test": at > q["q90"],
    }


def candidate_table(amplitudes: tuple[float, ...], rc: tuple[float, ...], rgamma: float) -> np.ndarray:
    levels = (-rgamma, 0.0, rgamma)
    values = [(a, c, rv, rap, rh) for a, c, rv, rap, rh in product(amplitudes, rc, levels, levels, levels)]
    return np.asarray(values, dtype=float)


def candidate_sha256(candidates: np.ndarray) -> str:
    digest = hashlib.sha256()
    for index, row in enumerate(candidates):
        digest.update(struct.pack(">I5d", index, *row))
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--split-replay", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    geometry = json.loads(args.geometry.read_text(encoding="utf-8"))
    replay = json.loads(args.split_replay.read_text(encoding="utf-8"))
    x = read_x_only(args.xlsx)
    at = x[:, 0]
    masks = partition_masks(at, geometry)
    source_hash = sha256(args.xlsx)
    index_hashes = {name: hash_indices(np.flatnonzero(mask)) for name, mask in masks.items()}
    membership = np.full(at.size, 255, dtype=np.uint8)
    for code, name in enumerate(("train", "validation", "guard_band", "confirmatory_test")):
        membership[masks[name]] = code
    replay_checks = {
        "source_workbook_sha256_match": source_hash == replay["source_identity"]["workbook_sha256"],
        "geometry_artifact_sha256_match": sha256(args.geometry) == replay["source_identity"]["geometry_artifact_sha256"],
        "partition_index_hashes_match": index_hashes == replay["partition_index_sha256"],
        "partition_membership_hash_match": hashlib.sha256(membership.tobytes()).hexdigest() == replay["partition_membership_sha256"],
    }
    if not all(replay_checks.values()):
        raise ValueError(f"Frozen split replay mismatch: {replay_checks}")

    train_x = x[masks["train"]]
    train_median = np.median(train_x[:, 1:], axis=0)
    train_q25, train_q75 = np.quantile(train_x[:, 1:], (0.25, 0.75), axis=0, method="linear")
    train_iqr = train_q75 - train_q25
    if np.any(train_iqr <= 0):
        raise ValueError("Train X IQR is nonpositive")
    u = (at - 24.79) / 4.45
    z = (x[:, 1:] - train_median) / train_iqr
    u_minus = float(abs(np.min(u)))
    u_plus = float(np.max(u))
    z_star = float(np.max(np.sum(np.abs(z), axis=1)))
    if not all(np.isfinite((u_minus, u_plus, z_star))) or min(u_minus, u_plus, z_star) <= 0:
        raise ValueError("Nonpositive or nonfinite shape-envelope statistic")
    rc_minus, rc_plus, rgamma = 0.25 / u_minus, 0.25 / u_plus, 0.25 / z_star
    rc_levels = (-rc_minus, 0.0, rc_plus)
    candidates = candidate_table(AMPLITUDES, rc_levels, rgamma)
    candidate_hash = candidate_sha256(candidates)
    replay_candidate_hash = candidate_sha256(candidate_table(AMPLITUDES, rc_levels, rgamma))
    unique_tuples = len({tuple(row) for row in candidates})
    amplitude_counts = Counter(float(row[0]) for row in candidates)

    u_endpoints = np.array((float(np.min(u)), float(np.max(u))))
    max_brackets: list[float] = []
    max_derivatives: list[float] = []
    max_excesses: list[float] = []
    for amplitude, rcurv, rv, rap, rh in candidates:
        interaction = z[:, 0] * rv + z[:, 1] * rap + z[:, 2] * rh
        bracket = -1.0 + 2.0 * rcurv * u_endpoints[:, None] + interaction[None, :]
        max_bracket = float(np.max(bracket))
        max_derivative = float(amplitude * max_bracket)
        max_brackets.append(max_bracket)
        max_derivatives.append(max_derivative)
        max_excesses.append(max_derivative - (-0.25 * amplitude))
    monotone = np.asarray(max_excesses) <= EPSILON
    if not np.all(monotone):
        raise ValueError("Candidate grid violates frozen monotonicity budget")

    shell_mask = at > geometry["at_quantiles"]["q85"]
    shell_u, shell_z = u[shell_mask], z[shell_mask]
    g = np.column_stack((shell_u, shell_u**2, shell_u[:, None] * shell_z))
    singular_values = np.linalg.svd(g, compute_uv=False)
    design_rank = int(np.linalg.matrix_rank(g))
    continuation = np.empty((candidates.shape[0], shell_u.size), dtype=float)
    for index, (amplitude, rc, rv, rap, rh) in enumerate(candidates):
        continuation[index] = amplitude * (
            -shell_u
            + rc * shell_u**2
            + shell_u * (shell_z[:, 0] * rv + shell_z[:, 1] * rap + shell_z[:, 2] * rh)
        )
    if not np.isfinite(continuation).all():
        raise ValueError("Nonfinite candidate continuation")
    gram = np.einsum("ik,jk->ij", continuation, continuation)
    norms = np.sum(continuation**2, axis=1)
    squared = np.maximum((norms[:, None] + norms[None, :] - 2.0 * gram) / shell_u.size, 0.0)
    distances = np.sqrt(squared)
    upper = distances[np.triu_indices(candidates.shape[0], k=1)]
    summary = {
        "pair_count": int(upper.size),
        "min": float(np.min(upper)),
        "q05": float(np.quantile(upper, 0.05, method="linear")),
        "median": float(np.median(upper)),
        "q95": float(np.quantile(upper, 0.95, method="linear")),
        "max": float(np.max(upper)),
        "pairs_at_or_below_1e-10": int(np.sum(upper <= DISTINCTNESS_TOLERANCE)),
    }
    d0_checks = {
        "shape_envelope_finite_positive": True,
        "candidate_count_405": candidates.shape[0] == 405,
        "unique_parameter_tuples_405": unique_tuples == 405,
        "exactly_81_per_amplitude": all(amplitude_counts[node] == 81 for node in AMPLITUDES),
        "candidate_table_replay_sha256_match": candidate_hash == replay_candidate_hash,
        "all_continuations_finite": bool(np.isfinite(continuation).all()),
        "all_empirical_scope_monotone": bool(np.all(monotone)),
        "future_shell_design_rank_5": design_rank == 5,
        "all_pairwise_continuations_distinct": summary["min"] > DISTINCTNESS_TOLERANCE,
    }
    if not all(d0_checks.values()):
        raise ValueError(f"D0 construct audit failed: {d0_checks}")
    artifact = {
        "protocol": "E16-B CCPP candidate-grid D0 v1",
        "final_status": "PASS",
        "source_hashes": {
            "workbook_sha256": source_hash,
            "geometry_artifact_sha256": sha256(args.geometry),
            "split_replay_artifact_sha256": sha256(args.split_replay),
        },
        "target_access": "prohibited; only AT,V,AP,RH loaded",
        "coordinate_convention": {
            "u": "(AT - 24.79) / 4.45",
            "z": "(V, AP, RH - train median) / train IQR",
            "train_x_median": train_median.tolist(),
            "train_x_iqr": train_iqr.tolist(),
        },
        "shape_envelope": {"U_minus": u_minus, "U_plus": u_plus, "Z_star": z_star},
        "derivative_budgets": {"b_c": 0.50, "b_gamma": 0.25, "b_margin": 0.25, "epsilon": EPSILON},
        "shape_levels": {"r_c_minus": rc_minus, "r_c_plus": rc_plus, "r_gamma": rgamma, "r_c": list(rc_levels), "r_interaction": [-rgamma, 0.0, rgamma]},
        "amplitude_reference_measure": {"nodes": list(AMPLITUDES), "mass_each": 0.2, "shape_mass_each_level": 1 / 3, "candidate_mass": 1 / 405},
        "candidate_count": int(candidates.shape[0]),
        "candidate_table_sha256": candidate_hash,
        "candidate_order": "amplitude, r_c, r_V, r_AP, r_RH; each in frozen displayed order",
        "monotonicity_audit": {
            "all_pass": bool(np.all(monotone)),
            "maximum_bracket_derivative": float(np.max(max_brackets)),
            "maximum_normalized_derivative": float(np.max(max_derivatives)),
            "maximum_bound_excess": float(np.max(max_excesses)),
        },
        "future_shell": {"definition": "AT > q85 = 27.96; guard plus confirmatory X rows only", "row_count": int(shell_u.size), "design_rank": design_rank, "singular_values": singular_values.tolist()},
        "pairwise_distinctness": summary,
        "replay_checks": replay_checks,
        "d0_checks": d0_checks,
        "scope": "target-free candidate construction and geometry audit; no model, loss, MAP, weighting, or outcome",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final_status": artifact["final_status"], "candidate_count": artifact["candidate_count"], "distinctness_min": summary["min"]}, indent=2))


if __name__ == "__main__":
    main()
