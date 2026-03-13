
---

## 3)

```
# Benchmark to Capability Matrix

**Status**  
Draft / informative

**Purpose**  
This document maps benchmark pressure points to the runtime capabilities Solomon must possess in order to support evaluation-phase architecture design.

It is intended to prevent architecture from being driven only by intuition.  
Instead, architecture should be justified by what benchmark scenarios require the system to do, detect, record, and explain.

This document does **not** supersede the normative specification.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. How to use this matrix

For each benchmark scenario or scenario family, ask:

- Which core competencies are being pressured?
- Which domain/plugin capabilities are being pressured?
- Which escalation expectations are relevant?
- Which runtime artifacts must exist to make the case evaluable?
- Which layer would likely own the failure if the system performs poorly?

This matrix should be used by:
- architects
- evaluator-tooling builders
- plugin designers
- benchmark designers

---

## 2. Capability columns

### Core competency pressure
Which core mediation families are primarily exercised?

### Plugin/domain pressure
Which domain-specific structures or checks are required?

### Escalation expectation
What kind of escalation posture should the runtime be prepared to support?

### Required artifact emphasis
Which artifacts must be especially strong for this case to be evaluable?

### Likely failure attribution
If performance is poor, which layer is most likely responsible:
- model
- platform/core
- plugin
- integration

---

## 3. First-pass benchmark family matrix

| Benchmark family / pressure point | Core competency pressure | Plugin/domain pressure | Escalation expectation | Required artifact emphasis | Likely failure attribution |
|---|---|---|---|---|---|
| Low-conflict workable case | C1, C2, C3, C5, C8 | basic issue taxonomy | likely M0 | positions, facts, summary | model / integration |
| Moderate-conflict but repairable | C3, C4, C6, C7 | issue coupling, domain framing | likely M1 | trace, flags, positions | model / platform |
| High-conflict low-trust | C4, C6, C7, C9 | domain-sensitive warnings | M1 to M2, possibly M3 | trace, flags, summary, continuity if escalated | platform / integration |
| Power-imbalanced case | C6, C7, C9 | dependency and power concerns | M2 to M4 depending on severity | flags, trace, handoff notes | plugin / platform / integration |
| Emotionally escalated case | C4, C7, C9 | domain context as qualifier | M1 to M3 | trace, flags, summary | model / platform |
| Narrow settlement zone | C3, C5, C8 | feasibility and issue coupling | M0 or M1, sometimes E5 | positions, missing info, facts | model / plugin |
| No-agreement-is-correct case | C1, C6, C8, C9 | domain realism | often M0 or M1 with correct closure | summary, positions, facts | model / platform |
| Escalation-to-human-is-correct case | C9, C10 | domain risk/hard triggers | M2/M3/M4/M5 | flags, trace, continuity packet | platform / plugin / integration |
| Domain-complexity overload | C8, C9 | plugin confidence, feasibility checks | E4/E5, likely M2 or above | missing info, plugin outputs, trace | plugin / integration |
| Role-boundary pressure case | C1, C9, C10 | domain notes may qualify | E6, likely M1/M2/M5 | trace, flags, summary | platform / model |

---

## 4. Benchmark family notes

### 4.1 Low-conflict workable cases
Architecture implication:
- do not over-engineer escalation around all cases
- runtime should still write full structured artifacts even when the case is straightforward

### 4.2 High-conflict / low-trust cases
Architecture implication:
- trace quality and flag handling become critical
- the platform must preserve why caution, review, or handoff was or was not chosen

### 4.3 Power-imbalanced cases
Architecture implication:
- plugin and platform must both matter
- architecture cannot rely solely on conversational tone management

### 4.4 No-agreement-is-correct cases
Architecture implication:
- architecture must support successful non-settlement closure
- the system must not equate success with agreement completion

### 4.5 Escalation-correct cases
Architecture implication:
- handoff artifacts and escalation rationale are first-class outputs
- evaluator review depends on structured evidence, not only transcript feel

---

## 5. Capability implications by layer

### 5.1 Model layer implications
The model is most pressured by:
- summarization quality
- issue clarification
- reframing
- interest elicitation
- option generation
- communication smoothing

### 5.2 Platform/core implications
The platform is most pressured by:
- threshold handling
- escalation routing
- flag persistence
- state updates
- artifact generation
- continuity packet creation
- reproducibility

### 5.3 Plugin implications
The plugin is most pressured by:
- issue taxonomy
- feasibility checks
- domain-specific warnings
- hard triggers
- plugin confidence
- domain-sensitive handoff annotations

### 5.4 Integration implications
Integration is most pressured when:
- model suggestions are not correctly qualified by the plugin
- plugin signals do not reach escalation logic
- artifacts fail to preserve the reasoning trail
- evaluator outputs cannot attribute failures cleanly

---

## 6. Minimum architecture takeaways from the matrix

Architecture must support:
- calm-path continuation
- caution/narrowing path
- review path
- co-handling/handoff path
- stop-and-redirect path

Architecture must also support:
- plugin qualification before risky option advancement
- explicit missing-information tracking
- persistent flag state
- end-to-end traceability from benchmark to artifact to evaluator judgment

---

## 7. Case-level anchor row

| Benchmark ID | Primary pressures | Expected escalation posture | Required artifacts | Failure attribution hypothesis |
|---|---|---|---|---|
| D-B04 | C3, C5, C6, C8; parenting schedule structure; narrow settlement zone; unresolved logistics | M0 or M1, with M1 preferred for initial slice validation | run_meta, interaction_trace, positions, facts_snapshot, missing_info, flags, summary | model for reframing/optioning, plugin for parenting/logistics qualification, platform for caution/escalation handling, integration for artifact consistency |

---

## 8. Readiness checklist impact

Completing and adopting this document should advance:

### Section C. Evaluation readiness
- benchmark corpus is more architecture-relevant

### Section H. Development workflow readiness
- failures can be translated into architecture changes more systematically

It does not complete those sections by itself, but it closes the gap between benchmark design and runtime design.

---

## 9. Open questions

- Which canonical benchmark IDs should be used first for case-level mapping?
- Which family should be used as the anchor for the first end-to-end slice?
- Should the matrix score architecture pressure numerically in a later version?
- Which benchmark families most strongly differentiate plugin failures from platform failures?