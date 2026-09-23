# E16-B CCPP Train Capacity Audit v1

## Status

**PASS.** This stage opened only the 6,699 frozen train target rows.
Validation, guard, and confirmatory targets remained prohibited.

## Frozen train-only quantities

- \(m_y=462.68\); \(R_y=23.87\), both calculated on train rows only.
- The common 10-term nuisance basis and zero-based-index modulo-5 folds
  replayed exactly; fold assignment SHA-256 is
  `41607f07db26c966c1525ad1ae37b68c5a72a2c20017d0b293bf9ae01d37e1b6`.
- The single shared ridge selection was \(\lambda_{spec}=10^{-4}\).
- The frozen Gaussian working-likelihood scale is
  \(\sigma_{ref}=0.2653687227\), the median candidate train out-of-fold RMSE.

## Post-fit realization audit

The 405 full-train candidate fits were evaluated only at validation, guard,
and confirmatory **X locations**. No corresponding held-out targets were read.

| Quantity | Value |
|---|---:|
| Future-X rows | 1,433 |
| Pairwise candidate predictions | 81,810 |
| Minimum post-fit RMS distance | 0.0033225 |
| Exact-equivalent pairs at \(10^{-10}\) | 0 |
| Centered prediction rank | 5 |
| Centered prediction condition number | 121.43 |

Thus candidate-specific nuisance fitting did not collapse the frozen
continuation family into prediction-identical alternatives. This is an
implementation realization PASS, not a performance result and not a reason to
modify the D0 reference measure.

## Next gate

Validation targets may now be opened exactly once to calculate frozen Gaussian
working-likelihood scores, select the deterministic MAP candidate, and freeze
the 405 mixture weights. Guard and confirmatory targets remain sealed.
