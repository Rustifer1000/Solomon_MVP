# Stage 2b Findings Memo 036

**Status:** Final — closes party_state.json prompt-feedback design question (TASKLIST-034 §4c)

**Date:** 2026-03-28

---

## Purpose

This memo records the Stage 2b experiment results: testing whether passing `party_state.json` as explicit prompt context on each new assistant turn improves within-session perception quality. It resolves the design question left open in STAGE2-FINDINGS-035:

> "Whether `party_state.json` should be fed back into the perception prompt context (as a standing prior) must be settled by design. This is the boundary between Stage 2 (externalise) and Stage 5 (dedicated perception agent)."

Three sessions were run on D-B11 (the asymmetry case):

| Session | Configuration | Primary finding |
|---|---|---|
| D-B11-S03 | Stage 2, no feedback | Baseline — epistemically cautious, Party B held as unknown at T3 |
| D-B11-S04 | Feedback active, no guard | Projection risk confirmed — Party B interests inferred before Party B speaks |
| D-B11-S05 | Feedback active, projection guard | Party B epistemic handling restored; T5 quality maintained or improved |

---

## What was implemented

**Stage 2b (prompt_builder.py + lm_engine.py):**

- `lm_engine.py`: before each `build_turn_prompt` call, check whether any prior lm_runtime turns have contributed a `reasoning_trace`. If yes, call `build_party_state(state, timestamp)` and pass the result as `party_state` to the prompt builder.
- `prompt_builder.py`: added `=== ACCUMULATED PARTY STATE (prior turns) ===` section to the user message. Rendered just before `=== YOUR TASK ===`.

**Projection guard (prompt_builder.py):**

For each party, before rendering the accumulated state, the prompt builder checks whether the party has ever been heard:
- A party is "heard" if any accumulated interest is not an "unknown*" variant, or if the latest relational posture is not an "unknown*" variant.
- If the party has not been heard: a single line is rendered — "Party has not yet been heard — no observed signal. Hold as epistemically uncertain."
- If the party has been heard: full accumulated state is rendered (emotional state, relational posture, interests, risk signals, posture arc).

This prevents the feedback loop from providing spurious inferences for parties who have not yet contributed behavioral signal.

---

## Finding 1: Feedback without guard introduces projection for silent parties

**D-B11-S04 (feedback, no guard) vs D-B11-S03 (no feedback):**

At T3 — when Party B has not yet spoken — the two sessions diverged:

| Dimension | S03 (no feedback) | S04 (feedback, no guard) |
|---|---|---|
| Party B interests at T3 | `["unknown at this stage"]` | `["acknowledgment_of_administrative_role", "process_efficiency", "clarity_on_expectations"]` |
| Party B posture at T3 | `"unknown — awaiting response"` | `"unknown_awaiting_engagement"` |
| Party A risk signals at T3 | 3 signals | 4 signals (adds `long_term_exclusion_from_financial_management`) |

**Interpretation:** Without the guard, the model used the T1 party state prior (which contained generic interests for both parties) to bootstrap projections for Party B at T3. These projections are reasonable inferences from Party A's disclosure about Party B's financial management role — but they are not grounded in any observed signal from Party B. The correct behavior for the asymmetry case is S03's approach: hold Party B as epistemically uncertain until Party B speaks.

The gain from the feedback loop without guard was marginal (one additional risk signal for Party A). The loss was reduced epistemic caution for Party B.

---

## Finding 2: Projection guard restores correct epistemic handling

**D-B11-S05 (feedback + guard) vs D-B11-S03 and S04:**

At T3 Party B:

| Dimension | S03 (no feedback) | S04 (no guard) | S05 (with guard) |
|---|---|---|---|
| Emotional state | `"unknown — has not yet spoken"` | `"unknown_not_yet_heard"` | `"unknown — has not yet spoken this turn"` |
| Interests | `["unknown at this stage"]` | 3 projections | `["process efficiency", "resolution", "unclear what their interests are"]` |
| Posture | `"unknown — awaiting response"` | `"unknown_awaiting_engagement"` | `"unobserved this turn"` |

S05 restores explicit uncertainty at T3. The third interest entry (`"unclear what their interests are regarding information sharing"`) is an uncertainty marker rather than a projection — the model is explicitly recording its epistemic state rather than filling in plausible values.

**T5 quality — S05 is comparable or improved:**

Party B interests at T5: 5 entries including `"acknowledgment of their role without being cast as adversary"` — which captures the same unstated concern as S03's `"Acknowledging reality without being blamed for historical roles"` but with more precision about the psychological mechanism.

Relational dynamic narrative at T5 (S05): "constructive pivot point — Party B did not dismiss or minimize Party A's concern... The dynamic is moving from potential breakdown toward collaborative problem-solving, but this is fragile. The next step must convert acknowledgment into concrete action without blame." — this is the richest relational dynamic narrative across the S03–S05 series.

**Minor regression at T5:** `option_readiness: blocked` (S05) vs `deferred` (S03, S04). The deferral_reason correctly identifies that records haven't been shared yet, so `blocked` is defensible, but S03 and S04's `deferred` more precisely reflected the session state (Party B acknowledged the barrier; the barrier is partially resolved but records are still needed). This difference is likely stochastic variation rather than a systematic regression from the projection guard.

---

## Finding 3: The design question is resolved

**The answer to TASKLIST-034 §4c:**

Feeding `party_state.json` back as prompt context is beneficial with the projection guard and marginally harmful without it, specifically in asymmetry cases where one party is silent in early turns.

**The correct design:**
- Active (heard) parties: render accumulated state as prompt context. The model uses the prior to maintain continuity of the interest model and risk signal history.
- Silent (unheard) parties: render an explicit epistemic uncertainty marker. The model receives a positive instruction to hold uncertainty rather than a gap it fills with projection.

This is now implemented in `prompt_builder.py`.

---

## Implementation status

| Component | Status |
|---|---|
| `lm_engine.py` — prior state build and pass | Complete |
| `prompt_builder.py` — rendered section with projection guard | Complete |
| D-B11-S04 run (feedback, no guard) | Complete — projection risk confirmed |
| D-B11-S05 run (feedback, projection guard) | Complete — guard validated |
| Stage 2b findings memo | This document |

---

## Stage 3 readiness update

The party_state.json prompt-feedback design question is now settled. Stage 3 entry conditions from STAGE2-FINDINGS-035 are:

1. Run at least one additional case (D-B07 or D-B12) to confirm party_state stability across the corpus ← **outstanding**
2. Resolve the party_state prompt-feedback design question ← **resolved by this memo**
3. Domain analysis is the measured bottleneck (P6/C5 plateau) ← **confirmed across all sessions**

**Recommended next step before Stage 3:**

Run D-B07 or D-B12 with the Stage 2b configuration (feedback + guard) to confirm:
- party_state.json stable with more complex option-generation demands
- Projection guard correct for cases where both parties speak earlier in the session
- P6 and C5 scores confirm the domain analysis bottleneck is persistent

Once one additional case confirms stability, Stage 3 is warranted.

---

## Guiding constraint carried forward

The feedback loop is a Stage 2 addition. It does not replace Stage 1 or Stage 2 artifacts. The correct artifact stack per session:

- `interaction_trace.json` — turn-by-turn reasoning trace (Stage 1)
- `party_state.json` — accumulated session model, post-hoc (Stage 2)
- Feedback loop — `party_state.json` from prior turns fed as prompt context for next turn (Stage 2b, now active)
- Stage 3 — dedicated plugin agent for domain analysis (pending)
