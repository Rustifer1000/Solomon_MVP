## Post-Fourth-Slice Divorce Review

### Findings

#### P1. The shared divorce plugin still models logistics deeply and other issue clusters lightly
The divorce path now spans four issue clusters, but the shared plugin still has one richly modeled family: logistics/schedule feasibility. `runtime/plugins/divorce_shared.py` has explicit logistics issue sets, logistics keywords, and logistics-specific uncertainty handling, while the newer issue clusters mostly pass through as generic issue labels plus option posture.

Why this matters:
- The architecture now looks broader than the shared domain logic really is.
- New non-logistics divorce slices will tend to validate the runtime more than they validate the plugin's substantive mediation logic.
- This is now the biggest remaining mismatch between slice breadth and domain-depth.

Primary location:
- `runtime/plugins/divorce_shared.py`

#### P1. Artifact summaries are still too lossy for the richer multi-slice state model
`D-B07` exposed that a slice can carry a meaningful bounded package in state, while the summary still only surfaces two accepted facts and a generic bounded-package sentence. The artifact layer is healthy enough for coherence, but not yet rich enough to reliably preserve the most important distinguishing details of later slices.

Why this matters:
- Evaluators can miss what actually made a slice distinct.
- Different workable packages can collapse into the same generic narrative shape.
- The current summary layer may start hiding useful differences as slice count grows.

Primary location:
- `runtime/artifacts.py`

#### P2. Divorce policy is now benchmark-owned, but still duplicated between benchmark config and authored/runtime content
The new policy and narrative seams are real improvements, but slice meaning is still declared in multiple places: case metadata, simulation descriptors, authored turns, and runtime turns. That duplication is manageable now, but it is the next likely maintenance burden as more slices are added.

Why this matters:
- The same slice posture is now represented in several files.
- Future drift is more likely to come from “almost matching” slice definitions than from shared runtime bugs.

Primary locations:
- `runtime/benchmarks/d_b04_*`
- `runtime/benchmarks/d_b05_*`
- `runtime/benchmarks/d_b06_*`
- `runtime/benchmarks/d_b07_*`

#### P2. The benchmark scaffold reduced plumbing well, but authored/runtime slice content is still mostly hand-paired
The new scaffold solved the simulation boilerplate problem. The next repetition hotspot is now the parallel authored/runtime turn content per slice. This is not urgent, but it is the next place where repetitive drift will accumulate.

Why this matters:
- It increases maintenance cost per new slice.
- Small slice edits often need to be mirrored twice.

Primary locations:
- `runtime/benchmarks/*_authored.py`
- `runtime/benchmarks/*_runtime.py`

#### P3. Shared divorce qualification metadata is still schedule/logistics-biased
`qualify_case_shared(...)` still advertises feasibility constraints and caution notes primarily in schedule/logistics terms. That did not break the newer slices, but it does mean the top-level divorce-plugin framing still reads narrower than the actual four-slice divorce coverage.

Primary location:
- `runtime/plugins/divorce_shared.py`

### What Is Healthy Here

- Four distinct divorce slices now run through the same plugin-neutral runtime.
- Benchmark-owned plugin policy and artifact narrative seams are real and working.
- The benchmark scaffold meaningfully reduced simulation and registry boilerplate.
- The shared runtime, state, and artifact chain is stable enough that new slices are now exposing domain-model limitations rather than basic architecture fragility.

### Readiness Judgment

The divorce path is now a strong executable evaluation system for one domain family. The next bottleneck is no longer architecture wiring. It is domain-shape depth: making the shared divorce plugin and evaluator-facing artifacts do more justice to the broader set of divorce issue clusters the runtime can now execute.

### Recommended Next Moves

1. Expand the shared divorce plugin beyond logistics-first depth.
2. Improve artifact summaries so bounded package details survive more clearly across slices.
3. Reduce duplication between authored and runtime slice content where it is safe to do so.
4. Then add a fifth divorce slice only after those two higher-value depth improvements land.
