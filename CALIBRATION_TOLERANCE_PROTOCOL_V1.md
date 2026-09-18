# Frozen protocol — E5b Calibration Tolerance Curve v1

**Status:** frozen before execution.  
**Scope:** short E5 extension; it does not introduce a new concept.

Correct family is fixed. Noise is `.015`, observability is low/mid/high, and
there are 50 independent draws/cell. The narrow interval is E5's fixed width:
onset ±`.03`; other fields ±5% of truth. Bias grid is normalized parameter-range
error `b_norm = [0,.025,.05,.075,.10,.15,.20,.30,.40]`, always in the positive
direction and clipped to model bounds. Broad-correct uses E5's ±`.20` onset or
±30% non-onset constraints.

Fields: regime `{onset, scale, onset+scale}`, curvature `{scale, shape,
scale+shape}`, bound `{lower bound}`. Primary outcome is D3 difference
`U(narrow biased,b) - U(broad correct)`; report the first grid point that is
negative only descriptively, not as a continuous threshold estimate. Also
report `P(U<0|b)`. No bias grid changes after results.
