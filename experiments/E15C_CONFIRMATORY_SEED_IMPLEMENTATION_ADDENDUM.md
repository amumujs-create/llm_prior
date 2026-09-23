# E15-C confirmatory seed implementation addendum

The manifest namespace `e15c-confirmatory-v1.1` is converted to proposal seeds deterministically:

\[
\operatorname{seed}(j)=\operatorname{uint64}\bigl(\operatorname{SHA256}(
\texttt{"e15c-confirmatory-v1.1:proposal:}j\texttt{"})[0:8]\bigr)\bmod 2^{63},
\]

using the first eight SHA-256 bytes interpreted big-endian. Proposal indices are evaluated in ascending order. Accepted tasks receive `task_id` in their ascending acceptance order. Each proposal independently generates `q`, amplitude magnitude/sign, and its master standardized noise from its own seed.

The runner stops after 125 accepted tasks or 133 proposals. Any numerical rejection is recorded with its proposal index and reason; no resampling, reordering, or outcome-dependent selection is allowed.

This addendum changes neither the manifest's scientific contract nor its SHA-256. It fixes only deterministic replay and task ordering.
