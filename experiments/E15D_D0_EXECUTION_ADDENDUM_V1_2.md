# E15-D0 v1.2 execution addendum

E15-D0 v1.2 inherits without change every public-grid, sum-NLL, natural-log
entropy, linear-quantile, exact continuous-RMS, clique, and RNG convention
from `E15D_D0_IMPLEMENTATION_ADDENDUM_V1_1.md`.

Its only execution change is the fresh discarded namespace
`e15d-d0-v1.2-discarded`. It uses task IDs 0–399 exactly once, with the same
first-eight-digest-byte big-endian seed derivation and the same frozen draw
order. The v1.1 namespace must never be reused.

The v1.2 runner removes only the two overlap failures named in
`E15D_D0_V1_2_OVERLAP_GATE_AMENDMENT.md`; all core median gates remain active.
It remains outcome-free and cannot calculate or persist policy predictions,
predictive losses, contrasts, ranks, signs, or winners.
