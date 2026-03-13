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

Recommended future companion:
- `SPEC-TO-ARCH-INPUTS.md`

---

## 3. Current overall status snapshot

### Phase status
- [ ] Core conceptual basis stable enough for architecture translation
- [ ] Core/plugin boundary stable enough for architecture translation
- [ ] Evaluation design stable enough for architecture translation
- [ ] Scoring and escalation framework stable enough for architecture translation
- [ ] Artifact contracts stable enough for architecture translation
- [ ] Reproducibility / persistence rules stable enough for architecture translation
- [ ] One end-to-end benchmark run can be evaluated and explained

### Overall assessment
**Current assessment:** Not yet ready for full runtime architecture design  
**Reason:** Foundational direction is strong, but several architecture inputs still need to be made explicit and testable.

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

**Status:** Open

---

### D-003. Escalation authority boundary
**Question:**  
Which escalation cues may be surfaced by the model, and which escalation decisions must be owned by the platform and/or plugin?

**Why it matters:**  
Escalation is one of the strongest architecture drivers in the spec.

**Target output:**  
Escalation authority matrix.

**Status:** Open

---

### D-004. Artifact source-of-truth design
**Question:**  
Which artifacts are mandatory in the first implementation, and what is their minimum required schema/shape?

**Why it matters:**  
The spec says offline evaluation should use structured artifacts as the source of truth.

**Target output:**  
Artifact contract pack.

**Status:** Open

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

### G-002. Plugin contract not yet explicit
**Needed:**  
Clear plugin input/output responsibilities, extension points, and non-substitution rule.

**Status:** Not started

---

### G-003. Benchmark corpus not yet tied directly to architecture questions
**Needed:**  
A matrix showing which benchmark cases pressure which runtime capabilities.

**Status:** Not started

---

### G-004. Scoring model needs operational evaluator workflow
**Needed:**  
A repeatable score sheet, review order, and calibration process.

**Status:** Partially drafted

---

### G-005. Escalation framework needs implementation rules
**Needed:**  
Explicit definitions for hard triggers, sufficient repair attempts, and minimum handoff packet requirements.

**Status:** In progress

---

### G-006. Runtime artifact contracts not yet stabilized
**Needed:**  
Minimum contracts for `run_meta.json`, `interaction_trace.json`, `flags.json`, `positions.json`, `facts_snapshot.json`, `missing_info.json`, `summary.txt`, and handoff/brief artifacts.

**Status:** Not started

---

### G-007. Reproducibility and persistence rules need implementation framing
**Needed:**  
Concrete required metadata fields, seed policy, version traceability, and profile-specific write rules.

**Status:** Not started

---

## 6. Active work items

These are the current tasks that should move the project materially closer to architecture translation.

### A-001. Finalize architecture-decision folder structure
- [ ] Add `README.md` for `annexes/architecture_decisions/`
- [ ] Add `ADR-001-model-core-plugin-evaluator-boundary.md`
- [ ] Add `READINESS-001-pre-architecture-checklist.md`
- [ ] Add `STATUS-001-spec-to-architecture-plan.md`

**Status:** In progress

---

### A-002. Convert Part I into architecture inputs
- [ ] Extract the core competency families into a working matrix
- [ ] Extract the core responsibilities list
- [ ] Extract the plugin responsibilities list
- [ ] Extract the escalation modes, categories, and threshold bands
- [ ] Extract mandatory artifact expectations

**Status:** Not started

---

### A-003. Draft runtime artifact contracts
- [ ] Draft `run_meta.json` minimum contract
- [ ] Draft `interaction_trace.json` minimum contract
- [ ] Draft `flags.json` minimum contract
- [ ] Draft `positions.json` minimum contract
- [ ] Draft `facts_snapshot.json` minimum contract
- [ ] Draft `missing_info.json` minimum contract
- [ ] Draft `summary.txt` expectations
- [ ] Draft continuity packet contract

**Status:** Not started

---

### A-004. Draft plugin interface v0
- [ ] Define required plugin metadata
- [ ] Define ontology / taxonomy contract
- [ ] Define domain red-flag contract
- [ ] Define feasibility-check contract
- [ ] Define plugin confidence output
- [ ] Define domain handoff annotation fields

**Status:** Not started

---

### A-005. Draft escalation authority matrix
- [ ] Separate detection cues from final routing authority
- [ ] Separate core triggers from plugin-local triggers
- [ ] Define stop / narrow / review / co-handle / handoff decision points
- [ ] Define minimum rationale fields

**Status:** Not started

---

### A-006. Build benchmark-to-capability matrix
- [ ] Map benchmark scenarios to competencies
- [ ] Map benchmark scenarios to escalation expectations
- [ ] Map benchmark scenarios to plugin requirements
- [ ] Map benchmark scenarios to required artifacts
- [ ] Map benchmark scenarios to likely failure attribution classes

**Status:** Not started

---

### A-007. Prepare first end-to-end evaluation slice
- [x] Select one benchmark case: `D-B04`
- [ ] Define one synthetic participant pair
- [ ] Define minimum runtime flow for one session
- [ ] Define expected artifacts from that run
- [ ] Define evaluator review order for that run

**Status:** In progress

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

---

## 8. Blockers

These are current blockers that would make architecture work premature or lower quality.

### B-001. No explicit runtime contract pack yet
**Impact:**  
Architecture diagrams would remain too abstract.

### B-002. Plugin interface not yet formalized
**Impact:**  
Risk of mixing divorce-specific logic into the core.

### B-003. Benchmark evidence not yet translated into architecture requirements
**Impact:**  
System design may be driven by intuition rather than evaluation pressure.

### B-004. No single end-to-end reference run defined
**Impact:**  
Hard to test whether the architecture is sufficient.

---

## 9. Next milestone

## Milestone M-001: Architecture input pack complete

**Definition of done:**
- [ ] Core competency families mapped to observable outputs
- [ ] Core/platform/plugin/evaluator responsibilities documented
- [ ] Artifact contracts drafted
- [ ] Plugin interface v0 drafted
- [ ] Escalation authority matrix drafted
- [ ] Benchmark-to-capability matrix drafted
- [ ] One end-to-end benchmark slice selected

**Outcome:**  
The team is ready to begin drafting a first runtime architecture document.

---

## 10. Recommended next actions

### Immediate next actions
1. Create `SPEC-TO-ARCH-INPUTS.md`
2. Draft runtime artifact contracts
3. Draft plugin interface v0
4. Draft escalation authority matrix
5. Select first end-to-end benchmark slice

### After that
1. Draft initial runtime architecture outline
2. Draft component diagram
3. Draft artifact flow diagram
4. Draft escalation/handoff sequence diagram
5. Validate architecture against one benchmark slice

---

## 11. Owners and dates

- **Status owner:**  
- **Last updated:**  
- **Next review date:**  
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