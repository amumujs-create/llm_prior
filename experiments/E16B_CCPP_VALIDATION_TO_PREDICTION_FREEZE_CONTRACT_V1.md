# E16-B CCPP Validation-Evidence and Prediction-Freeze Contract v1

**Status: FROZEN before guard or confirmatory PE is opened.** This contract
implements the authorized sequence in the affine-equivalence/CRPS amendment.

## Validation-only evidence

The validation partition, and only that partition, may supply PE values after
the train-only capacity and affine-equivalence audits pass. Each of the frozen
405 full-train fits is scored in normalized target units by

\[
\ell_h^{val}=\frac{\sum_{i\in val}(\tilde y_i-f_h(x_i))^2}
{2\sigma_{ref}^2},\qquad
\sigma_{ref}=0.26536872271489265.
\]

`specification_MAP` is the candidate with minimum loss; an exact numerical tie
is resolved by the smaller frozen candidate index. `specification_weighted`
uses stable softmax weights \(\exp[-(\ell_h-\ell_{min})]\) with no
temperature, clipping, rescaling, or candidate-grid revision. Entropy and ESS
are descriptive frozen records only.

## Exact CRPS implementation audit

Before any guard or confirmatory PE access, the finite Gaussian-mixture CRPS
implementation must pass: singleton, identical-component, one-hot-weight,
weight-sum, finite/nonnegative, deterministic replay, and fixed toy numerical
integration checks. The audit uses no CCPP target values.

## Prediction freeze

After validation MAP and weights are frozen, read **only four X columns** for
the confirmatory rows (`AT > 29.24`). Persist the 956-by-405 normalized
component-mean matrix, uniform/weighted weights, MAP index, and the frozen
\(\sigma_{ref}\). The machine-readable manifest records hashes, shapes, and
target-access attestations. It contains no guard or confirmatory PE values and
no test scoring result.

The next authorized operation after this freeze is confirmatory CRPS scoring.
