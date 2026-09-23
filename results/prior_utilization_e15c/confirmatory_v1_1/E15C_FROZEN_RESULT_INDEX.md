# E15-C v1.1 frozen result index

## Confirmatory corpus

- Confirmatory manifest SHA-256:
  `1d6da0e4984be39d92dfcfd1fec82e248a68d4f9919e2ddda014fe65e3d2f18f`
- Confirmatory row artifact SHA-256:
  `943923b9f0131a04001b340fcee942a4276270dfaad9cd873b9d6abc295349fd`
- Corpus: 125 latent tasks × 3 prefix exposures × 5 policies = 1,875 rows.
- Corpus/integrity freeze: commit `71acf84`.
- Every result below uses 5,000 replicate latent-task paired bootstrap and
  cellwise 95% confidence intervals. No exposure-change interaction inference
  is part of this result index.

## Result artifacts

| Result | Estimand | Frozen source | Result commit | Main conclusion |
| --- | --- | --- | --- | --- |
| C1 | weighted residual mixture − residual MAP | `E15C_C1_CELLWISE_PAIRED_BOOTSTRAP.csv` | `1bc1932` | With weakly identified residual shape, retaining residual diversity beat early residual-MAP commitment. |
| C2 | weighted residual mixture − uniform residual ensemble | `E15C_C2_CELLWISE_PAIRED_BOOTSTRAP.csv` | `0a3c812` | Weighting was harmful at low exposure, compatible with zero at medium exposure, and beneficial at high exposure within the still-weak residual-evidence regime. |
| Closed stress | closed mechanism − invariant residual ensemble | `E15C_CLOSED_MECHANISM_STRESS_CELLWISE_PAIRED_BOOTSTRAP.csv` | `9a0adb9` | A correct invariant was not a complete predictive model; setting the residual to zero increased error in every cell. |
| C_inv | invariant residual ensemble − matched free baseline | `E15C_INVARIANT_BACKBONE_CELLWISE_PAIRED_BOOTSTRAP.csv` | `6ddde90` | Correct invariant sharing improved prediction at low and medium exposure, with high-exposure incremental value compatible with zero. |

## Result hashes

- C1 table: `24706c1050a94a5c1bb54bde5b0b8ff6eb494aaf1c019827f8641b80c21bf780`
- C2 table: `bb49d82544f9938f218772e5b63dba399e1117e7596ecc3d44038ed1662c4f24`
- Closed-stress table: `440b70be0ff35a78c5408953e584ab7a3d1a58721749040c06a2f7edef734e95`
- Invariant-backbone table: `5ccfe04def0706340a73197d7019e6142fb9de15d05496ccf24ad1fe047492f4`
- Integrated figure: `a18f52e76573a1e8954b260455250e5b3fa1e9df2c74c1154f11058f3605a9d8`

## Frozen interpretation

E15-C v1.1 tests an exact shared invariant with a common known residual
amplitude envelope and unresolved residual-shape uncertainty. The evidence
target and the weighted uncertainty dimension are both residual shape `q`.

The frozen results support four distinct conclusions:

1. Preserve residual-shape diversity while that dimension is weakly
   identified.
2. Within retained diversity, apply residual-likelihood weighting only when
   the prefix becomes informative about that same residual-shape dimension.
3. Do not treat a valid invariant as a complete future model by discarding the
   unresolved residual.
4. A correct shared invariant can add extrapolative value beyond a
   capacity-matched free model.

All low, medium, and high cells in this v1.1 family retain weak realized
residual evidence. The C2 pattern therefore does not establish behavior under
strong residual identification. E15-C v1.1 also conditions on the common
known residual-amplitude envelope and does not characterize unconstrained
residual-amplitude uncertainty.
