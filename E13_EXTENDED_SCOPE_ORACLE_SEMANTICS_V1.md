# E13 extended-scope atom oracle semantics v1

`P_star` membership is frozen once on the core domain `Omega_0=[.40,.80]`.
Atoms which become true only after `.80` never alter this envelope. For each
horizon `h`, every frozen envelope atom is evaluated on `[.40,h]`.

First compute raw atom validity
`V_a(h_j)=I(raw atom checker passes on [.40,h_j])`. Then define contiguous
atom validity `C_a(h_j)=product_{k<=j} V_a(h_k)`. A later raw pass can therefore
never repair an earlier scope failure. Candidate validity is
`C_P(h_j)=product_{a in P} C_a(h_j)`.

| Atom | `V_a(h)=1` raw checker rule |
|---|---|
| `direction_decreasing` | non-increasing derivative fraction meets the frozen E11 tolerance on `[.40,h]` |
| `curvature_convex` | non-negative curvature fraction meets the frozen E11 tolerance on `[.40,h]` |
| `lower_bound_0` | `min f(x)>=0` within frozen tolerance on `[.40,h]` |
| `inflection_concave_to_convex` | exactly one ordered concave-to-convex transition on `[.40,h]`; no extra transition is allowed |
| `turning_maximum` | exactly one increasing-to-decreasing transition on `[.40,h]`; no extra transition is allowed |
| `regime_postchange` | paired frozen latent regime metadata declares the original post-change mechanism still active through `h`, with no second switch |
| `asymptote_to_0_from_above` | paired frozen latent asymptotic mechanism still targets zero from above through `h`; realized trajectory remains positive on `[.40,h]` |

Generation carries paired semantic state:
`(f_base,z_base) -> (f_int,z_int)` under frozen intervention `T_phi`.
`z_int` is the post-intervention clean generative state, not a breaker label.
The scorer receives only `(f_int,z_int)` and never requested stratum, proposed
onset, intended breaker atom, or desired failure horizon. This lets regime and
asymptote use their frozen mechanistic/latent-assisted semantics after an
intervention without silently relying on proposal metadata.
