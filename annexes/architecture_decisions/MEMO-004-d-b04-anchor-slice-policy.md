## Memo 004: `D-B04` Anchor Slice Policy

`D-B04` is the deliberately bespoke anchor slice for the current divorce-eval runtime.

Why this is intentional:
- it is the deepest runtime-generated divorce slice in the repo
- it pressures logistics caution, bounded optioning, and unresolved-feasibility handling more than the patterned package slices
- it gives the benchmark layer one explicit stress-test slice rather than flattening every benchmark into the same authored/runtime pattern

Policy implication:
- `D-B04` should remain discoverably special in benchmark metadata and run artifacts
- newer package-oriented slices should continue to prefer the scaffolded helper pattern unless there is a clear reason not to
- future cleanup should not “normalize” `D-B04` accidentally just because the other slices are more declarative

Current implementation marker:
- benchmark descriptor id: `d_b04_bespoke_anchor`
