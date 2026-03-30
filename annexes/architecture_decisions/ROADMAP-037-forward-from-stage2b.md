# Forward Roadmap 037 — From Stage 2b

**Date:** 2026-03-28
**Status:** Active planning document

---

## Where we are

| Stage | Status | Evidence |
|---|---|---|
| Stage 0 — Diagnostic baseline | **Complete** | D-B04-S01, D-B07-S01, D-B11-S01 evaluated |
| Stage 1 — Five-step structured reasoning | **Complete** | CONTRACT-014, reasoning_trace per turn, D-B04-S02/D-B11-S02 |
| Stage 2 — Explicit party state artifact | **Complete** | CONTRACT-015, party_state.json, D-B04-S03/D-B11-S03 |
| Stage 2b — Party state feedback loop | **Complete** | Projection guard, D-B11-S04/S05, D-B07-S02 |
| Stage 3 — Plugin as active domain reasoner | **Complete** | domain_reasoner.py, D-B07-S10 (P6 resolved), D-B11-S06, D-B04-S04; STAGE3-FINDINGS-039 |
| Stage 4 — Option generation decoupled | **Complete** | option_generator.py, domain_reasoner Option B additive pool, D-B07-S11 (+4.5 composite, C5 4→5), D-B04-S05 regression check PASS; STAGE4-FINDINGS-041 |
| Stage 5 — Safety monitor as dedicated agent | **Complete** | STAGE5-DESIGN-042; safety_monitor.py, flags.schema.json, orchestrator/lm_engine/domain_reasoner wiring; RT01-S02/RT02-S03/RT03-S02 all PASS; commit a4b8cdd |
| Stage 6 — Full multi-agent orchestration | **Complete** | STAGE6-DESIGN-043; perception_agent.py + lm_engine wiring + evaluation extension; all 8 benchmark sessions PASS; evaluation files written; D-B04 C7 3→4 (focus competition gap resolved) |

The Stage 3 entry conditions from STAGE2B-FINDINGS-036 are all met:
1. party_state.json stability confirmed across D-B04, D-B11, D-B07
2. Feedback loop design question resolved
3. P6/C5 domain bottleneck confirmed as persistent and precisely characterised

---

## What we know from the diagnostic set

These are the measured findings that Stage 3 must address. They are not hypotheses — they are observed in multiple sessions.

### Finding 1: Option qualification is the primary bottleneck

Across every lm_runtime session:

| Session | Candidate options | Qualified options | premature_option_work |
|---|---|---|---|
| D-B04-S03 | generated | 0 | True (T7, option_generation phase) |
| D-B11-S03/S04/S05 | generated | 0 | True throughout |
| D-B07-S02 | 6 at T5 | 0 | True (option_generation phase) |

The model generates plausible candidate options but disqualifies all of them on the grounds of unresolved information gaps. In bounded-package cases (D-B07) where parties have articulated clear interests and the domain constraints are knowable, this is over-caution. The parties reached agreement_building anyway (D-B07 T6), which means the options were ready. The model couldn't release them.

**P6 scores:** 3 across all sessions. Plugin domain score plateau: 82.8 on D-B07 (S01 and S02 identical), ~88 on D-B11 (all sessions identical). P6 is the only plugin family not moving.

### Finding 2: Domain analysis is monolithic

In the current five-step prompt, Step 2 (domain analysis) and Step 3 (option scan) are both handled by the same model pass that also handles Steps 1, 4, and 5. The domain feasibility determination — is this option viable given the legal/financial/parenting realities of this specific case? — is being made simultaneously with perception, safety assessment, and response synthesis.

A practitioner reading D-B07 at T5 would immediately recognise that: tiered notice, receipt standards, and approval thresholds are all viable for this couple because (a) both parties have stated clear process interests, (b) there are no legal constraints blocking these structural options, (c) the documentation tension is a process problem, not a disputed fact. The model doesn't make this determination — it defers everything pending "more information."

### Finding 3: Perception quality is stable but not a current bottleneck

PQ band: competent across all sessions. Perception is working — the five-step structure enforces it and party_state.json accumulates it correctly. There is room to improve from competent to strong, but that improvement (Stage 5, dedicated perception agent) is not the bottleneck that is suppressing scores right now. P6 is.

### Finding 4: Integration infrastructure is in good shape

Integration scores are high (91–92) across Stage 2b sessions. The artifact layer is coherent and evaluatable. This is a good foundation for Stage 3 — the infrastructure that will consume domain reasoner output already exists and works.

---

## Stage 3 — Plugin as active domain reasoner

### What Stage 3 does

Replaces the monolithic Step 2 (domain analysis) in the five-step prompt with a **dedicated domain reasoning call**. Before the main LLM generates its five-step response, a domain reasoner is called with:

- Current session state (positions, missing_info, facts_snapshot)
- Party state from party_state.json (accumulated interests, risk signals, relational dynamic)
- Candidate option pool (from the option families known for this plugin domain)
- Plugin context (issue families active, flag types triggered, plugin confidence)

The domain reasoner returns a structured `domain_analysis` artifact with:
- `option_readiness` determination — `ready | deferred | blocked` with explicit rationale
- `qualified_candidate_options` — options the domain reasoner has assessed as feasible given current state
- `blocking_constraints` — specific constraints that would need to be resolved before blocked options become viable
- `material_gaps` — information gaps that, if resolved, would unlock deferred options
- `domain_confidence` — how certain the domain assessment is

This output replaces the model's self-generated domain_analysis block in the five-step prompt. The model at Step 2 now reads a pre-computed assessment rather than constructing one from scratch.

### Why this design

The bottleneck is not the model's knowledge of what a reasonable reimbursement option looks like. The model generates six valid options at T5 on D-B07. The bottleneck is the model's willingness to qualify them — to make the judgment that these options are ready now, not waiting for more information.

A separate reasoning call that has already made this judgment, and presents it as a structured input to the main pass, removes the qualification uncertainty from the generation context. The main model no longer needs to simultaneously decide "is this option viable?" and "what should I say?" It receives the viability determination as a prior.

### Implementation plan

**Step 3.1 — Define `domain_analysis` artifact schema (CONTRACT-016)**

Extend `schema/domain_analysis.schema.json`. Key fields:
- `option_readiness`: `ready | deferred | blocked`
- `qualified_candidates`: list with `option_label`, `feasibility_rationale`, `confidence`
- `blocking_constraints`: list with `constraint`, `what_would_resolve_it`
- `material_gaps`: inherited from current prompt structure, but now explicit
- `domain_confidence`: `low | moderate | high`
- `domain_notes`: free-text practitioner read

**Step 3.2 — Build `domain_reasoner.py` in `runtime/engine/`**

A focused LLM call. Separate system prompt that positions the model as a domain practitioner making feasibility assessments, not a mediator generating responses. Much shorter prompt than the main five-step system prompt. Uses same Anthropic client as `lm_engine.py`.

Input: structured context built from state + party_state + plugin_assessment.
Output: `domain_analysis` dict matching the schema.

**Step 3.3 — Wire into `lm_engine.py`**

Before calling `build_turn_prompt`:
1. Call `domain_reasoner.generate_domain_analysis(state, party_state, plugin_assessment)`
2. Pass result to `build_turn_prompt` as `pre_computed_domain_analysis`

**Step 3.4 — Update `prompt_builder.py`**

Replace the `=== PLUGIN ASSESSMENT ===` section with `=== DOMAIN ANALYSIS (pre-computed) ===` when a pre-computed domain analysis is available. The model's Step 2 prompt changes from "here is the plugin context, now perform domain analysis" to "here is the domain analysis, confirm and extend if warranted."

**Step 3.5 — Run Stage 3 diagnostics**

- D-B07-S03: primary target. Does the domain reasoner qualify options at T5?
- D-B04-S04: secondary. Does option_readiness progression change?
- D-B11-S06: confirm no regression on the asymmetry case

**How you know Stage 3 worked:** P6 scores improve from 3 → 4 or 5 on bounded-package cases. `option_readiness=ready` appears on at least one session where previously deferred. C5 scores improve on D-B07 specifically.

---

## Stage 4 — Option generation decoupled

### What Stage 4 does

Adds a **brainstorming agent** that runs after the domain reasoner but before the main response generation pass. It takes the party state model + domain reasoner's qualified candidates + established interests and generates an expanded option pool — without filtering for domain feasibility (that's already done) and without filtering for what to say in the response (that comes later).

The key principle from ARCH-007: **good brainstorming requires temporarily suspending constraint-checking.** The current model generates conservative options because it's simultaneously thinking about domain feasibility and what to say. The brainstorming agent doesn't generate responses — it generates ideas.

### Why Stage 4 follows Stage 3

Stage 4 requires Stage 3's domain reasoner to be working first. The brainstorming agent generates an unconstrained pool; the domain reasoner qualifies that pool. Without Stage 3, you have an unconstrained pool with no qualification mechanism, which is worse than the current state.

Stage 4 is also where C5 scores should cross from 4 into 5 territory on complex cases.

### Implementation notes

**Option pool artifact** (`option_pool.json`):
- `unconstrained_candidates`: brainstormer's raw output
- `domain_qualified`: subset that passed domain reasoner qualification
- `presented_to_parties`: subset selected for inclusion in response

This three-layer structure makes C5 evaluation precise: evaluators can see what was generated, what survived domain qualification, and what was actually offered.

---

## Stage 5 — Safety monitor as dedicated agent

### What Stage 5 does

Extracts the escalation and safety function into a dedicated agent that:
- Reads the full session history but does not generate responses
- Maintains a continuous escalation assessment (not just per-turn)
- Has exclusive authority to interrupt and escalate
- Is governed separately from all quality agents — its update path cannot be degraded by training runs that improve C3/C5 scores

This implements the constraint/optimisation separation that ARCH-006 and ARCH-007 §2 identify as architecturally necessary for safe improvement.

### Why Stage 5 is not next

The current safety/escalation framework is working correctly. ES scores are 5 across all sessions. The M0/M1 calibration on D-B11 is precisely correct. Safety is not the current bottleneck.

Stage 5 becomes essential **when we start improving the quality agents** (Stages 3–4). At that point, we need the architectural guarantee that safety monitoring cannot be degraded by a quality improvement run. That guarantee requires Stage 5 to be in place before quality agents are updated via training.

**Stage 5 must be complete before any quality agent undergoes training-based improvement.** Until then, the current embedded safety assessment is adequate.

### Stage 5 also resolves the feedback loop design question for perception

Stage 5 is also the natural home for the accumulated party_state to feed back into perception in a principled way. The current Stage 2b feedback loop is a workaround — party_state is derived post-hoc and fed back via prompt context. Stage 5's dedicated perception monitor would maintain the party state in real time, update it after each turn (not derived at session close), and make it available as a live prior for subsequent turns. This is the architecture the Stage 2b projection guard was building toward.

---

## Stage 6 — Full multi-agent orchestration

When Stages 3–5 are complete, Stage 6 runs the full five-agent stack and validates against the complete diagnostic corpus. This is the integration stage, not a new capability stage — each agent slot has been designed and tested independently through Stages 1–5.

Stage 6 also extends the evaluation framework to score perception quality and option quality as first-class dimensions (currently they're inferred from C-family scores). PQ review becomes formal scoring.

---

## Sequencing and priorities

```
Now                Stage 3 (domain reasoner)
                       ↓
              Stage 3 diagnostics (D-B07-S03, D-B04-S04, D-B11-S06)
                       ↓
              Stage 4 (option generation decoupled)
                       ↓
              Before quality training runs → Stage 5 (safety monitor)
                       ↓
              Stage 6 (full orchestration + extended evaluation)
```

**What can run in parallel:**
- Authoring adversarial red-team cases (ARCH-006) — can begin now, important for Stage 5 validation
- Expanding the diagnostic corpus to D-B12/D-B13/D-B14 — useful for Stage 3 validation but not blocking
- Layer B template engine Phase 2 (variation volume) — needed for Stage 6 corpus scale, not blocking Stages 3–5

---

## Open design questions for Stage 3

**3a. Domain reasoner as separate API call vs. same-call tool use**

Option A: Call `domain_reasoner.generate_domain_analysis()` as a separate API request before the main five-step call. Clean separation, independent token budget, fully auditable. Cost: two API calls per assistant turn.

Option B: Use the Anthropic tool use API — the main model calls a `domain_analysis` tool and receives structured output. Single API call. More complex prompt engineering.

Recommended: Option A for the initial Stage 3 diagnostic. Simplest to implement, easiest to evaluate, matches the eventual multi-agent architecture. Tool use can be explored in Stage 4 when the option generator also needs to be wired in.

**3b. Domain reasoner scope: full domain or option-qualification only?**

The domain reasoner could be scoped narrowly (option qualification only) or broadly (full domain practitioner read including material_gaps, blocking_constraints, missing-info detection).

Recommendation: Start narrow — option_readiness + qualified_candidates only. This is the precise gap the diagnostic runs identified. Expand scope in Stage 4 when the option pool artifact is introduced.

**3c. How to handle domain_analysis when option work is genuinely not ready**

The domain reasoner must handle cases where options are truly premature (early turns, missing key information, D-B11-class asymmetry). It should not push option_readiness to `ready` when the session genuinely can't support it.

Design rule: the domain reasoner gets access to party_state.json. If the party state shows active risk signals (power imbalance, conflict_avoidance pattern, information asymmetry unresolved), `option_readiness` stays `blocked` regardless of option availability. Safety signals in party_state.json are a veto on option release.

---

## Tracking

| Item | Status |
|---|---|
| CONTRACT-016 (domain_analysis schema) | **Complete** |
| `runtime/engine/domain_reasoner.py` | **Complete** |
| Stage 3 prompt for domain reasoner | **Complete** — reactive interest sufficiency, process vs. substantive distinction, scope restriction |
| `lm_engine.py` wiring | **Complete** — bracket-counter parser, max_tokens=4096 |
| `prompt_builder.py` domain analysis section | **Complete** |
| D-B07-S10 diagnostic run (P6 bottleneck) | **Complete** — PASS, P6 3→4, 4 qualified candidates at T5 |
| D-B04-S04 regression check | **Complete** — PASS, T7=ready with 2 bounded candidates, no regressions |
| D-B11-S06 safety veto regression check | **Complete** — PASS, veto correctly withheld for passive asymmetry |
| Stage 3 findings memo | **Complete** — STAGE3-FINDINGS-039.md |
| Adversarial red-team D-B-RT01 (AF-3) | **Complete** — S01 authored, behavioral target met |
| Adversarial red-team D-B-RT02 (AF-2) | **Complete** — S02 authored, CATEGORY 2 veto fires |
| Adversarial red-team D-B-RT03 (AF-1) | **Complete** — S01 authored, T6 discordant signal caught |
| CONTRACT-017 + option_pool.schema.json | **Complete** 2026-03-28 |
| `runtime/engine/option_generator.py` | **Complete** 2026-03-28 — guard cascade fix, 5-10 candidate target |
| domain_reasoner.py Stage 4 update | **Complete** 2026-03-28 — Option B additive pool, max_tokens=6000 |
| lm_engine.py Stage 4 wiring | **Complete** 2026-03-28 — prior_readiness gate removed |
| prompt_builder.py Stage 4 update | **Complete** 2026-03-28 |
| artifacts.py + policy_profiles.py Stage 4 | **Complete** 2026-03-28 — option_pool.json under eval_support/dev_verbose |
| D-B07-S11 Stage 4 diagnostic | **Complete** 2026-03-28 — PASS, composite 87.2 (+4.5), C5 4→5, pool 4→11 |
| D-B04-S05 Stage 4 regression check | **Complete** 2026-03-28 — PASS (T7=ready, 6 qualified); brainstormer silent failure at T7 noted |
| STAGE4-FINDINGS-041 memo | **Complete** 2026-03-28 |
| Codebase review Track 1-5 fixes | **Complete** 2026-03-28 — Stage 3 fallback in build_option_pool, safety_veto_reason population, DEFERRED/BLOCKED prompt rule, phase constant deduplication, domain_analysis.schema clarification, TestBuildOptionPool (8 tests) |
| STAGE5-DESIGN-042 | **Complete** 2026-03-28 — safety_monitor agent design, 8 implementation items, adversarial validation plan |
| Stage 5 implementation | **Complete** 2026-03-29 — all 8 items, RT01-S02/RT02-S03/RT03-S02 PASS, commit a4b8cdd |
| STAGE6-DESIGN-043 | **Complete** 2026-03-29 — perception agent design, OQ evaluation extension, benchmark validation plan |
| Stage 6 implementation | **Complete** 2026-03-29 — all 11 items, 8 benchmark sessions PASS, D-B04 C7 3→4 (focus competition gap resolved) |
| **ARCH-006 Option 1 — Step 5 response design revision** | **Complete** 2026-03-30 — prompt_builder.py Step 5 three-rule addition (transition marker, per-option interest-connection, tentative framing) + INSTRUCTION block update; artifacts.py _normalize_pool_entry + _normalize_confidence fixes; diagnostic D-B07-S13 Core 89.6 (+3.2 vs S12), D-B04-S07 Core 87.4/Plugin 87.6/Integration 98.0 (+5.0/+7.6/+18.0 vs S06); constraint gate 17/17 PASS; C6 4→5 confirmed on expense coordination and parenting schedule domains |
