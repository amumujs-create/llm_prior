# E15-C0 v1.1 amendment — bounded nuisance-amplitude profile

## Reason for versioning

E15-C v1 was not advanced to confirmation. Its protected variance-only quota calculation returned 184,957 tasks because, under weak low-prefix support, unconstrained residual-amplitude profiling could yield highly dispersed future continuations when the residual profile-basis norm was very small. No outcome mean, sign, policy score, ranking, or winner was inspected.

This is treated as an estimator-feasibility signal, not as a scientific result about residual uncertainty.

\[
\text{scientific residual uncertainty}\neq\text{nuisance-profile blow-up}.
\]

## Sole estimator change

For every residual-shape candidate, replace the unconstrained linear profile with its projection onto the already known generator-admissible amplitude range:

\[
\hat A_{\rm LS}(q)=
\frac{\sum_i z_q(t_i)[y_i-y_{\rm inv}(t_i)]}{\sum_i z_q(t_i)^2},
\]

\[
\hat A_{\rm bounded}(q)=
\operatorname{clip}\left(\hat A_{\rm LS}(q),-1.5A_{\rm ref},+1.5A_{\rm ref}\right).
\]

No lower magnitude bound is imposed on fitted amplitude. In particular, the generator support lower magnitude, `|A|/A_ref >= .5`, is not injected into the estimator.

The matched-free branch must use the same amplitude bound when it is implemented for confirmation.

## Held fixed from v1

- exact supplied invariant and initial state;
- `Delta q=.05`, `rho=.10`, exposure endpoints `.25/.50/.75`, and `x_far=1.00`;
- public coordinate, residual family, `R_inv`, `A_ref`, task generator, standardized noise construction, and deterministic `z_q=(1-q)z_1+qz_3` response construction;
- all outcome-free C0 construct gates and protected precision target.

`E_r` is recomputed from the bounded-profile loss. C0 gates and protected variance-only quota calibration must both be rerun. Policy RMSE, C1/C2 mean, contrast sign, ranking, CRPS, and winner remain unavailable.
