# MEMO-001: Architecture Assumptions and Non-Goals

**Status**  
Active / informative

**Purpose**  
This memo provides a short operational checklist for implementation work so the runtime architecture stays inside the current MVP evaluation boundary.

It inherits from:

- `docs/03_MVP Eval Intent Lock.md`
- `ARCH-001-first-runtime-architecture-outline.md`

If this memo conflicts with the normative docs in `docs/` or the schemas in `schema/`, the normative sources win.

---

## 1. Working assumption

The current architecture effort is building an **evaluation-phase runtime**, not a production mediation platform.

Implementation decisions should therefore optimize for:

- evaluator-reviewable evidence
- boundary clarity
- artifact coherence
- controlled offline execution
- correct escalation behavior

They should not optimize first for:

- scale
- final product UX
- deployment sophistication
- broad generality across future plugins

---

## 2. Architecture assumptions

Treat the following assumptions as active unless the normative spec changes.

### 2.1 Runtime shape

- the first runtime is offline and step-orchestrated
- benchmark slices such as `D-B04` are the primary implementation anchor
- `D-B04-S01` is the baseline reference run for current architecture translation

### 2.2 Authority model

- the core owns domain-general mediation process behavior
- the plugin owns domain structure, qualification, warnings, and feasibility signals
- the platform owns authoritative state, persistence policy, thresholding, and routing
- evaluator tooling consumes emitted artifacts after the run

### 2.3 Artifact model

- structured artifacts are authoritative
- summaries are derived artifacts, not independent sources of truth
- missing information must remain explicit
- escalation rationale must be preserved in emitted artifacts

### 2.4 Success model

- bounded continuation with caution can be a successful outcome
- human escalation, co-handling, or handoff can be evidence of good system behavior
- success is not defined primarily by settlement or recommendation strength

---

## 3. Non-goals for the current phase

The following are out of scope unless the repo explicitly advances phases.

- production live-session architecture
- final disputant-facing UX or frontend flows
- multi-tenant serving or deployment topology
- broad plugin-generalization beyond what the current contracts require
- highly optimized storage, throughput, or latency design
- autonomous handling of all mediation scenarios
- replacing human mediators as the default design target
- using persuasion or closure pressure as a success strategy

---

## 4. Implementation guardrails

When making architecture or code decisions, keep these guardrails fixed:

- do not let prompts become the hidden system architecture
- do not let the model own authoritative state
- do not let plugin logic silently collapse into the core
- do not let evaluator review depend on hidden internal state
- do not treat transcripts as required when structured artifacts can support evaluation
- do not introduce production-style complexity unless it solves a current evaluation-phase need

---

## 5. Checklist before approving an architecture change

Before accepting a new runtime design decision, check:

- Does it improve evaluator-reviewable artifact quality or implementation clarity?
- Does it preserve the core/plugin/platform boundary?
- Does it keep human escalation as a first-class success mode?
- Does it stay grounded in benchmark evidence such as `D-B04-S01`?
- Does it avoid implying a production commitment that the repo has not made?

If the answer to any of these is no, pause and re-check against the intent lock before proceeding.

---

## 6. Practical default

When there is uncertainty, prefer the simpler design that:

- keeps authority explicit
- preserves artifact coherence
- supports replay and evaluator inspection
- stays narrow enough to validate the MVP evaluation target

That default is more aligned with the current phase than speculative product completeness.
