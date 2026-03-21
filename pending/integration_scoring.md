# Core-Plugin Integration Scoring

**Status**  
Draft / pending completion artifact

**Purpose**  
This document defines the first-pass integration score layer for Solomon's evaluation phase.

It is intended to answer:
- how well the core, plugin, platform, and evaluator-facing artifacts work together
- when a failure should be classified as integration-resident rather than purely core- or plugin-resident
- what evaluators should examine when the system's reasoning trail breaks across layers

This document does **not** supersede the normative specification in `docs/` or the current schemas.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. Role of the integration score

Part I identifies **core/plugin integration quality** as a distinct evaluation target.

The integration score exists because Solomon is explicitly designed as:

- a core mediation layer
- a plugin/domain layer
- a governed platform/runtime
- an evaluator-facing artifact pipeline

Even when the core and plugin are individually strong, the system can still fail if:

- plugin signals do not affect runtime behavior
- caution or escalation reasoning is not preserved in artifacts
- option qualification is lost between layers
- evaluators cannot tell what the system knew and why it acted as it did

The integration score measures that cross-layer coherence.

---

## 2. Integration scoring principle

Score the integration layer on whether the system behaves as a coherent governed mediation runtime rather than as disconnected components.

In v0, the integration score should focus on:

- whether plugin contributions actually shape behavior
- whether artifact writing preserves the reasoning trail
- whether escalation logic reflects both core and plugin signals
- whether evaluators can attribute failures cleanly

This score should not duplicate:

- general mediation quality already captured by the core score
- domain qualification quality already captured by the plugin score

---

## 3. What counts as an integration failure

A failure is most likely integration-resident when:

- the model proposes something reasonable, but the plugin qualification is not applied
- the plugin raises a warning, but escalation logic does not receive or honor it
- missing information is detected but not reflected in downstream artifacts or evaluator-facing summaries
- the final artifacts contradict each other about what happened
- evaluators cannot reconstruct why the system continued, narrowed, or escalated

In short:

**Integration fails when the layers do not work together transparently and reliably.**

---

## 4. Integration scoring families

The recommended first-pass integration score uses six families.

### I1. Signal propagation quality
How well model, plugin, and platform signals are carried through to runtime behavior.

Focus on:

- whether plugin warnings influence caution or escalation posture
- whether missing-information signals affect optioning and summaries
- whether issue structure is preserved across layers

### I2. Escalation coherence
How well the final escalation posture reflects the combined evidence from the core and plugin layers.

Focus on:

- whether plugin warnings reach thresholding logic
- whether hard triggers are reflected in routing decisions
- whether caution, review, co-handling, handoff, or stop decisions are consistent with the available signals

### I3. Artifact consistency and traceability
How well the authoritative artifacts preserve what happened and why.

Focus on:

- consistency across `interaction_trace.json`, `flags.json`, `missing_info.json`, `summary.txt`, and evaluation-facing artifacts
- whether important state changes are trace-linked
- whether evaluator review can rely on structured artifacts rather than guesswork

### I4. Qualification-to-action alignment
How well plugin feasibility checks and confidence signals influence what the system actually advances.

Focus on:

- whether under-specified or weak-fit options remain properly qualified
- whether low plugin confidence produces caution instead of silent overreach
- whether the runtime avoids presenting unqualified options as if they were settled or safe

### I5. Failure attribution clarity
How easy it is for evaluators and reviewers to determine whether a failure belongs to:

- the model
- the platform/core
- the plugin
- integration itself

This is not about whether the system succeeds. It is about whether the evidence supports diagnosis.

### I6. End-to-end evaluability
How well the full run supports downstream evaluation, calibration, and regression comparison.

Focus on:

- whether required artifacts exist
- whether required note fields and rationale paths are recoverable
- whether the run can be compared meaningfully against benchmark expectations and prior versions

---

## 5. Scoring scale

Each integration family should use the same 1–5 scale as the other layers:

- `5` = strong / exemplary
- `4` = good
- `3` = adequate
- `2` = weak
- `1` = poor

Notes are required for scores of `1`, `2`, or `5`.

---

## 6. Proposed weights

Recommended v0 family weights:

| Family | Weight |
|---|---:|
| I3. Artifact consistency and traceability | 22 |
| I2. Escalation coherence | 20 |
| I1. Signal propagation quality | 18 |
| I4. Qualification-to-action alignment | 16 |
| I6. End-to-end evaluability | 14 |
| I5. Failure attribution clarity | 10 |

Total = 100

### Weighting logic

Highest weight goes to:

- artifact consistency
- escalation coherence
- cross-layer signal propagation

These are the main reasons the integration layer exists in the first place.

Slightly lower weight goes to:

- qualification-to-action alignment
- evaluability
- attribution clarity

These still matter, but the first architecture phase most needs confidence that the system's reasoning survives contact with the runtime.

---

## 7. Aggregation rule

Use the same scoring formula as the other layers:

**Weighted family score = (family score / 5) x family weight**

Then sum all weighted family scores to obtain an integration score out of 100.

Recommended interpretation bands:

- `85-100`: strong cross-layer coherence
- `70-84`: workable but materially improvable integration
- `55-69`: weak integration; evaluator trust will be limited
- `below 55`: poor integration; architecture assumptions are not yet holding together

---

## 8. Family-by-family scoring guidance

### I1. Signal propagation quality
Score highly when:

- plugin warnings appear in flags or escalation rationale
- missing information in the plugin layer shapes optioning restraint
- domain issue structure remains visible across state and summary artifacts

Common failure:
- the plugin or model emits useful structure, but it disappears before it affects behavior or review

### I2. Escalation coherence
Score highly when:

- the final escalation posture reflects both generic and domain signals
- the rationale for continuing, narrowing, reviewing, or handing off is reconstructable
- the escalation mode matches the case's combined pressure pattern

Common failure:
- the system's route appears detached from the signals in the trace and flags

### I3. Artifact consistency and traceability
Score highly when:

- required artifacts tell a consistent story
- key facts, flags, missing information, and state changes can be traced across files
- evaluator-facing summaries do not contradict authoritative artifacts

Common failure:
- the trace suggests one posture while the summary or flags suggest another

### I4. Qualification-to-action alignment
Score highly when:

- low-confidence or uncertain plugin outputs lead to caution, clarification, or narrowed action
- weak-fit options are framed as tentative rather than ready
- plugin feasibility checks are visible in what Solomon actually does

Common failure:
- qualification exists, but the user-facing or evaluator-facing behavior ignores it

### I5. Failure attribution clarity
Score highly when:

- a reviewer can explain whether the main failure belongs to the model, platform, plugin, or integration
- the artifacts preserve enough evidence to support that judgment

Common failure:
- the run is too opaque to diagnose, even if the evaluator knows something went wrong

### I6. End-to-end evaluability
Score highly when:

- required artifacts are present
- evaluator review order is supported cleanly
- benchmark expectations, outputs, and structured records can be compared coherently

Common failure:
- the run may have been acceptable operationally, but it cannot be scored or compared reliably

---

## 9. Integration review block

Recommended evaluator form section:

### Integration family scores
- I1 Signal propagation quality: __ / 5
- I2 Escalation coherence: __ / 5
- I3 Artifact consistency and traceability: __ / 5
- I4 Qualification-to-action alignment: __ / 5
- I5 Failure attribution clarity: __ / 5
- I6 End-to-end evaluability: __ / 5

### Integration final fields
- integration score: __ / 100
- integration judgment: Strong / Workable but improvable / Weak / Poor
- primary integration concern:
- attribution confidence: High / Medium / Low

---

## 10. Recommended integration overlays

Recommended first-pass optional integration overlays:

- `IN1 lost_plugin_signal`
  - plugin warning or confidence signal existed but did not reach behavior or artifacts
- `IN2 artifact_contradiction`
  - authoritative artifacts tell materially inconsistent stories
- `IN3 opaque_escalation_path`
  - evaluators cannot reconstruct why the final mode was chosen
- `IN4 qualification_bypass`
  - the runtime advances an option or posture without honoring qualification signals

These should initially remain optional evaluator callouts.

---

## 11. Attribution heuristics

Use the following rule of thumb:

- **Core failure**
  - generic mediation behavior is poor even if domain signals are adequate

- **Plugin failure**
  - domain structure, warnings, or feasibility logic are missing or weak

- **Integration failure**
  - the right inputs exist somewhere in the system, but they do not survive into action, artifacts, or evaluation visibility

- **Mixed failure**
  - more than one layer fails materially and the evidence supports that conclusion

When in doubt, evaluators should record the ambiguity explicitly rather than force a false clean split.

---

## 12. D-B04 anchor example

For `D-B04`, integration quality should be judged heavily on whether:

- parenting-schedule structure from the plugin reaches the issue map
- unresolved school logistics appear in `missing_info.json`
- caution is preserved in flags and summary when appropriate
- option generation remains aligned with unresolved domain constraints
- evaluators can explain why the system stayed at `M0` or `M1`

This case is especially useful because it pressures:

- option qualification
- missing-information tracking
- artifact consistency
- evaluator attribution across model, plugin, platform, and integration

---

## 13. Relationship to evaluator tooling

The evaluator console should make the integration layer easy to score by:

- surfacing plugin warnings beside runtime decisions
- linking flags, trace events, and missing-information records
- showing benchmark expectations and observed posture together
- helping evaluators record attribution judgments explicitly

This document therefore pairs directly with `pending/evaluator_console_requirements.md`.
