## Post-Third-Slice Divorce Architecture Review

### Findings

#### P1. Benchmark policy is still too implicit at the shared runtime boundary
The runtime is now plugin-neutral, but benchmark-to-plugin shaping is still mostly inferred from `case_id`, `case_metadata`, and current state rather than being declared through a clearer benchmark-facing policy contract.

Why this matters:
- It makes slice behavior harder to reason about from the outside.
- It encourages more hidden convention as additional divorce slices are added.
- It weakens the architectural separation between shared runtime, shared plugin logic, and slice-owned policy.

Primary locations:
- `runtime/benchmarks/base.py`
- `runtime/orchestrator.py`
- `runtime/plugins/divorce_policy.py`

#### P1. Divorce policy is still centralized around case-id branching
The divorce plugin split was the right move, but `runtime/plugins/divorce_policy.py` still uses a central `_default_policy(case_id)` switch. That is cleaner than before, but it does not yet scale elegantly as more divorce slices are added.

Why this matters:
- A fourth and fifth slice will keep growing one central policy table.
- It keeps slice-specific behavior in one shared file instead of letting slices declare their own policy descriptors.
- It makes the shared divorce plugin look more general than it really is.

Primary location:
- `runtime/plugins/divorce_policy.py`

#### P2. Artifact narration is slice-neutral, but not yet explicitly policy-aware
`runtime/artifacts.py` is much healthier than it was earlier, but it still derives all narrative posture from state alone. That works for the current three slices, but there is not yet a clean way for a slice to lightly shape evaluator-facing narration without leaking back into shared logic.

Why this matters:
- It is the next likely drift point once more divorce slices are added.
- Without a light narrative-policy seam, slice nuance may start reappearing as shared-state or shared-artifact conditionals.

Primary location:
- `runtime/artifacts.py`

#### P2. Benchmark creation is still repetitive enough to invite drift
The repo now has checklists, which helps, but adding a new slice still requires creating and wiring multiple files manually. The pattern is understandable, but not yet compact.

Why this matters:
- Manual repetition is now one of the main sources of future drift risk.
- The architecture is mature enough that a benchmark skeleton would pay for itself.

Primary locations:
- `runtime/benchmarks/d_b04_*`
- `runtime/benchmarks/d_b05_*`
- `runtime/benchmarks/d_b06_*`
- `runtime/benchmarks/__init__.py`

#### P3. The shared divorce layer is holding up, but still reveals its logistics-first ancestry
The plugin works across three slices, including a communication-centered one, which is a meaningful success. But `runtime/plugins/divorce_shared.py` still treats logistics-related uncertainty as the most richly modeled signal family.

Why this matters:
- It is not a correctness bug right now.
- It is the main conceptual place to watch as the divorce path broadens further.

Primary location:
- `runtime/plugins/divorce_shared.py`

### What Is Healthy Here

- The benchmark seam is real across three distinct divorce slices.
- Plugin neutrality is now embodied in code, not just design intent.
- Shared runtime, state, and artifact layers are much cleaner than they were before the second and third slices.
- The divorce plugin split into shared analysis plus policy overlay was the right intermediate architecture.
- The test suite is now broad enough to make slice-growth safer than it was earlier in the project.

### Readiness Judgment

The divorce path is now a credible multi-slice executable evaluation system rather than a disciplined single-slice scaffold. The next bottleneck is not emergency correctness cleanup. It is making divorce-slice growth more declarative, less centralized, and less repetitive so that breadth within the divorce domain does not gradually reintroduce hidden coupling.

### Recommended Next Moves

1. Add an explicit benchmark-owned divorce policy descriptor so slices stop depending on central `case_id` branching in `runtime/plugins/divorce_policy.py`.
2. Let simulations expose small narrative-policy hints so evaluator-facing artifacts stay slice-aware without pushing logic back into shared artifact conditionals.
3. Add a benchmark scaffold/template utility to reduce repetitive file and registry work.
4. Then add a fourth divorce slice that stresses a still-underrepresented issue cluster.
