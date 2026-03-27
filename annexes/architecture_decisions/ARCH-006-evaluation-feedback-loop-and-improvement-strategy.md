# ARCH-006: Evaluation Feedback Loop and Improvement Strategy

**Status**
Planning / v0 approved

**Purpose**
This document records the agreed strategy for closing the loop between Solomon's evaluation output and system improvement, with escalation and safety behaviour treated as constraints rather than optimisation objectives.

---

## 1. Context

Solomon produces structured, machine-readable evaluation output for every session: quality scores across twenty-two competency families, binary pass/fail overlays for five categories of serious failure, and a dedicated escalation review track with its own scores. The question this document addresses is: how should that output feed back into the system to improve performance over time, without inadvertently degrading the escalation and safety behaviour the system depends on?

The risk is not hypothetical. A naive feedback loop that optimises on aggregate quality scores could produce a system that learns to *look* like good mediation while becoming less reliable about when to stop and bring in a human. Escalation calibration in particular is dangerous to optimise without care — a model rewarded for holding M0 longer might do so at the cost of missing genuine risk signals.

---

## 2. Key Architectural Observation

The evaluation schema already encodes the right constraint structure. Its three sections map directly onto three distinct roles in a feedback loop:

| Evaluation section | Schema fields | Role in feedback loop |
|---|---|---|
| Quality scores | C1–C10, P1–P6, I1–I6 family scores and weighted totals | **Optimisation targets** — improve these |
| Automatic fail overlays | F1–F5 (pass/fail) | **Hard constraints** — never use a triggered example as positive training signal |
| Escalation review | ES1–ES5, observed/preferred mode, primary category | **Validation metrics** — confirm these do not degrade; do not train toward them |

This three-way separation means constrained improvement is architecturally natural, not a retrofit.

---

## 3. Decision: Layered Improvement Strategy

Improvement proceeds through four options in ascending order of complexity and risk. Each option is a prerequisite for the next.

### Option 1 — Human-mediated prompt and instruction revision (current phase)

The safest loop does not touch the model. Human reviewers examine sessions surfaced by the `requires_calibration_review` flag, identify recurring patterns in what went wrong, and revise system instructions, prompts, or plugin policies accordingly.

**Constraint gate:** before any revision is deployed, it runs against the full benchmark suite (D-B01 through D-B14). The fourteen benchmark cases span M0 cooperative baseline through M4/M5 full-handoff and represent the full escalation spectrum. Any revision that degrades performance on an escalation-sensitive benchmark case is rejected.

This option builds the human-reviewed corpus that makes Options 2 and 3 possible.

### Option 2 — Constrained dataset construction for fine-tuning

When the human-reviewed corpus is large enough to support fine-tuning, the constraint is applied at the data selection stage.

**Rule:** only include examples that have been human-verified on the escalation and safety dimensions — specifically, examples where an expert reviewer confirmed that the escalation behaviour was correct, not just that the quality scores were good. Sessions where escalation behaviour was questionable are excluded from the training set, even if the overall score was high.

The training signal is drawn from the quality score dimensions only. The escalation behaviour is protected by the fact that every training example already demonstrates it correctly. Automatic fail overlay triggers are treated as unconditional exclusions.

### Option 3 — Architectural separation of improvement targets

The deeper option is to treat mediation quality and escalation/safety detection as independently updatable components. The escalation detector — the logic that identifies flags, calibrates threshold bands, and selects mode — is updated on a more conservative schedule, requires higher evidence thresholds for any change, and is never updated solely on the basis of quality score improvements.

This is the correct long-term architecture for a system where some decisions need to be held to a higher standard than others. It is harder to implement if Solomon is currently a single model and is recorded here as a planning target rather than a current requirement.

### Option 4 — Adversarial red-team regression (applies from Option 1 onwards)

Independent of which improvement option is active, a dedicated adversarial benchmark should be maintained specifically to probe escalation failure modes: cases designed to tempt under-escalation, cases with subtle coercion signals, cases where impairment is not immediately obvious, cases where one party's quietness looks like cooperation but is not.

The existing fourteen benchmark cases are a starting point. Cases specifically designed to be tempting to get wrong are more valuable as safety constraints than representative cases, because they surface the failure modes that general quality improvement is most likely to introduce.

Any candidate update that fails any red-team case is automatically rejected, regardless of quality score improvement.

---

## 4. What to Avoid

**Do not close the loop on quality scores alone.** A system that improves on the scored competency dimensions without the human review filter in place is more dangerous than one that stays where it is. The quality scores measure things that are observable and measurable; escalation correctness in edge cases is not always either. The human review step is not a bottleneck to be optimised away — it is the mechanism by which the constraint remains meaningful.

**Do not treat escalation review scores as optimisation targets.** ES1–ES5 measure whether the system got escalation right. Optimising toward them directly creates the same risk as optimising toward any measurable proxy: the system learns to score well on the measure rather than to do the thing the measure is trying to capture. These scores are monitors, not objectives.

---

## 5. Current Status and Near-Term Actions

| Action | Status |
|---|---|
| Evaluation framework producing structured output | Complete |
| Benchmark suite (D-B01 – D-B14) validated and schema-conformant | Complete |
| `requires_calibration_review` flag in evaluation output | Complete |
| Human review process for flagged sessions | Defined; not yet operationalised |
| Red-team adversarial benchmark cases | Planned; not yet authored |
| Fine-tuning corpus construction (Option 2) | Deferred pending human review corpus |
| Architectural separation of escalation component (Option 3) | Long-term planning target |

The immediate next action is to operationalise the human review process for sessions surfaced by `requires_calibration_review`, and to begin authoring adversarial red-team cases that probe the escalation failure modes described in Section 4.

---

## 6. Relationship to Other Architecture Decisions

| Document | Relationship |
|---|---|
| ARCH-004 (persistence profiles) | Defines which artifacts are available for evaluator review under each policy profile |
| ARCH-005 (Layer B template engine) | Layer B will eventually produce the variation volume needed to support Options 2 and 3 |
| Evaluation schema (`schema/evaluation.schema.json`) | The constraint structure described in Section 2 is encoded directly in this schema |
