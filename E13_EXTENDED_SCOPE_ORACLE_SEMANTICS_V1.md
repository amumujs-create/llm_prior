# E13 extended-scope atom oracle semantics v1

For each horizon `h`, every atom is evaluated on the common declared interval
`[.40,h]`. This extends the frozen E11 core semantics without changing atom IDs.

| Atom | `C_a(h)=1` rule |
|---|---|
| `direction_decreasing` | non-increasing derivative fraction meets the frozen E11 tolerance on `[.40,h]` |
| `curvature_convex` | non-negative curvature fraction meets the frozen E11 tolerance on `[.40,h]` |
| `lower_bound_0` | `min f(x)>=0` within frozen tolerance on `[.40,h]` |
| `inflection_concave_to_convex` | exactly one ordered concave-to-convex transition on `[.40,h]`; no extra transition is allowed |
| `turning_maximum` | exactly one increasing-to-decreasing transition on `[.40,h]`; no extra transition is allowed |
| `regime_postchange` | paired frozen latent regime metadata declares the original post-change mechanism still active through `h`, with no second switch |
| `asymptote_to_0_from_above` | paired frozen latent asymptotic mechanism still targets zero from above through `h`; realized trajectory remains positive on `[.40,h]` |

The paired latent fields are semantic oracle state, not intervention proposal or
breaker metadata. The scorer receives only the clean trajectory plus this
atom-specific frozen semantic state. Candidate scope is the atomwise AND:
`C_P(h)=product_{a in P} C_a(h)`.
