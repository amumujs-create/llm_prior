# E16-B CCPP Final Scoring and Inference Contract v1

**Status: FROZEN before confirmatory PE is opened.** The only authorized next
target access is final scoring of the already frozen test-X predictive
distributions.

## Primary estimand and scoring

For each of the 956 confirmatory rows, use the exact finite Gaussian-mixture
CRPS with the frozen component means, weights, and
\(\sigma_{ref}=0.26536872271489265\). Define

\[
\Delta_{1,i}=CRPS_U(i)-CRPS_M(i),\qquad
B_1^{CRPS}=956^{-1}\sum_i\Delta_{1,i}.
\]

The prospective directional prediction remains \(B_1^{CRPS}<0\).

## Inference and primary disposition

Use 5,000 paired empirical-row bootstrap replicates of the mean
\(\Delta_{1,i}\), sampled with replacement over the 956 row positions. The
frozen NumPy PCG64 seed is `20260924`; percentile endpoints use the `linear`
quantile convention at 0.025 and 0.975.

| Condition | Primary disposition |
|---|---|
| mean < 0 and CI entirely < 0 | Supported |
| mean < 0 and CI includes 0 | Direction-compatible, inconclusive |
| mean > 0 and CI includes 0 | Direction-incompatible, inconclusive |
| CI entirely > 0 | Prospective failure |

This is an empirical row-resampling interval for the frozen 956-row CCPP
confirmatory partition. It is not a population-wide interval for every
combined-cycle operating environment.

## Secondary endpoints and release order

After B1 is separately frozen, score
\(B_2^{CRPS}=CRPS_W-CRPS_U\) as a secondary non-directional contrast with the
same paired-row bootstrap convention. Only after that release the secondary
point diagnostics \(B_1^{NRMSE}\) and \(B_2^{NRMSE}\). NRMSE must be labelled
a point-specification diagnostic, not evidence of retained predictive
diversity.

No result authorizes a candidate-grid, \(\sigma_{ref}\), temperature,
weighting, or policy change.
