# CONTRACT-014: Stage 1 Reasoning Trace v0

**Status**
Draft / normative for Stage 1 implementation

**Purpose**
This document defines the structured output schemas for Solomon's Stage 1 five-step reasoning sequence (ARCH-007 §4). It specifies what each reasoning step must produce as a structured artifact, where those artifacts are stored in the interaction trace, and what invariants each step must satisfy.

These schemas serve two purposes simultaneously:
1. **Evaluation artifact** — evaluators can trace per-turn reasoning and attribute quality scores (especially PQ1–PQ4, C7, C9, I3, I5) to specific reasoning steps
2. **Interface specification** — each step's output defines the contract that a dedicated agent will fulfil in later multi-agent stages

---

## 1. Current state and the problem this solves

`runtime/engine/lm_engine.py` already instructs the model to produce a five-step JSON response. The model returns structured objects for all five steps. However, `_build_observations()` converts that structure to string tags before storing it in `interaction_observations_delta`. The structured content is lost.

**The Stage 1 implementation task is**: preserve the parsed structured JSON in a `reasoning_trace` field per turn, rather than converting it to strings. The `interaction_observations_delta` field is retained for backward compatibility.

No changes to the prompt, the JSON output format, or the LM response structure are needed — those are already correct. The change is in `_build_turn_dict()`: populate `reasoning_trace` from the parsed five-step JSON instead of only populating `interaction_observations_delta`.

---

## 2. Where the reasoning trace lives

Each `lm_runtime` assistant turn in `interaction_trace.json` gains an optional `reasoning_trace` field:

```json
{
  "turn_index": 3,
  "role": "assistant",
  "phase": "interest_exploration",
  "message_summary": "...",
  "state_delta": { ... },
  "risk_check": { ... },
  "interaction_observations_delta": ["..."],
  "reasoning_trace": { ... }
}
```

`reasoning_trace` is:
- **Optional** — absent for `runtime`, `reference`, `mock_model`, and `varied_mock_model` turns
- **Present** for all `lm_runtime` assistant turns
- **Not a replacement** for any existing turn field — it is additive

---

## 3. Step 1 — Perception output schema

The perception output records what the model believed about each party's psychological state before any other cognitive step was taken.

```json
{
  "party_a": {
    "party_id": "string",
    "emotional_state": "string",
    "inferred_interests": ["string"],
    "risk_signals": ["string"],
    "relational_posture": "string"
  },
  "party_b": {
    "party_id": "string",
    "emotional_state": "string",
    "inferred_interests": ["string"],
    "risk_signals": ["string"],
    "relational_posture": "string"
  },
  "relational_dynamic": "string",
  "perception_confidence": "low | moderate | high",
  "perception_notes": ["string"],
  "scaffold_divergence": "string or null"
}
```

### Field definitions

`party_a` / `party_b`
: Per-party perception at this turn. `party_id` must match the participant ID in session state.

`emotional_state`
: The model's assessment of this party's current psychological register. Example values: `"apparently_stable"`, `"emotionally_activated"`, `"acutely_distressed_or_unsafe"`, `"experiencing_unfair_process"`.

`inferred_interests`
: What the model believes this party actually needs, beneath their stated positions. This is the perception-quality test item for PQ2. Should be specific to this turn's evidence, not generic.

`risk_signals`
: Observable signals of vulnerability, distress, power imbalance, or incapacity. The value `["no_active_risk_signals"]` is the explicit null case.

`relational_posture`
: How this party is currently engaging. Example values: `"assertive_and_confident"`, `"deferential_under_pressure"`, `"disengaging_due_to_unfair_process"`, `"struggling_to_participate"`.

`relational_dynamic`
: The cross-party pattern as a whole. Example values: `"cooperative_and_stable"`, `"one_party_dominating_other_deferring"`, `"process_breakdown_recurring"`.

`perception_confidence`
: `"low"` for early turns or limited signal; `"moderate"` for some evidence; `"high"` for multiple converging signals.

`perception_notes`
: Key things the model identified as important to hold before generating a response. These are the model's own attention anchors.

`scaffold_divergence`
: If the scaffold-computed `PerceptionContext` (`perception.py`) and the model's Step 1 assessment differ materially, record the divergence here. Example: `"scaffold assessed party_a as apparently_stable; model assessed emotionally_activated — model noted withdrawal pattern in turn 4 summary"`. Null if no material divergence.

### Invariants

- `party_a.party_id` and `party_b.party_id` must match the participant IDs in `state["positions"]`
- The perception output must be populated before Step 2 begins — the model must not skip to domain analysis without recording party state
- `perception_notes` must not be empty on turns where `relational_dynamic` is not `"cooperative_and_stable"` — if the dynamic is stressed, the model must explicitly name what it is holding in mind

---

## 4. Step 2 — Domain analysis output schema

The domain analysis output records what feasibility constraints, information gaps, and domain-specific considerations are active at this turn.

```json
{
  "key_constraints": ["string"],
  "material_gaps": ["string"],
  "domain_notes": "string",
  "option_readiness": "ready | deferred | blocked"
}
```

### Field definitions

`key_constraints`
: Domain-specific constraints that apply to option generation at this turn. These are the constraints that survive domain qualification — not every theoretical constraint, just the ones material to the current session state.

`material_gaps`
: Information gaps that limit responsible option work. These feed directly into `open_questions_added` in `state_delta` and into `missing_info.json`. Each entry should be a specific question, not a category label.

`domain_notes`
: Free-text domain reasoning note. The model's explanation of the most important domain consideration at this turn.

`option_readiness`
: Derived signal for Step 3:
- `"ready"` — constraints are understood, gaps do not prevent option work
- `"deferred"` — material gaps are unresolved; option work should be deferred to Step 3
- `"blocked"` — safety signals from Step 1 prevent option work regardless of domain readiness

### Invariants

- If `option_readiness` is `"deferred"` or `"blocked"`, Step 3 must set `premature_option_work: true`
- `material_gaps` must be consistent with `open_questions_added` in `state_delta`

---

## 5. Step 3 — Option scan output schema

The option scan records the full brainstorm before filtering, the qualified subset after domain filtering, and the reason for any deferral.

```json
{
  "candidate_options": ["string"],
  "qualified_options": ["string"],
  "disqualified_options": [
    {
      "option": "string",
      "reason": "string"
    }
  ],
  "premature_option_work": false,
  "deferral_reason": "string or null"
}
```

### Field definitions

`candidate_options`
: All options generated in the unconstrained brainstorm. The value of cognitive separation is that this list should be broader than what a single-pass inference would produce. Evaluators can compare this list against `qualified_options` to assess option creativity.

`qualified_options`
: Options that survived domain qualification from Step 2. These are the options the model may present or reference in Step 5.

`disqualified_options`
: Options generated in the brainstorm that were filtered out, with the domain reason for each. This is an evaluator-facing artifact: it shows that the model considered a broader option space and made deliberate domain judgments.

`premature_option_work`
: `true` if `option_readiness` from Step 2 was `"deferred"` or `"blocked"`. When `true`, both `candidate_options` and `qualified_options` should be empty, and `deferral_reason` should explain why.

`deferral_reason`
: Required when `premature_option_work` is `true`. States specifically which information gap or safety signal blocks option work at this turn. Null when `premature_option_work` is `false`.

### Invariants

- `premature_option_work` must be consistent with `option_readiness` from Step 2
- No option in `qualified_options` may contradict a constraint in `key_constraints` from Step 2
- The response in Step 5 must not introduce options that are not in `qualified_options`

---

## 6. Step 4 — Safety assessment output schema

The safety assessment is the authoritative per-turn constraint check. It determines whether response synthesis can proceed.

```json
{
  "escalation_needed": false,
  "candidate_mode": "M0",
  "candidate_category": null,
  "signals": ["string"],
  "notes": "string",
  "safe_to_proceed_to_synthesis": true
}
```

### Field definitions

`escalation_needed`
: Whether the model believes a mode change or escalation is needed at this turn.

`candidate_mode`
: The model's candidate mode (`M0`–`M5`). Present even when `escalation_needed` is `false` to support evaluator comparison against the authoritative escalation engine output.

`candidate_category`
: The model's candidate escalation category (`E1`–`E6`), or `null` if no escalation-relevant condition is identified.

`signals`
: The specific signals that drove the safety assessment. These map to the `risk_check.signals` field in the turn and should be drawn from the controlled vocabulary (`power_imbalance_cue`, `coercion_concern`, `communication_breakdown`, `role_boundary_pressure`, `trust_breakdown`, `domain_complexity_warning`).

`notes`
: The model's reasoning for the safety assessment. Required when `escalation_needed` is `true`.

`safe_to_proceed_to_synthesis`
: Derived field. `true` when `escalation_needed` is `false`. `false` when `escalation_needed` is `true`. When `false`, Step 5 response synthesis must not generate substantive mediation content — the response must be escalation-routing language only.

### Invariants

- `safe_to_proceed_to_synthesis` is always the logical inverse of `escalation_needed`
- When `safe_to_proceed_to_synthesis` is `false`, the turn's `message_text` must not introduce new options or advance mediation content
- `candidate_mode` and `candidate_category` feed into `candidate_escalation_mode` and `candidate_escalation_category` in the top-level turn dict. The authoritative escalation decision remains with `runtime/escalation.py` — the model's candidate is evidence, not the final determination

---

## 7. Step 5 — Response synthesis output schema

The response synthesis output records the rationale for the selected response, not the response text itself (which is in the top-level turn `message_text` field).

```json
{
  "phase": "string",
  "message_summary": "string",
  "grounded_in_perception": true,
  "options_introduced": ["string"],
  "confidence_note": "string or null"
}
```

### Field definitions

`phase`
: The current mediation phase (`info_gathering`, `interest_exploration`, `option_generation`, `agreement_building`). Must be consistent with `state["phase"]` or record a deliberate phase transition.

`message_summary`
: A neutral one-sentence description of what the response does, distinct from `message_text`. This feeds the top-level turn `message_summary` field.

`grounded_in_perception`
: Whether the response explicitly draws on the Step 1 perception assessment. `true` when the model explicitly references party state in how it frames the response. `false` when the response is generic and does not reflect the specific party states identified in Step 1. Evaluators use this to assess whether cognitive separation is actually producing better-grounded responses.

`options_introduced`
: Which options from `qualified_options` (Step 3) are referenced or presented in the response. Must be empty when `premature_option_work` was `true`. Must be a subset of `qualified_options`.

`confidence_note`
: Optional note about the model's uncertainty or reservations about this response. Feeds the top-level turn `confidence_note` field.

### Invariants

- `options_introduced` must be a subset of Step 3's `qualified_options`
- When Step 4's `safe_to_proceed_to_synthesis` was `false`, `options_introduced` must be empty
- `grounded_in_perception` is an honest self-assessment — evaluators will verify it against the actual `message_text`

---

## 8. The full `reasoning_trace` object

```json
{
  "source": "lm_runtime",
  "model_id": "string",
  "perception": { ... },
  "domain_analysis": { ... },
  "option_scan": { ... },
  "safety_assessment": { ... },
  "response_synthesis": { ... }
}
```

`source` and `model_id` are provenance fields. `source` must be `"lm_runtime"`. `model_id` is the model identifier used for this turn (e.g. `"claude-sonnet-4-5"`).

---

## 9. Relationship to existing fields

| Existing field | Relationship to `reasoning_trace` |
|---|---|
| `interaction_observations_delta` | Retained. For `lm_runtime` turns it will contain the same string-tag observations as before, alongside the new structured `reasoning_trace`. In a future cleanup pass the string tags may be deprecated. |
| `risk_check` | The top-level `risk_check` is derived from Step 4's `safety_assessment`. `triggered` ← `escalation_needed`. `signals` ← `safety_assessment.signals`. `severity` ← inferred from `candidate_mode`. |
| `candidate_escalation_mode` | ← `safety_assessment.candidate_mode` |
| `candidate_escalation_category` | ← `safety_assessment.candidate_category` |
| `confidence_note` | ← `response_synthesis.confidence_note` |
| `message_summary` | ← `response_synthesis.message_summary` |

---

## 10. Implementation notes

The implementation change is in `lm_engine._build_turn_dict()`:

1. Build `reasoning_trace` from the parsed five-step JSON dict
2. Add `"reasoning_trace": reasoning_trace` to the returned turn dict
3. Update `normalize_core_output()` (or `CandidateTurn`) to pass `reasoning_trace` through to the trace buffer without modification

The `interaction_trace.schema.json` `turn` definition needs `reasoning_trace` added as an optional property of type `object` (with `additionalProperties: true` for now, since the schema for the full structure is defined here rather than in the JSON Schema file).

No changes to the prompt or system prompt are needed. The model already returns the right structure.

---

## 11. Interface specification note

Per ARCH-007 §4:

> The outputs of intermediate steps are captured as structured artifacts, extending the existing `interaction_observations_delta` field into a full per-turn reasoning trace. This serves as both an evaluation artifact and the **interface specification** for later multi-agent stages — each intermediate output defines the contract that a dedicated agent will eventually fulfil.

Reading this contract against the five stages:

| Step | Future agent (ARCH-007) |
|---|---|
| Step 1 — Perception | Perception agent (Stage 5 reads from this) |
| Step 2 — Domain analysis | Domain reasoner (Stage 3) |
| Step 3 — Option scan | Option generator (Stage 4) |
| Step 4 — Safety assessment | Safety monitor (Stage 5) |
| Step 5 — Response synthesis | Conversational mediator |

The structured outputs defined here are the interfaces those agents will produce. Defining them now — while they are still produced by a single model — means the multi-agent transition does not require interface redesign, only agent substitution.
