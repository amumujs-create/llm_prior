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
  `2945001efae09e24879fadbc37d6a70e46f8f125aaa2e7d01367be7400ee2fbd`
- corpus verification: passed with zero errors

The metadata corpus is immutable. Full outcome execution remains locked until
the eight registered triples pass the frozen three-generator 20/20 constructor
validation and the complete scoring runner receives a code hash.
