"""Render frozen E16-B train-only capacity diagnostics without held-out targets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    ridge = artifact["ridge_contract"]
    postfit = artifact["postfit_pairwise_distinctness"]
    oof = artifact["train_oof_rmse_summary"]
    singular = artifact["centered_prediction_matrix"]["singular_values"][:5]
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    labels = ["min", "q05", "median", "q95", "max"]

    ax = axes[0, 0]
    lambdas = [float(value) for value in ridge["aggregate_cv_mse_by_lambda"]]
    scores = list(ridge["aggregate_cv_mse_by_lambda"].values())
    ax.semilogx(lambdas, scores, marker="o", color="#4C78A8")
    ax.axvline(ridge["selected_lambda"], color="#E45756", linestyle="--", label=f"selected = {ridge['selected_lambda']:g}")
    ax.set_xlabel("Shared ridge λ")
    ax.set_ylabel("Mean 405-candidate train CV MSE")
    ax.set_title("Train-only common regularization")
    ax.legend(frameon=False)

    ax = axes[0, 1]
    ax.plot(labels, [oof[label] for label in labels], marker="o", color="#54A24B", linewidth=2)
    ax.axhline(artifact["working_likelihood"]["sigma_ref"], color="#E45756", linestyle="--", label="σ_ref")
    ax.set_ylabel("Candidate train OOF RMSE")
    ax.set_title("Train-only working-likelihood scale")
    ax.legend(frameon=False)

    ax = axes[1, 0]
    ax.plot(labels, [postfit[label] for label in labels], marker="o", color="#F58518", linewidth=2)
    ax.set_yscale("log")
    ax.set_ylabel("Post-fit candidate RMS distance")
    ax.set_title("Realized candidate distinctness on future X shell")
    ax.text(0.5, 0.10, f"{postfit['pair_count']:,} pairs; exact-equivalent = 0", transform=ax.transAxes, ha="center")

    ax = axes[1, 1]
    ax.bar(range(1, 6), singular, color="#9C755F")
    ax.set_yscale("log")
    ax.set_xticks(range(1, 6), [f"SV{i}" for i in range(1, 6)])
    ax.set_ylabel("Centered prediction singular value")
    ax.set_title(f"Realized prediction rank = {artifact['centered_prediction_matrix']['numerical_rank']}")
    ax.text(0.5, 0.10, f"condition number = {artifact['centered_prediction_matrix']['condition_number']:.1f}", transform=ax.transAxes, ha="center")

    fig.suptitle("E16-B: Frozen train-only capacity and realization audit", fontsize=14)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
