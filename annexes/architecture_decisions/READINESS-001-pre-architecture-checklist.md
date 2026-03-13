# READINESS-001: Pre-Architecture Readiness Checklist

**Status**  
Draft / informative

**Purpose**  
This checklist defines the minimum readiness threshold Solomon should meet before translating the current specification package into a concrete runtime architecture.

**Readiness principle**  
Solomon is ready for architecture translation when the team can run and evaluate at least one offline divorce-mediation case end-to-end, explain why the system continued or escalated, and attribute failures to the model, core platform, plugin layer, or integration boundary.

---

## A. Core conceptual readiness

### A1. Core competency model is stable
- [ ] The team agrees on the core competency families C1-C10.
- [ ] Each competency has a plain-language definition.
- [ ] Each competency has at least one observable success condition.
- [ ] Each competency has at least one observable failure condition.
- [ ] The team agrees on which competencies are core-general rather than domain-specific.

### A2. Core non-goals are stable
- [ ] The team agrees Solomon is not a judge, arbitrator, therapist, or legal decision-maker.
- [ ] The team agrees Solomon is not optimized for settlement at the expense of autonomy.
- [ ] The team agrees human mediation is a normal success mode, not only a fallback.

### A3. Expert-in-the-middle principle is stable
- [ ] The team agrees correct escalation can be evidence of good performance.
- [ ] The team agrees autonomous handling is not always the preferred mode.
- [ ] The team agrees human review, co-handling, and handoff must be first-class system outcomes.

**Exit condition for Section A:**  
The team can describe Solomon’s purpose, role limits, and success conditions in one page without contradiction.

---

## B. Boundary readiness

### B1. Core / plugin boundary is stable
- [ ] The team has a written definition of what the core owns.
- [ ] The team has a written definition of what the plugin owns.
- [ ] The team has a written non-substitution rule for plugins.
- [ ] The team agrees what the plugin may extend.
- [ ] The team agrees what the plugin may not override.

### B2. Model / platform / plugin / evaluator split is stable
- [ ] The team has reviewed the current boundary memo.
- [ ] The team agrees the model is not the final authority for escalation, policy, or persistence.
- [ ] The team agrees the platform is the authoritative owner of state and artifacts.
- [ ] The team agrees the plugin is the authoritative owner of domain ontology, domain checks, and domain red flags.
- [ ] The team agrees the evaluator plane is responsible for benchmarking, scoring, regression, and failure attribution.

### B3. Interface contracts are drafted
- [ ] Plugin input contract exists.
- [ ] Plugin output contract exists.
- [ ] Escalation packet contract exists.
- [ ] Session-state contract exists.
- [ ] Artifact naming and folder conventions exist.

**Exit condition for Section B:**  
A developer can tell, for any new feature, whether it belongs in the model, core platform, plugin, or evaluator plane.

---

## C. Evaluation readiness

### C1. Evaluation objective is stable
- [ ] The team agrees the first phase is offline and synthetic.
- [ ] The team agrees the purpose is to test legitimacy, safety, self-determination, fair participation, and escalation quality before live deployment.
- [ ] The team agrees architecture choices will be driven by evaluation evidence.

### C2. Canonical benchmark set exists
- [ ] A first benchmark set has been assembled.
- [ ] Each benchmark has an ID.
- [ ] Each benchmark has a short scenario summary.
- [ ] Each benchmark has intended challenge types.
- [ ] Each benchmark has expected focal scoring areas.
- [ ] Each benchmark has an expected escalation posture where relevant.

### C3. Coverage is sufficient for first-pass architecture work
- [ ] Low-conflict workable cases are covered.
- [ ] Moderate-conflict cases are covered.
- [ ] High-conflict / low-trust cases are covered.
- [ ] Power-imbalanced cases are covered.
- [ ] Emotionally escalated cases are covered.
- [ ] Narrow-settlement-zone cases are covered.
- [ ] No-agreement-is-correct cases are covered.
- [ ] Escalation-to-human-is-correct cases are covered.

### C4. Synthetic user design exists
- [ ] Synthetic role profiles exist for both participants.
- [ ] Profiles include goals, concerns, red lines, communication style, and disclosure tendencies.
- [ ] Profiles are structured enough for repeatable generation.

**Exit condition for Section C:**  
The team can explain how benchmark evidence will validate or invalidate a future architecture choice.

---

## D. Scoring readiness

### D1. Core scoring model is usable
- [ ] Core scoring families and weights are frozen.
- [ ] Evaluators can apply the 1-5 scale consistently.
- [ ] Interpretation bands are defined.
- [ ] Automatic-fail overlays are defined clearly enough to apply.

### D2. Plugin and integration scoring are drafted
- [ ] Plugin-domain scoring categories are drafted.
- [ ] Core/plugin integration scoring categories are drafted.
- [ ] The team can identify whether a failure is core, plugin, or integration.

### D3. Evaluator workflow is practical
- [ ] A score sheet template exists.
- [ ] Reviewer instructions exist.
- [ ] Artifact review order exists.
- [ ] Calibration guidance exists for borderline cases.

**Exit condition for Section D:**  
Two evaluators can review the same run and produce meaningfully comparable judgments.

---

## E. Escalation readiness

### E1. Escalation framework is stable
- [ ] Modes M0-M5 are agreed.
- [ ] Categories E1-E6 are agreed.
- [ ] Threshold bands T0-T4 are agreed.
- [ ] The team agrees which hard triggers are universal.
- [ ] The team agrees which hard triggers are plugin-local.

### E2. Escalation decision policy is concrete
- [ ] The team can define severity, persistence, and recoverability.
- [ ] The team can define a sufficient repair attempt.
- [ ] The team can define when caution is enough and when human review is mandatory.
- [ ] The team can define the minimum required rationale for escalation.

### E3. Handoff expectations are concrete
- [ ] The minimum continuity packet fields are frozen.
- [ ] Human review expectations are documented.
- [ ] Co-handling and full handoff are distinguishable in practice.

**Exit condition for Section E:**  
The team can explain why a given case should continue, narrow, escalate, hand off, or stop.

---

## F. Artifact readiness

### F1. Source-of-truth artifacts are defined
- [ ] `run_meta.json` contract exists.
- [ ] `interaction_trace.json` contract exists.
- [ ] `positions.json` contract exists.
- [ ] `facts_snapshot.json` contract exists.
- [ ] `flags.json` contract exists.
- [ ] `missing_info.json` contract exists.
- [ ] `summary.txt` contract exists.

### F2. Required optional artifacts are defined
- [ ] Intake brief contract exists.
- [ ] Early dynamics brief contract exists.
- [ ] Risk alert brief contract exists.
- [ ] Evaluation artifact contract exists.
- [ ] Expert review artifact contract exists.
- [ ] Continuity packet contract exists.

### F3. Trace semantics are concrete
- [ ] Required turn fields are defined.
- [ ] `state_delta` semantics are defined.
- [ ] `risk_check` semantics are defined.
- [ ] Phase labels are defined.
- [ ] Rules for transcript persistence vs trace persistence are defined.

**Exit condition for Section F:**  
A developer can build storage and orchestration without guessing what must be emitted.

---

## G. Reproducibility and policy readiness

### G1. Persistence profiles are stable
- [ ] `dev_verbose` is defined.
- [ ] `sim_minimal` is defined.
- [ ] `redacted` is defined.
- [ ] Allowed outputs are listed per profile.
- [ ] Forbidden outputs are listed per profile.

### G2. Redaction and policy hooks are defined
- [ ] Redaction points are identified.
- [ ] Evaluator-visible vs runtime-only artifacts are distinguished.
- [ ] Policy enforcement responsibility is assigned to the platform.

### G3. Reproducibility contract is stable
- [ ] Required metadata fields are frozen.
- [ ] Seed handling is defined.
- [ ] Model/provider configuration fields are defined.
- [ ] Prompt/version identifiers are defined.
- [ ] Code-version traceability is defined.

**Exit condition for Section G:**  
A reviewer can determine what configuration produced a result and what policy profile governed its outputs.

---

## H. Development workflow readiness

### H1. Baseline implementation strategy exists
- [ ] The team agrees to start with a strong baseline model plus prompting and structured outputs.
- [ ] The team agrees not to fine-tune first.
- [ ] The team agrees platform enforcement and plugin validation come before adaptation decisions.

### H2. Failure attribution workflow exists
- [ ] The team can classify a failure as model-resident, platform-resident, plugin-resident, or integration-resident.
- [ ] The team has a procedure for translating benchmark failures into architecture changes.
- [ ] The team has a procedure for deciding whether a failure justifies model adaptation.

### H3. Go / no-go rule exists
- [ ] The team has a named readiness owner.
- [ ] The team has a decision date for architecture translation.
- [ ] The team has an explicit minimum threshold for proceeding.

**Exit condition for Section H:**  
The team knows what evidence is required to move from specification work to architecture work.

---

## Final go / no-go decision

### Proceed to architecture translation only if:
- [ ] Sections A-H are materially complete.
- [ ] No major contradiction remains in the core competency model.
- [ ] No major contradiction remains in the core/plugin boundary.
- [ ] At least one offline benchmark run can be evaluated end-to-end.
- [ ] The team can explain the reason for continuation or escalation in that run.
- [ ] The team can attribute the main failures in that run to the correct layer.

### Do not proceed yet if:
- [ ] The team is still debating what Solomon fundamentally is.
- [ ] The team cannot distinguish core from plugin responsibilities.
- [ ] The scoring model is too vague to compare runs.
- [ ] The escalation framework cannot be applied consistently.
- [ ] Required artifacts are not yet specified.
- [ ] The team would be forced to hide unresolved system design inside the model.

---

## Recommended sign-off fields

- **Readiness owner:**  
- **Date reviewed:**  
- **Sections complete:**  
- **Blocking gaps:**  
- **Decision:** Go / No-Go  
- **Notes:**  