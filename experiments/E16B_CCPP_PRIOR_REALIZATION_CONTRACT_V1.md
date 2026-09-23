# E16-B CCPP Prior-Realization Contract v1

## Status and amendment scope

**FROZEN before validation or confirmatory target outcomes are opened.** This
contract instantiates the residual specification uncertainty under the frozen
primary packet, \(\partial PE/\partial AT\le0\). It amends only policy
semantics and estimands in `E16B_CCPP_SEMANTIC_CONTRACT_V1.md`; it does not
change source, AT split, compound-shift classification, or the supplied sign.

## Frozen coordinates and target boundary

With the frozen train boundary \(AT_0=24.79\) deg C and guard-band endpoint
\(AT_G=29.24\) deg C,

\[
u=\frac{AT-AT_0}{AT_G-AT_0}=\frac{AT-24.79}{4.45}.
\]

Train rows have \(u\le0\), validation rows have \(0<u\lesssim0.71\), the
guard endpoint is \(u=1\), and confirmatory rows have \(u>1\). For
\(j\in\{V,AP,RH\}\),

\[
z_j=\frac{x_j-\operatorname{median}_{\rm train,j}}
{\operatorname{IQR}_{\rm train,j}}.
\]

Train-only robust statistics are reused unchanged in all later partitions.
Neither coordinate requires target values.

## Prior-realization family

Each specification is \(h=(s,c,\gamma_V,\gamma_{AP},\gamma_{RH})\), with

\[
T_h(u,z)=su+cu^2+u\gamma^\top z,\qquad f_h(u,z)=B_\eta(z)+T_h(u,z).
\]

\(s\), \(c\), and \(\gamma\) respectively specify boundary slope,
curvature, and conditional AT sensitivity. \(B_\eta\) is a common
background/nuisance family whose basis, capacity, fitting rule, target scale,
and regularization remain for the capacity contract. Every candidate uses the
same rule.

Candidate ranges, spacing, count, target scale, and deterministic tie rule
are deferred to a subsequent **outcome-free** numerical-design stage. It may
use frozen X-only geometry, coordinate scales, numerical stability,
monotonicity feasibility, and continuation distinctness. It must not use
validation or confirmatory target values to select the grid.

## Admissibility over the empirical operating scope

\[
D_h(u,z)=\frac{\partial f_h}{\partial u}=s+2cu+\gamma^\top z.
\]

Since \(AT_G-AT_0>0\), the sign of the AT derivative equals the sign of
\(D_h\). A proposed \(h\) is in the common candidate set \(\mathcal H\) only
if

\[
D_h(u_{\min},z_i)\le0\quad\text{and}\quad D_h(u_{\max},z_i)\le0
\]

for every canonical Sheet1 \((V,AP,RH)\) row and observed canonical AT
endpoints \(u_{\min},u_{\max}\). These endpoint checks suffice because
\(D_h\) is linear in \(u\). The check is X-only feasibility, not a fitted
monotonicity test.

## Exact common-candidate aggregation block

Once \(\mathcal H=\{h_1,\ldots,h_K\}\) is frozen, the following policies
must share exactly the same candidate predictions, nuisance rule, train data,
preprocessing, and validation likelihood. They differ only by aggregation.

| Policy | Definition |
|---|---|
| `specification_MAP` | \(h_{MAP}=\arg\min_h\ell_h^{val}\); predicts \(f_{h_{MAP}}\). |
| `specification_uniform_ensemble` | \(\hat f_U=K^{-1}\sum_hf_h\). |
| `specification_weighted_mixture` | \(w_h=\exp[-(\ell_h^{val}-\ell_{min}^{val})]/\sum_r\exp[-(\ell_r^{val}-\ell_{min}^{val})]\), \(\hat f_W=\sum_hw_hf_h\). |

## Data roles

| Partition | Permitted use |
|---|---|
| Train, \(AT\le24.79\) | Fit each candidate's common nuisance/background rule. |
| Validation, \(24.79<AT\le27.96\) | Score frozen candidates; determine MAP and weights. |
| Guard, \(27.96<AT\le29.24\) | Never used for fitting, tuning, scoring, weighting, or calibration. |
| Confirmatory, \(AT>29.24\) | Sealed until every prediction is fixed; final scoring only. |

Validation is never merged into training. Guard and confirmatory targets may
not influence candidate-grid design, capacity, regularization, likelihood
scale, policy definition, or error scale.

## Constraint-policy block

`free_baseline`, `hard_sign_constraint`, and `soft_sign_constraint` form a
separate incremental-value block. They must share one design matrix/basis,
parameter count, target transform, and regularization. They differ only in
whether the AT derivative is unrestricted, directly constrained non-positive,
or penalized when positive. Hard sign enforcement is not `specification_MAP`:
hard constraint applies a structure, whereas MAP collapses valid futures.

## Prospective estimands and boundary

\[
B_1=Error_{specification\ uniform}-Error_{specification\ MAP},\qquad B_1<0
\]

is primary: it tests retained valid continuation diversity against point
collapse of the exact same candidate set. The secondary, non-directional
weighting contrast is

\[
B_2=Error_{weighted}-Error_{uniform}.
\]

Because validation scores the same \((s,c,\gamma)\) dimension it weights,
the evidence target is structurally aligned; no favourable B2 sign is
preregistered. The setting is frozen as **high-AT extrapolation under compound
covariate shift**. Thus failure to beat `free_baseline` does not alone
invalidate the conditional AT prior, and success does not establish resolution
of the full \((V,AP,RH)\) shift.

## Next authorized steps

1. Target-free split replay integrity audit.
2. Outcome-free candidate numerical-design contract.
3. Capacity contract before validation targets are opened.
