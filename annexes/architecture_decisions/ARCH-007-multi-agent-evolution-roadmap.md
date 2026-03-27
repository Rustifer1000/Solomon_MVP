# ARCH-007: Multi-Agent Evolution Roadmap

**Status**
Planning / v0 approved

**Purpose**
This document records the agreed strategy for evolving Solomon from a single-model mediation engine to a purpose-structured multi-agent system, including the role of the evaluation framework in validating each stage and the relationship between the existing Core/Plugin architecture and the Constraints/Optimisation separation required for safe improvement.

---

## 1. Context

The current Solomon architecture is a single-model pipeline. One inference pass does everything: perceive party state, apply domain knowledge, generate options, assess safety signals, and produce a response. The runtime, artifact pipeline, escalation framework, and evaluation infrastructure surrounding that model are well-developed. The model itself is undifferentiated.

Three capability areas have been identified where the single-model approach creates structural limitations:

**Perception quality.** Reading communication styles, psychological states, and relational dynamics accurately requires sustained, focused attention to signals that are easily crowded out by the response generation task. A single inference pass trades perception depth against response fluency.

**Option creativity.** Good brainstorming requires temporarily suspending constraint-checking. When generation and qualification happen simultaneously, options produced are conservative. The non-obvious options that represent a core value proposition of Solomon (see Section 3.4 of the Foundations spec) are most likely to be discovered when the generation pass is not simultaneously filtering for domain-feasibility.

**Safety and escalation monitoring.** Escalation detection benefits from continuous, independent observation rather than being one task among several in each turn. A dedicated monitor that reads the conversation without having to generate a response can attend to cumulative patterns — across turns, not just within them — that turn-by-turn assessment misses.

The multi-agent evolution addresses all three by separating cognitive functions into dedicated components, each improvable independently.

---

## 2. The Constraint Architecture Question

Before describing the evolution stages, it is worth addressing a specific architectural question: does the existing Core/Plugin separation map cleanly onto a Constraints/Optimisation separation?

The answer is: **partially, but not cleanly, and conflating them would cause confusion.**

The Core/Plugin split was designed for **domain portability** — it defines what travels across all mediation contexts (Core) versus what is specific to a given dispute type (Plugin). This is a useful and correct separation.

The Constraints/Optimisation split needed for safe improvement (per ARCH-006) is a different thing. It asks: which capabilities must be held to a higher standard, updated more conservatively, and never degraded by a training run that improves everything else? The answer maps onto:

| Constraint track | Optimisation track |
|---|---|
| C9 (safety, escalation, boundary handling) | C1–C8, C10 (all other core families) |
| C6 (fair process — domination detection, self-determination) | P1–P6 (all plugin domain families) |
| F1–F5 (automatic fail overlays) | I1–I6 (integration quality) |
| ES1–ES5 (escalation review) | |

Most of the Core families (C1–C5, C7, C8, C10) are **quality optimisation targets**, not safety constraints. And the Plugin families, while domain-specific, may also carry constraint-weight in domains where domain-specific safety risks exist (e.g., domestic violence flags in divorce).

**Practical implication:** when building the dedicated safety monitor agent (Stage 5 below), its scope should be defined by the constraint track above, not by "everything in Core." The Core/Plugin boundary and the Constraint/Optimisation boundary are orthogonal architectural cuts, each valid for its own purpose.

---

## 3. The Five-Agent Target Architecture

The evolution targets five dedicated agents operating under the runtime orchestrator:

| Agent | Primary function | Evaluation families served |
|---|---|---|
| **Perception agent** | Reads party state, communication style, psychological signals, relational dynamics | C7, C9, C6 |
| **Domain reasoner** | Active contextual domain analysis, feasibility qualification, domain-specific risk | P1–P6 |
| **Option generator** | Unconstrained creative brainstorming followed by domain qualification | C5, P3 |
| **Safety monitor** | Continuous escalation and constraint assessment; exclusive escalation authority | C9, C6, F1–F5, ES1–ES5 |
| **Conversational mediator** | Synthesis and response generation, informed by all other agents | C1–C4, C8, C10 |

The runtime orchestrator — session state management, artifact writing, policy governance, evaluation output — already exists and requires no redesign. The agents read from and write to the shared state bus that the existing artifacts already define.

---

## 4. Evolution Stages

### Stage 0 — Diagnostic baseline (parallel; begins now)

**What it is:** A structured evaluation run designed to map capability gaps in the current single-model architecture. Not a general benchmark sweep but a targeted diagnostic against cases chosen to probe the three capability areas: perception quality in subtle or high-conflict cases, option creativity in constrained scenarios, escalation calibration where signals are present but not explicit.

**What it produces:** A scored map of where the current system is strong (these dimensions need less architectural investment) and where it fails systematically (these direct Stage priority). Simultaneously begins populating the ARCH-006 improvement corpus with human-reviewed sessions.

**How you know it worked:** The specific failure mode profile is named and evidenced: "the current system's primary limitation is X across families C\_\_ and P\_\_." This informs Stage priority.

**Runs in parallel with** Stage 1 and continues as the validation mechanism throughout all stages.

---

### Stage 1 — Structured multi-step reasoning within the single model

**What it is:** Restructure the way the single model is prompted to enforce cognitive separation before multi-agent work begins. The model runs a structured sequence rather than one undifferentiated inference pass:

1. Perception pass — what is each party experiencing?
2. Domain analysis — what are the domain-relevant observations?
3. Option scan — what are possible moves?
4. Safety assessment — any flags or threshold signals?
5. Response synthesis — given all of the above, what to say?

The outputs of intermediate steps are captured as structured artifacts, extending the existing `interaction_observations_delta` field into a full per-turn reasoning trace.

**What it produces:** A richer interaction trace where each turn's reasoning is decomposed. This serves as both an evaluation artifact and the **interface specification** for later multi-agent stages — each intermediate output defines the contract that a dedicated agent will eventually fulfil.

**How you know it worked:** C7 and C9 scores improve in cases where subtle signals were previously missed. Evaluators can read the reasoning chain, improving I3 (artifact traceability) and I5 (failure attribution) scores.

**What it unlocks:** The cognitive separation is defined and tested at the interface level before any multi-agent complexity is introduced.

---

### Stage 2 — Explicit party state modelling

**What it is:** Add a dedicated per-party state artifact — a structured, turn-by-turn model of each party's psychological state, communication style, engagement level, inferred interests beneath stated positions, and emerging risk indicators. Still single-model, but the perception function is an explicit, evaluatable output rather than an implicit input to response generation.

**What it produces:** A `party_state.json` artifact alongside the existing interaction trace. A new evaluation dimension: **perception quality** — how accurately does the system's model of each party reflect what is actually happening?

**How you know it worked:** C9 escalation calibration improves in cases where coercion or incapacity signals were previously missed. C7 emotional acknowledgment quality improves because the model has an explicit representation of party state before generating a response.

**What it unlocks:** The perception interface is well-defined. The dedicated perception agent in Stage 5 slots into a tested interface rather than requiring interface design from scratch.

---

### Stage 3 — Plugin as active domain reasoner

**What it is:** Replace the static plugin structure (issue taxonomy, red-flag lists, feasibility constraints) with a domain reasoning call. The domain reasoner takes current session state — party states, issues on the table, what has been said — and produces active contextual analysis: which options are feasible given domain realities, what domain-specific risks are present in this specific situation, what a practitioner in this domain would be thinking right now.

This is the difference between a checklist of domain red flags and a live practitioner reading — "given what this couple has described about their financial arrangements, option B will be unworkable because of the pension timing issue, there is a legal constraint that hasn't been surfaced yet, and the pattern in how Party A frames housing decisions warrants attention."

**What it produces:** Domain reasoning output as a first-class artifact. P-family evaluation scores become meaningful in a new way — not "did the plugin provide the right structure" but "did the domain reasoner provide contextually correct analysis."

**How you know it worked:** P2 (domain warning quality), P3 (feasibility qualification), and P4 (missing-information detection) scores improve measurably, specifically in cases involving complex issue coupling or domain-specific risk.

**What it unlocks:** New domains (labour, HR, commercial) become viable additions — each gets a domain reasoning agent rather than a taxonomy. Domain portability becomes genuine rather than structural.

---

### Stage 4 — Option generation decoupled

**What it is:** Separate creative option generation from response generation. A dedicated brainstorming pass takes the party state model, domain reasoner output, and established interests, and generates a broad option space without premature filtering. The domain reasoner then qualifies options against domain realities. The conversational mediator selects from qualified options rather than generating them in the moment.

The key principle: good brainstorming requires temporarily suspending constraint-checking. When generation and qualification happen simultaneously, outputs are conservative by construction. Separating them produces more creative options that are then filtered to the usable ones.

**What it produces:** An option pool artifact. A new evaluation dimension: **option quality** — diversity, creativity, domain-fit, party-interest alignment. C5 scores improve and become more meaningful.

**How you know it worked:** Evaluators note that options presented are more creative and less obvious than in Stage 0 while domain-feasibility qualification is maintained or improved.

**What it unlocks:** Option generation is independently improvable. The brainstorm agent, domain qualifier, and conversational presenter can each be improved without coupling.

---

### Stage 5 — Safety monitor as dedicated agent

**What it is:** Extract the escalation and safety function into a dedicated monitoring agent. This agent reads the conversation but does not generate responses and has no role in mediation quality scoring. Its only job is to maintain an ongoing safety and escalation assessment and to hold exclusive authority to interrupt and escalate.

This implements ARCH-006 Option 3 as a live system component. The safety monitor corresponds to the constraint track identified in Section 2 (C9, C6, F1–F5, ES1–ES5) as a running process rather than a scoring dimension. It maintains threshold band assessment continuously and can attend to cumulative patterns across turns that turn-by-turn assessment misses.

**Critical property:** this agent's update path is governed separately from all quality agents. It cannot be degraded by a training run that improves C3 or C5 scores. This is the architectural guarantee that ARCH-006's constraint/optimisation separation requires.

**How you know it worked:** Escalation calibration in subtle cases improves (ES1–ES5 scores). Crucially, escalation performance does not degrade when the mediation quality agents are subsequently updated.

**What it unlocks:** ARCH-006 Option 3 is implemented. The improvement loop can operate on quality agents independently. The safety monitor is the structural guarantee of the improvement loop's safety.

---

### Stage 6 — Full multi-agent orchestration

**What it is:** All five agents (Section 3) operating under the existing runtime orchestrator. The evaluation framework is extended to score perception quality and option generation quality as first-class dimensions alongside the existing C/P/I families.

**How you know it worked:** Systematic comparison against the Stage 0 diagnostic baseline across all evaluation dimensions. The full fourteen-case benchmark suite — spanning M0 cooperative through M4/M5 full handoff — validates that quality improvements have not degraded escalation discipline.

---

## 5. The Role of Evaluation in the Evolution

Running evaluations is not a precondition for starting this workflow. It is a continuous thread running through every stage.

The question "should we run evaluations before beginning architectural work" dissolves once evaluations are understood as the validation mechanism at each stage rather than a preliminary gate. The right frame is:

- **Stage 0 evaluations** (diagnostic): begin now, in parallel with Stage 1. Purpose is failure mode mapping and corpus building, not comprehensive documentation of current-state performance.
- **Stage N evaluations**: each stage runs its targeted evaluation set before Stage N+1 begins. Stage N's improvements must be evidenced before Stage N+1's architectural investment is committed.
- **Adversarial red-team cases** (per ARCH-006 Option 4): authoring begins during Stage 1 and runs throughout. These cases specifically probe the escalation failure modes that quality improvement is most likely to introduce.

What to avoid: running many undirected evaluations purely to build a documentation record before architectural work starts. This is sequential and adds delay without adding information. Directed evaluations — with a specific diagnostic question behind each run — accelerate the evolution by answering the questions that determine Stage priority.

---

## 6. Current Status

| Stage | Status |
|---|---|
| Stage 0 — Diagnostic baseline | Planned; not yet run |
| Stage 1 — Structured multi-step reasoning | Planned |
| Stage 2 — Explicit party state modelling | Planned |
| Stage 3 — Plugin as active domain reasoner | Planned |
| Stage 4 — Option generation decoupled | Planned |
| Stage 5 — Safety monitor as dedicated agent | Planned |
| Stage 6 — Full multi-agent orchestration | Planned |
| Adversarial red-team benchmark cases | Planned; not yet authored |

The immediate next action is to design the Stage 0 diagnostic evaluation set — specifically, to define the diagnostic questions it is intended to answer and to select or author cases that best probe perception quality, option creativity, and subtle escalation calibration.

---

## 7. Relationship to Other Architecture Decisions

| Document | Relationship |
|---|---|
| ARCH-004 (persistence profiles) | Defines which artifacts are available for evaluation under each policy profile; Stage 2 adds `party_state.json` which requires a profile decision |
| ARCH-005 (Layer B template engine) | Layer B Phase 2 provides the variation volume that Stage 0 diagnostic work and ARCH-006 corpus building eventually require |
| ARCH-006 (evaluation feedback loop) | This document is the execution roadmap for ARCH-006 Option 3; Stage 5 implements the architectural separation that ARCH-006 records as a planning target |
| ADR-001 (core/plugin boundary) | Core/Plugin boundary is preserved; this evolution does not collapse it but adds a second orthogonal cut (Constraint/Optimisation) that crosses it |
| Foundations spec Section 3.4 (creative mediation value) | Stage 4 directly targets the non-obvious option generation capability identified as a core value proposition |
