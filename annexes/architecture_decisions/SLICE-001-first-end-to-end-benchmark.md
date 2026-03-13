
# SLICE-001: First End-to-End Benchmark Selection

**Status**  
Draft / informative

**Purpose**  
This document selects the first end-to-end benchmark slice for Solomon’s pre-architecture validation work.

The goal is not to prove the full system.  
The goal is to pick the smallest benchmark slice that can validate whether the emerging runtime architecture is coherent, evaluable, and properly split across model, platform, plugin, and evaluator responsibilities.

This document does **not** supersede the normative specification.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. Selection principle

The first slice should be:
- narrow enough to implement
- rich enough to pressure architecture meaningfully
- likely to exercise both core and plugin responsibilities
- likely to require structured artifacts, not just good wording
- suitable for evaluator review
- likely to reveal whether escalation logic is placed correctly

The first slice should **not** be:
- trivially easy
- dependent on final UI
- dependent on full production infrastructure
- so extreme that every outcome collapses immediately into stop-and-redirect

---

## 2. Recommended first slice type

**Recommended first slice:**  
A divorce-mediation benchmark with:
- active parenting-schedule conflict
- moderate-to-high trust strain
- at least one domain-specific feasibility uncertainty
- at least one caution-worthy but not yet fully dispositive escalation signal

This is recommended because it exercises:
- issue clarification
- interest elicitation
- option-generation limits
- plugin qualification
- missing-information tracking
- cautionary escalation handling
- evaluator review of whether the system continued appropriately

---

## 3. Why this slice is the best first choice

### 3.1 It pressures both core and plugin
A parenting-schedule conflict is not just a generic conversation problem.  
It requires:
- domain issue structure
- feasibility sensitivity
- sequencing awareness
- caution around family and dependency dynamics

### 3.2 It pressures artifacts
This slice requires:
- positions
- facts
- missing information
- flags
- trace updates
- likely summary and evaluator review

### 3.3 It pressures escalation without forcing immediate stop
A good first slice should test escalation logic without making architecture trivial.  
Moderate caution is better than an immediate hard-stop case for the first slice, because it reveals whether the system can:
- continue responsibly
- narrow scope appropriately
- explain why it did not escalate further yet

### 3.4 It supports failure attribution
If the system performs poorly on this slice, the team can more plausibly distinguish:
- model wording/reframing failure
- plugin feasibility failure
- platform escalation failure
- integration failure across layers

---

## 4. Proposed first-slice profile

### 4.1 Scenario profile
- Domain: divorce mediation
- Primary issue: parenting schedule
- Secondary issue: housing transition or logistics
- Trust condition: strained / low-trust
- Conflict level: moderate to high
- Power concern: mild-to-moderate indicator, not yet a fully dispositive hard stop
- Information state: important logistics unresolved
- Desired posture: continue with caution unless stronger triggers emerge

### 4.2 Architecture posture expected
This slice should most likely exercise:
- `M1` Continue with caution / narrowed scope

Potential escalation categories likely to be relevant:
- `E1` safety-risk if dependency/power concern becomes stronger
- `E3` legitimacy/trust if confidence in AI-only handling drops
- `E4` domain complexity due to unresolved logistics
- `E5` decision-quality due to missing information

### 4.3 Success condition
The runtime should:
- identify the main issues correctly
- preserve participant positions separately from facts
- record unresolved missing information
- surface caution-worthy signals
- avoid overclaiming domain feasibility
- choose a defensible continuation or review posture
- emit artifacts sufficient for evaluator review

---

## 5. Minimum runtime components required for this slice

The first slice should require at minimum:

### Model layer
- session framing
- issue clarification
- interest elicitation
- option exploration
- rationale drafting

### Core/platform layer
- state management
- artifact writing
- escalation threshold handling
- summary generation
- continuity-ready reasoning trail

### Plugin layer
- parenting-related taxonomy
- schedule/logistics feasibility sensitivity
- domain warnings
- plugin confidence
- handoff annotations if needed

### Evaluator/control layer
- benchmark record
- artifact review order
- evaluation output
- failure attribution notes

---

## 6. Minimum artifacts required from this slice

Required:
- `run_meta.json`
- `interaction_trace.json`
- `positions.json`
- `facts_snapshot.json`
- `flags.json`
- `missing_info.json`
- `summary.txt`

Recommended:
- `evaluation.json`
- `evaluation_summary.txt`

Conditional:
- continuity packet
- risk alert brief

---

## 7. Suggested first-slice execution flow

1. Select one benchmark case matching the profile above.
2. Define two synthetic participant profiles.
3. Run one offline session under `sim_minimal`.
4. Emit all required artifacts.
5. Have an evaluator review the artifacts in a fixed order.
6. Record:
   - observed escalation posture
   - preferred escalation posture
   - main failure attribution hypothesis
7. Use findings to refine:
   - artifact contracts
   - plugin interface
   - escalation authority matrix
   - component boundaries

---

## 8. Evaluator review order for the slice

Recommended order:
1. `run_meta.json`
2. `summary.txt`
3. `flags.json`
4. `positions.json`
5. `facts_snapshot.json`
6. `missing_info.json`
7. `interaction_trace.json`
8. `evaluation.json`

This order lets evaluators form a high-level view first, then inspect the structured basis for that view.

---

## 9. Reasons not to choose other slice types first

### Immediate stop-condition case
Not ideal for the first slice because:
- architecture becomes too escalation-dominant
- it reveals less about bounded continuation

### Very low-conflict easy case
Not ideal for the first slice because:
- it under-pressures plugin qualification
- it may hide architecture weaknesses

### Pure domain-complexity overload case
Not ideal for the first slice because:
- it may require too much plugin sophistication before the core runtime is validated

---

## 10. First-slice decision

**Decision:**  
The first end-to-end slice should be a divorce benchmark centered on parenting-schedule conflict with unresolved logistics and caution-worthy trust/power signals, designed to test `M1` continuation with caution as the most likely initial posture.

This is a working selection pending mapping to a specific benchmark ID.
## 10. First-slice decision

**Selected benchmark ID:** `D-B04`

**Benchmark title:**  
Parenting conflict with narrow settlement zone

**Reason for selection:**  
D-B04 best matches the first architecture-validation slice because it pressures:
- parenting-related plugin structure
- issue clarification and interest elicitation
- creative but noncoercive option generation
- missing-information tracking
- caution-capable continuation rather than immediate hard escalation

**Expected initial posture:**  
Likely `M0` or `M1`, with `M1` as the preferred working expectation for the first validation slice.

**Immediate comparator benchmark:**  
`D-B05` should be treated as the next follow-on comparator for fair-process and asymmetry stress testing.

---

## 11. What must be chosen next

To operationalize this slice, the team still needs to choose:
- one specific benchmark ID
- one participant-A profile
- one participant-B profile
- one prompt bundle version
- one plugin version
- one evaluator review template

---

## 12. Readiness checklist impact

Completing and adopting this document should advance:

### Section C. Evaluation readiness
- a first architecture-relevant slice is chosen

### Section H. Development workflow readiness
- the team has a concrete target for end-to-end validation

It does not complete those sections by itself, but it creates the anchor the architecture phase needs.

---

## 13. Open questions

- Which exact benchmark ID best fits this profile?
- Should the first slice include one explicit human-request-for-review event, or leave that for slice 2?
- Should the first slice end before option packaging, or include early option generation?
- How much transcript-like content, if any, should be persisted under `sim_minimal` during this first validation run?