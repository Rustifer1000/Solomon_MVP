# MVP Execution Tasklist

**Status**  
Active execution checklist

**Purpose**  
This file is the working execution roadmap for getting Solomon from its current evaluation-runtime scaffold to a fully capable MVP evaluation system.

This is intentionally optimized for execution:

- short tasks
- explicit priority labels
- checkboxes
- milestone ordering
- minimal narrative

If a task is not clearly helping the MVP evaluation runtime become executable, trustworthy, or repeatable, it should not displace `Required` work.

---

## Priority labels

- `Required`
- `Very helpful`
- `Nice but not necessary`
- `Unnecessary right now`

---

## Completion rule

The MVP should be considered execution-capable when:

- at least one benchmark slice runs end to end without authored final-state shortcuts
- the minimum artifact bundle is emitted coherently
- evaluator review can rely on emitted artifacts
- the run is repeatable enough for regression comparison
- the core/plugin/platform/evaluator boundary is enforced in code, not just prose

---

## Milestone 1: Make One Slice Genuinely Executable

- [ ] `Required` Replace authored turn replay with a real core-output generation path for `D-B04`.
- [ ] `Required` Keep `normalize_core_output(...)` as the only path from raw core output into authoritative state.
- [ ] `Required` Strengthen state mutation so artifacts are fully derived from committed state, not handcrafted artifact assumptions.
- [ ] `Required` Replace fixed escalation defaults with runtime reasoning over state, plugin warnings, and unresolved information.
- [ ] `Required` Implement real divorce-plugin qualification behavior for the active slice.
- [ ] `Very helpful` Add explicit runtime configuration handling for source, policy profile, seed, process variant, and plugin config.
- [ ] `Nice but not necessary` Improve CLI ergonomics and human-readable run output.

---

## Milestone 2: Make The Artifacts Trustworthy

- [ ] `Required` Ensure `run_meta.json`, `interaction_trace.json`, `positions.json`, `facts_snapshot.json`, `flags.json`, `missing_info.json`, and `summary.txt` remain internally coherent.
- [ ] `Required` Preserve positions, facts, missing information, flags, and escalation rationale as separate artifact concerns.
- [ ] `Required` Ensure plugin qualification constrains stronger optioning and recommendation behavior.
- [ ] `Required` Ensure anti-authority posture is preserved in summary, trace, flags, and tests.
- [ ] `Very helpful` Add automated schema/contract validation to the test path.
- [ ] `Very helpful` Add artifact comparison tooling to make rerun differences easy to inspect.
- [ ] `Nice but not necessary` Add richer reviewer-facing summaries beyond the minimum bundle.

---

## Milestone 3: Make The Run Repeatable

- [ ] `Required` Keep end-to-end tests passing for the active runtime path.
- [ ] `Required` Add regression expectations for at least one benchmark slice.
- [ ] `Required` Record enough metadata to explain run source, process variant, and runtime conditions.
- [ ] `Very helpful` Expand multi-source execution coverage (`reference`, `mock_model`, `varied_mock_model`) for comparison against the same runtime loop.
- [ ] `Very helpful` Add failure-attribution hooks for core, plugin, platform, and integration failures.
- [ ] `Nice but not necessary` Add more benign process and phrasing variation once artifact stability is established.

---

## Milestone 4: Prove The Architecture Is Reusable

- [ ] `Required` Add a second benchmark slice that runs through the same architecture with minimal special-casing.
- [ ] `Required` Show that the runtime can support another slice without collapsing the core/plugin boundary.
- [ ] `Very helpful` Add slice-level fixtures and regression baselines for both the first and second benchmark.
- [ ] `Very helpful` Add explicit evaluator-side checks that artifact-only review remains viable.
- [ ] `Nice but not necessary` Add broader plugin abstractions after the second slice is stable.

---

## Current guardrails

- `Required` work should usually outrank all other work.
- `Very helpful` work is appropriate when it directly reduces risk to `Required` execution.
- `Nice but not necessary` work should not block the MVP path.
- `Unnecessary right now` work should be recorded elsewhere and intentionally deferred.

---

## Unnecessary right now

- [ ] `Unnecessary right now` Production deployment architecture
- [ ] `Unnecessary right now` Multi-tenant infrastructure
- [ ] `Unnecessary right now` Final user-facing product polish
- [ ] `Unnecessary right now` Live-session production workflows
- [ ] `Unnecessary right now` Broad multi-domain generalization
- [ ] `Unnecessary right now` Advanced model-routing complexity
- [ ] `Unnecessary right now` Large observability/telemetry stacks
- [ ] `Unnecessary right now` Voice or emotion-signal integration for the current MVP baseline
- [ ] `Unnecessary right now` Settlement-rate optimization or persuasive-closure tuning

---

## Working rule

When choosing the next task:

1. pick the highest-leverage unchecked `Required` item
2. prefer changes that strengthen executable truth over document polish
3. prefer changes that preserve Level 1 alignment
4. avoid widening scope before the current slice is trustworthy
