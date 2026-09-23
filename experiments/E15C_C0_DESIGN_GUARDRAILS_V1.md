# E15-C0 design guardrails v1 — exact invariant, residual-shape uncertainty

This addendum preserves the frozen E15-C semantic contract and fixes the separation required for numerical calibration. It does not freeze numerical ranges, grids, noise, exposure endpoints, or quota.

## Exact supplied invariant

The shared backbone is supplied exactly in E15-C v1. For the candidate family,

\[
\dot y(t)=-k_0 y(t)+r(t),
\]

`k0` is fixed and shared by the task generator and every invariant-using policy. It is **not** re-estimated task by task, optimized as a nuisance parameter, or treated as a confirmatory uncertainty factor.

Consequently, `E_inv` is a construct audit that the correct backbone is supplied and shared, not a manipulated evidence axis. C1/C2 must isolate residual-realization uncertainty only.

## Residual family: neither event nor scope

The residual must be present from the start and must not introduce an onset event, a validity endpoint, or a finite-scope transition. The E15-C0 candidate family is

\[
r(t)=A\,g_q(x),\qquad
g_q(x)=(1-q)x+q x^3,\qquad q\in[0,1],
\]

where `x` is normalized time, `A` is a task-specific nuisance residual amplitude, and `q` is a residual-shape coordinate.

For a frozen candidate `q_k`, the residual profile loss is

\[
\ell_k=\min_A\ \operatorname{NLL}(D_{\rm prefix}\mid q_k,A,G_{\rm inv}),
\]

and the evidence-weighted residual distribution is constructed only from these shared prefix losses:

\[
w_k\propto\exp[-(\ell_k-\ell_{\min})],\qquad
E_r=1-\frac{H(w)}{\log K}.
\]

The future distinction among residual hypotheses must grow smoothly with exposure; no abrupt event or scope boundary may be used to create identifiability.

## Frozen policy interpretation

- `invariant_residual_MAP` selects a single `q_k` from the common residual grid.
- `invariant_residual_ensemble` retains the same grid with uniform weights.
- `evidence_weighted_residual_mixture` retains the same grid with weights derived from the common profile losses.
- `closed_mechanism` fixes `A=0`; it is an incompleteness stress condition.
- `free_baseline` does not impose the `-k0 y` backbone.

## Matched free-backbone comparison

The secondary backbone comparison must preserve residual capacity. A candidate matched-free family is

\[
\dot y(t)=c\,y(t)+A\,g_q(x),
\]

where `c` is fitted from the prefix, while the invariant branch fixes `c=-k0`. It tests backbone sharing rather than a difference in residual family or numerical capacity.

## E15-C0 outcome-free gates

Numerical calibration may inspect only the following:

1. `E_r` increases across low/medium/high exposure without universal 0/1 saturation.
2. Candidate residual shapes generate meaningfully distinct forecast continuations.
3. The uniform residual ensemble is not prediction-equivalent to the closed-mechanism stress policy.
4. Invariant and matched-free branches have equivalent residual capacity and deterministic solver budgets.
5. All policies use prefix data only; true residual shape and future labels are inaccessible before scoring.

Policy RMSE, CRPS, contrast means, signs, rankings, and winners remain unavailable during E15-C0.
