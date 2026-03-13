
# Escalation Authority Matrix

**Status**  
Draft / informative

**Purpose**  
This document defines the first-pass authority boundary for escalation-related behavior in Solomon’s evaluation-phase runtime.

It is intended to answer:
- what the model may surface
- what the plugin may qualify
- what the platform/core must decide
- what should be recorded for evaluator review
- what conditions should result in continued handling, narrowed scope, review, co-handling, handoff, or stop-and-redirect

This document does **not** supersede the normative specification.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. Framing

The Solomon specification treats escalation as a **core mediation competence**, not merely a failure outcome.

Architecture should therefore assume:
- correct escalation may be evidence of good performance
- escalation requires structured reasoning, not only model intuition
- the model, plugin, platform, and evaluator each have different roles in escalation

This document defines those roles for the first runtime architecture phase.

---

## 2. Escalation principle

Use this rule:

**The model may surface cues.  
The plugin may qualify domain-specific risk or complexity.  
The platform/core owns thresholding, routing, and final escalation mode selection.  
The evaluator verifies whether the escalation outcome was appropriate.**

This rule keeps Solomon from hiding escalation logic inside opaque model behavior.

---

## 3. Escalation modes and categories assumed

### 3.1 Modes
This document assumes the normative mode set:
- `M0` Continue autonomously
- `M1` Continue with caution / narrowed scope
- `M2` Request human review in the loop
- `M3` Escalate to human mediator co-handling
- `M4` Full handoff to human mediator
- `M5` Stop mediation and redirect

### 3.2 Categories
This document assumes the normative category set:
- `E1` Safety-risk escalation
- `E2` Process-breakdown escalation
- `E3` Legitimacy and trust escalation
- `E4` Domain-complexity escalation
- `E5` Decision-quality escalation
- `E6` Ethical-boundary escalation

### 3.3 Threshold bands
This document assumes the normative threshold bands:
- `T0` no threshold crossed
- `T1` mild concern
- `T2` moderate concern
- `T3` high concern
- `T4` immediate stop condition

---

## 4. Escalation authority by layer

### 4.1 Model authority
The model may:
- identify conversational or interactional cues
- express uncertainty
- propose a candidate escalation category
- propose a candidate escalation mode
- summarize the rationale for caution or escalation

The model may **not**:
- make the authoritative final escalation decision
- suppress platform-required escalation logic
- override a hard trigger emitted by the platform or plugin
- decide persistence policy
- decide whether required handoff artifacts are written

### 4.2 Plugin authority
The plugin may:
- identify domain-specific risk or feasibility concerns
- emit domain-specific hard triggers
- add domain-specific complexity or dependency warnings
- lower plugin confidence when domain qualification is weak
- add handoff annotations relevant to a human mediator/reviewer

The plugin may **not**:
- silently redefine Solomon’s core mediation role
- unilaterally finalize routing without platform review
- override core fairness, noncoercion, or self-determination obligations

### 4.3 Platform/core authority
The platform/core must:
- aggregate model cues, plugin warnings, and state history
- assess severity, persistence, and recoverability
- determine the authoritative escalation category
- determine the authoritative threshold band
- select the authoritative escalation mode
- record the rationale and required artifacts
- trigger human review, co-handling, handoff, or stop behavior when required

The platform/core is the final authority for escalation routing in v0.

### 4.4 Evaluator authority
The evaluator may:
- review whether escalation-sensitive conditions were present
- compare observed mode to preferred mode
- score detection accuracy, threshold calibration, mode selection, rationale quality, and handoff quality
- determine whether escalation was too weak, too strong, too late, or appropriate

The evaluator does not control runtime routing directly, but is the authority on retrospective assessment.

---

## 5. Escalation signal classes

The first implementation should distinguish at least four sources of escalation-relevant input:

1. **Model-surfaced interaction cues**
2. **Plugin-surfaced domain warnings**
3. **Platform-observed state/history conditions**
4. **User- or party-explicit requests**

These should remain distinct in artifacts so evaluators can tell where the escalation reasoning came from.

---

## 6. Matrix: who does what

| Escalation function | Model | Plugin | Platform/Core | Evaluator |
|---|---|---|---|---|
| Detect conversational tension or distress cues | May surface | May add domain interpretation | Reviews and incorporates | Scores |
| Detect domain-specific risk | May hint | Owns domain qualification | Reviews and incorporates | Scores |
| Detect hard trigger | May suggest | May emit domain hard trigger | Owns authoritative handling | Scores |
| Determine threshold band | May suggest | May contribute evidence | Owns final decision | Scores |
| Select escalation category | May suggest | May qualify | Owns final decision | Scores |
| Select mode M0-M5 | May suggest | May recommend | Owns final decision | Scores |
| Write rationale | May draft | May add domain note | Owns authoritative record | Reviews |
| Produce continuity packet | May help draft text | May add annotations | Owns required artifact | Reviews |
| Decide stop-and-redirect | No | May recommend | Owns final decision | Scores |

---

## 7. Hard-trigger handling rule

### 7.1 Principle
A hard trigger is a condition that presumptively forces stronger escalation handling.

### 7.2 Types
Hard triggers may come from:
- core/platform logic
- plugin/domain logic

### 7.3 Rule
If a hard trigger is present:
- the platform must record it
- the platform must elevate threshold handling
- the platform must produce required flags and rationale
- the platform must not silently continue in `M0` without an explicit, reviewable rationale

### 7.4 v0 consequence
In v0, a hard trigger should generally prevent silent continuation and should push the system toward at least:
- `M1` for cautionary narrowing when evidence is incomplete, or
- `M2` / `M3` / `M4` / `M5` when severity or non-recoverability is stronger

---

## 8. Severity, persistence, recoverability

The platform should compute escalation using three factors:

### 8.1 Severity
How serious is the observed concern right now?

### 8.2 Persistence
Is the concern momentary, repeated, or worsening across turns?

### 8.3 Recoverability
Can the issue likely be repaired through bounded interventions, or is autonomous handling becoming unreliable or illegitimate?

### 8.4 Rule
The platform should never use a single cue alone as the general escalation authority unless:
- it is a designated hard trigger, or
- it is an explicit party request with normative force, or
- policy requires immediate stop/review behavior

---

## 9. Mandatory special cases

### 9.1 Explicit request for human involvement
If a participant explicitly requests human involvement, the platform should treat this as at least an `E3` legitimacy/trust signal.

Default v0 rule:
- do not remain silently in `M0`
- move to at least `M2` unless there is a documented reason to do otherwise

### 9.2 Strong coercion or acute safety concern
If strong coercion or acute safety concern is detected:
- treat as presumptively `E1`
- elevate threshold band accordingly
- produce flags and rationale
- prefer `M3`, `M4`, or `M5` depending on severity and recoverability

### 9.3 Persistent process breakdown
If communication collapse, domination, or repeated failed repair persists:
- treat as presumptively `E2`
- do not rely only on further conversational smoothing
- escalate when recoverability is low

### 9.4 Domain qualification failure
If plugin confidence is low and important domain feasibility cannot be assessed responsibly:
- treat as escalation-relevant under `E4` and/or `E5`
- do not continue as if option work were well-grounded

### 9.5 Role-boundary pressure
If the system is being pushed to adjudicate, provide one-sided strategic assistance, or act beyond mediation role:
- treat as `E6`
- narrow, review, hand off, or redirect as appropriate

---

## 10. v0 escalation routing heuristics

These are architecture heuristics, not final normative policy.

### `M0` Continue autonomously
Use when:
- threshold remains at `T0`
- no meaningful hard trigger is present
- recoverability is high
- legitimacy and trust remain intact

### `M1` Continue with caution / narrowed scope
Use when:
- concern is present but not yet severe enough for review/handoff
- evidence is incomplete
- bounded repair or narrowing is still plausible
- evaluator should be able to see why full escalation was not yet chosen

### `M2` Request human review in the loop
Use when:
- legitimacy/trust concern is material
- domain complexity is rising
- confidence is weakened
- responsible progress requires oversight before stronger routing

### `M3` Escalate to human mediator co-handling
Use when:
- autonomous handling is still partly valuable
- active human support is now preferable
- recovery is possible but not appropriate as AI-only handling

### `M4` Full handoff to human mediator
Use when:
- autonomous continuation is no longer appropriate
- continuity matters
- a human should take over the mediation function

### `M5` Stop mediation and redirect
Use when:
- immediate stop condition is present
- mediation should not continue in the current mode
- redirection is more appropriate than handoff continuation

---

## 11. Required runtime outputs for escalation

Whenever the platform selects or materially considers escalation, the runtime should record:

- candidate cues surfaced by the model if any
- plugin warnings if any
- authoritative escalation category
- authoritative threshold band
- authoritative mode
- rationale for the mode chosen
- whether a hard trigger was present
- whether review/handoff artifact creation was required

These should appear across:
- `interaction_trace.json`
- `flags.json`
- continuity packet when applicable
- evaluator-facing outputs

---

## 12. Minimum rationale fields

For any non-trivial escalation decision, the platform should record at least:

```json
{
  "authoritative_category": "E1 | E2 | E3 | E4 | E5 | E6 | none",
  "threshold_band": "T0 | T1 | T2 | T3 | T4",
  "selected_mode": "M0 | M1 | M2 | M3 | M4 | M5",
  "hard_trigger_present": false,
  "severity_summary": "string",
  "persistence_summary": "string",
  "recoverability_summary": "string",
  "short_rationale": "string"
}
13. First-pass decision table
Condition	Default category	Default minimum mode	Final authority
Mild but notable concern, recoverable	context-dependent	M1	Platform/Core
Explicit request for human involvement	E3	M2	Platform/Core
Plugin low confidence on important domain issue	E4/E5	M2	Platform/Core
Repeated communication collapse	E2	M2 or M3	Platform/Core
Strong coercion or unsafe participation	E1	M3/M4/M5	Platform/Core
Role-boundary pressure beyond mediation function	E6	M1/M2/M5	Platform/Core
Immediate stop condition	context-dependent	M5	Platform/Core
14. Evaluator review mapping

The evaluator should be able to inspect and score:

detection accuracy

threshold calibration

mode selection quality

rationale quality

handoff/review quality

The runtime should therefore never compress escalation into a single opaque label without evidence fields.

15. Readiness checklist impact

Completing and adopting this document should advance:

Section E. Escalation readiness

escalation framework is more concrete

authority boundary is explicit

handoff expectations are closer to implementation

Section B. Boundary readiness

model / platform / plugin division is more operational

This document does not complete those sections by itself, but it closes one of the largest remaining architecture gaps.

16. Open questions

Should explicit human-request signals always force M2 or above with no exception?

Should plugin hard triggers be separately labeled from core hard triggers in artifacts?

Should v1 use a numeric recoverability score?

Should candidate model/plugin suggestions always be preserved in the trace, even when platform rejects them?

Which stop-and-redirect cases should bypass co-handling/handoff entirely?