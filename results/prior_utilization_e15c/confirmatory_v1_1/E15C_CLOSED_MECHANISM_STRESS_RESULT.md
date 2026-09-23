# E15-C v1.1 closed-mechanism stress result

## Frozen estimand

`C_closed = NRMSE(closed mechanism) - NRMSE(invariant residual ensemble)`.

The contrast is a secondary incompleteness stress test. It asks whether a
valid shared invariant can be treated as a complete model by setting the
residual to zero. It is not a C1/C2 residual-shape allocation comparison.

## Cellwise latent-task paired bootstrap

| Prefix exposure | Latent tasks | Mean C_closed | 95% CI |
| --- | ---: | ---: | ---: |
| Low | 125 | +0.063812 | [+0.012063, +0.115633] |
| Medium | 125 | +0.254625 | [+0.227645, +0.280989] |
| High | 125 | +0.291389 | [+0.270446, +0.312259] |

All intervals use 5,000 latent-task paired-bootstrap replicates and are
cellwise 95% intervals. The source corpus SHA-256 is
`943923b9f0131a04001b340fcee942a4276270dfaad9cd873b9d6abc295349fd`.

## Interpretation boundary

The closed-mechanism policy was worse than the invariant-plus-residual
ensemble in every exposure cell. Thus the shared invariant was valid but not
complete: setting the unresolved residual to zero incurred extrapolation
cost. The larger medium/high point estimates are descriptive across exposure;
no exposure-change interaction inference is made here.

## Frozen artifacts

- `E15C_CLOSED_MECHANISM_STRESS_CELLWISE_PAIRED_BOOTSTRAP.csv` SHA-256:
  `440b70be0ff35a78c5408953e584ab7a3d1a58721749040c06a2f7edef734e95`
- `figures/E15C_CLOSED_MECHANISM_STRESS_EXPOSURE_CELLWISE.png` SHA-256:
  `a2794b38ca130d04bcec375af9918888a46b23593311f1ee7d57a5afe67db7f3`

No matched-free backbone comparison is calculated or interpreted in this
artifact.
