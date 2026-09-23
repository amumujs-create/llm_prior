# E15-C0 coordinate and nuisance contract v1

This contract fixes residual-coordinate and nuisance semantics before numerical calibration. It supplements, but does not modify, `E15C_SEMANTIC_CONTRACT_V1.md` or `E15C_C0_DESIGN_GUARDRAILS_V1.md`.

## Fixed public residual coordinate

Residual shape is always evaluated using one public, task-independent coordinate:

\[
x(t)=\frac{t-t_{\min}}{t_{\max}-t_{\min}}.
\]

`t_min` and `t_max` are the frozen full admissible-domain endpoints. They are not recomputed from a prefix, exposure endpoint, forecast horizon, or individual residual hypothesis. Thus the same `q` always denotes the same function

\[
g_q(x)=(1-q)x+qx^3
\]

at low, medium, and high exposure.

## Supplied initial state and profile nuisance set

For E15-C v1, `y0` is supplied and fixed alongside the exact shared `k0`. It is not estimated separately for tasks, exposures, or residual hypotheses.

For every residual candidate `q_k`, the sole profile nuisance parameter is residual amplitude `A`:

\[
\ell_k=\min_A\ \operatorname{NLL}(D_{\rm prefix}\mid q_k,A,y_0,k_0).
\]

The profile nuisance set is identical for every `q_k`, policy that uses residual evidence, and prefix exposure. No candidate-specific nuisance parameter, fit bound, solver budget, or coordinate transform is permitted.

## C0 candidate sweep constraints

The following are numerical candidates rather than confirmatory freezes:

- residual-shape grids over `q in [0, 1]` with candidate spacings `.025` and `.05`;
- low/medium/high prefix endpoints expressed in the fixed public coordinate;
- noise-ratio candidates `{.01, .025, .05, .10}`;
- several far-horizon candidates selected by the longest-admissible rule.

`k0`, the residual-amplitude sampling range, horizon, grid, noise, acceptance thresholds, and quota remain to be chosen in C0 without reading confirmatory policy outcomes.

## Construct-validity gates for C0

1. **Residual nondegeneracy.** Sampled amplitudes must satisfy a predeclared scale-free lower bound, `|A| / A_ref >= a_min`, so the residual-shape coordinate is genuinely present. This is not a policy-performance gate.
2. **Residual evidence geometry.** `E_r` is computed on the full residual-shape domain, is finite, and typically increases from low to medium to high exposure without universal 0/1 saturation.
3. **Continuation distinctness.** More than one residual hypothesis must create a distinguishable future continuation on the common forecast grid.
4. **Closed-model separation.** The uniform residual ensemble must not be prediction-equivalent to the `A=0` closed-mechanism stress condition.
5. **No coordinate leakage.** Prefix length may restrict observations only; it must never change the definition of `x`, the candidate `q` grid, or the residual hypotheses.

The C0 question is therefore fixed as follows:

> Given an exactly supplied invariant and initial state, when should uncertainty about an only partially identified residual future be retained or reduced?
