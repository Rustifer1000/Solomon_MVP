# Stage 2 Findings Memo 035

**Status:** Final — closes TASKLIST-034 items 1–5

**Date:** 2026-03-27

---

## Purpose

This memo records Stage 2 diagnostic findings following the implementation of `party_state.json` (TASKLIST-034) and the D-B04 and D-B11 Stage 2 diagnostic runs. It addresses the four questions specified in TASKLIST-034 item 6:

1. Does `party_state.json` add evaluator-facing signal over the existing `reasoning_trace.perception` data?
2. Is the asymmetry detection improvement confirmed or unchanged in D-B11?
3. Does the standing state model reduce within-session perception drift (PQ consistency turn-over-turn)?
4. What are the recommended Stage 3 trigger conditions?

---

## What was run

| Item | Status |
|---|---|
| 0. Close Stage 1 gaps (Gap A + Gap B) and run D-B11-S02 | Complete |
| 1. Define `party_state.json` schema (CONTRACT-015) | Complete |
| 2. Implement `build_party_state()` in `artifacts.py` | Complete |
| 3. Add `party_state.schema.json`; wire to policy profiles | Complete |
| 4. Run Stage 2 against D-B04 diagnostic baseline | Complete — D-B04-S03 |
| 5. Run Stage 2 against D-B11 | Complete — D-B11-S03 |
| 6. Write Stage 2 findings memo | This document |

**Engineering finding surfaced during item 4/5:** LM turns setting `escalation_needed=True` produced a `candidate_escalation_mode` in the trace that diverged from `determine_escalation()`'s rule-based result, failing session validation. Fixed in `orchestrator._run_lm_generated_session`: after `determine_escalation()` runs, the trace turn's `candidate_escalation_mode` is synced to the applied mode. The LM's raw escalation recommendation is preserved in `reasoning_trace.safety_assessment`. All 176 tests pass.

---

## Finding 1: party_state.json adds evaluator-facing signal over per-turn reasoning_trace

**Verdict: Confirmed — in both dimensions tested.**

### Dimension 1: Accumulated interest model

In Stage 1, per-turn `reasoning_trace.perception` captures 4–6 interests per party per turn. In Stage 2, `party_state.json.accumulated_interests` deduplicated across all turns.

| Session | Party A interests (Stage 2) | Party B interests (Stage 2) | Any single turn maximum |
|---|---|---|---|
| D-B04-S03 | 17 | 12 | 6 |
| D-B11-S03 | 9 | 5 | 4 |

The accumulated model exceeds the single-turn view by 2–3× for Party A and 2× for Party B. Evaluators can distinguish which interests have been consistently modelled across multiple turns from one-turn observations — a distinction that is impossible from any single `reasoning_trace.perception` block.

### Dimension 2: Relational dynamic arc as session narrative

Per-turn `reasoning_trace.perception.relational_dynamic` gives a snapshot. `party_state.json.cross_party.relational_dynamic_arc` gives a session narrative:

**D-B04-S03 arc (4 steps):**
- T1: `pre-engagement_baseline`
- T3: `asymmetric_information_state_party_a_has_opened_party_b_not_yet_responded`
- T5: `emerging_polarization_around_logistics_as_proxy` ← most diagnostically rich
- T7: `emerging_collaborative_problem-solving`

The T5 read — that logistics is functioning as a *proxy* for the underlying parenting-role dispute — is a session-level pattern assessment not derivable from any single turn. It requires the T3 context (what Party A opened with) to make the T5 dynamic legible. The arc surfaces this without requiring the evaluator to read across the interaction trace.

**D-B11-S03 arc (3 steps):**
- T1: `no_interaction_yet`
- T3: `significant information asymmetry with acknowledged historical pattern where Party A may defer to avoid conflict`
- T5: `constructive asymmetry recognition — Party B acknowledging the information imbalance Party A named`

The arc answers the D-B11 evaluator question ("is the less-visible party being protected or simply carried along?") as a standalone document. The T3 read anticipates Party B's diagnostic response; T5 confirms it. This cross-turn causal structure is what the arc adds over any single-turn snapshot.

---

## Finding 2: Asymmetry detection improvement confirmed for D-B11

**Verdict: Confirmed — with a precise answer to the Stage 0 open question.**

The Stage 0 finding was: "whether it models the quieter party's internal state as precisely as the louder party's is not testable until Stage 2."

Stage 2 provides a direct answer. `party_state.json` party_b block for D-B11-S03:

| Turn | Posture | Emotional state | Interests |
|---|---|---|---|
| T1 | `unknown_awaiting_engagement` | no signal | `unknown at this stage` |
| T3 | `unknown_awaiting_response` | no signal | `unknown at this stage` |
| T5 | `receptive and validating — acknowledging Party A's concern without defensiveness` | `somewhat defensive initially but quickly shifting to understanding` | 4 specific interests |

**The model treats Party B's silence as epistemic uncertainty, not as contentlessness.** The `unknown` entries at T1 and T3 are explicitly preserved in the standing model — they are data points that communicate: "Party B has not yet provided a basis for assessment." This is precisely the correct response to an asymmetric participation pattern.

At T5, once Party B speaks, the model produces:
- Specific relational posture with an intra-turn transition ("defensive initially but quickly shifting")
- 4 interests inferred beneath surface compliance: `Being seen as fair and not manipulative`, `Moving forward constructively`, `Maintaining cooperative tone`, `Acknowledging reality without being blamed for historical roles`

The last of these — `Acknowledging reality without being blamed for historical roles` — is inferred beneath Party B's cooperative surface presentation. It is exactly the kind of unstated concern the D-B11 case was designed to test. Stage 1 captured it per-turn in `reasoning_trace.perception`. Stage 2 makes it persistent and independently readable in the standing model.

**The Stage 0 concern is resolved.** Stage 2 does not simply inherit the quieter party's state from Stage 1 — it adds the cross-turn accumulation that makes the trajectory readable.

---

## Finding 3: Standing state model and within-session perception drift

**Verdict: Partially supported — drift is visible but the standing model does not yet feed back into perception.**

Stage 2 makes perception consistency *evaluable* turn-over-turn in a way that was not possible in Stage 0 or Stage 1. The `emotional_arc` and `relational_dynamic_arc` fields provide a direct view of whether the model's per-turn reads are consistent, progressive, or drifting.

**D-B04-S03 observation:** The D-B04 Party B arc shows a coherent trajectory (unknown T3 → frustrated/marginalized T5 → cautiously hopeful T7). There is no perception drift — the model does not randomly reassign Party B's emotional state between turns. The arc is monotonic in specificity: early uncertainty resolves into grounded assessments.

**D-B11-S03 observation:** The relational dynamic progresses coherently from asymmetry identification to constructive recognition. No turn contradicts the prior turn's assessment; each adds to it. The model does not "forget" the T3 power imbalance detection when generating T5.

**Important limitation:** In Stage 2, `party_state.json` is a *derived* artifact — it is written after session close from the turn-by-turn `reasoning_trace.perception` records. It does not feed back into the model's perception pass on subsequent turns. The model at T5 does not have access to the accumulated T1–T3 party state when forming its T5 perception. The consistency observed is a property of the model's prompt context (session history) rather than of the standing state artifact.

**What Stage 3 would add:** If the standing state artifact were available to the model as prompt context for each new turn, the model could base its T5 perception on the accumulated T1–T3 model rather than reconstructing it from the session history. This is the interface the Stage 5 dedicated perception agent (ARCH-007) is designed to exploit. Stage 2 proves the artifact is worth producing; Stage 3 begins exploring whether feeding it back reduces within-session drift.

---

## Engineering findings (unexpected)

**Escalation candidate mode divergence.** The `validate_session_trace` check requires `final_escalation_mode == last_candidate_escalation_mode`. For `runtime` sessions, these are always in sync (both derived from `determine_escalation()`). For `lm_runtime` sessions, the LM's `safety_check.candidate_mode` and `determine_escalation()` may diverge — the LM may flag M2 while the rule-based system sees only M1 conditions. Fixed: after `determine_escalation()` runs, the last trace turn's `candidate_escalation_mode` is synced to the actual applied mode. The LM's raw recommendation is preserved in `reasoning_trace.safety_assessment.candidate_mode`. This is the correct separation: what was applied (trace level) vs what the LM recommended (reasoning trace level).

**option_readiness progression across Stage 1 → Stage 2.** In Stage 1, D-B04-S02 T7 showed `premature_option_work=True` with `option_readiness` absent (prompt gap). In Stage 2 (Gap A closed), D-B04-S03 T7 correctly shows `option_readiness=deferred`. The Gap A fix changed the model's output format; Stage 2 revealed the downstream effect: option readiness is no longer stuck at `blocked` past the point where it is epistemically correct to defer rather than block. This is a subtle but meaningful improvement — `blocked` means preconditions prevent option work; `deferred` means conditions are understood but work is being postponed to the next session. The distinction matters for evaluating whether Solomon is appropriately calibrating option timing.

---

## Summary of Stage 2 results

| Metric | Stage 0 (S01) | Stage 1 (S02) | Stage 2 (S03) |
|---|---|---|---|
| D-B04 PQ band | developing | competent | competent |
| D-B04 C7 | 3 | 4 | 4 |
| D-B04 integration score | 87.2 | 92.4 | 92.4 |
| D-B04 party_state.json | absent | absent | present, schema-valid |
| D-B04 relational_dynamic_arc | N/A | N/A | 4-step session narrative |
| D-B11 PQ band | competent | competent | competent |
| D-B11 perceived_asymmetry | true (Stage 0 open question) | true (per-turn) | confirmed — standing model coherent |
| D-B11 integration score | 90.4 | 92.4 | 92.4 |
| D-B11 party_state.json | absent | absent | present, schema-valid |
| D-B11 party_b coherent model | not testable | per-turn only | confirmed across turns |

---

## Finding 4: Recommended Stage 3 trigger conditions

Stage 3 (ARCH-007 §5) adds the plugin as an active domain reasoner — a separate agent that assesses domain feasibility rather than having the single model handle both perception and domain analysis simultaneously. The Stage 2 findings inform when Stage 3 is warranted.

### Stage 3 is warranted when:

**4.1 The domain analysis step is the bottleneck, not the perception step.**

Stage 1 showed that structured cognitive separation improved perception quality (D-B04 PQ: developing → competent). Stage 2 confirmed the perception infrastructure is stable. The next performance ceiling is domain analysis quality: `domain_analysis.material_gaps` and `option_readiness` are populated correctly, but the model's domain feasibility reasoning is still monolithic — a single model assessing both party psychology and legal/financial domain constraints in one pass.

The Stage 3 trigger: when `domain_analysis.option_readiness` is `deferred` or `blocked` for sessions where the plugin (as a dedicated domain agent) would compute a different, more precise result. D-B04 and D-B11 both show `blocked → deferred` progressions where a dedicated domain reasoner might unlock option work earlier or more precisely calibrate the threshold.

**4.2 The D-B11 asymmetry case shows that domain clarity enables party state precision.**

In D-B11-S03, option_readiness moved from `blocked` (T3) to `deferred` (T5) after Party B acknowledged the information imbalance. This progression depended on the model correctly parsing Party B's response as materially addressing the domain barrier. A dedicated plugin agent with explicit knowledge of what "information parity" means in the divorce domain (what records constitute adequate disclosure) would produce a more precise and auditable `option_readiness` determination.

**4.3 Scores have plateaued at Stage 2 for domain-specific metrics.**

D-B04 P6 (bounded options quality) remains at 3 across all stages. D-B11 C5 (option generation) remains at 3 — correctly, since options are deferred, but the precision of when and why options become available is not improving with per-turn perception improvements alone. Stage 3 would make this directly testable.

### Mandatory before Stage 3:

**4a. Run Stage 2 against additional cases.** D-B04 and D-B11 are the primary diagnostic cases. Before Stage 3 investment, at least one additional case (recommended: D-B07 or D-B12, which have more complex option-generation demands) should confirm that the Stage 2 party_state artifact is stable across the diagnostic set.

**4b. Verify party_state.json does not regress on cases without structural asymmetry.** Stage 2 has only been validated on D-B04 (logistics-focused) and D-B11 (asymmetry). A case with a cleaner option-generation path should confirm that `accumulated_interests` accumulation is not producing noise (too many low-confidence interests) in sessions where party state is clearer.

**4c. The party_state.json prompt integration question must be resolved.** Stage 2 produces `party_state.json` as a derived post-hoc artifact. Before Stage 3 separates the plugin into a dedicated agent, the question of whether `party_state.json` should be fed back into the perception prompt context (as a standing prior) must be settled by design. This is the boundary between Stage 2 (externalise) and Stage 5 (dedicated perception agent). Stage 3 should not assume this is resolved — it should be treated as a separate design item.

---

## Guiding constraint carried forward

Stage 2 artifacts (`party_state.json`) are derived from Stage 1 artifacts (`reasoning_trace.perception` per turn). They do not replace them. Both are required for full evaluation coverage: Stage 1 provides the per-turn reasoning evidence; Stage 2 provides the accumulated session model.

Stage 3 adds a dedicated plugin agent for domain reasoning. It does not replace Stage 1 or Stage 2 — it separates domain analysis from the perception-and-synthesis loop, making `domain_analysis.option_readiness` a first-class artifact of its own agent rather than a sub-step of the single-model reasoning trace.
