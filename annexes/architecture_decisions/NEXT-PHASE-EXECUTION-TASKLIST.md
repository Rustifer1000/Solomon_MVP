# Next-Phase Execution Tasklist

Use this tasklist after the first remediation pass. It is optimized for execution, not explanation.

## Working Rule

Prefer the highest-leverage unchecked `Required` item. Do not widen scope until the current item is implemented and covered by tests.

## Milestone 1: Make Runtime Structure Benchmark-Owned

- [ ] `Required` Move session-plan ownership into the benchmark layer so the generic orchestrator does not hardcode one eight-turn alternating structure.
- [ ] `Required` Define a benchmark-provided turn/session plan contract that covers turn order, role, and timestamps or timestamp generation.
- [ ] `Very helpful` Add session-level validation for turn ordering, monotonic timestamps, and legal phase progression.

Done when:
- [ ] `runtime/orchestrator.py` no longer hardcodes `1..8`, assistant/client slots, or per-turn timestamps.
- [ ] `D-B04` supplies its own session structure through the benchmark layer.
- [ ] Tests cover invalid session plans and valid runtime execution through the new plan.

## Milestone 2: Decompose D-B04 Simulation Logic

- [ ] `Required` Split `runtime/benchmarks/d_b04.py` into smaller modules with clear ownership.
- [ ] `Required` Separate authored reference/mock turn sources from runtime-generated turn logic.
- [ ] `Required` Keep simulation registration thin and declarative.
- [ ] `Very helpful` Add a short benchmark README or module docstring describing the split.

Done when:
- [ ] No single `D-B04` benchmark file is carrying all authored turns, generation logic, and registration.
- [ ] A new benchmark slice could be added by copying a small, legible pattern rather than a giant mixed file.

## Milestone 3: Reduce String-Heuristic Authority in State

- [ ] `Required` Push more explicit normalized structure into turn deltas so the state layer does less inference from prose.
- [ ] `Required` Identify the most brittle inference points in `runtime/state.py` and replace them with structured fields first.
- [ ] `Required` Add tests proving phrasing variation does not silently change authoritative issue, fact, or participant interpretation.
- [ ] `Very helpful` Introduce helper types or explicit enums for issue ids, fact status, and participant ids.

Done when:
- [ ] State no longer depends primarily on string matching for core interpretation.
- [ ] Phrasing variation tests pass without changing authoritative state semantics.

## Milestone 4: Make Plugin and Escalation Logic More State-Aware

- [ ] `Required` Expand plugin assessment beyond unresolved-question counts.
- [ ] `Required` Make escalation consider a fuller state picture: issue map, option state, flags, and plugin posture.
- [ ] `Very helpful` Encode a few benchmark-specific escalation examples as tests.
- [ ] `Nice but not necessary` Add richer plugin rationale fields for evaluator review.

Done when:
- [ ] Plugin confidence and escalation mode are not driven mainly by counts alone.
- [ ] Tests show the same unresolved-count total can still yield different assessment when the rest of state differs.

## Milestone 5: Add a Second Minimal Benchmark Slice

- [ ] `Required` Add a second narrow benchmark simulation to pressure-test the runtime seam.
- [ ] `Required` Reuse the same orchestrator, normalization, state, plugin, escalation, and artifact path without benchmark-specific hacks in generic layers.
- [ ] `Very helpful` Keep the second slice intentionally small and structurally different from `D-B04`.

Done when:
- [ ] Two benchmark slices run through the same generic runtime path.
- [ ] Adding the second slice does not require re-hardcoding the orchestrator or loader.

## Milestone 6: Clarify Evaluator-Facing Summary Trust

- [ ] `Required` Decide whether `summary.txt` is intended to be selective or near-complete.
- [ ] `Required` If selective, label it clearly in implementation/docs and keep invariant tests aligned with that choice.
- [ ] `Very helpful` If near-complete, widen the state coverage included in summary generation.

Done when:
- [ ] The summary’s trust contract is explicit.
- [ ] Tests reflect the intended role of the summary instead of assuming more completeness than it provides.

## Not The Priority Right Now

- [ ] `Unnecessary right now` Production deployment architecture
- [ ] `Unnecessary right now` Rich evaluator UI
- [ ] `Unnecessary right now` Broad domain/plugin generalization before the second slice exists
- [ ] `Unnecessary right now` More output style variation before the runtime seam is stronger

