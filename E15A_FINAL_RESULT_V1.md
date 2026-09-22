# E15-A — Final result v1

## Frozen scope

E15-A evaluates the frozen single-regime onset family only. Its conclusion is
not a universal utilization rule for other prior families.

The confirmatory manifest SHA-256 is
`c13519c7e7f5e8c0b4af4d8a550d5b36a4735de60354c2a998e6c0017bf736b3`.
The experiment contains 125 paired latent tasks and 15,750 policy rows.

## Integrity and representation audits

- Exact support: hard midpoint, MAP point, distributional prior, uniform
  ensemble, and evidence mixture were prediction-identical.
- Existence-only support: free-onset baseline and evidence-MAP were
  prediction-identical.
- The CRPS/distance outcome completion regenerated all 15,750 frozen NRMSE
  values with zero mismatches before adding predeclared outcomes.

## Primary result: C1

`C1 = NRMSE_mixture - NRMSE_MAP` isolates uncertainty retention after the same
onset likelihood has been used. Under weak prefix evidence, retaining multiple
prior-consistent onset hypotheses reduced far-OOD error, especially for broad
and existence-only onset support. That advantage contracted as exposure and
onset evidence increased, and was near zero at high exposure.

The probabilistic endpoint agrees. For normalized CRPS, C1 was `-0.0908`
(`95% CI [-0.1011, -0.0800]`) for broad/low and `-0.1184`
(`[-0.1327, -0.1031]`) for existence-only/low. At high exposure, the
corresponding CRPS contrasts were near zero and their cellwise CIs included
zero.

Distance-wise C1 supports the same interpretation. In broad/low, mixture
benefit remained negative across all three common far-OOD thirds. In
existence-only/low, its magnitude increased toward the farthest third. Some
high-evidence distance segments showed a small reversal; this does not support
a claim of general MAP superiority because the corresponding whole-window CRPS
CIs include zero.

## Secondary results and interpretation boundary

`C2 = NRMSE_mixture - NRMSE_uniform` indicates that likelihood weighting is
most useful once onset information is available while support remains broad.
`C3 = NRMSE_MAP - NRMSE_hard_midpoint` is secondary only: in centered valid
intervals, the hard midpoint coincides with the true onset by construction, so
C3 is not a pure evidence-selection comparison.

The predeclared catastrophic threshold was not activated in this controlled
family; it is reported as non-informative rather than as a method benefit.

## Frozen conclusion

> **Preserve uncertainty when identification is weak; concentrate only when
> the data justify it.**

More specifically, under controlled regime-onset uncertainty, broad onset
support and weak prefix evidence favored retaining multiple prior-consistent
future hypotheses over early MAP commitment. This advantage contracted as
onset evidence became informative. Likelihood-based reweighting became useful
once the prefix supplied enough onset information.

All reported bootstrap intervals are `5,000`-replicate latent-task paired,
cellwise percentile 95% CIs. They are not familywise multiple-comparison
claims.

## Artifact hashes

- Outcome completion rows:
  `81a0444cf9305c56a3fffc20ea23fd24fa35f47f990de01cbda73950147e6f47`
- Outcome completion integrity:
  `4bdffb1dfd662da18d3ea2e7740141f7da8139e71b643a18b6dcce60ba433d30`
- Cellwise bootstrap table:
  `0a93fb32b00c7ed35d4b88887fad02c2f8ffc96e076e5038f71e8075a03f8a1e`
- Bootstrap integrity:
  `6070d62fe5bbf734146c8ea8afe2043c03a81f591022b5cdcb9480bf69f2b472`
