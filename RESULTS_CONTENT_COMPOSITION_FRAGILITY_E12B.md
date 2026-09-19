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

Of 1530 reversals, `301` (0.197) have
`Delta S_rev<-.10 nat`; `482` (0.315) are within
`±.10 nat`; and `747` (0.488)
exceed `.10 nat`. The mean/median divergence therefore reflects a heterogeneous
response, not a typical large sharpness increase.

| Reversed source atom | Rows | 5th percentile | Median `Delta S_rev` | 95th percentile |
|---|---:|---:|---:|---:|
| `asymptote_to_0_from_above` | 540 | -6.176 | 3.833 | 7.239 |
| `curvature_convex` | 270 | -0.579 | 0.000 | 4.088 |
| `direction_decreasing` | 360 | -0.898 | 0.147 | 6.731 |
| `inflection_concave_to_convex` | 270 | -5.471 | -0.658 | 2.781 |
| `turning_maximum` | 90 | 0.684 | 6.228 | 6.948 |


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
