#!/usr/bin/env python3
"""Protected variance-only quota calibration for E15-D v1.2."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "experiments" / "E15D_QUOTA_RUNTIME_CONFIG_V1_2.json"
DEFAULT_OUTPUT = ROOT / "results" / "prior_utilization_e15d" / "quota_v1_2" / "E15D_PROTECTED_QUOTA_V1_2.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed(namespace: str, task_id: int) -> int:
    digest = hashlib.sha256(f"{namespace}:task:{task_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False) % (2**63)


def task_draws(namespace: str, task_id: int) -> tuple[float, float, np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed(namespace, task_id)))
    return float(rng.random()), float(rng.random()), rng.standard_normal(101)


def grid(config: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    x = np.arange(101, dtype=float) / 100.0
    support = config["support"]
    values = np.arange(float(support["lower"]), float(support["upper"]) + 1e-12, float(config["grid_spacing"]))
    return x, values


def prefix_likelihood(y: np.ndarray, x: np.ndarray, exposure: float, coefficients: np.ndarray, rho: float) -> tuple[np.ndarray, np.ndarray]:
    mask = x <= exposure
    residual = y[mask] - x[mask]
    x2, x6 = x[mask] ** 2, x[mask] ** 6
    syy, syk, syl = residual @ residual, residual @ x2, residual @ x6
    skk, skl, sll = x2 @ x2, x2 @ x6, x6 @ x6
    k, lam = coefficients[:, None], coefficients[None, :]
    loss = np.maximum(syy - 2*k*syk - 2*lam*syl + k*k*skk + 2*k*lam*skl + lam*lam*sll, 0.0) / (2.0 * rho**2)
    mass = np.exp(-(loss - np.min(loss)))
    return mass / np.sum(mass), loss


def curves(weights: np.ndarray, loss: np.ndarray, coefficients: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    marginal_kappa = np.sum(weights, axis=1)
    marginal_lambda = np.sum(weights, axis=0)
    uniform = np.full(len(coefficients), 1.0 / len(coefficients))
    def curve(kappa_weights: np.ndarray, lambda_weights: np.ndarray) -> np.ndarray:
        return x + np.sum(coefficients * kappa_weights) * x**2 + np.sum(coefficients * lambda_weights) * x**6
    uniform_curve = curve(uniform, uniform)
    selective_curve = curve(marginal_kappa, uniform)
    factorized_curve = curve(marginal_kappa, marginal_lambda)
    row, col = np.unravel_index(int(np.argmin(loss)), loss.shape)
    map_curve = x + coefficients[row] * x**2 + coefficients[col] * x**6
    return uniform_curve, selective_curve, factorized_curve, map_curve


def score(curve: np.ndarray, truth: np.ndarray, far_mask: np.ndarray) -> float:
    return float(math.sqrt(np.mean((curve[far_mask] - truth[far_mask]) ** 2)))


class VarianceAccumulator:
    def __init__(self) -> None:
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0

    def update(self, value: float) -> None:
        self.n += 1
        delta = value - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (value - self.mean)

    def sd(self) -> float:
        return math.sqrt(self.m2 / (self.n - 1)) if self.n > 1 else 0.0


def run(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("status") != "FROZEN":
        raise ValueError("protected quota requires frozen config")
    x, coefficients = grid(config)
    far_mask = (x > float(config["far_window"]["lower_open"])) & (x <= float(config["far_window"]["upper_closed"]))
    accumulators = {name: VarianceAccumulator() for name in config["quota_estimands"]}
    for task_id in range(int(config["task_count"])):
        u_kappa, u_lambda, epsilon = task_draws(config["seed_namespace"], task_id)
        low, high = float(config["support"]["lower"]), float(config["support"]["upper"])
        kappa_truth, lambda_truth = low + (high - low) * u_kappa, low + (high - low) * u_lambda
        truth = x + kappa_truth * x**2 + lambda_truth * x**6
        y = truth + float(config["rho"]) * epsilon
        scores: dict[str, tuple[float, float, float, float]] = {}
        for regime in ("S", "J"):
            weights, loss = prefix_likelihood(y, x, float(config["exposures"][regime]), coefficients, float(config["rho"]))
            scores[regime] = tuple(score(curve, truth, far_mask) for curve in curves(weights, loss, coefficients, x))
        uniform_s, selective_s, factorized_s, map_s = scores["S"]
        _, selective_j, factorized_j, _ = scores["J"]
        accumulators["D1_S"].update(selective_s - uniform_s)
        accumulators["D2_S"].update(factorized_s - selective_s)
        accumulators["D2_J"].update(factorized_j - selective_j)
        accumulators["D3_S"].update(map_s - factorized_s)
    epsilon = float(config["epsilon"])
    summaries = []
    for name, accumulator in accumulators.items():
        paired_sd = accumulator.sd()
        required = math.ceil((1.96 * paired_sd / epsilon) ** 2)
        summaries.append({"estimand": name, "n_tasks": accumulator.n, "paired_sd": paired_sd, "required_quota": required})
    final_quota = max(int(config["minimum_quota"]), *(entry["required_quota"] for entry in summaries))
    return {
        "protocol": "E15-D-quota-v1.2",
        "protected": True,
        "discarded_calibration": {"seed_namespace": config["seed_namespace"], "task_count": config["task_count"], "no_replacement": True},
        "precision_contract": {"epsilon": epsilon, "minimum_quota": config["minimum_quota"]},
        "variance_summary": summaries,
        "confirmatory_quota": final_quota,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = run(config)
    result["source_hashes"] = {"runner_sha256": sha256_file(Path(__file__)), "config_sha256": sha256_file(args.config)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
