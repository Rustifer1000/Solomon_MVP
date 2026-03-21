# Evaluator Console Requirements

**Status**  
Draft / pending completion artifact

**Purpose**  
This document defines the first-pass requirements for an evaluator console for Solomon's evaluation phase.

It is intended to make evaluator work:

- consistent
- lower-burden
- auditable
- aligned with the repo's schemas and scoring logic

This document does **not** supersede the normative specification in `docs/` or the JSON schemas.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. Role of the evaluator console

The evaluator console is part of the evaluator/control plane. It does not run live mediation sessions. It exists to support:

- review of benchmark and offline session outputs
- rubric-based scoring
- escalation assessment
- overlay marking
- calibration and adjudication workflows
- writing structured evaluation outputs

The console should help evaluators answer:

- what happened in the session
- what Solomon detected
- why it continued, narrowed, or escalated
- whether plugin signals influenced the outcome
- whether the failure belongs to the core, plugin, platform, or integration boundary

---

## 2. Primary users

The console is primarily for:

- evaluators scoring `evaluation.json`
- expert reviewers writing `expert_review.json`
- calibration leads comparing evaluator judgments
- technical architects reviewing failure patterns

It is not a mediator-facing product UI.

---

## 3. Core design principles

### 3.1 Structured artifacts first
The console should privilege structured artifacts over raw conversational impression.

### 3.2 Review order should be enforced gently
The console should encourage the repo's intended evidence review order rather than leaving evaluators to improvise.

### 3.3 Scoring should be rubric-driven
The console should not leave family definitions, overlays, or escalation dimensions implicit.

### 3.4 Required notes should be captured at the point of scoring
The console should prompt for mandatory rationale when triggered instead of relying on later cleanup.

### 3.5 Calibration and attribution should be first-class
The console should support disagreement review and failure attribution rather than treating them as afterthoughts.

---

## 4. Minimum supported inputs

The evaluator console should be able to read, display, or link to the following inputs when present:

- benchmark scenario record or case summary
- `interaction_trace.json`
- `summary.txt`
- `flags.json`
- transcript if policy allows it
- relevant briefs
- continuity packet if escalation occurred
- plugin-domain context if available
- prior `evaluation.json` for expert-review or adjudication flows

The console must tolerate policy-limited cases where transcripts are unavailable.

---

## 5. Required evaluator workflows

### 5.1 Single-run evaluation workflow
Support a reviewer in producing one `evaluation.json` from one case/session package.

### 5.2 Expert review workflow
Support a reviewer in producing one `expert_review.json` layered on top of one or more evaluation records.

### 5.3 Calibration workflow
Support comparison between multiple evaluator judgments on the same case.

### 5.4 Benchmark rerun comparison workflow
Support side-by-side comparison of runs across model or system versions when used for regression evaluation.

---

## 6. Minimum screen or panel set

The console should support the following functional panels. Exact UI layout is flexible.

### 6.1 Case overview panel
Shows:

- case ID
- session ID
- plugin
- benchmark ID if applicable
- case summary
- challenge type
- expected escalation posture
- focal scoring areas
- policy profile

### 6.2 Artifact navigator
Provides quick access to:

- `flags.json`
- `summary.txt`
- `interaction_trace.json`
- transcript if present
- briefs
- continuity packet
- plugin outputs if present

### 6.3 Structured evidence panel
Shows evaluator-relevant structured state such as:

- active flags
- missing information
- issue map or issue clusters
- positions and facts if available
- escalation posture and rationale markers

### 6.4 Scoring panel
Lets evaluators enter:

- core family scores
- plugin-domain scores
- integration scores
- automatic-fail overlays
- escalation review scores
- final judgment and confidence

### 6.5 Notes and rationale panel
Captures:

- required notes
- short rationale
- calibration notes
- attribution notes

### 6.6 Review comparison panel
For expert-review or calibration mode, shows:

- prior evaluator scores
- disagreements
- override points
- disposition status

---

## 7. Required behavior for the single-run evaluation flow

### 7.1 Metadata prefill
The console should pre-fill all metadata it can infer from case and session artifacts.

At minimum:

- case ID
- session ID
- plugin
- benchmark ID if available
- policy profile if available

### 7.2 Evidence review order guidance
The console should guide evaluators through this order:

1. benchmark scenario record or case summary
2. `flags.json`
3. `summary.txt`
4. relevant briefs
5. `interaction_trace.json`
6. transcript if available
7. continuity packet if applicable

The console does not need to hard-lock the order, but it should make the intended workflow visible.

### 7.3 Score entry assistance
The console should present:

- family labels
- score definitions
- weight values
- brief scoring prompts

### 7.4 Required notes enforcement
The console must require notes when:

- a core, plugin, or integration family score is `1`, `2`, or `5`
- an automatic-fail overlay is `Borderline / review` or `Yes`
- the escalation block is used

### 7.5 Automatic calculations
The console should compute automatically:

- weighted core score
- weighted plugin-domain score
- weighted integration score
- interpretation bands where applicable

The evaluator should still be able to review the underlying component scores.

### 7.6 Output writing
The console should write results into:

- `evaluation.json`
- optionally `expert_review.json` in review workflows

It should not force evaluators to hand-build these files.

---

## 8. Required scoring support

### 8.1 Core score support
The console must support the ten core families C1-C10 and the existing weighted score model.

### 8.2 Automatic-fail overlay support
The console must support:

- F1 coercive steering
- F2 false authority
- F3 one-sidedness
- F4 unsafe continuation
- F5 fabrication

### 8.3 Escalation review support
The console must support:

- escalation-sensitive condition present
- primary escalation category
- threshold band
- observed mode
- evaluator-preferred mode
- ES1-ES5 scores and notes

### 8.4 Plugin-domain scoring support
The console should support the plugin-domain families defined in `pending/plugin_domain_scoring.md`.

### 8.5 Integration scoring support
The console should support the integration families defined in `pending/integration_scoring.md`.

---

## 9. Required validation behavior

The console should validate before saving:

- all required metadata fields are present
- all required scores are filled
- all triggered note fields are filled
- enum-like fields use supported values
- expert-review mode includes at least one source evaluation

Validation errors should be clear and field-specific.

---

## 10. Artifact display requirements

### 10.1 `flags.json`
The console should surface:

- active flags first
- severity
- flag type
- source
- hard-trigger status
- related escalation categories if present

### 10.2 `interaction_trace.json`
The console should allow evaluators to inspect:

- turns in order
- phase labels
- state deltas
- risk-check fields
- escalation-related state changes

### 10.3 `summary.txt`
The console should display the summary while making clear that structured artifacts are authoritative.

### 10.4 Transcripts
If transcripts are available, the console should support quick navigation between transcript evidence and the structured state used in scoring.

### 10.5 Continuity packet
If escalation occurred, the console should make the continuity packet easy to inspect alongside the escalation review block.

---

## 11. Expert-review requirements

In expert-review mode, the console should additionally support:

- loading one or more `evaluation.json` files
- showing score differences by section
- recording overrides to:
  - core family scores
  - plugin-domain scores
  - integration scores
  - overlay status
  - escalation assessment
- recording agreement level:
  - full agreement
  - partial agreement
  - substantial disagreement
- recording final disposition

The expert-review workflow should write schema-aligned `expert_review.json`.

---

## 12. Calibration requirements

The console should support calibration exercises by:

- allowing side-by-side evaluator comparison on the same case
- highlighting score deltas
- highlighting disagreements on overlays and escalation
- capturing calibration notes for future rubric updates

Recommended calibration emphasis areas:

- C5 option generation
- C6 fair process
- C9 escalation and boundary handling
- plugin-domain feasibility qualification
- integration attribution

---

## 13. Benchmark and regression support

The console should support benchmark use by:

- showing benchmark expectations
- showing observed mode and evaluator-preferred mode together
- allowing comparison across reruns of the same benchmark ID
- making model/provider or version metadata visible when present

This is important for regression testing and architecture validation.

---

## 14. Auditability and export requirements

The evaluator console should preserve enough information to answer later:

- who scored the run
- when it was reviewed
- which artifacts were available
- what judgment was recorded
- what notes justified extreme scores or overlays

At minimum, the console should export or persist:

- the final evaluation file
- the final expert-review file if applicable
- review metadata

---

## 15. Nice-to-have but non-blocking features

These are useful but not required for the first implementation:

- side-by-side transcript and trace synchronization
- inline benchmark expectation prompts per scoring family
- score-distribution analytics across evaluators
- bulk benchmark queue management
- annotation bookmarks for notable turns

---

## 16. Non-goals for the first console

The first evaluator console does **not** need to provide:

- live mediation controls
- final production admin tooling
- general analytics dashboards
- end-user reporting workflows
- multi-tenant product infrastructure

It should remain tightly scoped to offline evaluation and review.

---

## 17. Definition of done for v0

The evaluator console is sufficiently specified for the first architecture phase when:

- a reviewer can load one benchmark run and produce schema-aligned `evaluation.json`
- an expert reviewer can load a scored run and produce schema-aligned `expert_review.json`
- the console enforces required notes and score completeness
- weighted scoring is computed automatically
- structured artifacts are displayed clearly enough to support consistent scoring
- plugin-domain and integration scoring can be recorded as first-class review outputs
