#!/usr/bin/env python3
"""Censoring-aware scope and dependency-masked association analysis for E13.

The full E13 scorer consumed manifest ``a45ea...``.  The working-tree
preflight directory may contain later generation attempts, so this analysis
reads the manifest directly from the frozen scorer commit and verifies its
SHA-256 before joining implied-atom metadata.  It never uses requested scope
or intervention metadata as an analysis variable.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/joint_prior_anatomy_e13/corrected_run/run"
OUT = ROOT / "results/joint_prior_anatomy_e13/corrected_analysis_scope"
FROZEN_MANIFEST_COMMIT = "8ea0a9c"
FROZEN_MANIFEST_PATH = "results/joint_prior_anatomy_e13/corrected_preflight/accepted_manifest.csv"
FROZEN_MANIFEST_SHA256 = "a45ea724f2442ba919035ff73e65fc643ac732d48e15a550feb9d4b483579298"
HORIZONS = (".85", ".90", "1.00", "1.10", "1.20")
BOOTSTRAPS = 1000
BOOTSTRAP_SEED = 20260920


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as handle:
        return list(csv.DictReader(handle))


def frozen_manifest() -> list[dict[str, str]]:
    text = subprocess.check_output(
        ["git", "show", f"{FROZEN_MANIFEST_COMMIT}:{FROZEN_MANIFEST_PATH}"],
        cwd=ROOT,
    )
    digest = hashlib.sha256(text).hexdigest()
    if digest != FROZEN_MANIFEST_SHA256:
        raise RuntimeError(f"frozen manifest SHA mismatch: {digest}")
    return list(csv.DictReader(io.StringIO(text.decode())))


def write_csv(name: str, rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def grouped(rows: list[dict]) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        result[row["task_id"]].append(row)
    return result


def weighted_rate(rows: list[dict], predicate) -> float | None:
    denominator = sum(float(row["task_weight"]) for row in rows)
    if not denominator:
        return None
    numerator = sum(float(row["task_weight"]) for row in rows if predicate(row))
    return numerator / denominator


def weighted_mean(rows: list[dict], value) -> float | None:
    denominator = sum(float(row["task_weight"]) for row in rows)
    if not denominator:
        return None
    return sum(float(row["task_weight"]) * value(row) for row in rows) / denominator


def clustered_ratio_ci(rows: list[dict], numerator) -> tuple[float | None, float | None]:
    """Bootstrap a task-clustered weighted ratio without materializing rows."""
    by_task = grouped(rows)
    task_ids = sorted(by_task)
    # Each tuple is the within-task candidate-weighted numerator/denominator.
    contributions = []
    for task_id in task_ids:
        task_rows = by_task[task_id]
        denominator = sum(float(row["task_weight"]) for row in task_rows)
        contributions.append((
            sum(float(row["task_weight"]) for row in task_rows if numerator(row)),
            denominator,
        ))
    if not contributions:
        return None, None
    rng = random.Random(BOOTSTRAP_SEED)
    values: list[float] = []
    for _ in range(BOOTSTRAPS):
        num = den = 0.0
        for _ in task_ids:
            task_num, task_den = contributions[rng.randrange(len(contributions))]
            num += task_num
            den += task_den
        if den:
            values.append(num / den)
    values.sort()
    return values[int(.025 * len(values))], values[int(.975 * len(values)) - 1]


def bools(row: dict) -> None:
    row["reliable"] = float(row["ESS"]) >= 100
    row["informative"] = float(row["S"]) >= .10
    row["observable"] = row["O_P"] == "1"
    row["incomplete"] = int(row["omitted_count"]) > 0
    row["exact_gap"] = row["gap_status"] == "exact"
    row["info_complete"] = (
        row["incomplete"]
        and row["reliable"]
        and row["exact_gap"]
        and float(row["delta_S_miss"]) <= .10
    )
    row["cp"] = [value == "1" for value in row["C_P"].split("|")]
    row["cpstar"] = [value == "1" for value in row["C_Pstar"].split("|")]


def main() -> None:
    rows = read_csv(RUN / "rows.csv")
    manifest = {row["task_id"]: row for row in frozen_manifest()}
    if {row["task_id"] for row in rows} != set(manifest):
        raise RuntimeError("run rows and frozen manifest do not contain the same task IDs")
    for row in rows:
        bools(row)

    # Censoring-aware survival profile.  This is the primary scope summary;
    # it never converts an H_valid*>1.20 censoring marker to a number.
    profile = []
    full = [row for row in rows if not row["incomplete"]]
    proper = [row for row in rows if row["incomplete"]]
    for index, horizon in enumerate(HORIZONS):
        all_survival = weighted_rate(rows, lambda row, i=index: row["cp"][i])
        full_survival = weighted_rate(full, lambda row, i=index: row["cp"][i])
        extension = weighted_rate(
            proper,
            lambda row, i=index: row["cp"][i] and not row["cpstar"][i],
        )
        lo, hi = clustered_ratio_ci(
            proper, lambda row, i=index: row["cp"][i] and not row["cpstar"][i]
        )
        profile.append(
            {
                "horizon": horizon,
                "all_candidate_survival": all_survival,
                "full_survival": full_survival,
                "proper_subset_scope_extension_rate": extension,
                "extension_cluster_bootstrap_95ci_low": lo,
                "extension_cluster_bootstrap_95ci_high": hi,
                "interpretation": "extension is empirical magnitude; subset>=full direction is masked as nesting-defined",
            }
        )
    write_csv("censored_scope_profile.csv", profile)

    # The full-prior stratum is quota-balanced.  This table is descriptive
    # provenance, not a test that scope was naturally distributed this way.
    by_stratum = []
    for stratum in ("limited", "intermediate", "persistent_within_tested_domain"):
        selected = [row for row in rows if row["measured_scope_stratum"] == stratum]
        for index, horizon in enumerate(HORIZONS):
            by_stratum.append(
                {
                    "scope_stratum": stratum,
                    "horizon": horizon,
                    "all_candidate_survival": weighted_rate(selected, lambda row, i=index: row["cp"][i]),
                    "full_survival": weighted_rate(
                        [row for row in selected if not row["incomplete"]],
                        lambda row, i=index: row["cp"][i],
                    ),
                    "note": "full-prior scope stratum was quota-balanced by design",
                }
            )
    write_csv("scope_profile_by_full_stratum.csv", by_stratum)

    # Non-definitional, descriptive S <-> C_P(h) conditional profiles.
    # Scope is a controlled factor, so these are associations, never effects.
    reliable = [row for row in rows if row["reliable"]]
    informative = [row for row in reliable if row["informative"]]
    information_scope = []
    for index, horizon in enumerate(HORIZONS):
        survivor = [row for row in reliable if row["cp"][index]]
        failed = [row for row in reliable if not row["cp"][index]]
        conditional = weighted_rate(informative, lambda row, i=index: row["cp"][i])
        lo, hi = clustered_ratio_ci(informative, lambda row, i=index: row["cp"][i])
        information_scope.append(
            {
                "horizon": horizon,
                "P_scope_survives_given_informative_reliable": conditional,
                "survival_given_informative_cluster_bootstrap_95ci_low": lo,
                "survival_given_informative_cluster_bootstrap_95ci_high": hi,
                "mean_S_if_survives": weighted_mean(survivor, lambda row: float(row["S"])),
                "mean_S_if_failed": weighted_mean(failed, lambda row: float(row["S"])),
                "P_informative_if_survives": weighted_rate(survivor, lambda row: row["informative"]),
                "P_informative_if_failed": weighted_rate(failed, lambda row: row["informative"]),
                "note": "descriptive association; eta and full-prior scope are controlled, not causal treatments",
            }
        )
    write_csv("information_scope_profile.csv", information_scope)

    # Completeness <-> scope uses exact, reliable incomplete rows only.
    # It makes no numeric use of censored H_valid* values.
    complete_rows = [row for row in reliable if row["incomplete"] and row["exact_gap"]]
    completeness_scope = []
    for index, horizon in enumerate(HORIZONS):
        survivor = [row for row in complete_rows if row["cp"][index]]
        failed = [row for row in complete_rows if not row["cp"][index]]
        for status, selected in (("survives", survivor), ("failed", failed)):
            rate = weighted_rate(selected, lambda row: row["info_complete"])
            lo, hi = clustered_ratio_ci(selected, lambda row: row["info_complete"])
            completeness_scope.append(
                {
                    "horizon": horizon,
                    "scope_status": status,
                    "candidate_rows": len(selected),
                    "latent_tasks": len({row["task_id"] for row in selected}),
                    "mean_delta_S_miss": weighted_mean(selected, lambda row: float(row["delta_S_miss"])),
                    "P_info_complete_exact_reliable": rate,
                    "info_complete_cluster_bootstrap_95ci_low": lo,
                    "info_complete_cluster_bootstrap_95ci_high": hi,
                    "note": "descriptive, exact-gap only; delta_S_miss is not correlated with S here",
                }
            )
    write_csv("completeness_scope_profile.csv", completeness_scope)

    # O_P has only 117 positives in the whole corpus.  Save its support audit
    # rather than reporting unstable O_P association estimates as discoveries.
    observable_audit = []
    for eta in ("low", "mid", "high"):
        for stratum in ("limited", "intermediate", "persistent_within_tested_domain"):
            selected = [row for row in reliable if row["eta"] == eta and row["measured_scope_stratum"] == stratum]
            observable_audit.append(
                {
                    "eta": eta,
                    "scope_stratum": stratum,
                    "reliable_rows": len(selected),
                    "observable_rows": sum(row["observable"] for row in selected),
                    "observable_rate": weighted_rate(selected, lambda row: row["observable"]),
                    "analysis_status": "support audit only; O_P associations are descriptive-only because positives are sparse",
                }
            )
    write_csv("observability_support_audit.csv", observable_audit)

    dependency_mask = [
        {"relation": "core validity <-> any axis", "status": "masked", "reason": "all E13 rows condition on core coverage=1"},
        {"relation": "candidate size <-> C_atom", "status": "masked", "reason": "partly definitional"},
        {"relation": "S <-> delta_S_miss", "status": "masked", "reason": "shared sharpness term by definition"},
        {"relation": "N_obs <-> O_P", "status": "masked", "reason": "both derive from the same atom evidence"},
        {"relation": "subset/full scope direction", "status": "masked", "reason": "AND/nesting invariant"},
        {"relation": "S <-> C_P(h)", "status": "descriptive empirical panel", "reason": "controlled eta and scope, not causal"},
        {"relation": "delta_S_miss <-> C_P(h)", "status": "descriptive empirical panel", "reason": "exact-gap reliable incomplete candidates only"},
        {"relation": "O_P <-> C_P(h)", "status": "support-limited", "reason": "only 117 observable rows in this corpus"},
    ]
    write_csv("dependency_mask.csv", dependency_mask)

    # Static figures are descriptive renderings of the two primary profile
    # tables, not additional analysis or a replacement for censored data.
    figures = ROOT / "figures"
    figures.mkdir(exist_ok=True)
    x = list(range(len(HORIZONS)))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), constrained_layout=True)
    axes[0].plot(x, [row["all_candidate_survival"] for row in profile], marker="o", label="all candidates")
    axes[0].plot(x, [row["full_survival"] for row in profile], marker="s", label="oracle full")
    axes[0].set(xticks=x, xticklabels=HORIZONS, ylim=(0, 1), xlabel="horizon", ylabel="P(C_P(h)=1)")
    axes[0].set_title("Censoring-aware scope profile")
    axes[0].legend(frameon=False)
    ext = [row["proper_subset_scope_extension_rate"] for row in profile]
    lower = [row["extension_cluster_bootstrap_95ci_low"] for row in profile]
    upper = [row["extension_cluster_bootstrap_95ci_high"] for row in profile]
    axes[1].errorbar(x, ext, yerr=[[a - b for a, b in zip(ext, lower)], [a - b for a, b in zip(upper, ext)]], marker="o", capsize=3)
    axes[1].set(xticks=x, xticklabels=HORIZONS, ylim=(0, .16), xlabel="horizon", ylabel="P(C_P=1, C_P*=0 | proper subset)")
    axes[1].set_title("Empirical scope extension (95% cluster CI)")
    fig.savefig(figures / "fig42_e13_censored_scope_profile.png", dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), constrained_layout=True)
    for status, marker in (("survives", "o"), ("failed", "s")):
        series = [row for row in completeness_scope if row["scope_status"] == status]
        axes[0].plot(x, [row["P_info_complete_exact_reliable"] for row in series], marker=marker, label=status)
        axes[1].plot(x, [row["mean_delta_S_miss"] for row in series], marker=marker, label=status)
    for axis, ylabel, title in (
        (axes[0], "P(informationally complete)", "Conditional completeness by scope status"),
        (axes[1], "mean ΔS_miss (nat)", "Missing information by scope status"),
    ):
        axis.set(xticks=x, xticklabels=HORIZONS, xlabel="horizon", ylabel=ylabel, title=title)
        axis.legend(frameon=False)
    fig.savefig(figures / "fig43_e13_completeness_scope_profile.png", dpi=200)
    plt.close(fig)

    summary = {
        "run_manifest_sha256": FROZEN_MANIFEST_SHA256,
        "manifest_source_commit": FROZEN_MANIFEST_COMMIT,
        "task_count": len(manifest),
        "candidate_rows": len(rows),
        "scope_endpoint_policy": "censoring-aware C_P(h) profiles only; H_valid* is not numerically summarized",
        "association_policy": "within-task candidate weights plus latent-task clustered bootstrap (B=1000); descriptive/non-causal",
        "observability_policy": "support audit only because O_P positives are sparse",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
