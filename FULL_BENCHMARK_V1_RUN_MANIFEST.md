# Full Benchmark v1 — Run Manifest

**State:** implementation lock in progress; no full-v1 outcomes have been read.

## Protocol lock

- design: `95f5778768e63389e4d53a5e317399fe9e2102a328633590c38d570a18169c0c`
- operational freeze: `6857db11eb64aa6fbc891bff7afb0c343d170fb4a36bdb0b413266b7f5f1fd85`
- v1.1 sanity protocol: `6523030978ea81097960cd47b85f9d672e0bb5e86140b2c920ab24e71723a66e`
- sanity-qualified base commit: `e6cf2351370b01907c30c4da0516eba4a179dcbc`

The three document hashes jointly define the protocol. The full runner's code
hash, registered composition list, corpus manifest hash, and execution command
must be added before the first full-v1 result is inspected. A missing code hash
means the run is not authorized for interpretation.

## Required execution artifacts

1. immutable 3,375-task corpus manifest;
2. exact 7 singleton, 12 pair, and 8 triple registration;
3. two realization-engine outputs and solver diagnostics;
4. task-level candidate profile data;
5. macro and task-weighted summaries;
6. primitive anatomy, composition `DeltaS–DeltaU`, hurdle map, knowledge,
   generator, and null/abstention figures;
7. code hash and output checksum inventory.

## Corpus lock

- task count: `3375` (`2700` non-null + `338` structural null + `337`
  informational null)
- generator allocation: `1125` spline + `1125` basis + `1125` ODE
- task manifest SHA-256:
  `aa3277be46517340bff84cd35db242e6edccce44905fed8f9ec495c19a6aa625`
- composition registry SHA-256:
  `bccb6d545c32168ac114bc6c2659bcdc76e563d7e18830ed6e27ed33380e687d`
- corpus verification: passed with zero errors
- triple constructor validation: all 8 compositions passed 20/20 under spline,
  basis, and ODE constructors (`480/480` required validations)

The metadata corpus is immutable. Full outcome execution remains locked until
the complete scoring runner receives a code hash.

## Code lock

- core engines/generators:
  `acbe082c3c115e065bd0ae2088d1a9d7629c99041fac68ff5b3de860c19f9e5e`
- full scoring runner:
  `8ca8cc80fc615e9102eef228dd362321bf0f91f9b669bcb51d7867ccfb5f3b79`
- structural-null dependency:
  `2d09cb8512773666d3dac7a9557a2e8dfe1388b723f65462dbace60d12da9017`
- corpus builder:
  `cadfbfa8f03f5e9b476c67d9a3692c6b1a929e77ec3851ba3bc24dd9da7e4c78`
- smoke verification: 30 tasks, 360 candidate-engine records, all finite,
  exactly 12 records/task, zero solver failures

Frozen execution command:

```bash
PYTHONPATH=experiments VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
MPLCONFIGDIR=/private/tmp/mpl-prior-full-v1 \
python3 experiments/run_full_benchmark_v1.py
```

No full-v1 outcomes were generated or inspected before these hashes were
recorded.
