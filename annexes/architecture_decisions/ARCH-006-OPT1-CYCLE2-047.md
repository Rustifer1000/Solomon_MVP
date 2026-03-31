# ARCH-006 Option 1 Cycle 2 — C7 Perception-Response Coupling

**Date:** 2026-03-31
**Stage:** ARCH-006 Option 1 — Human-mediated prompt and instruction revision (second cycle)
**Status:** Prompt change complete — awaiting diagnostic run
**Target:** C7 4→5 on D-B07 and D-B04 diagnostic cases

---

## Context

Cycle 1 (ARCH-006-OPT1-FINDINGS-044) achieved C6 4→5 on both primary diagnostic cases (D-B07-S13, D-B04-S07) via three Step 5 response design rules. The residual gap identified for Cycle 2 is C7.

**C7 scores before this cycle:**

| Session | C7 | C6 | Evaluator note |
|---|---|---|---|
| D-B07-S13 | 4 | 5 | Scaffold divergence detected, correctly characterised, but coupling to response not demonstrable |
| D-B04-S07 | 4 | 5 | Richer characterisation than scaffold, but coupling to response not demonstrable |
| D-B11-S07 | 4 | — | Perception agent correctly identified asymmetry pattern, coupling not demonstrable |
| D-B01-S01 | 4 | — | (reference session) |

C7=5 is rare in the corpus — only D-B12-S01 achieves it, and that case reaches M3 where the escalation decision itself is the demonstrable coupling (the act of escalating to co-handling is emotionally regulated because it preserves dignity).

C2 was considered for this cycle but is ceiling-appropriate across all current diagnostic cases (narrow settlement zone cases have fewer distinct issue families by design; the issue map is smaller, not wrong).

---

## Diagnostic of the Gap

The C7 evaluator notes across diagnostic sessions follow a consistent pattern:
- "Correctly assessed [dynamic]" — perception accuracy is confirmed
- "Richer characterisation than scaffold" — Stage 6 perception agent is adding value
- No mention of the response demonstrating the characterisation

The gap is not perception accuracy — it is **perception-response coupling visibility**. The perception assessment correctly identifies party state; the response is appropriate to that state; but a reviewer reading the response cannot identify a specific move that was made *because* of the perception assessment. The response is grounded in perception implicitly, not explicitly.

`grounded_in_perception: true` already exists in the output format but carries no coupling information — it is a boolean that the model self-reports without specifying what the coupling is.

---

## What Changed

### 1. System Prompt — PERCEPTION-RESPONSE COUPLING RULE (added to Step 1)

A new rule inserted immediately after the Step 1 description and before Step 2. The rule requires:

1. After completing Step 1, identify the **single most important insight** from the assessment and state explicitly how it will shape the Step 5 response.
2. The coupling must be **specific** to this party, this turn, this signal — not a generic observation applicable to any session.
3. The coupling must be **actionable** — naming a concrete response move, not a general intention.
4. The coupling must be **visible** — a reviewer reading the Step 5 response should be able to identify where the coupling note's specific move appears in the message_text.

Example coupling notes (required format: "Because I assess X, I will Y"):
- "Because Party B's posture shifted to deferential after raising their concern, I will explicitly invite Party B's reaction before proceeding rather than assuming acceptance."
- "Because the scaffold assessed cooperative_and_stable but I assess coordination-under-low-trust, I will name the trust dimension explicitly before presenting options."
- "Because Party A's risk signal is financial anxiety about surprise obligations, I will acknowledge the advance-notice concern directly before any option framing."

### 2. Output Format — `perception_coupling_note` field (added)

Added to the `perception` object in the output format:

```json
"perception_coupling_note": "Because I assess [specific observation], I will [specific response move in Step 5]."
```

This makes the coupling:
- **Explicit** — captured in the reasoning trace, not inferred by reviewers
- **Evaluable** — can be cross-checked against the message_text at evaluation time
- **Traceable** — the HUMAN-REVIEW-PROTOCOL-046 reviewer sees the coupling note and can verify it in the response

### 3. No changes to downstream code

The reasoning_trace is opaque to the contract validator — the new field is passed through without code changes to lm_engine.py or normalization. The constraint gate (source="runtime") is unaffected.

---

## Why This Change Should Move C7

The C7 4→5 boundary requires perception that "actively and demonstrably informs how the mediator positions the next turn." The boundary is not about perception quality (already at 4) — it is about whether the response text shows *evidence* that the perception assessment changed something.

The PERCEPTION-RESPONSE COUPLING RULE creates this evidence at the generation point:
- The model must identify a specific coupling before writing Step 5
- The coupling is recorded in the reasoning_trace
- The Step 5 response must execute the coupling move
- The evaluator can verify the coupling in both the reasoning_trace and the message_text

The analogy to Cycle 1 is direct: the C6 Step 5 rules required the response to show specific structural evidence (transition marker, interest connection, tentative framing). C7 requires the response to show specific evidence that a perception assessment changed an approach. The mechanism is the same — a prompt rule that requires visible evidence of the thing being scored.

---

## Constraint Gate

212/212 tests pass. The constraint gate covers:
- All 14 D-B01–D-B14 benchmark cases (source="runtime") — no regression
- 3 adversarial RT cases (D-B-RT01, RT02, RT03) — safety paths unaffected
- The Step 1 addition only affects the system prompt for lm_runtime sessions; source="runtime" sessions use the deterministic simulation, not the LLM
- The PERCEPTION-RESPONSE COUPLING RULE only fires during Step 1 of LLM generation; it does not affect escalation logic, option qualification, or safety paths

---

## Diagnostic Plan

**Primary case: D-B07-S14** (expense coordination, bounded package)
- Expected posture: M0, option_generation phase
- C7 target: 4→5
- Check: perception_coupling_note in reasoning_trace T5; coupling move visible in message_text T5
- Check: `scaffold_divergence` field reflects the trust/authority dimension correctly assessed at T3/T5

**Secondary case: D-B04-S08** (parenting schedule, narrow settlement zone)
- Expected posture: M0, option_generation phase
- C7 target: 4→5
- Check: perception_coupling_note in reasoning_trace T7; coupling move visible in message_text T7
- Check: "phased trial" reframe (C4 signal from S07) appears with explicit coupling note

**Run instructions:**

```
python -m runtime.cli.run_benchmark \
    --case-dir annexes/benchmark_cases/D-B07 \
    --output-dir annexes/benchmark_cases/D-B07/sessions/D-B07-S14 \
    --source lm_runtime \
    --policy-profile eval_support \
    --review-transcript-renderer prototype_local_v0 \
    --generated-at <ISO-timestamp>

python -m runtime.cli.run_benchmark \
    --case-dir annexes/benchmark_cases/D-B04 \
    --output-dir annexes/benchmark_cases/D-B04/sessions/D-B04-S08 \
    --source lm_runtime \
    --policy-profile eval_support \
    --review-transcript-renderer prototype_local_v0 \
    --generated-at <ISO-timestamp>
```

**Success criteria:**
- C7 = 5 on at least one diagnostic case
- `perception_coupling_note` present and specific in all assistant turns (not generic placeholder)
- Coupling move visible in message_text for turns where coupling note was recorded
- No regression on C6 (must remain 5 on both cases)
- No regression on C4, P2, P4 (must hold 5 on D-B04)
- Constraint gate confirms escalation paths unchanged after diagnostic completion

**After diagnostic runs:**
Write ARCH-006-OPT1-CYCLE2-FINDINGS-048.md covering primary/secondary mover analysis, constraint gate confirmation, and residual gaps.

---

## Tracking

| Item | Status |
|---|---|
| PERCEPTION-RESPONSE COUPLING RULE addition (Step 1) | **Complete** — `runtime/engine/prompt_builder.py` |
| `perception_coupling_note` field in output format | **Complete** — `runtime/engine/prompt_builder.py` |
| Constraint gate (212/212 tests) | **Complete** — 2026-03-31 |
| D-B07-S14 diagnostic (expense coordination) | Pending |
| D-B04-S08 diagnostic (parenting schedule) | Pending |
| Constraint gate post-diagnostic (17-case) | Pending |
| ARCH-006-OPT1-CYCLE2-FINDINGS-048 memo | Pending |
