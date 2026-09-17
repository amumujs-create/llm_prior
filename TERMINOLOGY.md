# Terminology: prior truth, structural family, and full information

## Required terminology

| Term | Information supplied to the method | What remains unknown | Expected behavior |
|---|---|---|---|
| **World-truth prior** | Nothing; this is a property of the data-generating process | Family and all parameters | Not an executable method input |
| **Generative-family oracle** | The correct structural family, e.g. `regime_change` | Change time, rates, exponents, bound, and all other parameters | May harm when prefix evidence cannot identify consequential parameters |
| **Full-information oracle** | Correct family **and** actual parameter values | Nothing relevant to the generated tail | Must be at least as good as the generative-family oracle; admission should never reject it |
| **Contrast prior** | A deliberately different family | Its parameters are fit from prefix | Negative control for misspecification |
| **Fallback** | No structural family | — | Linear least-squares extrapolation |

## Core distinction

The experiments evaluate a **generative-family oracle**, not a full-information
oracle. A matching family label says that the structural class is correct, but
does not identify where a transition occurs, how fast curvature grows, or where
a bound lies. Multiple parameter settings can be indistinguishable on the
observed support and diverge outside it.

Therefore:

```text
world-truth family ≠ parameter identifiability from the prefix
generative-family oracle < fallback is possible
full-information oracle ≥ generative-family oracle
```

Admission asks neither “is this family true in the world?” nor “is it a
full-information oracle?” It asks: **given only the currently observed support,
is applying this fitted structural prior expected to have positive utility?**

## Presentation language

Use:

- “generative-family oracle” or “matching-family structural prior” for the
  evaluated matched-family baseline;
- “full-information oracle (not evaluated in v1/v2)” for the parameter-known
  upper bound;
- “admission rejects a *currently unidentifiable matching-family prior*,” not
  “admission rejects the oracle.”

Avoid “oracle prior” without a qualifier.

## Legacy artifact compatibility

Frozen v1 data and code use historical keys such as `oracle_utility` and
`oracle_gate_uniform`. They mean:

| Frozen key | Correct reading |
|---|---|
| `oracle_utility` | utility of the **generative-family oracle** |
| `oracle_gate_uniform` | uniform gate applied to a **generative-family oracle** |
| `oracle_gate_tail` | tail-weighted gate applied to a **generative-family oracle** |

These keys are not renamed because altering frozen artifacts would invalidate
their recorded hashes. All new prose and future artifacts follow this document.
