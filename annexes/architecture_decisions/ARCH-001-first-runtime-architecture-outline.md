# ARCH-001: First Runtime Architecture Outline

**Status**  
Draft / informative

**Purpose**  
This document outlines the first runtime architecture for Solomon's offline evaluation-phase implementation.

It is intended to translate the current specification, contract pack, and `D-B04-S01` worked reference run into a concrete implementation shape that a developer can begin building against.

It explicitly inherits its phase target and guardrails from `docs/03_MVP Eval Intent Lock.md`.

This document does **not** define the final production architecture.  
It is the first architecture outline for the evaluation-phase runtime only, serving the builder/evaluator team rather than a live disputant-facing product.

If there is any conflict between this document and the normative specification in `docs/` or the current schemas, the normative specification wins.

---

## 1. Architecture role

This outline describes the minimum coherent system needed to:

- run one offline synthetic mediation session
- preserve the core/plugin boundary
- emit authoritative structured artifacts
- support evaluator scoring and review
- explain continuation and escalation behavior
- support reproducible benchmark comparison later

It is intentionally narrow. It is anchored to the `D-B04-S01` baseline rather than to a generalized production platform, and it should be read as an implementation bridge for the MVP evaluation target rather than as a product-architecture commitment.

---

## 2. Baseline anchor

### 2.1 Reference slice

This architecture is anchored to:

- benchmark case: `D-B04`
- reference session: `D-B04-S01`
- plugin: divorce mediation
- expected posture: `M1` continue with caution
- active constraints:
  - unresolved school logistics
  - bounded option exploration
  - evaluator-visible artifact consistency

### 2.2 What the baseline proves

`D-B04-S01` pressures the architecture in the following ways:

- positions must remain separable from facts
- missing information must be explicit before stronger optioning
- plugin qualification must constrain runtime behavior
- escalation must remain cautious rather than binary
- artifacts must be consistent enough for evaluator reconstruction without transcript dependence

### 2.3 What the baseline does not yet prove

This slice does not yet validate:

- hard-stop safety routing
- co-handling or full handoff
- multi-plugin support beyond one real plugin
- live-session UX
- production storage or deployment infrastructure
- broad product readiness

---

## 3. Architecture goals

The first runtime architecture should optimize for:

- correctness of role and boundary handling
- clarity of state transitions
- artifact authority
- evaluator visibility
- domain qualification before stronger option commitment
- implementation simplicity

It should not optimize first for:

- maximum throughput
- multi-tenant serving
- final user-facing polish
- highly generalized plugin infrastructure
- model-routing sophistication
- settlement-rate maximization
- persuasive closure behavior

---

## 4. Architecture invariants

The runtime should treat the following as fixed:

- the core owns domain-general mediation process behavior
- the plugin owns domain structure, domain warnings, and domain feasibility qualification
- the platform owns authoritative state, artifact writing, thresholding, and routing
- the evaluator plane consumes artifacts after the run rather than participating in live control
- structured artifacts are authoritative
- persistence is policy-controlled
- human escalation is a first-class success mode
- the runtime exists to generate evaluator-reviewable evidence, not to simulate a finished live product

---

## 5. First-pass component model

The first implementation should use five runtime components and one evaluator-side consumer.

### 5.1 Session Orchestrator

Owns:

- session startup
- step ordering
- phase progression
- component invocation order
- final close-out

Minimum responsibilities:

- load case package
- initialize session state
- run one turn loop
- invoke model, plugin, and escalation logic in sequence
- invoke artifact writer

### 5.2 Core Mediation Engine

Owns:

- process framing
- issue clarification behavior
- interest elicitation behavior
- communication management behavior
- bounded option-generation behavior
- explanation drafting

In v0, this can be implemented as:

- one baseline model invocation path
- structured output normalization
- core prompts/instructions aligned to the competency model

### 5.3 Divorce Plugin Adapter

Owns:

- issue taxonomy lookup
- domain warning generation
- domain feasibility qualification
- missing-domain-information identification
- plugin confidence output
- domain-specific handoff annotations

For `D-B04-S01`, this component must be able to:

- recognize parenting-schedule structure
- surface school-logistics constraints
- warn when stronger recommendation outruns domain support
- keep phased or contingent options qualified rather than overcommitted

### 5.4 Escalation and Policy Engine

Owns:

- aggregation of model cues and plugin warnings
- severity/persistence/recoverability assessment
- authoritative escalation category
- authoritative threshold band
- authoritative mode selection
- persistence profile enforcement

For `D-B04-S01`, this component must produce:

- `E5`-shaped caution logic
- `T1` threshold handling
- `M1` continuation with caution
- explicit rationale visible in trace and flags

### 5.5 Artifact Writer

Owns:

- `run_meta.json`
- `interaction_trace.json`
- `positions.json`
- `facts_snapshot.json`
- `flags.json`
- `missing_info.json`
- `summary.txt`
- optional evaluation-facing outputs when present

This component should be treated as authoritative for output shape and write order, not the model.

### 5.6 Evaluator Consumer Layer

This is outside the live runtime loop, but the architecture must support it.

Owns:

- artifact loading
- scoring
- review order
- adjudication inputs
- regression comparison later

The runtime should be designed so this layer can work from structured artifacts without hidden internal state.

---

## 6. First-pass deployment shape

For the first implementation, use a **step-orchestrated local/offline runtime**.

This deployment shape should be understood as an evaluation-phase proving shape, not as a commitment to the eventual production topology.

Recommended shape:

1. load case package
2. initialize session state object
3. run turn step
4. normalize model output
5. run plugin qualification
6. run escalation/policy assessment
7. commit authoritative state mutations
8. append trace entry
9. write or refresh derived artifacts
10. repeat until close condition

This is preferable to an event bus for v0 because:

- it is easier to inspect
- it aligns well with evaluator-visible turn logic
- it keeps the authority boundary explicit
- it avoids overbuilding infrastructure before the second slice exists
- it better serves the MVP evaluation goal of understandable artifact generation over platform generality

---

## 7. Session-state model

The runtime should maintain one authoritative session-state object in memory during the run.

### 7.1 Required state areas

The first version should track at least:

- case identity
- session identity
- participant identities
- current phase
- issue map
- positions
- facts
- missing information
- option state
- active flags
- escalation state
- summary-relevant narrative state

### 7.2 State-authority rule

The model may suggest updates, but the platform owns final state mutation.

This means:

- model output must be normalized before state changes are committed
- plugin output must be attached as structured evidence, not as hidden reasoning
- escalation state must be computed from state plus signals, not from model prose alone

### 7.3 Recommended first-pass in-memory shape

Suggested top-level state object:

```text
session_state
  meta
  participants
  phase
  issue_map
  positions
  facts
  missing_info
  options
  flags
  escalation
  trace_buffer
  summary_state
```

---

## 8. Turn loop outline

The first runtime should use a repeatable turn loop with explicit checkpoints.

### 8.1 Step 1: Read current state

Inputs:

- current session state
- current policy profile
- active plugin
- current benchmark slice metadata

### 8.2 Step 2: Generate core mediation move

The core mediation engine produces:

- candidate conversational move
- candidate issue updates
- candidate interest updates
- candidate option updates
- candidate rationale fragments

### 8.3 Step 3: Run plugin qualification

The divorce plugin adapter produces:

- relevant issue clusters
- domain warnings
- missing domain information
- option feasibility qualification
- plugin confidence
- optional handoff annotations

### 8.4 Step 4: Run escalation and policy assessment

The escalation engine computes:

- candidate category if any
- authoritative category
- threshold band
- authoritative mode
- persistence/write permissions
- rationale summary

### 8.5 Step 5: Commit state changes

The platform commits:

- updated positions
- updated facts
- updated missing information
- updated flags
- updated option state
- updated escalation state

### 8.6 Step 6: Append trace record

The runtime writes one structured turn entry into the interaction trace buffer.

### 8.7 Step 7: Refresh output artifacts

The artifact writer writes or refreshes:

- trace
- positions
- facts snapshot
- flags
- missing info
- summary

### 8.8 Step 8: Evaluate close condition

End the session when:

- the slice objective is reached
- a stop/handoff condition is reached
- the bounded next-step state is explicit enough for evaluator review

---

## 9. D-B04-S01 sequence interpretation

Against `D-B04-S01`, the architecture should support this high-level sequence:

1. initialize parenting-schedule case context
2. frame role and process
3. capture opposing positions
4. translate positions into interest structure
5. expose missing logistics as domain-relevant blockers
6. permit only bounded phased or contingent option exploration
7. select `M1`
8. close with unresolved questions and next-step clarity

This sequence is the baseline architecture test.

---

## 10. Artifact pipeline

### 10.1 Authoritative artifacts

The runtime must emit, at minimum:

- `run_meta.json`
- `interaction_trace.json`
- `positions.json`
- `facts_snapshot.json`
- `flags.json`
- `missing_info.json`
- `summary.txt`

For `D-B04-S01`, these are sufficient to reconstruct:

- what the core did
- what the plugin contributed
- why the system did not recommend a final schedule
- why `M1` was chosen

### 10.2 Write ordering

Recommended write order:

1. `run_meta.json` at session initialization
2. `interaction_trace.json` append/update each turn
3. state artifacts update after each committed turn
4. `summary.txt` refresh after each committed turn or at close
5. evaluation artifacts after runtime completion

### 10.3 Derived-summary rule

`summary.txt` should be derived from authoritative state, not treated as an independent source of truth.

---

## 11. Persistence and policy outline

The first runtime should support named policy profiles even if only `sim_minimal` is used first.

These profiles exist to control evaluator-relevant evidence handling during the MVP evaluation phase, not to express a full production data-governance design.

### 11.1 Minimum profile support

The runtime should recognize at least:

- `dev_verbose`
- `sim_minimal`
- `redacted`

### 11.2 `D-B04-S01` expectation

For the baseline run:

- no transcript is required
- structured trace is mandatory
- state artifacts are mandatory
- evaluation output is allowed

### 11.3 Policy enforcement location

Policy enforcement belongs in the platform layer, not in prompts and not in evaluator tooling.

---

## 12. Core/plugin boundary in implementation terms

### 12.1 Core responsibilities in code terms

The core should be implemented as the owner of:

- orchestration-facing mediation prompts
- response normalization
- issue and interest extraction candidates
- option-generation candidates
- explanation and summary drafting

The core should not be treated as a hidden substitute for domain qualification, routing authority, or evaluator policy.

### 12.2 Plugin responsibilities in code terms

The plugin should be implemented as the owner of:

- domain dictionaries and issue maps
- warning rules
- feasibility checks
- domain confidence logic
- domain annotations for review or handoff

The plugin should qualify and constrain mediation behavior in-domain, but it should not silently replace the core mediation role or the platform's routing authority.

### 12.3 Boundary test from `D-B04-S01`

If the runtime reaches a fixed schedule recommendation without explicit logistics resolution, that is likely:

- a plugin failure
- an integration failure
- or both

If the runtime surfaces logistics correctly but fails to preserve them in artifacts, that is likely:

- a platform or integration failure

---

## 13. Escalation architecture outline

The escalation engine should be a separate platform component, even in v0.

### 13.1 Inputs

- current flags
- plugin warnings
- current missing info
- recent trace history
- candidate model cues
- explicit participant requests if present

### 13.2 Outputs

- authoritative escalation category
- threshold band
- selected mode
- rationale
- handoff requirement boolean

### 13.3 `D-B04-S01` baseline output

The baseline output should be:

- category: `E5`
- threshold: `T1`
- mode: `M1`
- rationale: unresolved logistics materially limit stronger optioning

---

## 14. Evaluator-plane alignment

The evaluator plane in this phase exists to judge whether the runtime produced coherent, qualified, and reviewable artifacts under bounded synthetic conditions.

It is not a live-operations console for steering user-facing mediation in real time.

The runtime must be easy to review in the order already defined for `D-B04`.

That means:

- metadata must be readable first
- summary must not hide uncertainty
- flags and missing info must support the caution posture
- positions and facts must remain distinguishable
- trace must preserve why the system narrowed instead of escalating further

The architecture should therefore optimize for evaluator reconstruction, not just runtime completion.

---

## 15. Suggested implementation modules

One reasonable v0 folder/module split would be:

```text
runtime/
  orchestrator/
  core_engine/
  plugins/
    divorce/
  escalation/
  state/
  artifacts/
  policy/
  evaluation_support/
```

This is illustrative, not normative. The important point is authority separation, not exact file layout.

---

## 16. Minimal implementation order

Build in this order:

1. case/session loader
2. session-state model
3. artifact writer for required outputs
4. one core mediation loop
5. divorce plugin qualification path
6. escalation engine
7. `D-B04-S01` replay-or-reference validation
8. evaluator-side loading and score pass

This order keeps the architecture evidence-driven and tied to the baseline slice.

---

## 17. Risks to avoid in the first architecture draft

- hiding state mutations inside model prose
- letting the plugin silently redefine core mediation behavior
- treating summary text as authoritative
- implementing escalation as a single opaque score
- overbuilding a generalized plugin marketplace abstraction
- overfitting architecture to only transcript-rich workflows

---

## 18. Immediate follow-on outputs

After this outline, the next architecture artifacts should be:

- component diagram
- artifact flow diagram
- turn-loop sequence diagram
- escalation sequence diagram
- persistence/profile matrix
- initial runtime responsibility table mapped to real modules

---

## 19. Definition of done for this outline

This outline is sufficient for the next phase when:

- a developer can identify the core runtime components
- the `D-B04-S01` baseline can be mapped onto those components without guesswork
- the authority boundary across core, plugin, platform, and evaluator is explicit
- the required artifacts have a clear place in the runtime
- the architecture can be elaborated into concrete diagrams and implementation tasks
