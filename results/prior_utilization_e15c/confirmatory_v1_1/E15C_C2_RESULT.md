# E15-C v1.1 C2 result

## Frozen estimand

`C2 = NRMSE(evidence-weighted residual mixture) - NRMSE(invariant residual ensemble)`.

The contrast tests whether residual profile-loss weighting improves on uniform
retention of the same residual-shape hypotheses. The invariant and known
residual-amplitude envelope are identical across the compared policies.

## Cellwise latent-task paired bootstrap

| Prefix exposure | Latent tasks | Mean C2 | 95% CI |
| --- | ---: | ---: | ---: |
| Low | 125 | +0.012970 | [+0.009030, +0.017008] |
| Medium | 125 | +0.001337 | [-0.002535, +0.005311] |
| High | 125 | -0.008515 | [-0.012559, -0.004609] |

All intervals use 5,000 latent-task paired-bootstrap replicates and are
cellwise 95% intervals. The source corpus SHA-256 is
`943923b9f0131a04001b340fcee942a4276270dfaad9cd873b9d6abc295349fd`.

## Interpretation boundary

At low prefix exposure, residual profile-loss weighting was worse than uniform
averaging. The medium-exposure contrast was compatible with zero. At high
prefix exposure, weighting improved on uniform averaging within this frozen
family. All three cells nevertheless retain weak realized residual evidence;
this result does not establish behavior under strongly identified residual
shape.

## Frozen artifacts

- `E15C_C2_CELLWISE_PAIRED_BOOTSTRAP.csv` SHA-256:
  `bb49d82544f9938f218772e5b63dba399e1117e7596ecc3d44038ed1662c4f24`
- `figures/E15C_C2_EXPOSURE_CELLWISE.png` SHA-256:
  `75168345ff0146019b01889b5af1a49469abd91f6fa66aee25eedbf11317772f`

No closed-mechanism or matched-free result is calculated or interpreted in
this artifact.
