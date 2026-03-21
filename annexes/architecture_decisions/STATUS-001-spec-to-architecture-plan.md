# STATUS-001: Spec-to-Architecture Plan

**Status**  
Active / informative

**Purpose**  
This document tracks Solomon’s progress from evaluation-phase specification toward concrete runtime architecture.

It is the working coordination document for:
- open architecture-shaping decisions
- readiness gaps
- active work items
- completed work items
- blockers
- next milestone

This file does **not** supersede the normative specification.  
If there is any conflict between this file and the normative documents in `docs/` or the JSON schemas, the normative documents win.

For the current phase, `docs/03_MVP Eval Intent Lock.md` should be treated as the short purpose lock for interpreting this status file and the active architecture work.

---

## 1. Current phase

**Current phase:** Pre-architecture preparation

**Objective of this phase:**  
Reach the point where Solomon can be translated from specification into a first concrete runtime architecture without hiding unresolved design decisions inside the model.

**Readiness principle:**  
Proceed when the team can run and evaluate at least one offline divorce-mediation case end-to-end, explain why the system continued or escalated, and attribute failures to the model, core platform, plugin layer, or integration boundary.

---

## 2. Companion documents

This status file should be used together with:

- `ADR-001-model-core-plugin-evaluator-boundary.md`
- `READINESS-001-pre-architecture-checklist.md`

Companion documents also now include:
- `SPEC-TO-ARCH-INPUTS.md`
- `benchmark_to_capability_matrix.md`
- `escalation_authority_matrix.md`
- `CONTRACT-001-runtime-artifacts-v0.md`
- `CONTRACT-002-plugin-interface-v0.md`
- `CONTRACT-003-flags-positions-facts-missing-summary-v0.md`
- `CONTRACT-004-continuity-packet-v0.md`
- `competency_to_artifact_matrix.md`

---

## 3. Current overall status snapshot

### Phase status
- [x] Core conceptual basis stable enough for architecture translation
- [x] Core/plugin boundary stable enough for architecture translation
- [x] Evaluation design stable enough for architecture translation
- [x] Scoring and escalation framework stable enough for architecture translation
- [x] Artifact contracts stable enough for architecture translation
- [ ] Reproducibility / persistence rules stable enough for architecture translation
- [x] One end-to-end benchmark run can be evaluated and explained

### Overall assessment
**Current assessment:** Ready to begin a first runtime architecture draft, with reproducibility and persistence still needing final tightening  
**Reason:** The specification, contracts, and first reference-run slice are now coherent enough to support architecture translation without major guessing.

---

## 4. Open architecture-shaping decisions

These are the highest-priority unresolved questions that could materially affect the runtime architecture.

### D-001. Core competency operationalization
**Question:**  
How will each core competency family be translated into observable runtime behaviors and evaluable outputs?

**Why it matters:**  
The architecture cannot be designed cleanly until the system knows what it must emit, preserve, and justify.

**Target output:**  
A competency-to-artifact mapping table.

**Status:** Open

---

### D-002. Core vs plugin interface
**Question:**  
What exact inputs, outputs, constraints, and extension points define the plugin contract?

**Why it matters:**  
Without this, divorce-specific logic may leak into the core or remain hidden inside prompts.

**Target output:**  
Plugin interface draft with required and optional fields.

**Status:** In progress

---

### D-003. Escalation authority boundary
**Question:**  
Which escalation cues may be surfaced by the model, and which escalation decisions must be owned by the platform and/or plugin?

**Why it matters:**  
Escalation is one of the strongest architecture drivers in the spec.

**Target output:**  
Escalation authority matrix.

**Status:** In progress

---

### D-004. Artifact source-of-truth design
**Question:**  
Which artifacts are mandatory in the first implementation, and what is their minimum required schema/shape?

**Why it matters:**  
The spec says offline evaluation should use structured artifacts as the source of truth.

**Target output:**  
Artifact contract pack.

**Status:** In progress

---

### D-005. Persistence and redaction enforcement
**Question:**  
How will persistence profiles and redaction hooks be represented and enforced in the runtime?

**Why it matters:**  
This affects storage, orchestration, evaluator access, and compliance posture.

**Target output:**  
Persistence profile matrix and enforcement notes.

**Status:** Open

---

### D-006. Failure attribution workflow
**Question:**  
How will the team distinguish model-resident, platform-resident, plugin-resident, and integration-resident failures?

**Why it matters:**  
Without this, architecture iteration will turn into guesswork.

**Target output:**  
Failure attribution rubric.

**Status:** Open

---

## 5. Readiness gaps

These gaps are derived from `READINESS-001`.

### G-001. Core competency model needs implementation-facing definitions
**Needed:**  
Observable success and failure signals per competency family.

**Status:** In progress

---

### G-002. Plugin contract needs stabilization and canonical placement
**Needed:**  
Clear plugin input/output responsibilities, extension points, and non-substitution rule.

**Status:** Drafted / canonicalizing

---

### G-003. Benchmark corpus needs stronger architecture linkage
**Needed:**  
A matrix showing which benchmark cases pressure which runtime capabilities.

**Status:** Partially drafted

---

### G-004. Scoring model needs final operational alignment
**Needed:**  
A repeatable score sheet, review order, and calibration process.

**Status:** Mostly drafted

---

### G-005. Escalation framework needs final implementation rules
**Needed:**  
Explicit definitions for hard triggers, sufficient repair attempts, and minimum handoff packet requirements.

**Status:** Partially drafted

---

### G-006. Runtime artifact contracts need stabilization and cleanup
**Needed:**  
Minimum contracts for `run_meta.json`, `interaction_trace.json`, `flags.json`, `positions.json`, `facts_snapshot.json`, `missing_info.json`, `summary.txt`, and handoff/brief artifacts.

**Status:** Drafted / canonicalizing

---

### G-007. Reproducibility and persistence rules need implementation framing
**Needed:**  
Concrete required metadata fields, seed policy, version traceability, and profile-specific write rules.

**Status:** Not started

---

## 6. Active work items

These are the current tasks that should move the project materially closer to architecture translation.

### A-001. Finalize architecture-decision folder structure
- [x] Add `README.md` for `annexes/architecture_decisions/`
- [x] Add `ADR-001-model-core-plugin-evaluator-boundary.md`
- [x] Add `READINESS-001-pre-architecture-checklist.md`
- [x] Add `STATUS-001-spec-to-architecture-plan.md`

**Status:** Completed

---

### A-002. Convert Part I into architecture inputs
- [ ] Extract the core competency families into a working matrix
- [ ] Extract the core responsibilities list
- [ ] Extract the plugin responsibilities list
- [ ] Extract the escalation modes, categories, and threshold bands
- [ ] Extract mandatory artifact expectations

**Status:** In progress

---

### A-003. Draft runtime artifact contracts
- [x] Draft `run_meta.json` minimum contract
- [x] Draft `interaction_trace.json` minimum contract
- [x] Draft `flags.json` minimum contract
- [x] Draft `positions.json` minimum contract
- [x] Draft `facts_snapshot.json` minimum contract
- [x] Draft `missing_info.json` minimum contract
- [x] Draft `summary.txt` expectations
- [x] Draft continuity packet contract

**Status:** Drafted / canonicalizing

---

### A-004. Draft plugin interface v0
- [x] Define required plugin metadata
- [x] Define ontology / taxonomy contract
- [x] Define domain red-flag contract
- [x] Define feasibility-check contract
- [x] Define plugin confidence output
- [x] Define domain handoff annotation fields

**Status:** Drafted / canonicalizing

---

### A-005. Draft escalation authority matrix
- [x] Separate detection cues from final routing authority
- [x] Separate core triggers from plugin-local triggers
- [x] Define stop / narrow / review / co-handle / handoff decision points
- [x] Define minimum rationale fields

**Status:** Drafted

---

### A-006. Build benchmark-to-capability matrix
- [x] Map benchmark scenarios to competencies
- [x] Map benchmark scenarios to escalation expectations
- [x] Map benchmark scenarios to plugin requirements
- [x] Map benchmark scenarios to required artifacts
- [x] Map benchmark scenarios to likely failure attribution classes

**Status:** Drafted

---

### A-007. Prepare first end-to-end evaluation slice
- [x] Select one benchmark case: `D-B04`
- [x] Define one synthetic participant pair
- [x] Define minimum runtime flow for one session
- [x] Define expected artifacts from that run
- [x] Define evaluator review order for that run
- [x] Add one worked reference session artifact set: `D-B04-S01`

**Status:** Completed

---

## 7. Completed work items

### C-001. Repository purpose and phase clarified
- [x] Confirmed that the repository is an MVP evaluation-phase spec package, not the final production architecture.

### C-002. Model/core/plugin/evaluator boundary framed
- [x] Drafted boundary position that treats Solomon as a model-centered but platform-governed system.

### C-003. Pre-architecture readiness structure created
- [x] Drafted a readiness checklist defining what must be stable before architecture translation.

### C-004. Architecture-decision folder usage clarified
- [x] Drafted folder-level README positioning ADRs and readiness notes as informative implementation guidance.

### C-005. First end-to-end benchmark selected
- [x] Selected `D-B04` as the first architecture-validation benchmark slice.

### C-006. Architecture input pack materially expanded
- [x] Added `SPEC-TO-ARCH-INPUTS.md`, benchmark-to-capability mapping, and an escalation authority matrix.

### C-007. Plugin and artifact contract drafts added
- [x] Added plugin-interface and runtime-artifact contract drafts and normalized them into clean publishable markdown.

### C-008. Pending scoring and evaluator artifacts drafted
- [x] Added drafts for flags schema, synthetic user role profiles, plugin-domain scoring, integration scoring, evaluator console requirements, fairness checks, trigger-class testing, and regression protocol.

### C-009. First worked reference session artifact set added
- [x] Added `D-B04-S01` with run metadata, trace, state artifacts, summary, and evaluation output.

### C-010. Contract pack overlap reviewed
- [x] Reconciled key overlap across `CONTRACT-001` through `CONTRACT-004`, including naming alignment and cross-contract artifact authority.

---

## 8. Blockers

These are current blockers that would make architecture work premature or lower quality.

### B-001. Reproducibility and persistence framing is still not fully frozen
**Impact:**  
The architecture can now be drafted, but persistence-policy enforcement and replay expectations still need a final pass before implementation hardens.

### B-002. The current reference run is a worked baseline, not yet a multi-rerun validation set
**Impact:**  
The repo now has one stable end-to-end example, but it still needs follow-on reruns and comparisons for stronger regression confidence.

---

## 9. Next milestone

## Milestone M-001: Architecture input pack complete

**Definition of done:**
- [ ] Core competency families mapped to observable outputs
- [ ] Core/platform/plugin/evaluator responsibilities documented
- [x] Artifact contracts drafted
- [x] Plugin interface v0 drafted
- [x] Escalation authority matrix drafted
- [x] Benchmark-to-capability matrix drafted
- [x] One end-to-end benchmark slice selected

**Outcome:**  
The team is ready to begin drafting a first runtime architecture document.

---

## 10. Recommended next actions

### Immediate next actions
1. Cross-check example records and benchmark packages against the current schemas and contracts
2. Decide which draft architecture-input documents are stable enough to treat as the active pack
3. Draft the first runtime architecture outline against the now-cleaned contract pack
4. Tighten reproducibility and persistence rules for implementation
5. Add the first rerun/comparison package against the `D-B04-S01` baseline

### After that
1. Draft initial runtime architecture outline
2. Draft component diagram
3. Draft artifact flow diagram
4. Draft escalation/handoff sequence diagram
5. Validate architecture against one benchmark slice

---

## 11. Owners and dates

- **Status owner:** Russell Collins / active repo steward
- **Last updated:** 2026-03-14
- **Next review date:** After the first runtime architecture draft is written against the `D-B04-S01` baseline
- **Current milestone:** M-001  
- **Current decision:** Continue pre-architecture preparation

---

## 12. Notes

This file should be updated whenever:
- an open decision is resolved
- a readiness gap is closed
- a blocker is removed
- a milestone changes
- the project becomes ready to move from pre-architecture preparation into architecture design
