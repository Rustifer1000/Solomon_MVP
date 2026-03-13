# SPEC-TO-ARCH-INPUTS

**Status**  
Draft / informative

**Purpose**  
This document converts the Solomon MVP evaluation-phase specification into a concrete set of inputs for runtime architecture design.

It is intended to answer:

- what architecture must treat as fixed
- what architecture must treat as provisional
- what contracts and decisions must exist before architecture design begins
- what first implementation slice should be used to validate the architecture

This document does **not** replace the normative specification in `docs/` or the schemas.  
If there is any conflict between this document and the normative specification, the normative specification wins.

---

## 1. Role of this document

This document is the handoff layer between:

1. the evaluation-phase specification
2. pre-architecture planning
3. first-pass runtime architecture design

It should be used together with:

- `ADR-001-model-core-plugin-evaluator-boundary.md`
- `READINESS-001-pre-architecture-checklist.md`
- `STATUS-001-spec-to-architecture-plan.md`

---

## 2. Architecture framing

### 2.1 What the architecture phase is trying to produce

The architecture phase should produce a first concrete runtime design for Solomon’s **offline evaluation-phase implementation**.

That architecture is not yet the final production architecture.  
It is the minimum coherent system required to:

- run offline synthetic mediation sessions
- emit authoritative evaluation artifacts
- support scoring and review
- support escalation and handoff logic
- separate core-general mediation behavior from plugin-domain logic
- preserve traceability and reproducibility

### 2.2 What architecture should not try to solve yet

The architecture phase should not attempt to finalize:

- live deployment architecture
- final UI
- full multi-domain product architecture
- final production inference stack
- every future plugin type

Those are outside the current phase and should not drive premature complexity.

---

## 3. Fixed inputs from the specification

These are the items architecture should treat as currently fixed enough to design around.

### 3.1 System identity
Solomon is an **expert-in-the-middle AI mediation system**.

Architecture should assume:
- autonomous handling is sometimes appropriate
- human mediation remains a normal and important success mode
- correct escalation is often evidence of good performance, not failure

### 3.2 Core system pattern
Architecture should assume a **core-plus-plugin** structure:
- the **core** owns domain-general mediation process behavior
- the **plugin** owns domain structure, domain constraints, and domain-specific checks

### 3.3 First evaluation setting
Architecture should assume the first implementation is:
- offline
- synthetic
- evaluator-facing
- artifact-centered

### 3.4 First domain
Architecture should assume:
- the first plugin is **divorce mediation**
- divorce is the initial test domain, not the definition of the whole system

### 3.5 Primary success criteria
Architecture should optimize first for:
- legitimacy
- safety
- self-determination
- fair participation
- noncoercion
- correct escalation

Architecture should **not** optimize first for:
- settlement rate
- agreement completion
- maximum autonomy at all costs

---

## 4. Architecture invariants

The following should be treated as non-negotiable design constraints.

### I-001. Human escalation is first-class
The runtime must support:
- continued autonomous handling
- narrowed autonomous handling
- human review
- co-handling
- full handoff
- stop-and-redirect modes

### I-002. Structured artifacts are authoritative
The runtime must produce structured outputs that serve as the source of truth for evaluation.

### I-003. Core and plugin remain separable
Domain-specific logic should not silently collapse into the core.

### I-004. Policy-controlled persistence is mandatory
Persistence must be explicitly governed by policy profile rather than assumed.

### I-005. Reproducibility and traceability are required
Each run must be attributable to:
- a specific case definition
- a model/configuration
- a prompt/version set
- a policy profile
- a code version

### I-006. Evaluation drives architecture
Architecture choices should be justified by benchmark and evaluator needs, not only by implementation convenience.

---

## 5. Architecture responsibility split

This section defines the intended first-pass boundary that architecture work should assume.

### 5.1 Model layer
The model layer should own:
- conversational generation
- reframing
- summarization
- interest elicitation
- issue-structure drafts
- option-generation drafts
- rationale drafting
- uncertainty expression

The model layer should **not** be the final authority for:
- escalation outcome
- persistence policy
- domain feasibility decisions
- authoritative state mutation
- final audit record structure

### 5.2 Core platform layer
The core platform should own:
- session orchestration
- authoritative runtime state
- issue map state
- facts/positions snapshots
- artifact generation
- persistence-profile enforcement
- redaction hooks
- escalation routing
- continuity packet generation
- human review routing
- run metadata
- version/configuration traceability

### 5.3 Plugin/domain layer
The plugin layer should own:
- ontology / issue taxonomy
- domain vocabulary
- domain red flags
- domain-specific hard triggers
- domain feasibility checks
- plugin confidence signals
- domain-specific evaluation extensions
- domain-specific handoff annotations
- synthetic template families

### 5.4 Evaluator/control layer
The evaluator/control layer should own:
- benchmark execution
- rubric scoring
- automatic-fail overlays
- regression comparison
- expert review
- calibration workflow
- failure attribution
- architecture feedback from benchmark results

---

## 6. Required architecture inputs

The following inputs must exist before runtime architecture design can proceed cleanly.

### 6.1 Competency-to-runtime mapping
Need:
- each core competency family mapped to observable runtime behaviors
- each competency mapped to at least one artifact or state representation
- each competency mapped to at least one likely failure mode

Target output:
- `competency_to_runtime_matrix.md` or equivalent working table

### 6.2 Core/plugin interface draft
Need:
- plugin inputs
- plugin outputs
- required metadata
- extension points
- non-substitution guardrails

Target output:
- `plugin_interface_v0.md` or equivalent contract draft

### 6.3 Escalation authority matrix
Need:
- which cues the model may surface
- which signals the plugin may add
- which thresholds the platform owns
- which conditions require human review or stop

Target output:
- `escalation_authority_matrix.md`

### 6.4 Artifact contract pack
Need minimum contracts for:
- `run_meta.json`
- `interaction_trace.json`
- `positions.json`
- `facts_snapshot.json`
- `flags.json`
- `missing_info.json`
- `summary.txt`
- continuity packet
- optional briefs
- evaluation and expert review outputs

Target output:
- contract drafts or schema drafts for the first implementation slice

### 6.5 Persistence/profile matrix
Need:
- profile names
- allowed writes
- forbidden writes
- redaction points
- evaluator-visible outputs
- runtime-only outputs

Target output:
- `persistence_profiles_matrix.md`

### 6.6 Benchmark-to-capability matrix
Need:
- benchmark scenarios mapped to competencies
- benchmark scenarios mapped to escalation expectations
- benchmark scenarios mapped to domain/plugin requirements
- benchmark scenarios mapped to required artifacts
- benchmark scenarios mapped to likely failure attribution classes

Target output:
- `benchmark_to_capability_matrix.md`

---

## 7. Runtime contracts architecture should assume

Architecture design should assume these contract areas exist, even if schema details are still being finalized.

### 7.1 Session state contract
Must represent at least:
- case identity
- session identity
- participant context
- issue map
- facts known
- positions known
- open questions
- option state
- escalation state
- current phase

### 7.2 Interaction trace contract
Must represent at least:
- turn index
- timestamp
- role
- phase
- state delta
- risk check
- rationale-supporting signals

### 7.3 Escalation packet contract
Must represent at least:
- case ID
- plugin type
- escalation category
- threshold band
- concise rationale
- issue map
- concerns/interests
- unresolved questions
- risk flags
- interventions already attempted
- current option-generation state
- uncertainty notes
- recommended next human role

### 7.4 Reproducibility contract
Must represent at least:
- schema version
- timestamp
- seed if any
- model/provider configuration
- prompt identifiers or version strings
- policy profile
- code version
- environment marker

---

## 8. Provisional areas architecture should not over-freeze

These areas remain important, but architecture should not become overly rigid around them yet.

### P-001. Final model strategy
Do not assume early whether Solomon needs:
- prompting only
- structured output prompting
- routing across multiple models
- fine-tuning
- post-training
- tool-augmented reasoning

Architecture should preserve optionality.

### P-002. Final UI and user workflow
Architecture should support evaluator-facing offline workflows first.

### P-003. Multi-plugin generalization depth
Architecture should preserve plugin boundaries now without overbuilding a full plugin marketplace abstraction.

### P-004. Full production persistence posture
Architecture should support policy-controlled persistence now without assuming the final deployment storage design.

---

## 9. First implementation slice

Architecture design should be anchored to a single narrow end-to-end slice.

### 9.1 Objective
Design the smallest runtime capable of validating the architecture assumptions.

### 9.2 Recommended first slice
One offline synthetic divorce-mediation session with:
- one selected benchmark case
- two synthetic participant profiles
- one model-backed conversation loop
- one divorce plugin
- one core orchestration path
- one escalation path
- one artifact writer
- one evaluator review pass

### 9.3 Minimum outputs from first slice
The slice should produce at least:
- `run_meta.json`
- `interaction_trace.json`
- `positions.json`
- `facts_snapshot.json`
- `flags.json`
- `missing_info.json`
- `summary.txt`

If triggered:
- continuity packet
- risk alert brief
- evaluation artifact

### 9.4 Success condition for first slice
The slice is successful when:
- the session can be run deterministically enough to inspect
- required artifacts are emitted
- an evaluator can score the run
- the continuation/escalation decision can be explained
- major failures can be attributed to the correct layer

---

## 10. Expected outputs of the next architecture phase

Once this input pack is complete, the next phase should produce:

- first runtime architecture memo
- component diagram
- artifact flow diagram
- session-state model
- continuation sequence diagram
- escalation/handoff sequence diagram
- plugin interface v0
- runtime artifact contract pack
- first benchmark validation plan

---

## 11. Open questions architecture may need to resolve

These are legitimate architecture questions, but should be resolved using the inputs above rather than by intuition alone.

- Should the runtime be event-driven, pipeline-oriented, or step-orchestrated?
- How much state should be recomputed versus persisted?
- Where should plugin checks occur in the turn loop?
- Should risk detection be turn-local, rolling, or both?
- How should model outputs be normalized before artifact writing?
- What is the minimal abstraction needed to support a second plugin later?

---

## 12. Go/no-go rule for entering architecture design

Proceed to runtime architecture design only when:
- the boundary memo exists
- the readiness checklist exists
- the status tracker exists
- the required architecture inputs are at least materially drafted
- one first implementation slice has been chosen
- no unresolved contradiction remains in the core/platform/plugin/evaluator split

Do not proceed yet if:
- the team is still debating what Solomon fundamentally is
- artifact requirements are still ambiguous
- the escalation boundary is still vague
- plugin responsibilities are still mixed into core assumptions
- architecture would be forced to hide unresolved design decisions inside model behavior

---

## 13. Recommended maintenance rule

Update this document when:
- a fixed input changes
- a provisional area becomes stable
- a contract draft is added
- the first implementation slice changes
- the project moves into formal runtime architecture design

When a substantial portion of this document becomes stable and implemented, its contents may be promoted into a future normative runtime architecture document.