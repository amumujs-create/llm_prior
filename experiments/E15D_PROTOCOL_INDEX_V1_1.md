# E15-D v1.1 protocol index

## Scientific role

E15-D is the E15 capstone: a held-out, prospective test of the
dimension-alignment principle derived retrospectively in E15-A/B/C.

> When different uncertainty dimensions are identified at different rates,
> reducing only the identified dimension is predicted to outperform all-or-none
> uncertainty reduction.

## Frozen components

| Component | Frozen contract |
| --- | --- |
| Prior family | \(f(x)=a+bx+\kappa x^2+\lambda x^6\), \(x\in[0,1]\) |
| Known terms | \(a=0,b=1,R_0=1\) |
| Uncertainty anatomy | \((U_\kappa,U_\lambda)\) only |
| Evidence | vector-valued \((E_\kappa,E_\lambda)\) |
| Candidate family | one common joint \((\kappa,\lambda)\) grid and continuation family for every policy |
| Primary regime | S: \(\kappa\) evidence increased, \(\lambda\) evidence still weak |
| Secondary regimes | L: both weak; J: \(\lambda\) evidence materially increased |
| Primary D1 | `kappa_selective − joint_uniform` |
| Primary D2 | `factorized_joint_weighted − kappa_selective` |
| Dependence contrast | `joint_weighted − factorized_joint_weighted` |
| Point-collapse stress | `joint_MAP − joint_weighted` |
| S predictions | \(D1_D<0\), \(D2_D>0\) |
| J prediction | conditional on J geometry, \(D2_D^J<0\) |
| Support ladder | broad \([.10,.90]\) → medium \([.20,.80]\) → narrow \([.30,.70]\) |
| Grid ladder | \(.05\) → \(.025\), coarsest admissible |
| Noise ladder | \(.10\) → \(.05\) → \(.025\) → \(.01\), largest admissible |
| Exposure triples | \(T_1=(.25,.55,.80)\) → \(T_2=(.25,.60,.85)\) → \(T_3=(.30,.65,.90)\) |
| Far horizon | \(1.00\) → \(.95\), longest admissible |
| Continuation distinctness | normalized RMS \(.01\), at least four mutually distinguishable joint continuations |
| D0 visible information | evidence geometry, continuation distinctness, finite/numerical stability |
| D0 prohibited information | policy predictions, RMSE, CRPS, contrast means/signs/rankings/winners |

## Connection to E15-A/B/C

| Study | Uncertainty anatomy | What evidence identifies | Utilization implication |
| --- | --- | --- | --- |
| E15-A | onset location | onset realization | preserve under weak identification; concentration can help when onset evidence grows |
| E15-B | validity scope | warranty endpoint, not post-scope realization | scope retention helps; scope weighting is not predictively aligned |
| E15-C | incomplete invariant plus residual shape | residual shape | retain weakly identified residual diversity; weight only when evidence concerns residual shape |
| E15-D | two-coordinate shape specification | \(\kappa\) and \(\lambda\) at different rates | prospective test of selective dimension-wise reduction |

E15-D success or failure is retained as the capstone result. E15 is not
extended with further synthetic anatomy after D; the next stage is E16 external
validation.
