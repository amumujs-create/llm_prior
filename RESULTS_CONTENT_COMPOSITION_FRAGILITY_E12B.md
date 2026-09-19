# E12-B — Content / Composition Fragility Results

## Integrity

- Catalog SHA-256: `8e393978884374dd2c4cd68e8bbf3ae0673a064253c31a57152a96b26ba47e1c`
- Expected / observed scoring rows: `5130` / `5130`
- Exhausted cells: `0`; all bank/ESS/support audits pass: `True`.
- Coverage invariants: omission `coverage=1` in 2160/2,160 rows; false addition `coverage=0` in 720/720; reversal `coverage=0` in 1530/1,530.
- All 4,410 operation sharpness comparisons are floor-exact; no floor-bound or unresolved comparison occurred.

## Conditional-information results

| Operation | Rows | Mean change (nat) | Median | IQR |
|---|---:|---:|---:|---:|
| Omission (`L_omit=S_full-S_omit`) | 2160 | 1.022 | 0.452 | [0.000, 1.350] |
| False addition (`Delta S_add`) | 720 | 0.699 | 0.499 | [0.000, 0.803] |
| Reversal (`Delta S_rev`) | 1530 | 1.578 | 0.013 | [0.000, 4.581] |

All invalid false-addition/reversal rows (2250) are
`inherited-sharp wrong`: their valid `P_full` baseline was already above the
`.10 nat` threshold. There are no induced-sharp, attenuated, or false-but-weak
rows in this frozen corpus. This is an attribution result—not evidence that
false atoms generally create sharpness.

### Reversal is heterogeneous, not a typical large increase

Of 1530 reversals, `331` (0.216) have
`Delta S_rev<0`; `482` (0.315) are within
`±.10 nat`; and `747` (0.488)
exceed `.10 nat`. The mean/median divergence therefore reflects a heterogeneous
response, not a typical large sharpness increase.

| Reversed source atom | Rows | Median `Delta S_rev` | 95th percentile |
|---|---:|---:|---:|
| `asymptote_to_0_from_above` | 540 | 3.833 | 7.239 |
| `curvature_convex` | 270 | 0.000 | 4.088 |
| `direction_decreasing` | 360 | 0.147 | 6.731 |
| `inflection_concave_to_convex` | 270 | -0.658 | 2.781 |
| `turning_maximum` | 90 | 6.228 | 6.948 |


### E12-A inheritance audit

Among the `1350` E12-A baseline specification states,
`1350` (1.000) already had
`S(P_0|D)>=.10 nat`. Thus E12-A's immediate invalid-but-sharp result must also
be interpreted against baseline inherited sharpness; it does not by itself
show that numeric misspecification newly created confidence.



### False additions are atom-stratified primary results

| Added atom | Rows | Mean `Delta S_add` (nat) |
|---|---:|---:|
| `regime_postchange` | 630 | 0.476 |
| `turning_maximum` | 90 | 2.257 |


Seven catalog cells add `regime_postchange`; one adds `turning_maximum`.
Consequently, their pooled mean is supplementary and must not be described as
a generic false-addition law.

## Interpretation and boundary

The signs of omission and false-addition changes are consequences of nested
AND semantics: removing a true atom can only relax the continuation set, and
adding an atom can only restrict it. Their empirical content is therefore the
magnitude and heterogeneity of the change—not its sign. Within this frozen 1D
grammar, omission, false addition, and reversal had non-interchangeable
conditional-information consequences. Coverage was designed as an integrity
invariant, not discovered as a result.

E12-B contains no predictor, utility, RMSE, prediction harm, engine
compatibility, or LLM component. Therefore it does **not** show that every
false structural statement is predictively harmful. Family-local
`D_violation` values are stored for audit and may not be pooled as a universal
severity scale.
