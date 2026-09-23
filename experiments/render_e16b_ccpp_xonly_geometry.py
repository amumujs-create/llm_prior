"""Render the frozen E16-B X-only geometry without accessing the target column."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import openpyxl


def read_at_only(path: Path) -> np.ndarray:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Sheet1"]
    rows = sheet.iter_rows(min_col=1, max_col=1, values_only=True)
    header = next(rows)[0]
    if header != "AT":
        raise ValueError(f"Expected AT in first column, found {header!r}")
    return np.asarray([float(row[0]) for row in rows], dtype=float)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    at = read_at_only(args.xlsx)
    q = artifact["at_quantiles"]
    counts = artifact["split_counts"]
    diagnostics = artifact["remaining_covariate_diagnostics"]
    nn = artifact["nearest_neighbor_diagnostic"]

    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    colors = {"train": "#4C78A8", "validation": "#72B7B2", "guard": "#F2CF5B", "test": "#E45756"}

    ax = axes[0, 0]
    groups = [
        (at <= q["q70"], "train", "Train"),
        ((at > q["q70"]) & (at <= q["q85"]), "validation", "Validation"),
        ((at > q["q85"]) & (at <= q["q90"]), "guard", "Guard band"),
        (at > q["q90"], "test", "Confirmatory test"),
    ]
    bins = np.linspace(float(at.min()), float(at.max()), 45)
    for mask, key, label in groups:
        ax.hist(at[mask], bins=bins, histtype="stepfilled", alpha=0.72, color=colors[key], label=f"{label} (n={int(mask.sum()):,})")
    for value, text in ((q["q70"], "q70"), (q["q85"], "q85"), (q["q90"], "q90")):
        ax.axvline(value, color="#333333", linewidth=1)
        ax.text(value + 0.1, ax.get_ylim()[1] * 0.92, text, rotation=90, va="top", fontsize=9)
    ax.set_title("AT-defined nested support split")
    ax.set_xlabel("Ambient temperature, AT (°C)")
    ax.set_ylabel("Rows per bin")
    ax.legend(frameon=False, fontsize=8)

    names = [item["feature"] for item in diagnostics]
    shifts = [item["median_shift_over_train_iqr"] for item in diagnostics]
    w1 = [item["wasserstein_over_train_iqr"] for item in diagnostics]
    y = np.arange(len(names))
    ax = axes[0, 1]
    ax.barh(y, shifts, color=["#4C78A8", "#F58518", "#54A24B"])
    ax.axvline(0, color="#333333", linewidth=0.8)
    ax.set_yticks(y, names)
    ax.set_xlabel("Test median − train median (train IQR units)")
    ax.set_title("Remaining-covariate median shifts")
    ax.invert_yaxis()

    ax = axes[1, 0]
    ax.barh(y, w1, color=["#4C78A8", "#F58518", "#54A24B"])
    ax.set_yticks(y, names)
    ax.set_xlabel("1-Wasserstein distance (train IQR units)")
    ax.set_title("Remaining-covariate distribution shifts")
    ax.invert_yaxis()

    ax = axes[1, 1]
    values = [nn["train_leave_one_out_nn_q95"], nn["test_to_train_nn_median"], nn["test_to_train_nn_q95"]]
    labels = ["Train LOO\nNN q95", "Test→train\nNN median", "Test→train\nNN q95"]
    ax.bar(np.arange(3), values, color=["#4C78A8", "#E45756", "#E45756"])
    ax.set_xticks(np.arange(3), labels)
    ax.set_ylabel("Robust-standardized 3D NN distance")
    ax.set_title("(V, AP, RH) support overlap")
    ax.text(
        0.5,
        0.92,
        f"C_overlap = {nn['c_overlap']:.1%}\ncompound covariate shift",
        transform=ax.transAxes,
        ha="center",
        va="top",
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "#FDECEC", "edgecolor": "#E45756"},
    )

    fig.suptitle("E16-B CCPP: Frozen X-only high-temperature extrapolation geometry", fontsize=14)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
