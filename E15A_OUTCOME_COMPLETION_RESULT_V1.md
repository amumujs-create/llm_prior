# E15-A — Deterministic outcome completion v1

The original confirmatory scorer stored the frozen far-OOD RMSE/NRMSE and
commitment descriptors but omitted two predeclared outcomes: Gaussian-mixture
CRPS and distance-wise degradation. This analysis-only completion reused the
frozen manifest and deterministic prefix-only policy implementation. It did
not generate new tasks, alter seeds, change a policy, tune any parameter, or
modify the original confirmatory rows.

## Integrity

- Frozen manifest SHA-256:
  `c13519c7e7f5e8c0b4af4d8a550d5b36a4735de60354c2a998e6c0017bf736b3`.
- Source confirmatory rows: `15,750`.
- Completion rows: `15,750`.
- Regenerated far-NRMSE mismatch count: `0` at absolute tolerance `1e-14`.
- CRPS: exact Gaussian-mixture energy form.
- Distance profile: three equal-index thirds of the fixed common far-OOD grid
  `(tau*+.10W_tau, tau*+.80W_tau]`.

The completed-row SHA-256 is
`81a0444cf9305c56a3fffc20ea23fd24fa35f47f990de01cbda73950147e6f47`.
The completion-integrity SHA-256 is
`4bdffb1dfd662da18d3ea2e7740141f7da8139e71b643a18b6dcce60ba433d30`.

## Scope

The completion supplies the previously missing predeclared outcome columns
only. Its artifact is separate from the confirmatory manifest and original
run hash; it must not be treated as a model, generator, or policy change.
