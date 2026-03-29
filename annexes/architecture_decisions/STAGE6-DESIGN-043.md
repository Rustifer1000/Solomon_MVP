# STAGE6-DESIGN-043: Full Multi-Agent Orchestration

**Date:** 2026-03-29
**Status:** Active design document
**Prerequisite:** Stage 5 complete (commit a4b8cdd)

---

## 1. What Stage 6 Is

Stage 6 completes the five-agent target architecture defined in ARCH-007 §3. Three of the five agents are already operational:

| Agent | Status |
|---|---|
| Perception agent | **Not yet extracted** — perception is embedded in `perception.py` (deterministic scaffold) + main LM Step 1 |
| Domain reasoner | **Complete** (Stage 3) — `runtime/engine/domain_reasoner.py` |
| Option generator | **Complete** (Stage 4) — `runtime/engine/option_generator.py` |
| Safety monitor | **Complete** (Stage 5) — `runtime/engine/safety_monitor.py` |
| Conversational mediator | **Operational** — `runtime/engine/lm_engine.py` main pass |

Stage 6 adds:
1. A dedicated **perception agent** (`runtime/engine/perception_agent.py`) — a focused LM call whose only job is to perceive party state at depth
2. Wiring of the perception agent output into the existing pipeline
3. Extended evaluation: PQ scoring and option quality scoring as first-class evaluation dimensions
4. Full benchmark validation against the complete diagnostic corpus

---

## 2. The Perception Gap

DIAG-001 §4 identifies the primary remaining architectural gap precisely:

> **Perception quality degrades when cognitive demand shifts to logistics and option generation.**
>
> D-B04 (logistics/options focus): PQ band **developing** — C7=3, weakest emotional state modeling in corpus.
>
> The single-model architecture cannot simultaneously attend to party state at full depth and generate domain-qualified options.

The current `perception.py` (`build_perception_context()`) is a deterministic rule-based scaffold. It derives perception from flags, positions, and trace buffer tags — correct and fast, but structurally limited: it cannot perceive subtle psychological signals, communication style shifts, or what a party is NOT saying. Its output feeds the five-step prompt as a structured prior.

The main LM's Step 1 (embedded in the five-step prompt) performs LM-based perception but is subject to focus competition: when the session demands option generation and domain qualification at the same turn, Step 1 perception is crowded out.

The dedicated perception agent resolves this by running a focused, independent LM pass — with its own token budget, its own system prompt, and no response-generation task — before the option generator, domain reasoner, or main pass run.

---

## 3. Perception Agent Architecture

### 3.1 Position in the Pipeline

```
[per-turn trigger]
      │
      ▼
build_perception_context()       ← deterministic scaffold (unchanged)
      │
      ▼
generate_perception_agent_result()   ← NEW: LM-based perception agent (Stage 6)
      │
      ▼
generate_safety_monitor_result()     ← Stage 5 (unchanged)
      │
      ▼
generate_option_pool()               ← Stage 4 (unchanged; now receives perception_agent_result)
      │
      ▼
generate_domain_analysis()           ← Stage 3 (unchanged; now receives perception_agent_result)
      │
      ▼
build_turn_prompt()                  ← Stage 1 (receives perception_agent_result as structured prior)
      │
      ▼
main LM call (conversational mediator)   ← Stage 1/5-step
```

The perception agent runs before the option generator and domain reasoner, so they can receive its output as context. The safety monitor also runs before those, and the perception agent result is available to it — but the safety monitor's cross-turn pattern detection does not depend on it.

### 3.2 Inputs

```python
generate_perception_agent_result(
    turn_index: int,
    timestamp: str,
    state: dict,
    scaffold_perception: PerceptionContext,    # from build_perception_context()
    interaction_history: list[dict],           # full trace_buffer
) -> dict   # PerceptionAgentResult
```

The agent has access to:
- Full interaction history (all prior turns, verbatim message text)
- Accumulated party state (from prior reasoning traces)
- Active flags
- Scaffold perception output (as a prior — the agent can confirm, deepen, or diverge from it)

### 3.3 Output: PerceptionAgentResult

```json
{
  "schema_version": "perception_agent.v0",
  "turn_index": 9,
  "timestamp": "2026-03-29T00:00:00Z",
  "confidence": "high | moderate | low | null",

  "party_a": {
    "emotional_state": "string — LM-assessed, richer than scaffold categories",
    "emotional_trajectory": "stable | escalating | de-escalating | volatile",
    "engagement_quality": "genuine | performative | disengaged | compliant_only",
    "communication_style": "direct | indirect | deflecting | avoidant | collaborative",
    "inferred_interests": ["string"],
    "inferred_concerns": ["string — what worries them, beneath stated positions"],
    "unsaid_signals": ["string — what this party is NOT saying but the pattern implies"],
    "relational_posture": "string"
  },

  "party_b": {
    "emotional_state": "string",
    "emotional_trajectory": "stable | escalating | de-escalating | volatile",
    "engagement_quality": "genuine | performative | disengaged | compliant_only",
    "communication_style": "direct | indirect | deflecting | avoidant | collaborative",
    "inferred_interests": ["string"],
    "inferred_concerns": ["string"],
    "unsaid_signals": ["string"],
    "relational_posture": "string"
  },

  "relational_dynamic": "string",
  "dynamic_trajectory": "improving | stable | deteriorating | volatile",

  "perception_signals": ["string — notable patterns observed this turn"],
  "scaffold_divergence": "string | null — where LM assessment differs from scaffold",
  "perception_notes": ["string — key items the conversational mediator must hold before responding"],

  "veto_signals": ["string | null — any perception-layer signals that should be passed to the safety monitor or domain reasoner"],

  "_null_result": false
}
```

Null result structure (turns 1–2, or on exception):
```json
{
  "schema_version": "perception_agent.v0",
  "turn_index": 1,
  "confidence": null,
  "_null_result": true
}
```

### 3.4 System Prompt Principles

The perception agent prompt positions the agent as a clinical observer — not a mediator, not a domain expert, not a safety assessor. Its only job is to perceive:

- What is this party experiencing right now?
- What do they want that they haven't said directly?
- What are they avoiding saying?
- How is the relational dynamic shifting over time?
- Where does the interaction history show patterns the scaffold's rule-based assessment cannot detect?

The prompt must explicitly prohibit:
- Response generation
- Option generation or evaluation
- Safety assessment (that is the safety monitor's role)
- Domain feasibility judgments

Conservative calibration: the agent should express moderate or low confidence on turns 1–4, and only escalate to high when multiple converging signals are present. Unsaid signals and engagement quality should be flagged with appropriate uncertainty rather than asserted.

### 3.5 Fail-Safe Behaviour

Identical pattern to `safety_monitor.py`:
- Returns null result on turns 1–2 without API call
- Returns null result (logs to stderr) on any exception
- Pipeline continues unchanged in both cases — the scaffold's `PerceptionContext` remains the fallback

### 3.6 New Fields the Agent Adds Over the Scaffold

| Field | Scaffold can provide | Perception agent adds |
|---|---|---|
| `emotional_state` | Rule-based categories from flag types | Nuanced LM-assessed state with trajectory |
| `emotional_trajectory` | No | Yes |
| `engagement_quality` | No | Yes — detects `compliant_only` (complements safety monitor CATEGORY 1) |
| `communication_style` | No | Yes |
| `inferred_interests` | From proposals + missing_info | From full conversation history, subtext, pattern |
| `inferred_concerns` | No | Yes |
| `unsaid_signals` | No | Yes — the most valuable new dimension |
| `relational_dynamic` | Rule-based from flag types | LM-assessed from full history |
| `dynamic_trajectory` | No | Yes |
| `scaffold_divergence` | N/A | Documents disagreements between scaffold and LM |

---

## 4. Wiring Changes

### 4.1 `runtime/orchestrator.py`

Add perception agent call block after safety monitor block, before option generator:

```python
from runtime.engine.perception_agent import generate_perception_agent_result

perception_agent_result = generate_perception_agent_result(
    turn_index=plan_entry.turn_index,
    timestamp=plan_entry.timestamp,
    state=state,
    scaffold_perception=scaffold_perception,
    interaction_history=list(state.get("trace_buffer", [])),
)
```

Pass `perception_agent_result` to `generate_lm_assistant_turn`.

### 4.2 `runtime/engine/lm_engine.py`

- `generate_lm_assistant_turn` signature: add `perception_agent_result: dict | None = None`
- Pass to `generate_option_pool`, `generate_domain_analysis`, `build_turn_prompt`
- Store in `reasoning_trace` via `_build_reasoning_trace`

### 4.3 `runtime/engine/option_generator.py`

- `generate_option_pool` signature: add `perception_agent_result: dict | None = None`
- Extract `party_a.inferred_interests`, `party_b.inferred_interests`, `party_a.inferred_concerns`, `party_b.inferred_concerns` and inject into brainstormer context
- Richer interest/concern signals → more targeted option generation

### 4.4 `runtime/engine/domain_reasoner.py`

- `generate_domain_analysis` signature: add `perception_agent_result: dict | None = None`
- Inject perception signals into domain context before option qualification
- `engagement_quality=compliant_only` from either party is a soft signal to the domain reasoner to defer option readiness unless safety monitor has already cleared it

### 4.5 `runtime/engine/prompt_builder.py`

Replace (or supplement) the scaffold perception section with the perception agent output when available. The main LM still receives perception as a structured prior, but the prior is now LM-assessed rather than rule-derived.

### 4.6 `runtime/reviewer_transcript_rendering.py`

Add `_render_perception_agent_summary()` block alongside the existing safety monitor log section. Shows per-turn perception output with trajectory and divergence notes.

---

## 5. Schema

### 5.1 `schema/perception_agent.schema.json`

New schema defining `PerceptionAgentResult`. Key constraints:
- `additionalProperties: false`
- All party fields nullable (fail-safe)
- `_null_result: boolean` as top-level flag
- `confidence` enum: `"high" | "moderate" | "low" | null`
- `engagement_quality` enum: `"genuine" | "performative" | "disengaged" | "compliant_only" | null`
- `communication_style` enum: `"direct" | "indirect" | "deflecting" | "avoidant" | "collaborative" | null`
- `dynamic_trajectory` enum: `"improving" | "stable" | "deteriorating" | "volatile" | null`
- `emotional_trajectory` enum: `"stable" | "escalating" | "de-escalating" | "volatile" | null`

---

## 6. Extended Evaluation Framework

### 6.1 PQ Scoring: From Proxied to Direct

Current state: PQ scores in `perception_quality_review` are proxied from action quality (C7, C6, C9). DIAG-001 §3 documents this as a Stage 0 methodological limitation.

Stage 6 makes PQ scoring direct: the evaluator reads the `perception_agent_result` stored in each turn's `reasoning_trace`, assesses whether the agent's perception of party state was accurate, and scores PQ1–PQ4 based on what the agent recorded rather than what the mediator subsequently did.

This requires no schema change — `perception_quality_review` already exists in `evaluation.schema.json`. What changes is the evidence basis: evaluators now have a first-class perception artifact to evaluate against.

### 6.2 Option Quality Scoring

Current state: option quality is inferred from C5 scores and the `option_pool.json` artifact. There is no dedicated scoring dimension for:
- Option diversity (are the options substantively different?)
- Insight quality (do the options reflect genuine interest alignment or are they obvious?)
- Domain-fit (does the option pool include options that match the parties' actual interests as perceived?)

Stage 6 adds an `option_quality_review` section to `evaluation.schema.json`, analogous to `perception_quality_review`. Scored dimensions:

| Dimension | What it measures |
|---|---|
| OQ1 — option diversity | Are the brainstormed options substantively distinct? |
| OQ2 — interest alignment | Do options map to inferred party interests? |
| OQ3 — domain fit | Do options respect domain constraints? |
| OQ4 — non-obvious value | Does the pool include options a non-expert would miss? |
| OQ5 — qualification accuracy | Did the domain reasoner correctly qualify/disqualify? |

Scores 1–5 per dimension; `option_quality_band`: `developing | competent | strong`.

### 6.3 `evaluation.schema.json` Changes

- Add `option_quality_review` section with OQ1–OQ5 dimensions
- `perception_quality_review` scoring basis changes from proxied to direct (no schema change, documentation note only)

---

## 7. Benchmark Validation Plan

### 7.1 Primary Validation Cases

The Stage 6 validation runs are a systematic sweep of the full diagnostic corpus, not targeted single-case diagnostics.

| Case | Purpose | Key questions |
|---|---|---|
| D-B04-S06 | Perception fix — logistics/options focus | Does perception agent maintain PQ band at competent or above when option generation is heavy? Does C7 improve from 3? |
| D-B07-S12 | Option quality — bounded package | Do OQ2/OQ4 scores reflect the richer interest signals from perception agent? |
| D-B11-S07 | Asymmetry — quiet compliance | Does perception agent detect `engagement_quality=compliant_only`? Does it add to safety monitor cross-turn detection? |
| D-B03-S02 | Emotional context — betrayal | Does perception agent maintain `strong` PQ band? No regression. |
| D-B08-S02 | Process breakdown + domination | Perception agent: correct `dynamic_trajectory=deteriorating`? PQ band maintained. |

### 7.2 RT Regression Checks

All three adversarial cases must still pass with the perception agent in the pipeline:
- D-B-RT01-S03: CATEGORY 1 false-positive still not triggered
- D-B-RT02-S04: CATEGORY 2 veto still fires structurally at T9
- D-B-RT03-S03: CATEGORY 3 veto still fires structurally at T9

### 7.3 Success Criteria

| Criterion | Target |
|---|---|
| D-B04 C7 | Improves from 3 to 4 or above |
| D-B04 PQ band | Improves from developing to competent or above |
| D-B11 `engagement_quality` detection | `compliant_only` detected at correct turn |
| RT regression | All three PASS (structural veto paths preserved) |
| No new integration failures | I-family scores stable or improved across all sessions |
| Option quality (OQ1–OQ5) | Scoreable on all new sessions (framework validated) |

---

## 8. Implementation Sequence

| Item | File | Description |
|---|---|---|
| 1 | `schema/perception_agent.schema.json` | PerceptionAgentResult schema |
| 2 | `runtime/engine/perception_agent.py` | LM-based perception agent, ~300 lines |
| 3 | `runtime/orchestrator.py` | Add perception agent call block |
| 4 | `runtime/engine/lm_engine.py` | Accept + store perception_agent_result |
| 5 | `runtime/engine/option_generator.py` | Inject perception signals into brainstormer |
| 6 | `runtime/engine/domain_reasoner.py` | Accept perception signals; `compliant_only` soft deferral |
| 7 | `runtime/engine/prompt_builder.py` | Use perception agent output as structured prior |
| 8 | `runtime/reviewer_transcript_rendering.py` | Add perception agent log block |
| 9 | `schema/evaluation.schema.json` | Add option_quality_review section |
| 10 | `tests/test_end_to_end.py` | TestPerceptionAgent unit tests (10 tests) |
| 11 | Benchmark validation runs (§7) | 5 primary cases + 3 RT regression checks |

---

## 9. Open Design Questions

**9a. Does the perception agent output replace or augment the scaffold's PerceptionContext?**

Recommendation: augment, not replace. The scaffold's `PerceptionContext` is cheap, deterministic, and always available as a fallback. The perception agent output is layered on top when available. The main LM receives both: scaffold perception as structural context, perception agent output as the richer LM-assessed prior. The agent's `scaffold_divergence` field makes disagreements explicit.

**9b. Should the perception agent feed into the safety monitor?**

The safety monitor already observes the full interaction history independently and does not depend on the perception agent's output for its CATEGORY 1/2/3 detection. However, the perception agent's `engagement_quality=compliant_only` signal is a complementary data point. Two options:

Option A: Pass `perception_agent_result` to `generate_safety_monitor_result()` as an additional input. The monitor can reference engagement quality without duplicating the detection logic.

Option B: Keep the agents completely independent. The safety monitor's structural guarantee must not depend on the perception agent being available.

**Recommendation:** Option B for the structural guarantee; Option A can be added as an informational enhancement in a subsequent iteration. The monitor must work correctly without the perception agent.

**9c. Should `engagement_quality=compliant_only` from the perception agent trigger a `compliance_only_pattern` flag?**

The safety monitor already owns CATEGORY 1 (compliance-only) detection. The perception agent detecting `compliant_only` engagement is a perception-layer signal, not a structural veto trigger — it should not bypass the safety monitor's threshold logic. The recommended approach: the perception agent notes it in `veto_signals` for context; the safety monitor still owns the veto decision.

**9d. `perception_agent_result` persistence tier**

Consistent with `domain_analysis` and `option_pool`: stored in `reasoning_trace.perception_agent_result` under `eval_support` and `dev_verbose` profiles. Not written as a standalone artifact file (unlike `party_state.json`) — it is a per-turn trace element, not a session-level accumulation.

---

## 10. Stage 6 Relationship to ARCH-007

ARCH-007 §4 Stage 6 definition:
> "All five agents operating under the existing runtime orchestrator. The evaluation framework is extended to score perception quality and option generation quality as first-class dimensions alongside the existing C/P/I families."

This design satisfies that definition exactly:
- Five agents: Perception agent (new) + Domain reasoner + Option generator + Safety monitor + Conversational mediator (main LM)
- Extended evaluation: PQ scoring direct (not proxied); OQ1–OQ5 added

The existing runtime orchestrator, artifact pipeline, and escalation framework are unchanged.
