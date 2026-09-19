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

### False additions are atom-stratified primary results

| Added atom | Rows | Mean `Delta S_add` (nat) |
|---|---:|---:|
| `regime_postchange` | 630 | 0.476 |
| `turning_maximum` | 90 | 2.257 |


Seven catalog cells add `regime_postchange`; one adds `turning_maximum`.
Consequently, their pooled mean is supplementary and must not be described as
a generic false-addition law.

## Interpretation and boundary

Within this frozen 1D grammar, removing a true atom reduced conditional
sharpness on average, while false addition and reversal produced heterogeneous
nonnegative/negative information changes. This establishes that omission,
false addition, and reversal are not interchangeable *information errors*.
Coverage was designed as an integrity invariant, not discovered as a result.

E12-B contains no predictor, utility, RMSE, prediction harm, engine
compatibility, or LLM component. Therefore it does **not** show that every
false structural statement is predictively harmful. Family-local
`D_violation` values are stored for audit and may not be pooled as a universal
severity scale.
