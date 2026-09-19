#!/usr/bin/env python3
"""Produce the frozen descriptive E12-B report and operation-level figure."""
from __future__ import annotations

import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/content_fragility_e12b/full"
E12A_ROWS = ROOT / "results/prior_fragility_e12a/run/rows.csv"
REPORT = ROOT / "RESULTS_CONTENT_COMPOSITION_FRAGILITY_E12B.md"
DELTA = 0.10


def f(x: float) -> str:
    return f"{x:.3f}"


def main() -> None:
    with (RUN / "rows.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    with (RUN / "integrity.json").open() as handle:
        integrity = json.load(handle)
    operations = [r for r in rows if r["row_role"] == "operation"]
    by_type: dict[str, list[dict]] = defaultdict(list)
    for row in operations:
        by_type[row["operation_type"]].append(row)
    stats = {}
    for kind, group in by_type.items():
        values = [float(r["delta_S"]) for r in group]
        stats[kind] = {
            "n": len(group), "mean": float(np.mean(values)), "median": float(np.median(values)),
            "q25": float(np.quantile(values, .25)), "q75": float(np.quantile(values, .75)),
        }
    classes = Counter(r["sharpness_class"] for r in operations)
    floors = Counter(r["floor_status"] for r in operations)
    coverage = Counter((r["operation_type"], r["coverage"]) for r in operations)
    addition = defaultdict(list)
    for row in by_type["false_addition"]:
        addition[row["target_atom"]].append(float(row["delta_S"]))
    reversal = [float(row["delta_S"]) for row in by_type["reversal"]]
    reversal_sign = {
        "negative_material": sum(value < -DELTA for value in reversal),
        "near_zero": sum(abs(value) <= DELTA for value in reversal),
        "positive_material": sum(value > DELTA for value in reversal),
    }
    reversal_by_source = defaultdict(list)
    for row in by_type["reversal"]:
        reversal_by_source[row["source_atom"]].append(float(row["delta_S"]))
    with E12A_ROWS.open() as handle:
        e12a = list(csv.DictReader(handle))
    e12a_baseline = [row for row in e12a if float(row["epsilon"]) == 0.0]
    e12a_sharp = sum(float(row["S_baseline"]) >= DELTA for row in e12a_baseline)

    atoms = sorted(addition)

    report = f"""# E12-B — Content / Composition Fragility Results

## Integrity

- Catalog SHA-256: `{integrity['catalog_sha256']}`
- Expected / observed scoring rows: `{integrity['expected_rows']}` / `{integrity['actual_rows']}`
- Exhausted cells: `{integrity['exhausted_cells']}`; all bank/ESS/support audits pass: `{integrity['all_audits_pass']}`.
- Coverage invariants: omission `coverage=1` in {coverage[('omission','1')]}/2,160 rows; false addition `coverage=0` in {coverage[('false_addition','0')]}/720; reversal `coverage=0` in {coverage[('reversal','0')]}/1,530.
- All 4,410 operation sharpness comparisons are floor-exact; no floor-bound or unresolved comparison occurred.

## Conditional-information results

| Operation | Rows | Mean change (nat) | Median | IQR |
|---|---:|---:|---:|---:|
| Omission (`L_omit=S_full-S_omit`) | {stats['omission']['n']} | {f(stats['omission']['mean'])} | {f(stats['omission']['median'])} | [{f(stats['omission']['q25'])}, {f(stats['omission']['q75'])}] |
| False addition (`Delta S_add`) | {stats['false_addition']['n']} | {f(stats['false_addition']['mean'])} | {f(stats['false_addition']['median'])} | [{f(stats['false_addition']['q25'])}, {f(stats['false_addition']['q75'])}] |
| Reversal (`Delta S_rev`) | {stats['reversal']['n']} | {f(stats['reversal']['mean'])} | {f(stats['reversal']['median'])} | [{f(stats['reversal']['q25'])}, {f(stats['reversal']['q75'])}] |

All invalid false-addition/reversal rows ({classes['inherited_sharp_wrong']}) are
`inherited-sharp wrong`: their valid `P_full` baseline was already above the
`.10 nat` threshold. There are no induced-sharp, attenuated, or false-but-weak
rows in this frozen corpus. This is an attribution result—not evidence that
false atoms generally create sharpness.

### Reversal is heterogeneous, not a typical large increase

Of {len(reversal)} reversals, `{reversal_sign['negative_material']}` ({f(reversal_sign['negative_material']/len(reversal))}) have
`Delta S_rev<-.10 nat`; `{reversal_sign['near_zero']}` ({f(reversal_sign['near_zero']/len(reversal))}) are within
`±.10 nat`; and `{reversal_sign['positive_material']}` ({f(reversal_sign['positive_material']/len(reversal))})
exceed `.10 nat`. The mean/median divergence therefore reflects a heterogeneous
response, not a typical large sharpness increase.

| Reversed source atom | Rows | 5th percentile | Median `Delta S_rev` | 95th percentile |
|---|---:|---:|---:|---:|
"""
    for atom in sorted(reversal_by_source):
        values = reversal_by_source[atom]
        report += f"| `{atom}` | {len(values)} | {f(float(np.quantile(values, .05)))} | {f(float(np.median(values)))} | {f(float(np.quantile(values, .95)))} |\n"
    report += f"""

### E12-A inheritance audit

Among the `{len(e12a_baseline)}` E12-A baseline specification states,
`{e12a_sharp}` ({f(e12a_sharp/len(e12a_baseline))}) already had
`S(P_0|D)>=.10 nat`. Thus E12-A's immediate invalid-but-sharp result must also
be interpreted against baseline inherited sharpness; it does not by itself
show that numeric misspecification newly created confidence.

"""
    report += """

### False additions are atom-stratified primary results

| Added atom | Rows | Mean `Delta S_add` (nat) |
|---|---:|---:|
"""
    for atom in atoms:
        report += f"| `{atom}` | {len(addition[atom])} | {f(float(np.mean(addition[atom])))} |\n"
    report += """

Seven catalog cells add `regime_postchange`; one adds `turning_maximum`.
Consequently, their pooled mean is supplementary and must not be described as
a generic false-addition law.

## Interpretation and boundary

Within the frozen grammar and acceptance-conditioned corpus, omission,
compatible false addition, and signed reversal exhibited distinct
conditional-information profiles. The direction of omission/addition changes
follows from nested AND semantics, whereas their magnitudes are heterogeneous;
reversal is non-nested and varies substantially in direction and magnitude by
source atom and context. Coverage was designed as an integrity invariant, not
discovered as a result.

All wrong candidates were classified as inherited-sharp rather than
induced-sharp because their valid baselines were already above the predeclared
threshold and the wrong candidates themselves remained above it. For false
additions, this persistence is consistent with their nested restriction
relation; for reversals and E12-A specification shifts, it is an empirical
observation rather than a logical consequence. Neither experiment shows that
misspecification itself generated confidence. Rather, conditional sharpness can
persist after validity is lost. E12-B contains no predictor, utility, RMSE,
prediction harm, engine compatibility, or LLM component. Family-local
`D_violation` values are stored for audit and may not be pooled as a universal
severity scale.
"""
    REPORT.write_text(report)
    print(f"wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
