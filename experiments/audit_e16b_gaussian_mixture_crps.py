"""Outcome-free deterministic audit for E16-B exact Gaussian-mixture CRPS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.special import ndtr


TOLERANCE = 1e-12
INTEGRATION_TOLERANCE = 1e-8


def a_function(difference: np.ndarray | float, scale: float) -> np.ndarray | float:
    z = np.asarray(difference) / scale
    return 2.0 * scale * np.exp(-0.5 * z**2) / np.sqrt(2.0 * np.pi) + np.asarray(difference) * (2.0 * ndtr(z) - 1.0)


def gaussian_mixture_crps(observation: float, means: np.ndarray, weights: np.ndarray, sigma: float) -> float:
    means = np.asarray(means, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if means.ndim != 1 or weights.shape != means.shape or sigma <= 0 or not np.isfinite(sigma):
        raise ValueError("Invalid Gaussian-mixture CRPS input")
    if not np.isfinite(means).all() or not np.isfinite(weights).all() or np.any(weights < 0) or not np.isclose(weights.sum(), 1.0, atol=TOLERANCE, rtol=0.0):
        raise ValueError("Invalid Gaussian-mixture components or weights")
    first = np.sum(weights * a_function(observation - means, sigma))
    pairwise = a_function(means[:, None] - means[None, :], np.sqrt(2.0) * sigma)
    return float(first - 0.5 * np.sum(weights[:, None] * weights[None, :] * pairwise))


def normal_cdf(value: float, mean: float, sigma: float) -> float:
    return float(ndtr((value - mean) / sigma))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    observation, sigma = 0.37, 0.26536872271489265
    means = np.asarray([-0.8, -0.1, 0.45, 1.05])
    weights = np.asarray([0.1, 0.2, 0.3, 0.4])
    single = float(a_function(observation - means[0], sigma) - 0.5 * a_function(0.0, np.sqrt(2.0) * sigma))
    singleton = gaussian_mixture_crps(observation, means[:1], np.asarray([1.0]), sigma)
    same_mean = gaussian_mixture_crps(observation, np.repeat(0.25, 4), weights, sigma)
    same_mean_reference = gaussian_mixture_crps(observation, np.asarray([0.25]), np.asarray([1.0]), sigma)
    one_hot = gaussian_mixture_crps(observation, means, np.asarray([0.0, 0.0, 1.0, 0.0]), sigma)
    one_hot_reference = gaussian_mixture_crps(observation, means[2:3], np.asarray([1.0]), sigma)
    analytic = gaussian_mixture_crps(observation, means, weights, sigma)
    mixture_cdf = lambda value: float(np.sum(weights * ndtr((value - means) / sigma)))
    numerical, _ = quad(lambda value: (mixture_cdf(value) - float(value >= observation)) ** 2, -np.inf, np.inf, epsabs=1e-11, epsrel=1e-11)
    replay = gaussian_mixture_crps(observation, means, weights, sigma)
    checks = {
        "singleton_equals_gaussian": abs(singleton - single) <= TOLERANCE,
        "identical_component_means_equals_single_gaussian": abs(same_mean - same_mean_reference) <= TOLERANCE,
        "one_hot_equals_selected_gaussian": abs(one_hot - one_hot_reference) <= TOLERANCE,
        "weights_sum_to_one": abs(float(weights.sum()) - 1.0) <= TOLERANCE,
        "finite_nonnegative": np.isfinite(analytic) and analytic >= 0.0,
        "deterministic_replay": analytic == replay,
        "toy_numerical_integration_agrees": abs(analytic - numerical) <= INTEGRATION_TOLERANCE,
    }
    artifact = {
        "protocol": "E16-B exact finite Gaussian-mixture CRPS implementation audit v1",
        "final_status": "PASS" if all(checks.values()) else "FAIL",
        "target_access": "no CCPP target values read",
        "checks": checks,
        "tolerances": {"algebraic": TOLERANCE, "numerical_integration": INTEGRATION_TOLERANCE},
        "fixed_toy": {"observation": observation, "sigma": sigma, "means": means.tolist(), "weights": weights.tolist()},
        "analytic_toy_crps": analytic,
        "numerical_integration_toy_crps": numerical,
        "absolute_difference": abs(analytic - numerical),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final_status": artifact["final_status"], "toy_difference": artifact["absolute_difference"]}, indent=2))
    if artifact["final_status"] != "PASS":
        raise SystemExit("Gaussian-mixture CRPS audit failure")


if __name__ == "__main__":
    main()
