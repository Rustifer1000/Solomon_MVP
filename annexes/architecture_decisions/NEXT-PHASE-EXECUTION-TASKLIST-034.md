# Next-Phase Execution Tasklist 034

## Purpose

This tasklist sequences Stage 2 work for Solomon's multi-agent evolution (ARCH-007), following:

- Completion of Stage 1 implementation and D-B04 diagnostic run: [STAGE1-FINDINGS-033](./STAGE1-FINDINGS-033.md)
- CONTRACT-014 defining the five-step intermediate output schemas: [CONTRACT-014](./CONTRACT-014-stage1-reasoning-trace-v0.md)

---

## Stage 1 status: complete — all items closed

Stage 1 ran on 2026-03-27 against D-B04 (primary diagnostic case) and D-B11 (asymmetry case). Primary finding: PQ band improving developing → competent on D-B04; asymmetry detection confirmed on D-B11. All Stage 1 gaps closed. Full findings in STAGE1-FINDINGS-033.

**Item 0 closed 2026-03-27:**

| Item | Description | Status |
|---|---|---|
| Stage 1 gap A | Four missing CONTRACT-014 fields added to system prompt | **CLOSED** — verified in D-B11-S02 |
| Stage 1 gap B | Step 3/Step 5 incoherence: `premature_option_work: True` while `message_text` discusses options | **CLOSED** — verified in D-B11-S02 |
| TASKLIST-029 item 5 | D-B11 Stage 1 run | **CLOSED** — D-B11-S02 evaluation complete |

---

## Stage 2 context

Stage 2 (ARCH-007 §4) adds a dedicated per-party state artifact. The perception function — currently captured inside `reasoning_trace.perception` per turn — becomes an explicit, named, session-level artifact: `party_state.json`.

The key difference from Stage 1: Stage 1 captures *what the model perceived at each turn* as part of the interaction trace. Stage 2 externalises that into a *standing party state model* that accumulates across turns and is readable independently of the turn-by-turn trace. This artifact:

- Makes per-party psychological state directly evaluable (PQ1–PQ4 no longer inferred from action quality)
- Provides a clean interface for the dedicated perception agent (Stage 5)
- Enables evaluators to check whether the model's party state model influenced subsequent response synthesis

**Stage 2 is still single-model.** No new inference calls. The party_state.json is derived from `reasoning_trace.perception` fields already being captured in Stage 1. Stage 2 is primarily an artifact and evaluation infrastructure change.

**How you know Stage 2 worked:** C7 and C9 scores improve in the asymmetry cases (D-B11) because the standing party state model forces the system to maintain a continuous model of each party rather than restarting perception from scratch each turn. I3 (artifact traceability) improves further because party state is independently readable. PQ scores become directly evaluable rather than inferred from action quality.

---

## Ranked worklist

### 0. Close Stage 1 gaps before proceeding

These two gaps must be resolved before Stage 2 diagnostic runs produce clean signal.

**Gap A — Prompt schema gaps (four missing CONTRACT-014 fields):**

Update `runtime/engine/prompt_builder.py` SYSTEM_PROMPT (or user message format) to request:
- `perception.perception_confidence` — `"low | moderate | high"`
- `domain_analysis.option_readiness` — `"ready | deferred | blocked"`
- `response.grounded_in_perception` — `true | false`
- `response.options_introduced` — list of option labels from Step 3

These are additive fields. No structural prompt change needed — add them to the existing JSON format specification.

**Gap B — Step 3/Step 5 incoherence:**

Add a prompt constraint to SYSTEM_PROMPT: when `option_scan.premature_option_work` is `true`, Step 5 response synthesis must not reference, present, or discuss specific options. The response must be limited to process moves (eliciting information, clarifying interests, framing next steps).

**After closing both gaps:** run D-B11 Stage 1 (TASKLIST-029 item 5) to confirm asymmetry improvement and close the Stage 1 diagnostic set.

---

### 1. Define the party_state.json schema (CONTRACT-015)

Specify the `party_state.json` artifact. Key design decisions:

- **Session-level, not turn-level**: one file per session, accumulating a running model of each party across turns. Distinct from `reasoning_trace.perception` (which is per-turn and embedded in the interaction trace).
- **Per-party blocks**: each party has a block that records emotional arc, interest model (accumulated, not just current-turn), risk signal history, engagement level trend, and relational posture progression.
- **Update trigger**: written (or overwritten) after each assistant turn where the model's perception assessment materially differs from the prior turn's.
- **Evaluator-facing**: designed for human evaluators to read as a standalone document. Should answer: "what does Solomon currently believe about each party's state?"

Minimum required fields per party:
- `current_emotional_state` — latest assessment
- `emotional_arc` — sequence of assessments across turns (turn index + assessment)
- `accumulated_interests` — deduplicated, turn-indexed interest model
- `risk_signal_history` — all signals seen, with turn indices
- `relational_posture_progression` — how engagement has evolved
- `scaffold_divergence_log` — where LM differed from scaffold, for evaluator visibility
- `last_updated_turn` — provenance

---

### 2. Update `lm_engine.py` and `artifacts.py` to produce `party_state.json`

**`lm_engine.py`:** no changes needed. The `reasoning_trace.perception` fields already capture per-turn party state. The data is there.

**`artifacts.py`:** add `build_party_state(state)` which reads from the trace buffer's `reasoning_trace.perception` fields and accumulates the per-party model. Write `party_state.json` at session close under `eval_support` and `dev_verbose` profiles.

**`policy_profiles.py`:** add `party_state.json` to the artifact manifest for `eval_support` and `dev_verbose`. Absent under `sim_minimal` and `redacted`.

---

### 3. Update `interaction_trace.schema.json` and add `party_state.schema.json`

Add `party_state.schema.json` to `schema/`. Reference it from the artifact validation in `artifacts.py`.

---

### 4. Run Stage 2 against D-B04 diagnostic baseline

Re-run D-B04 with Stage 1 gaps closed and `party_state.json` writing enabled.

Compare against D-B04-S02 (Stage 1 baseline):
- Is `party_state.json` populated and coherent across all four assistant turns?
- Does the accumulated interest model across turns add information beyond any single turn's `reasoning_trace.perception`?
- Is the `emotional_arc` readable as a session narrative?

---

### 5. Run Stage 2 against D-B11

D-B11 (quiet compliance / asymmetry) is the primary target for Stage 2. The Stage 0 finding was: the system detects the asymmetric dynamic but the quieter party's internal state may be less precisely modelled. Stage 2 creates a standing party state model that the system must maintain for both parties — including the quieter one.

Compare against D-B11-S01 (Stage 0 reference):
- Does `party_state.json` show a richer model of the quieter party's state than the reference evaluation inferred?
- Is `risk_signal_history` for the quieter party more complete?
- Does `accumulated_interests` for the quieter party capture unstated concerns beneath surface compliance?

---

### 6. Write Stage 2 findings memo

After diagnostic runs, record:
- Whether `party_state.json` adds evaluator-facing signal over the existing `reasoning_trace.perception` data
- Whether the asymmetry detection improvement is confirmed or unchanged in D-B11
- Whether the standing state model reduces within-session perception drift (PQ consistency turn-over-turn)
- The recommended Stage 3 trigger conditions (plugin as active domain reasoner)

---

## Guiding constraint

Stage 2 must not change deterministic simulation paths. `party_state.json` is produced only for `lm_runtime` sessions under `eval_support` and `dev_verbose` profiles. Existing benchmark sessions must remain schema-valid without it.

Stage 1 artifacts (`reasoning_trace` per turn, `message_text`, `interaction_observations_delta`) remain in place and are the source of truth for `party_state.json` derivation. Stage 2 does not replace Stage 1 — it adds an accumulation layer on top.

---

## Recommendation

The immediate next move is **item 0: close the Stage 1 gaps** (prompt schema and Step 3/Step 5 fix), then run D-B11 Stage 1 to close TASKLIST-029 fully. Stage 2 design and implementation (items 1–3) can follow immediately after.
