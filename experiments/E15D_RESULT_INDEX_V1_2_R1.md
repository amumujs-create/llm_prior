# E15-D v1.2 R1 Result Index

## Frozen confirmatory object

- Geometry: broad support `[0.10, 0.90]`, joint grid spacing `0.05`,
  `rho = 0.10`, nested L/S/J prefixes `(0.25, 0.60, 0.85)`, and common
  clean-target far window `(0.85, 1.00]`.
- Corpus: 153 latent tasks x 3 exposures x 4 policies = 1,836 rows.
- Bootstrap: 5,000 latent-task paired replicates; all intervals below are
  cellwise 95% intervals.
- Corpus row SHA-256:
  `2ee194755f3638bc8cc8421d25f9de914f249cba2737489e2c1cce2ef763812b`.
- Integrity SHA-256:
  `f2a3743df0d983ac15810f4544714953973c7e79e1fc91cd2aa61a9dae00b8ca`.

`joint_weighted` and `factorized_joint_weighted` are prediction-identical in
this additive continuation family once their marginals are fixed.  Their
equality is an integrity audit; `factorized_joint_weighted` is the retained
scientific policy label.

## Confirmatory results

| Estimand | Contrast | Mean paired NRMSE | Cellwise 95% CI | Pre-outcome direction | Disposition |
| --- | --- | ---: | --- | --- | --- |
| D1_S | kappa-selective - joint-uniform | -0.0722 | [-0.0956, -0.0483] | < 0 | Supported |
| D2_S | factorized-joint - kappa-selective | -0.0030 | [-0.0068, 0.0008] | > 0 | Direction-incompatible, inconclusive |
| D2_J | factorized-joint - kappa-selective | -0.0680 | [-0.0807, -0.0556] | < 0 | Secondary prediction supported |
| D3_S | joint-MAP - factorized-joint | +0.0831 | [+0.0577, +0.1081] | secondary stress | Point-collapse cost observed |

## Prospective interpretation

The prespecified primary conjunction required both `D1_S < 0` and `D2_S > 0`
with their full 95% paired-bootstrap intervals on the corresponding sides of
zero.  `D1_S` met this criterion, whereas `D2_S` did not: its point estimate
was slightly negative and its interval crossed zero.  Thus the primary
prospective principle is **not supported as a full conjunction** in this
frozen capstone; the D2_S result is direction-incompatible but inconclusive,
not a formal prospective failure.

The S result supports selective reduction of the strongly identified kappa
dimension relative to retaining both dimensions uniformly.  It does not show
the predicted cost of additionally factorized-weighting the weakly identified
lambda dimension.  In J, lambda evidence was materially greater than in S
(but was not labeled strong identification), and D2_J favored factorized
weighting.  D3_S separately shows that all-dimension MAP collapse incurred a
substantial cost.

The L/S/J conditions are frozen nested-prefix construct exemplars with
separated evidence distributions; they do not establish a continuous
threshold law for policy choice.

## Frozen artifacts

| Artifact | SHA-256 |
| --- | --- |
| D1_S paired bootstrap | `32e04fe9e72a0dab0a2ecec05970d92b6f631f9e75bbf4c03ed66f0c9d757901` |
| D2_S paired bootstrap | `b639126f771bb685aca252908018e8ee48e88cffc3ddb287cc13374c5571b1cf` |
| D2_J paired bootstrap | `aa80a7eff730a12198b5194646c44e5b3c326861af4351f1f925f08ec7ff3db3` |
| D3_S paired bootstrap | `690d24426db57125f581a24e37ea0ce5750d0aa9b1259fb34e336e93fbe8c6b8` |
| Combined contrast figure | `04c275df29b3c579a105e068ec0913bd390ab16e3cf7e94bfb95e21c626ddd31` |

The combined figure is
`results/prior_utilization_e15d/confirmatory_v1_2_r1/E15D_CONFIRMATORY_CONTRAST_SUMMARY_V1_2_R1.png`.
