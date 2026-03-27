# Next-Phase Execution Tasklist 029

## Purpose

This tasklist sequences Stage 1 work for Solomon's multi-agent evolution (ARCH-007), following:

- Closure of the renderer trial: [POST-RENDERER-TRIAL-FINDINGS-032](./POST-RENDERER-TRIAL-FINDINGS-032.md)
- Completion of Stage 0 diagnostic evaluations: [DIAG-001](./DIAG-001-stage0-diagnostic-evaluation-protocol.md)

---

## Stage 0 status: complete

Stage 0 ran on 2026-03-26 against five cases (D-B03, D-B04, D-B08, D-B10, D-B11). The diagnostic findings are recorded in DIAG-001.

**Primary finding:** Perception quality degrades when cognitive demand shifts to logistics and option generation. D-B04 returned a `developing` PQ band — the weakest emotional state modeling in the corpus — confirming the focus competition hypothesis. When option generation and logistics coordination are the session's primary cognitive demand, party state modeling is crowded out.

**Stage priority from DIAG-001:**

| Stage | Priority |
|---|---|
| Stage 1 — structured reasoning | High |
| Stage 2 — explicit party state | High |
| Stage 4 — decoupled option generation | High |
| Stage 3 — plugin as domain reasoner | Medium |
| Stage 5 — safety monitor | Lower urgency (PQ3 already strong) |

---

## Stage 1 context

Stage 1 restructures the way the single model is prompted to enforce cognitive separation **before** multi-agent work begins. The model runs a structured five-step sequence rather than one undifferentiated inference pass:

1. Perception pass — what is each party experiencing?
2. Domain analysis — what are the domain-relevant observations?
3. Option scan — what are possible moves?
4. Safety assessment — any flags or threshold signals?
5. Response synthesis — given all of the above, what to say?

**Current status:** `runtime/engine/lm_engine.py` implements a five-step reasoning sequence but captures intermediate outputs as strings appended to `interaction_observations_delta`. ARCH-007 §4 requires structured intermediate outputs — each step's output should define the interface contract that a dedicated agent will eventually fulfil.

**How you know Stage 1 worked:** C7 and C9 scores improve in cases where subtle signals were previously missed (specifically D-B04 and D-B11). Evaluators can read the reasoning chain, improving I3 (artifact traceability) and I5 (failure attribution) scores.

---

## Ranked worklist

### 1. Define the five-step intermediate output schemas

For each of the five reasoning steps, define the minimum structured output shape:

- **Perception pass output:** party state per participant (emotional register, engagement level, inferred interests, risk signals observed)
- **Domain analysis output:** domain-relevant observations, feasibility constraints, warnings surfaced
- **Option scan output:** candidate moves considered, with brief qualification note for each
- **Safety assessment output:** flag candidates, threshold band estimate, escalation recommendation
- **Response synthesis output:** selected move with rationale, links back to preceding steps

These schemas do not need to be formal JSON schemas yet. A clear field-level description in a CONTRACT or MEMO document is sufficient for Stage 1. The key requirement is that each output is **structured and traceable** — not a string blob.

The intermediate outputs should extend `interaction_observations_delta` or live in a parallel `reasoning_trace` field per turn.

### 2. Update `lm_engine.py` to produce structured intermediate outputs

Modify the five-step inference sequence to produce and return structured objects rather than narrative strings. The returned turn dict should include the intermediate step outputs in a form that `normalize_core_output()` can pass through to the trace.

This does not change the response synthesis output (what the model says to participants). It enriches what the runtime records about how the model arrived at that response.

### 3. Update `interaction_trace.schema.json` to accommodate the enriched per-turn reasoning trace

Add an optional `reasoning_trace` field (or extend `interaction_observations_delta`) to the turn schema to accommodate the structured five-step outputs.

### 4. Run Stage 1 against the D-B04 diagnostic baseline

Re-run D-B04 using `source=lm_runtime` with the updated structured reasoning. D-B04 is the primary diagnostic case — it is where focus competition was most visible in Stage 0.

Compare:
- PQ band (Stage 0: `developing`) against new run
- C7 score (Stage 0: 3) against new run
- C5 score (option quality) against new run
- Evaluator's ability to trace perception reasoning from the artifact

### 5. Run Stage 1 against D-B11

D-B11 (quiet compliance / asymmetry) returned `competent` with `perceived_asymmetry: true`. It is the best test for whether structured perception improves detection of the less-visible party's internal state — the asymmetry case where one party's state is harder to read.

### 6. Write a Stage 1 findings memo

After the diagnostic runs, record:

- whether structured reasoning measurably improves PQ scores in the focus-competition cases
- whether the intermediate step outputs are useful as interface specifications for later stages
- whether any unexpected degradation appears in the constraint track (C9, C6, ES scores)
- the recommended Stage 2 trigger conditions

---

## Guiding constraint

Stage 1 must not change the deterministic simulation paths (`source=runtime`, `source=reference`). The structured reasoning applies only to `lm_runtime` sessions. The evaluation framework and artifact schemas should accommodate Stage 1 output as optional fields — existing benchmark sessions must remain schema-valid without them.

---

## Recommendation

The immediate next move is **item 1: define the five-step intermediate output schemas**.

That document becomes the interface specification against which the implementation (item 2) is built and the evaluation (items 4-5) is designed.
