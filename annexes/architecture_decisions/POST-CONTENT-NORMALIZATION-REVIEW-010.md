## Post-Content-Normalization Review 010

### Findings

#### P1. `D-B04` is now explicitly the one bespoke anchor slice, but that decision is still encoded mainly by pattern rather than by dedicated metadata
The repo now effectively treats `D-B04` as the deep runtime-stress slice while the newer package-oriented slices use the content-helper pattern. That is a healthy architecture, but the distinction is still mostly visible through code shape rather than through an explicit benchmark-level marker.

Primary locations:
- `runtime/benchmarks/d_b04_runtime.py`
- `runtime/benchmarks/d_b04_simulation.py`

Why it matters:
- The decision is clearer than before, but still somewhat implicit in the benchmark layer.
- A future maintainer could still “normalize” `D-B04` by mistake without realizing it is meant to remain special.

#### P1. Shared package reasoning still depends on string markers, even though it is now central to cross-slice behavior
The package representation question is now the biggest remaining modeling issue. `runtime/plugins/divorce_shared.py` correctly identifies package families, but it does so by scanning string markers in `state["options"]`.

Primary locations:
- `runtime/plugins/divorce_shared.py`
- `runtime/state.py`

Why it matters:
- Package reasoning now affects plugin confidence, warnings, and summary detail across multiple slices.
- That makes string-based representation the clearest remaining semantics fragility in the divorce path.

#### P2. The content-helper pattern is useful, but still narrow
`runtime/benchmarks/content_helpers.py` now meaningfully reduces duplication, but it only supports direct reuse of reference raw turns. It does not yet support “reference content plus small runtime overlays,” which is likely the next useful maintainability step.

Primary location:
- `runtime/benchmarks/content_helpers.py`

#### P2. Summary selectivity remains a deliberate design choice
The summary layer now carries more package identity, which is good. At this point the remaining question is no longer whether it is too lossy by accident, but whether you want it to remain intentionally selective or become one step richer.

Primary location:
- `runtime/artifacts.py`

### What Is Healthy Here

- The divorce path has a clear split between one deep anchor slice and several cleaner patterned slices.
- The content-helper pattern is already paying off.
- Shared divorce logic is now doing enough cross-slice work that the next issues are mostly representation choices, not missing domain depth.

### Readiness Judgment

The divorce runtime is now in a mature enough state that the next best work is representational cleanup, not structural rescue. The highest-value remaining move is to make shared package meaning more explicit and less string-fragile.

### Recommended Next Moves

1. Add an explicit benchmark marker or memo-level contract that `D-B04` is the anchor bespoke slice.
2. Introduce a lightweight structured package representation.
3. Add tests that lock in that package representation across at least `D-B05`, `D-B06`, and `D-B07`.
4. Only then decide whether the summary should become one step richer.
