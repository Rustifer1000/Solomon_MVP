# CONTRACT-015: Party State Artifact v0

**Status:** Normative for Stage 2 implementation

**Depends on:** CONTRACT-014 (Stage 1 reasoning trace), ARCH-007 §4

---

## 1. Purpose

`party_state.json` is a session-level artifact that accumulates a standing model of each party's psychological state across turns. It externalises the perception function from the turn-by-turn `reasoning_trace.perception` records (Stage 1) into a named, independently readable artifact.

**What it adds over Stage 1:** Stage 1 captures *what the model perceived at each turn*, embedded inside the interaction trace. `party_state.json` accumulates those per-turn reads into a cross-turn narrative that is:

- Readable by a human evaluator without parsing the interaction trace
- Evaluable against PQ1–PQ4 directly (not inferred from action quality)
- A named interface for the dedicated perception agent (ARCH-007 Stage 5)
- A check on whether the model's party state model is consistent turn-over-turn or drifts

**What it does not add:** No new inference calls. The data is entirely derived from `reasoning_trace.perception` fields already captured in Stage 1. Stage 2 is an accumulation and externalisation step, not a new reasoning step.

---

## 2. Where it lives

One file per session, written at session close:

```
sessions/{session_id}/party_state.json
```

Written under `eval_support` and `dev_verbose` policy profiles only. Absent under `sim_minimal` and `redacted`. Existing benchmark sessions remain valid without it.

---

## 3. Schema

### Top-level object

```json
{
  "schema_version": "party_state.v0",
  "case_id": "string",
  "session_id": "string",
  "source": "lm_runtime",
  "turns_contributing": [1, 3, 5],
  "last_updated_turn": 5,
  "generated_at": "ISO-8601 timestamp",
  "party_a": { ... },
  "party_b": { ... },
  "cross_party": { ... }
}
```

`turns_contributing` — turn indices of all assistant turns whose `reasoning_trace.perception` contributed to this artifact. Allows evaluators to identify which turns drove the accumulated state.

`source` — always `"lm_runtime"`. This artifact is only produced for LM runtime sessions.

---

### Per-party block (party_a / party_b)

```json
{
  "party_id": "string",
  "current_emotional_state": "string",
  "emotional_arc": [
    {
      "turn_index": 1,
      "assessment": "string",
      "confidence": "low | moderate | high"
    }
  ],
  "accumulated_interests": [
    {
      "interest": "string",
      "first_seen_turn": 1,
      "last_seen_turn": 5,
      "confidence": "low | moderate | high"
    }
  ],
  "risk_signal_history": [
    {
      "signal": "string",
      "first_seen_turn": 3,
      "last_seen_turn": 5,
      "resolved": false,
      "resolution_note": null
    }
  ],
  "relational_posture_progression": [
    {
      "turn_index": 1,
      "posture": "string"
    }
  ],
  "scaffold_divergence_log": [
    {
      "turn_index": 3,
      "field": "string",
      "scaffold_value": "string",
      "model_value": "string"
    }
  ],
  "perception_notes_log": [
    {
      "turn_index": 3,
      "notes": ["string"]
    }
  ],
  "last_updated_turn": 5
}
```

**Field semantics:**

`current_emotional_state` — the emotional state assessment from the most recent contributing turn.

`emotional_arc` — ordered sequence of assessments across turns. Evaluators read this as a session narrative. If the assessment was `"unknown at this turn"` (legitimate when the party has not yet spoken), that is recorded as-is — do not omit or synthesise.

`accumulated_interests` — deduplicated across turns. When the same interest appears in multiple turns, update `last_seen_turn` and promote `confidence` if a later turn provides higher confidence. New interests from later turns are appended. Do not drop interests that do not recur — their absence in later turns is informative.

`risk_signal_history` — all risk signals seen across turns, with turn provenance. `resolved: true` if a later turn's perception explicitly notes the signal has dissipated. `resolution_note` records the basis for resolution if present. Do not mark resolved without explicit model evidence.

`relational_posture_progression` — one entry per contributing turn. Evaluators use this to track whether engagement posture shifted (e.g. from `"not yet observable"` → `"vulnerable but truth-telling"` → `"cautiously assertive"`).

`scaffold_divergence_log` — one entry per turn where the model's perception field differed materially from the scaffold-derived value. Drawn from `reasoning_trace.perception.scaffold_divergence`. Populated for any field where divergence was detected, not only `relational_dynamic`.

`perception_notes_log` — the raw `perception.perception_notes` array per turn, preserved with turn index. Evaluators use this to understand what the model flagged as notable at each step.

`last_updated_turn` — the most recent turn that contributed a material update to this party's block. A turn with `"unknown at this turn"` emotional state still updates `last_updated_turn` if it adds to `risk_signal_history` or `scaffold_divergence_log`.

---

### Cross-party block

```json
{
  "current_relational_dynamic": "string",
  "relational_dynamic_arc": [
    {
      "turn_index": 1,
      "assessment": "string",
      "confidence": "low | moderate | high"
    }
  ],
  "perception_confidence_arc": [
    {
      "turn_index": 1,
      "confidence": "low | moderate | high"
    }
  ]
}
```

`current_relational_dynamic` — the relational dynamic assessment from the most recent contributing turn.

`relational_dynamic_arc` — ordered sequence. This is the cross-party narrative: how the relational dynamic evolved across the session. The most diagnostically useful field for PQ4 evaluation.

`perception_confidence_arc` — ordered sequence of overall perception confidence values. Evaluators use this to judge whether the model's confidence tracking is calibrated (e.g. should increase as more signal accumulates).

---

## 4. Derivation logic

`build_party_state(state: dict) -> dict` in `runtime/artifacts.py`:

1. Collect all assistant turns from `state["trace_buffer"]` where `turn.get("reasoning_trace")` is not None.
2. Sort by `turn_index` ascending.
3. For each such turn, read `reasoning_trace["perception"]`.
4. Accumulate per-party and cross-party fields following the merge rules below.
5. Return the fully accumulated `party_state` dict.

**Merge rules:**

- `current_*` fields: overwrite with the latest contributing turn's value.
- `*_arc` fields: append one entry per contributing turn (do not deduplicate).
- `accumulated_interests`: deduplicate by interest text (case-insensitive). If same text seen again, update `last_seen_turn` and take max confidence. New text → append with `first_seen_turn = current turn`.
- `risk_signal_history`: deduplicate by signal text. If same signal seen again in a later turn, update `last_seen_turn`. If a later turn's perception does NOT include the signal, do not auto-resolve — only resolve if `perception_notes` or another field explicitly indicates resolution.
- `relational_posture_progression`: one entry per contributing turn (always append).
- `scaffold_divergence_log`: append all entries from all turns. Do not deduplicate — the evaluator may want to see whether the same divergence recurs.
- `perception_notes_log`: append all notes per turn. Do not filter.

---

## 5. Invariants

**I1 — source constraint:** `party_state.json` is only produced for `lm_runtime` sessions. Never produced for `reference`, `runtime`, `mock_model`, or `varied_mock_model` sessions.

**I2 — profile constraint:** Written under `eval_support` and `dev_verbose` profiles only.

**I3 — turns_contributing completeness:** Every turn index in `turns_contributing` must have contributed at least one field to at least one party block or the cross-party block. No phantom entries.

**I4 — arc ordering:** All `*_arc` fields must be ordered by `turn_index` ascending.

**I5 — last_updated_turn consistency:** `party.last_updated_turn` and top-level `last_updated_turn` must equal `max(turns_contributing)`.

**I6 — no synthesis beyond source:** `accumulated_interests`, `risk_signal_history`, and all arc fields must contain only values that appear in the source `reasoning_trace.perception` records. The derivation function must not infer, summarise, or generate new assessments.

---

## 6. Evaluator usage

`party_state.json` is designed to answer the following evaluator questions without requiring the interaction trace:

- **What does Solomon currently believe about each party's emotional state?** → `party.current_emotional_state`
- **How did the model's read of each party evolve across the session?** → `party.emotional_arc`
- **What interests has the model inferred for each party?** → `party.accumulated_interests`
- **What risk signals has the model detected and are they still active?** → `party.risk_signal_history`
- **Did the model's engagement read for each party change?** → `party.relational_posture_progression`
- **Where did the model diverge from the scaffold-derived prior?** → `party.scaffold_divergence_log`
- **How did the cross-party relational dynamic evolve?** → `cross_party.relational_dynamic_arc`
- **Is the model's confidence calibrated?** → `cross_party.perception_confidence_arc`

The key evaluator question for D-B11 (asymmetry case): does the quieter party's block accumulate a coherent model across turns, or does it stall at `"unknown at this turn"` past the point where that is epistemically justified? Stage 2 makes this directly evaluable.

---

## 7. Relationship to other artifacts

| Artifact | Scope | Source of truth |
|---|---|---|
| `interaction_trace.json` → `turn.reasoning_trace.perception` | Per-turn perception record | Authoritative per-turn perception |
| `party_state.json` | Session-level accumulated model | Derived from `reasoning_trace.perception`; never more authoritative than its source turns |
| `flags.json` | Risk flags (binary, rule-based) | Independent — not derived from party_state |
| `missing_info.json` | Information gaps | Independent |

`party_state.json` is a read-only derivative. If a `reasoning_trace` field is corrected, `party_state.json` must be regenerated from the updated trace.
