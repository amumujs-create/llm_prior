# E15-C v1.1 matched-capacity invariant-backbone result

## Frozen estimand

`C_inv = NRMSE(invariant residual ensemble) - NRMSE(matched free baseline)`.

Both branches use the same residual-shape grid, residual-amplitude envelope,
and bounded amplitude profiling. The invariant branch fixes the supplied
coefficient at `c = -k0`; the matched-free baseline instead profiles `c` on
its frozen public grid.

## Cellwise latent-task paired bootstrap

| Prefix exposure | Latent tasks | Mean C_inv | 95% CI |
| --- | ---: | ---: | ---: |
| Low | 125 | -0.100828 | [-0.163409, -0.037831] |
| Medium | 125 | -0.072814 | [-0.099305, -0.047556] |
| High | 125 | -0.000107 | [-0.007417, +0.007014] |

All intervals use 5,000 latent-task paired-bootstrap replicates and are
cellwise 95% intervals. The source corpus SHA-256 is
`943923b9f0131a04001b340fcee942a4276270dfaad9cd873b9d6abc295349fd`.

## Interpretation boundary

At low and medium prefix exposure, sharing the correct invariant improved
prediction relative to the capacity-matched free baseline. At high exposure,
the incremental contrast was compatible with zero. This is a matched-capacity
backbone comparison only; it is distinct from the C1/C2 residual-uncertainty
allocation results. The exposure pattern is descriptive because no
exposure-change interaction inference is calculated.

## Frozen artifacts

- `E15C_INVARIANT_BACKBONE_CELLWISE_PAIRED_BOOTSTRAP.csv` SHA-256:
  `5ccfe04def0706340a73197d7019e6142fb9de15d05496ccf24ad1fe047492f4`
- `figures/E15C_INVARIANT_BACKBONE_EXPOSURE_CELLWISE.png` SHA-256:
  `1ab735241afdd046c00e723a864fef902396a2eb6a65d6c26444fefa2925ce23`
