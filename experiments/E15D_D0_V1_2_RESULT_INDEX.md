# E15-D0 v1.2 result index

## Status

**FROZEN outcome-free numerical calibration.** D0 selected a geometry under
the v1.2 overlap-gate amendment. No predictive policy outcome was calculated,
opened, or used.

| Component | Frozen selection |
| --- | --- |
| support | broad \([.10,.90]\) |
| grid spacing | \(.05\) |
| noise ratio | \(\rho=.10\) |
| exposure triple | \(T2=(.25,.60,.85)\) |
| far horizon | \(1.00\) |
| D0 sample | 400 fresh discarded tasks, `e15d-d0-v1.2-discarded` |

The frozen lexicographic trace rejected T1 because J-level \(\lambda\)
evidence did not meet either J \(\lambda\) gate, then selected T2 as the
first admissible candidate. Thirty-six of 144 numerical candidates passed the
core geometry gates.

## Frozen evidence geometry

| Regime | \(E_\kappa\) median [q05, q95] | \(E_\lambda\) median [q05, q95] |
| --- | --- | --- |
| L | .0115 [.00069, .0731] | approximately 0 [.00000, .00000] |
| S | .3349 [.3306, .5742] | .00141 [.00003, .0101] |
| J | .4590 [.4039, .6385] | .1188 [.0382, .3711] |

The exact-continuous-RMS four-clique audit passed, with minimum witness
distance .03357, and all candidate computations were finite.

## Interpretation boundary

L/S/J are nested prefixes of one smooth trajectory, but their cross-sectional
evidence distributions are deliberately separated construct exemplars after
the v1.2 removal of the adjacent-overlap gate. E15-D therefore tests the
prospective selective-reduction principle across three frozen exposure
conditions with different degrees of coordinate identification. It does not
test a smooth policy-optimum threshold as evidence changes continuously.

J has materially increased \(\lambda\) evidence relative to S; this does not
license the description “strong identification.” A failure of the preregistered
J directional prediction remains a confirmatory result, not a D0 failure.

## Provenance

- Artifact SHA-256: `ac4c71ac39da0b86214460175d993ed6ed75d87ac71230b2f4ae4c7d5b2d6c46`.
- Figure SHA-256: `e5de58f7da1a9ad907f8434818a1f145659432329f9a454961dab926496451db`.
- Figure: `results/prior_utilization_e15d/d0_v1_2/E15D_D0_EVIDENCE_GEOMETRY_V1_2.png`.
