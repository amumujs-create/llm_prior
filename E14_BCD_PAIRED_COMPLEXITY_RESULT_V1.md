# E14-B/C/D paired complexity result v1

**Corpus.** The independent `e14-full-v1` corpus contains 216 base cells,
3,888 accepted paired latent groups, and 11,664 branch-condition scorings.
Its manifest SHA-256 is
`e4ae4980c2390a30ae169ed9f9eace2f4a82df0f2ca443db05af91fe88b5a01d`.
It is distinct from the E14-A measurement-sanity corpus.

All reported intervals are 5,000-replicate paired-latent-group clustered
bootstrap 95% intervals with equal generator weighting. Candidate subsets are
summarised within paired groups before resampling.

## Corpus integrity and pairing

- Required groups: 3,888 / 3,888; exhausted cells: 0.
- Direct checker-versus-AND audit failures: 0.
- Envelope, base-persistence, scope, semantic, numeric, and unclassified
  rejection counts: 0.
- `M_common=16384`, frozen from E14-A.

Thus the reported contrasts are paired comparisons inside the independent full
corpus, not a reuse of E14-A rows.

## E14-B — dimension

Primary `d8 - d3` changes were essentially stable for conditional sharpness
and mean atom evidence: `Delta S = +0.000011` (95% CI `[-0.000006,
+0.000028]`) and `Delta mean(E_a) = -0.000017` (`[-0.000059,+0.000026]`).
The completeness-gap change was positive but numerically tiny, `+0.000016`
(`[+0.0000002,+0.000031]`). Effective dimension and normalized continuation
dispersion changed by `+0.00116` and `+0.00000294`, respectively.

`d1 - d3` is retained as the predeclared E13 anchor rather than an
energy-matched dimensional effect. It shows lower context-balanced evidence
(`-0.05897`) and is not used to generalize the primary `d3 <-> d8` contrast.

## E14-C — interaction

Interaction changes were directional but small in absolute magnitude and not
monotone as a single “more interaction” effect:

- `pairwise - additive`: `Delta S=-0.000890`
  (95% CI `[-0.001163,-0.000612]`), `Delta mean(E_a)=+0.001950`
  (`[+0.001598,+0.002279]`), and `Delta Delta S_miss=-0.000713`
  (`[-0.000958,-0.000463]`).
- `entangled - additive`: `Delta S=+0.000469`
  (`[+0.000300,+0.000644]`), `Delta mean(E_a)=-0.001240`
  (`[-0.001461,-0.001024]`), and `Delta Delta S_miss=+0.000364`
  (`[+0.000213,+0.000517]`).

Thus the controlled realization form, rather than a scalar interaction-order
ranking, determines which continuous anatomy coordinates move.

## E14-D — structural heterogeneity

Heterogeneity also did not yield a monotone deterioration pattern:

- `moderate - none`: `Delta S=-0.000108`
  (95% CI `[-0.000183,-0.000030]`) and `Delta Delta S_miss=-0.000096`
  (`[-0.000165,-0.000027]`).
- `strong - none`: `Delta S=+0.000618`
  (`[+0.000519,+0.000720]`) and `Delta Delta S_miss=+0.000569`
  (`[+0.000482,+0.000658]`).

The strong condition increased mean atom evidence slightly (`+0.000457`),
whereas the moderate condition's increase was `+0.000273`. These are
controlled realization effects, not estimates of a universal heterogeneity
law.

## Stable anatomy coordinates

Every branch had exact, reliable completeness gaps. The informational-complete
rate among proper subsets was **85.0%** in every branch, so each paired
difference in that rate was exactly zero. The censoring-aware scope audit
recomputed `V_a -> C_a -> C_P` from frozen clean fields rather than requested
scope labels. Its candidate survival profiles and proper-subset extension
profiles were also exactly unchanged across every matched contrast.

## Conclusion and boundary

Under the frozen realized-context, `t`-continuation-uncertainty estimand, the
tested complexity axes leave binary completeness and scope anatomy stable.
Some continuous coordinates move, but their direction depends on the specific
dimension/interaction/heterogeneity construction. E14 therefore supports
axis-specific sensitivity rather than the blanket claim that greater
realization complexity uniformly weakens a structural prior.

The machine-readable paired estimates are in
`results/complexity_scaling_e14/e14bcd/analysis/paired_effects.csv`.
