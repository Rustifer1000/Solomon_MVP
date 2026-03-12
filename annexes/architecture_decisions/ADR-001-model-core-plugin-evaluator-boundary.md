ADR-001: Model, Core Platform, Plugin, and Evaluator Boundary

Status
Proposed / informative for MVP evaluation phase

Purpose
This memo translates Solomon’s evaluation-phase architecture into an implementation boundary for development planning. It defines what should live in the model, what should live in the core platform, what should live in the plugin layer, and what should live in the evaluator/control plane.

Decision
Solomon should be implemented as a model-centered but platform-governed system.

The model should provide most of the language intelligence and flexible mediation behaviors.
The core platform should own policy enforcement, state, orchestration, persistence, escalation decisions, and auditability.
The plugin layer should own domain structure, domain checks, and domain-specific evaluation extensions.
The evaluator/control plane should own benchmarking, scoring, regression testing, and failure attribution.

Guiding rule
Let the model propose, let the plugin qualify, let the platform decide, and let the evaluator verify.

1. What belongs in the model

The model should own capabilities that are:

language-heavy

cross-domain

probabilistic

useful even when imperfect

checkable by downstream logic

This includes:

neutral summarization

reframing and de-escalatory wording

interest elicitation

issue-structure drafts

option generation drafts

clarification questions

explanation and rationale drafting

uncertainty expression

The model should generally not be the final authority for:

escalation outcome

policy compliance

persistence decisions

domain feasibility judgments

safety-critical thresholding

authoritative state transitions

2. What belongs in the core platform

The core platform should own capabilities that are:

cross-domain

stateful

auditable

reproducible

policy-controlled

safety-relevant

This includes:

session orchestration

authoritative session state

issue map and state snapshots

artifact generation and storage

persistence-profile enforcement

escalation routing and handoff mode selection

continuity packet generation

human review routing

run metadata and version traceability

model/provider routing

prompt/version registry

redaction hooks

policy guardrails and enforcement

The platform is the source of truth for:

what happened

what state changed

why escalation occurred

what artifacts were produced

what version/configuration generated the run

3. What belongs in the plugin layer

The plugin layer should own capabilities that are:

domain-specific

ontology-dependent

constraint-bearing

feasibility-sensitive

evaluatively distinct by domain

This includes:

domain ontology and issue taxonomy

domain vocabulary

common scenario patterns

domain red flags

domain-specific hard triggers

feasibility checks for proposed options

plugin-local confidence signals

domain-specific scoring extensions

synthetic template families

domain-specific handoff annotations

For the divorce plugin, this includes:

parenting structures

support, property, debt, and housing categories

dependency and power concerns

legal-process timing signals

parenting-sensitive process protections

4. What belongs in the evaluator/control plane

The evaluator/control plane should own capabilities that are:

comparative

benchmark-oriented

diagnostic

used to improve the system rather than run the live session

This includes:

canonical benchmark execution

rubric scoring

automatic-fail overlays

regression testing

model-to-model comparison

failure attribution

escalation calibration review

expert adjudication

benchmark coverage management

The evaluator plane should answer:

Did the model fail?

Did the platform fail?

Did the plugin fail?

Did the integration fail?

Did the escalation mode match the case?

5. Boundary tests for future planning

When deciding where a new capability belongs, apply these tests:

Put it in the model when the task is mainly generative and can be checked afterward.
Put it in the platform when the task must be deterministic, reproducible, or policy-enforced.
Put it in the plugin when correctness depends on domain structure or domain constraints.
Put it in the evaluator plane when the task exists to measure, compare, diagnose, or calibrate.

6. Development workflow implication

Development should proceed in this order:

Define artifact and interface contracts.

Build a baseline using a strong general model with prompting and structured outputs.

Add core-platform enforcement for state, persistence, escalation, and handoff.

Add plugin validators, ontology, and domain constraints.

Run canonical benchmark scenarios and score failures.

Adapt or fine-tune the model only after repeated benchmark evidence shows that the failure is truly model-resident rather than platform-resident or plugin-resident.

7. Practical rule for model adaptation

Use model adaptation only when repeated evidence shows that the failure is primarily:

conversational

interpretive

reframing-related

option-generation-related

not better solved by state, policy, or domain checks

Do not use model adaptation to hide missing:

escalation logic

persistence policy

domain feasibility checks

audit trails

reproducibility

handoff design

8. Architecture position

Solomon should not be built as a heavy software platform that substitutes for model intelligence.
Solomon should be built as a governed mediation runtime around strong models, with plugins providing domain qualification and evaluator tooling providing measurable accountability.

For repo placement, I’d use this structure:

docs/01_foundations_and_architecture.md — normative principles

docs/02_operations_and_evaluator_workflow.md — normative evaluation process

annexes/architecture_decisions/ADR-001-model-core-plugin-evaluator-boundary.md — this memo

later, if stabilized: docs/03_runtime_architecture.md
