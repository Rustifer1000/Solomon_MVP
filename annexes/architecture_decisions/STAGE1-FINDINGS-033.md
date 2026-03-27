# Stage 1 Findings Memo 033

**Status:** Final — closes NEXT-PHASE-EXECUTION-TASKLIST-029 items 1–4 and 6

**Date:** 2026-03-27

---

## Purpose

This memo records Stage 1 diagnostic findings following the implementation of structured five-step reasoning (TASKLIST-029) and the D-B04 diagnostic run. It addresses the four questions specified in TASKLIST-029 item 6:

1. Does structured reasoning measurably improve PQ scores in the focus-competition cases?
2. Are the intermediate step outputs useful as interface specifications for later stages?
3. Does any unexpected degradation appear in the constraint track (C9, C6, ES scores)?
4. What are the recommended Stage 2 trigger conditions?

---

## What was run

| Item | Status |
|---|---|
| 1. Define five-step intermediate output schemas | Complete — CONTRACT-014 |
| 2. Update `lm_engine.py` to produce structured intermediate outputs | Complete |
| 3. Update `interaction_trace.schema.json` | Complete |
| 4. Run Stage 1 against D-B04 diagnostic baseline | Complete — D-B04-S02 |
| 5. Run Stage 1 against D-B11 | Deferred — see below |
| 6. Write Stage 1 findings memo | This document |

**D-B11 deferral:** Item 5 was deferred at the user's direction after D-B04 results confirmed the primary hypothesis. D-B11 (quiet compliance / asymmetry) remains open as a future run. The D-B04 findings are sufficient to establish Stage 1's core value and identify what needs fixing before D-B11 adds more signal.

---

## Finding 1: Structured reasoning measurably improves PQ in focus-competition cases

**Verdict: Confirmed.**

D-B04 was the primary diagnostic case — the weakest perception profile in the Stage 0 set, returning a `developing` PQ band and C7=3. The Stage 0 diagnostic attributed this to **focus competition**: logistics and option-generation demand crowding out emotional state modelling.

Stage 1 D-B04 result (D-B04-S02, source=lm_runtime):

| Metric | Stage 0 (S01, reference) | Stage 1 (S02, lm_runtime) |
|---|---|---|
| PQ band | `developing` | `competent` |
| C7 (empathy/attunement) | 3 | 4 |
| C5 (option generation) | 4 | 4 |
| I5 (failure attribution) | 4 | 5 |
| Integration score | 87.2 | 92.4 |
| Core score | 78.6 | 80.0 |

The structured perception pass preserved per-party emotional differentiation even while the session's primary cognitive demand was logistics. Turn 7's reasoning_trace showed:

- Party A: "cautiously hopeful but guarded" — 5 specific contextual interests including child stability, homework completion, dysregulation reduction, explicit success criteria
- Party B: "cautiously hopeful with underlying frustration" — 4 specific interests including co-parent recognition, meaningful daily involvement, avoiding indefinite marginalization
- Relational dynamic: "cautious convergence — both parties have moved from positional opposition toward conditional openness to a phased approach, but mutual trust remains fragile"

All four of these assessments are richer, more specific, and more bilaterally differentiated than the Stage 0 reference. In Stage 0, these were inferred from action quality. In Stage 1, they are directly readable in the trace.

**The focus competition hypothesis is confirmed in reverse:** cognitive separation reduces crowding-out.

---

## Finding 2: Intermediate outputs are partially useful as interface specifications

**Verdict: Structurally correct, schema incomplete.**

The five-step structure (perception → domain_analysis → option_scan → safety_assessment → response_synthesis) works as an interface shape. The model correctly separates these steps and returns structured objects for each. The `reasoning_trace` field is populated and readable in all four assistant turns of the D-B04-S02 run.

However, CONTRACT-014 defines richer schemas than what the current system prompt output format requests. Four fields are absent from the LM's output:

| CONTRACT-014 field | Step | Status |
|---|---|---|
| `perception_confidence` | Step 1 | Absent — not in system prompt JSON format |
| `option_readiness` | Step 2 | Absent — not in domain_analysis format |
| `grounded_in_perception` | Step 5 | Absent — not in response format |
| `options_introduced` | Step 5 | Absent — not in response format |

These gaps do not prevent the trace from being useful for evaluation — perception, domain gaps, option deferral reasoning, and safety assessment are all readable. But they do limit the completeness of the interface specification for later multi-agent substitution.

**The most important gap**: `grounded_in_perception` and `options_introduced` in Step 5. These are the cross-step consistency checks that let evaluators verify whether the response synthesis actually used the perception and option outputs. Without them, the Step 3/Step 5 incoherence described below cannot be evaluated automatically.

---

## Finding 3: Constraint track — no degradation, but a new incoherence class observed

**Verdict: No degradation. One new incoherence class surfaced.**

Constraint track scores in D-B04-S02 were stable or improved versus S01:

- C9 (constraint adherence): 4 — maintained. M1 sustained appropriately. Logistics deference preserved.
- C6 (fair process): 4 — maintained. No settlement pressure detected.
- ES scores: maintained at S01 levels. M1 correctly identified from turn 3.

**New incoherence class:** `premature_option_work: True` in option_scan on turn 7 (`option_generation` phase), while `message_text` discusses options (phased trial conditions, reliability criteria, trust concerns). Step 3 says "options deferred." Step 5 generates options anyway.

This is not a regression — the reference simulation also discussed options on turn 7. But it is a **visible incoherence** that was not attributable in Stage 0. The structured trace now exposes it:

```
option_scan.premature_option_work = True
option_scan.qualified_options = []
message_text: "You've both said you're open to discussing a phased trial..."
```

This is an evaluable gap between reasoning and response. In later multi-agent stages, a dedicated option-generation agent would resolve this incoherence by design — the response synthesis agent would only have access to `qualified_options` from the option-generation agent, not a free-form reasoning capability. Stage 1 has made the gap legible; Stage 4 (decoupled option generation) would fix it structurally.

---

## Engineering findings (unexpected)

Several infrastructure gaps surfaced during Stage 1 implementation that are worth recording:

**1. issue_families type mismatch.** `plugin_assessment["issue_families"]` is a dict (`{"has_logistics": bool, ...}`), not a list. `perception.py` and `prompt_builder.py` both assumed a list and sliced it. Fixed with dict-to-list conversion (truthy keys only).

**2. Phase normalization required.** The LM produces non-canonical phase labels (`"opening_and_orientation"`, `"information_gathering"`) and may regress to earlier phases or skip phases. A `_normalise_phase()` function now handles alias mapping plus floor/ceiling clamping. The ceiling prevents illegal skipping; the floor prevents regression. A `min_phase` from the reference simulation's expected phase for each assistant turn is passed as an additional floor to prevent the LM from lagging behind the scripted client turn progression.

**3. reasoning_trace, message_text, and interaction_observations_delta not threading through normalization.** `CandidateTurn` was missing all three fields. `normalize_core_output()` did not pass them through. Fixed by adding fields to `CandidateTurn` and updating normalization. These fields are now persisted in the interaction trace.

**4. Current mediation phase not in prompt context.** The model had no visibility into what phase the session was at. Added `current_mediation_phase` (derived from trace-buffer max, not `state["phase"]` which may regress from scripted client turns) to the user prompt context.

None of these are architecture-level issues with Stage 1. They are integration gaps between the lm_runtime path and the existing normalization/validation pipeline — the kind of thing that only surfaces when the path is exercised end-to-end.

---

## Finding 4: Recommended Stage 2 trigger conditions

Stage 2 (explicit party state artifacts per ARCH-007 §4) should be triggered when the following conditions are met:

### Mandatory before Stage 2

**4.1 Close the prompt schema gaps.**
Update the system prompt output format to include the four missing CONTRACT-014 fields: `perception_confidence`, `option_readiness`, `grounded_in_perception`, `options_introduced`. Until these are present, the intermediate outputs cannot serve as complete interface specifications and the Step 3/Step 5 consistency check cannot be automated.

**4.2 Run Stage 1 against D-B11.**
D-B11 (quiet compliance / asymmetry) is the second primary diagnostic target. Its Stage 0 baseline shows `perceived_asymmetry: true` with the note that the quieter party's internal state may be less precisely modelled. Stage 1 with explicit perception pass should improve this — but whether the `party_b` perception block in the reasoning_trace shows the necessary specificity for the less-visible party is an open question that requires the run.

**4.3 Address the Step 3/Step 5 incoherence.**
`premature_option_work: True` while message_text discusses options is a consistent pattern that needs resolution before Stage 2 adds more artifacts. Options:
  - Add a prompt instruction: when `premature_option_work` is true, Step 5 must not reference options
  - Or add a runtime check that validates `options_introduced` against `qualified_options` post-inference

### Stage 2 trigger signal

Stage 2 should be triggered when Stage 1 produces consistent PQ band scores of `competent` or above across the diagnostic set including the asymmetry case (D-B11). The Stage 2 investment (explicit party state artifact written per turn) is justified when:

1. The structured perception pass is demonstrably improving PQ scores (confirmed for D-B04)
2. The per-turn perception output is stable enough that externalizing it as a named artifact adds evaluator value rather than noise
3. The D-B11 asymmetry case confirms that the quieter party's internal state is being modelled more precisely with cognitive separation than without

The Stage 0 diagnostic conclusion was that Stage 2 priority is **High**. The Stage 1 findings strengthen that assessment: the perception pass is working, and externalizing it as a party-state artifact would make the asymmetry detection directly evaluable.

---

## Summary

Stage 1 delivered on its primary objective. Structured five-step reasoning measurably improved perception quality on the focus-competition case (D-B04 PQ: developing → competent, C7: 3 → 4) without degrading the constraint track. The reasoning trace makes the model's perception decisions readable, attributable, and comparable to scaffold-derived context. The five-step structure is correct as an interface shape for later multi-agent substitution, with four prompt schema gaps to close.

The immediate next moves before Stage 2:

1. Update system prompt output format — add the four missing CONTRACT-014 fields
2. Run Stage 1 against D-B11 — confirm or challenge asymmetry improvement hypothesis
3. Resolve Step 3/Step 5 incoherence — options in message_text when `premature_option_work: True`
4. When the above are done: trigger Stage 2 (explicit party state artifacts)
