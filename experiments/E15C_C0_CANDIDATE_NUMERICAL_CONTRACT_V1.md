# E15-C0 candidate numerical contract v1

This is a calibration-only candidate contract. It fixes a mode-independent normalization and the initial outcome-free sweep ladder; it is not the confirmatory E15-C manifest.

## Public normalized domain and invariant-only reference scale

Use a public normalized domain `x in [0, 1]`, with `x=(t-t_min)/T` and `T=t_max-t_min`. The initial candidate anchors are

\[
\kappa_0=k_0T=1,\qquad y_0=1.
\]

The task-independent reference scale is derived only from the supplied invariant:

\[
R_{\rm inv}=|y_0|\left(1-e^{-\kappa_0}\right)=1-e^{-1}.
\]

It is used for both task-noise scaling and NRMSE normalization:

\[
\sigma=\rho R_{\rm inv}.
\]

No residual amplitude, residual shape, or realized clean-trajectory range may enter this denominator. `R_inv` is never supplied to a policy other than as a common normalization convention.

## Residual-amplitude geometry

Define a public amplitude scale from the invariant drift:

\[
A_{\rm ref}=k_0|y_0|.
\]

The initial C0 proposal distribution is

\[
A=s\,\eta A_{\rm ref},\qquad s\in\{-1,+1\}\ \text{balanced},\qquad \eta\sim U[0.5,1.5],
\]

with `q ~ U[0,1]`. This makes `|A|/A_ref >= 0.5` an initial residual-nondegeneracy construct gate, not an outcome gate.

## Initial candidate ladder

| Quantity | C0 candidates |
| --- | --- |
| Residual-shape grid spacing | `.025`, `.05` over `[0,1]` |
| Prefix endpoints | `x = .25, .50, .75` for low, medium, high |
| Noise ratio `rho` | `.01`, `.025`, `.05`, `.10` |
| Common far endpoint `x_far` | `.90`, `1.00` |
| Evaluation window | `(.75, x_far]` |

The public coordinate is fixed across all prefixes; the `.25/.50/.75` endpoints do not reparameterize residual shape.

## Deterministic residual profiling

For fixed `q_k`, use the invariant-plus-residual solution

\[
y(t)=y_{\rm inv}(t)+A z_{q_k}(t),\qquad
z_q(t)=\int_{t_{\min}}^t e^{-k_0(t-s)}g_q(x(s))\,ds,
\]

where `y_inv(t)=y0 exp[-k0(t-t_min)]`. With Gaussian noise, profile amplitude in closed form:

\[
\hat A(q_k)=\frac{\sum_i z_{q_k}(t_i)[y_i-y_{\rm inv}(t_i)]}
                       {\sum_i z_{q_k}(t_i)^2}.
\]

The same formula, precision, time grid, and loss convention must be used for every `q_k`; no numerical optimizer is permitted for this profile.

## Outcome-free C0 selection sequence

1. Validate `R_inv`, amplitude nondegeneracy, and finite solution geometry.
2. Select residual-grid resolution using continuation distinctness and numerical stability.
3. Select `rho` using full-domain `E_r` geometry: ordered low/medium/high medians, adjacent 5–95% overlap, and no universal endpoint saturation.
4. Select the longest admissible `x_far` using finite trajectories, common evaluation support, and continuation geometry only.

Store an effective residual-continuation count on the common far grid. The initial construct gate is median count at least four under a predeclared normalized-RMS distinctness tolerance.

Policy RMSE, CRPS, contrast values, signs, rankings, and winners are unavailable throughout C0.
