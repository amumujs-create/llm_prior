# E16-B Post-hoc Mean–Spread Decomposition Results v1

**Status: post-hoc diagnostic, not confirmatory.** No candidate, weight,
component scale, split, or model fit was changed. The existing 956-by-405
component archive and confirmatory targets were used only to evaluate derived
predictive distributions.

## Weighted same-mean spread decomposition

| Term | Mean CRPS difference | 95% paired-row bootstrap CI |
|---|---:|---:|
| Retention \(F_{W,1}-F_{W,0}\) | +0.00006624 | [+0.00004206, +0.00009051] |
| Variance \(G_{W,1}-F_{W,0}\) | +0.00007280 | [+0.00004907, +0.00009680] |
| Shape \(F_{W,1}-G_{W,1}\) | -0.00000656 | [-0.00000905, -0.00000433] |

With the weighted predictive mean held fixed, retaining the full candidate
spread was slightly CRPS-harmful in this frozen family. The moment-matched
Gaussian's additional variance accounts for the positive term; mixture shape
recovers only a small part of it. These are score-path terms, not causal
attributions or calibrated epistemic-uncertainty estimates.

## Uniform-to-weighted recovery decomposition

| Term | Mean CRPS difference | 95% paired-row bootstrap CI |
|---|---:|---:|
| Center change \(L\) | -0.16904 | [-0.17778, -0.16019] |
| Variance change \(V\) | +0.02969 | [+0.02644, +0.03300] |
| Shape change \(S\) | +0.00379 | [+0.00322, +0.00435] |
| Recovery total \(W_1-U_1\) | -0.13556 | [-0.14063, -0.13029] |

Thus the weighted-mixture recovery over uniform arose primarily from the
prediction-center change. Relative changes in the variance and mixture-shape
terms partially offset that improvement.

Every mean-preservation, variance-match, \(F_0\) single-Gaussian, original
B1/B2 reproduction, row-level identity, and bootstrap-level identity audit
passed at the frozen \(10^{-12}\) normalized-target tolerance.
