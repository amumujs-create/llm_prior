# E13 scope-aware generator freeze v1

E13 uses a dedicated generator; it does not reuse the E11 completeness
generator as a scope corpus.

## Two-stage generation

1. Generate a persistent base `f_base` whose realized maximal E11 envelope
   `P_star` is valid on `[.40,1.20]`. It must retain the intended prefix,
   core-domain envelope, and E9 evidence condition.
2. Apply one frozen smooth post-`.80` intervention family to obtain `f_int`.
   The gate is zero on `x<=.80` and has at least C2 continuity at its onset.
   Requested scope is a proposal label only.

## Acceptance and measurement

The scope scorer receives `f_int` and frozen atom-oracle semantics only; it
never receives breaker metadata. For every atom it computes `C_a(h)` on the
clean trajectory, then forms `C_P(h)=product_{a in P} C_a(h)`. Full-envelope
`H_valid*` produces the measured scope stratum, which alone determines quota
acceptance. Subset scope is not designed or quota-balanced.

## Integrity contract

- `f_base(x)==f_int(x)` bitwise for every `x<=.80`.
- Regime and asymptote retain their frozen E11 mechanistic/latent-assisted
  semantics; they are not silently changed into derivative-only tests.
- Store requested/measured strata separately.
- Store base persistence, pre/post core hashes, intervention family/seed/
  parameters, atomwise `C_a(h)`, full `C_Pstar(h)`, censor state, envelope
  atoms, and every rejection reason.
- Extended `[.40,h]` atom semantics are frozen in
  `E13_EXTENDED_SCOPE_ORACLE_SEMANTICS_V1.md`. Event atoms retain their one
  core event and fail only with an absent/reversed/additional event; regime and
  asymptote retain paired latent semantic state.
- Freeze intervention families and parameter ranges before acceptance; do not
  tune them after observing joint-anatomy outcomes.

## Deprecated artifacts

`results/joint_prior_anatomy_e13/run/` and the earlier core-only preflight are
debug artifacts only. They are excluded from scientific E13 analysis because
scope was not accepted from a persistent-base clean oracle.
