# Solomon Evaluation Spec — Part III: MVP Eval Intent Lock

**Status**  
Working draft / normative for the current evaluation-phase lock.

**Purpose**  
This document locks the intended purpose of the Solomon MVP evaluation phase so the repository can move from specification into architecture without drifting away from the evaluation target.

If this document conflicts with older drafts, snapshots, or informative architecture notes, this document and Parts I-II should be treated as the active source of truth for the current phase.

---

## 1. Core purpose

The Solomon MVP evaluation phase is designed to test whether Solomon can produce evaluator-reviewable, domain-qualified mediation artifacts with appropriate escalation behavior in bounded synthetic cases.

It is not designed to validate a production-ready live mediation product.

---

## 2. What this MVP eval is designed to do

At this phase, the system is designed to:

- run bounded offline synthetic mediation sessions
- preserve a clear boundary between core mediation process behavior and domain-plugin qualification
- surface positions, facts, missing information, and flags in structured artifacts
- apply domain qualification before stronger optioning or recommendation behavior
- treat human escalation, co-handling, and handoff as valid success outcomes when indicated
- produce artifacts that let evaluators judge process quality, caution, and implementation readiness without depending on hidden internal state

---

## 3. What this MVP eval is not designed to do

At this phase, the system is not designed to:

- act as a production live mediation platform
- replace human mediators across all cases
- function as a judge, arbitrator, therapist, or legal decision-maker
- optimize primarily for settlement rate or persuasive closure
- prove multi-tenant deployment, final UX, or production infrastructure
- prove generality across many plugins beyond the initial divorce-mediation baseline

---

## 4. Primary actors

The primary actors for this phase are:

- developers implementing the first evaluation runtime
- technical architects translating the spec into runtime boundaries
- evaluators reviewing artifact quality and score coherence
- expert reviewers adjudicating difficult cases and calibration questions

The primary end user being served at this stage is the **builder/evaluator team**, not a live disputant population.

---

## 5. Required outputs

The MVP evaluation phase must produce, at minimum:

- normative specification documents
- evaluator and expert-review schemas
- benchmark slices with worked reference materials
- authoritative runtime artifact contracts
- at least one worked reference session package such as `D-B04-S01`
- architecture guidance that is narrow enough to support implementation without pretending to be final production architecture

For an executed or reference run, the minimum artifact set should include:

- `run_meta.json`
- `interaction_trace.json`
- `positions.json`
- `facts_snapshot.json`
- `flags.json`
- `missing_info.json`
- `summary.txt`

---

## 6. Evaluation success criteria

For the purposes of this MVP evaluation phase, success means the repository and first runtime can demonstrate that Solomon:

- maintains the core versus plugin boundary in practice
- produces internally coherent artifacts across trace, state, flags, and summary
- expresses missing information and caution explicitly rather than hiding uncertainty
- uses escalation and continuation modes appropriately
- supports evaluator scoring and expert review from emitted evidence
- is concrete enough that implementation can proceed without inventing the system from scratch

Success at this phase does **not** require:

- production deployment readiness
- polished end-user product flows
- broad domain coverage
- autonomous handling of all mediation scenarios

---

## 7. Architecture guardrails

As the repo moves into architecture and runtime implementation, the following guardrails should remain fixed:

- evaluation-first before production-generalization
- expert-in-the-middle rather than human-removed
- core owns process; plugin owns domain structure and qualification
- platform/runtime owns authoritative state, persistence policy, and routing
- structured artifacts are authoritative
- human escalation is a first-class success mode
- informative architecture documents must not silently override normative spec

---

## 8. Change-control note

This brief is intended to reduce drift during the transition from specification to architecture.

For the current phase, changes to this intent lock should be made only when:

- evaluation evidence shows that the current target is wrong or incomplete
- the normative specification is deliberately being revised
- the team is explicitly advancing to a new phase with different goals

Until then, architecture and implementation work should optimize for **faithfulness to this evaluation target**, not for speculative production completeness.
