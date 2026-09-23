# E15-C v1.1 C1 result

## Frozen estimand

`C1 = NRMSE(evidence-weighted residual mixture) - NRMSE(invariant residual MAP)`.

The contrast compares retention of residual-shape diversity with early
single-shape commitment, conditional on the same exact shared invariant, the
same known residual-amplitude envelope, and the same residual profile-loss
evidence.

## Cellwise latent-task paired bootstrap

| Prefix exposure | Latent tasks | Mean C1 | 95% CI |
| --- | ---: | ---: | ---: |
| Low | 125 | -0.065917 | [-0.082659, -0.049077] |
| Medium | 125 | -0.024609 | [-0.037099, -0.013001] |
| High | 125 | -0.011477 | [-0.017320, -0.005655] |

All intervals use 5,000 latent-task paired-bootstrap replicates and are
cellwise 95% intervals. The source corpus SHA-256 is
`943923b9f0131a04001b340fcee942a4276270dfaad9cd873b9d6abc295349fd`.

## Interpretation boundary

All three cells have progressively greater but still weak realized residual
evidence. This result supports retaining residual-shape diversity conditional
on a resolved invariant and common amplitude envelope. It does not test the
value of concentration under strongly identified residual shape.

## Frozen artifacts

- `E15C_C1_CELLWISE_PAIRED_BOOTSTRAP.csv` SHA-256:
  `24706c1050a94a5c1bb54bde5b0b8ff6eb494aaf1c019827f8641b80c21bf780`
- `figures/E15C_C1_EXPOSURE_CELLWISE.png` SHA-256:
  `e552ef03544583f665c91fbf81251a2fc2f7140561397056fc7bbc76ca05de31`

No C2, closed-mechanism, or matched-free result is calculated or interpreted
in this artifact.
