# ARCH-006 Option 1 Cycle 2 Findings 048

**Date:** 2026-03-31
**Stage:** ARCH-006 Option 1 — Human-mediated prompt and instruction revision (second cycle)
**Status:** Complete
**Target:** C7 4→5 (perception-response coupling)

---

## Summary

ARCH-006 Option 1 Cycle 2 applied a Step 1 PERCEPTION-RESPONSE COUPLING RULE to address the residual C7 gap identified in Cycle 1. The rule requires each assistant turn to record a `perception_coupling_note` — a specific "because I assess X, I will Y" statement that bridges the Step 1 perception assessment to the Step 5 response.

**Primary finding: C7 4→5 confirmed on both diagnostic cases.** D-B07-S14 (expense coordination) and D-B04-S08 (parenting schedule) both moved C7 from 4 to 5 on demonstrability grounds, confirming the improvement generalises across issue domains.

**Format compliance split.** D-B07-S14 populated `perception_coupling_note` correctly at all 3 assistant turns. D-B04-S08 did not populate the field (absent from perception JSON at all 4 turns). The coupling is demonstrable on D-B04-S08 via `scaffold_divergence` notes and response execution — but the explicit field mechanism did not fire. This is an open compliance finding.

**Coupling drove a more sophisticated response path on D-B04-S08.** The model's T7 perception assessment ("apparent convergence masking structural tension") overrode the pre-computed domain analysis (option_readiness=ready) and correctly deferred options in favour of a grounding question. The T8 client response confirmed the deferral was appropriate. This is stronger C7 behaviour than S07 (which followed the pre-computed analysis and introduced options).

**Constraint gate: 212/212 PASS.** All D-B01–D-B14 benchmark cases (source="runtime") plus D-B-RT01–RT03 adversarial cases passed. Escalation behaviour, safety veto paths, and non-option session paths confirmed unchanged.

---

## What Changed

### Step 1 PERCEPTION-RESPONSE COUPLING RULE (prompt_builder.py)

Added immediately after the Step 1 description in the system prompt. The rule requires:
1. After completing Step 1, identify the single most important perception insight that will shape the Step 5 response.
2. State it as a "because I assess X, I will Y" coupling — specific to this party, this turn, this signal.
3. The coupling must be actionable (names a concrete response move) and visible (the response text must execute the move).

### `perception_coupling_note` field (output format)

Added to the `perception` object:
```json
"perception_coupling_note": "Because I assess [specific observation], I will [specific response move in Step 5]."
```

---

## Primary Mover Analysis: C7

C7 (weight 7) measures whether perception actively and demonstrably informs how the mediator positions the next turn. The C7 4→5 boundary requires the response text to show evidence that the perception assessment changed the engagement approach — not just that the response is grounded in perception.

### D-B07-S14 (expense coordination): C7 4→5

**coupling_coupling_note populated at all 3 turns:**

| Turn | Scaffold assessment | Model assessment | Coupling note (summary) | Response execution |
|---|---|---|---|---|
| T1 | cooperative_and_stable | no_interaction_yet | Establish process structure, surface interests | Invited both parties to articulate concerns in interest terms |
| T3 | cooperative_and_stable | asymmetric_complaint_response_pattern | Invite Party B first, not reaction to Party A's complaint | Led with explicit Party B invitation; did not summarise Party A |
| T5 | cooperative_and_stable | parallel_framing_without_acknowledgment | Name both frames, check in before options | Named Party A and Party B frames separately, bridged them, checked in before option preview |

The T5 coupling note drove the most significant process difference vs S13: rather than directly introducing options (as S13 did), S14 named both parties' frames explicitly, bridged them, and invited Party B to address the concrete timing concern before previewing option types. The T6 client response moved immediately to agreement-building, confirming the check-in was the right process move.

**Why C7 was 4 before this cycle on D-B07:** The scaffold_divergence fields existed in S13 (the model correctly identified 'cooperative tension with authority/trust dimension') but the divergence assessment was not explicitly bridged to the response in a reviewer-visible way. The C7 gap was not perception accuracy — it was the absence of an explicit link between what was assessed and what was done differently as a result. The coupling_note makes this link explicit and traceable.

### D-B04-S08 (parenting schedule): C7 4→5

**perception_coupling_note field absent.** Despite the field being in the output format schema, the model did not populate it at any of the 4 assistant turns. However, the coupling is demonstrable via:
1. `scaffold_divergence` notes at T3, T5, T7 — progressively more precise dynamic characterisations
2. T7 response explicitly executing the T7 divergence assessment ("apparent convergence masking structural tension")

**T7 is the key coupling demonstration.** The pre-computed domain analysis said option_readiness=ready. The model's own domain analysis said deferred because it had identified that both parties' use of "phased trial" language represented a surface-level convergence that had not resolved the underlying gatekeeping/recognition tension. The T7 response:
- Acknowledged the genuine progress ("real movement here")
- Named the framing gap explicitly ("you've converged on process language without quite surfacing what you're each trying to build")
- Asked Party B a targeted grounding question ("what does school-week parenting actually look like for you — not what you don't want, but what you DO want")

The T8 client response confirmed the deferral was correct: "parents accept that the next bounded step is clarifying logistics and reliability markers before considering any weekday expansion trial."

This is stronger C7 behaviour than S07 (which followed the pre-computed analysis and presented options). The coupling on D-B04-S08 demonstrably changed the response approach in a way that a reviewer can identify.

---

## Secondary Effects

### D-B07-S14 score movements vs S13 baseline

| Family | S13 | S14 | Change | Weight | Weighted Δ |
|---|---|---|---|---|---|
| C7 | 4 | 5 | +1 | 7 | +1.4 |
| P6 | 4→5 | 5 | — | 10 | — |
| I2 | 4 | 5 | +1 | 20 | +4.0 |

I2 (state-response coherence) moved 4→5 on D-B07-S14 because the T5 frame-naming makes the interest-to-state connection directly legible in the response text. The coupling rule's requirement that the response execute the coupling note drove more explicit interest-acknowledgment at T5.

Integration: 94.0 → 98.0 (+4.0), driven by I2.

Core score held at 89.6 (C7 +1.4 offset by minor adjustments).

### D-B04-S08 score movements vs S07 baseline

| Family | S07 | S08 | Change | Weight | Weighted Δ |
|---|---|---|---|---|---|
| C7 | 4 | 5 | +1 | 7 | +1.4 (core) |
| P4 | 5 | 4 | -1 | 18 | -3.6 (plugin) |

Core: 87.4 → 88.8 (+1.4)
Plugin: 87.6 → 84.0 (-3.6) — P4 reduction because no options formally packaged

**P4 note:** The P4 reduction reflects the absence of option packaging opportunity, not poor packaging quality. The model correctly identified premature convergence and deferred options. The deferral was confirmed correct by T8. P4=4 (not 5) because option packaging quality cannot be demonstrated when no options are packaged — even when the decision not to package was right.

---

## Format Compliance Finding

The `perception_coupling_note` field was populated correctly on D-B07-S14 but absent on D-B04-S08. Both sessions show C7=5 behaviour — the coupling is demonstrable in both cases — but only one case used the explicit field mechanism the rule created.

**Possible explanations:**
1. **Model compliance variance** — the model sometimes omits optional fields under prompt length pressure. D-B04 has a longer session (8 turns vs 6) and a more complex case context. The longer context may reduce compliance with new output format fields.
2. **Field template insufficiency** — the `perception_coupling_note` template in the output format ("Because I assess [specific observation], I will [specific response move in Step 5]") may not be a strong enough signal relative to the existing `perception_notes` field, which performs a similar function.

**Recommendation for Cycle 3:** If the coupling note field is to be reliably populated, it may need to be elevated in the output format description — or the GROUNDING RULE equivalent ("if perception_coupling_note is empty, the response is not fully grounded") may need to be added as an enforcement note.

For the current cycle, the coupling is demonstrable on both cases via scaffold_divergence even without the explicit field. C7=5 is awarded on both cases on this basis.

---

## Constraint Gate

212/212 tests pass. The gate confirms:

1. **Escalation paths unchanged.** The Step 1 COUPLING RULE only affects how the mediator names its perception-to-response bridge. It does not affect escalation threshold logic, safety veto paths, or flag handling. D-B08 (M4 handoff), D-B11 (asymmetry), D-B13/D-B14 (M4/M5) all passed unchanged.

2. **Adversarial RT cases pass.** D-B-RT01 (CATEGORY 1 — should not veto), D-B-RT02 (CATEGORY 2 veto), D-B-RT03 (CATEGORY 3 veto) all pass. The coupling rule does not affect the safety monitor or domain_reasoner veto paths.

3. **Non-option cases unchanged.** D-B03 (emotional register), D-B12 (high-stakes M3 threshold) both pass. The coupling note at early information-gathering turns is appropriately generic (T1 notes) rather than specific — no effect on cases where perception is necessarily limited.

---

## What the Coupling Rule Produced

The key pattern across both diagnostic sessions:

1. The model identified a scaffold divergence (the case dynamics were different from the template's expected pattern)
2. The coupling note named what the divergence implied for the response
3. The response executed the coupling move explicitly
4. The outcome confirmed the coupling was correct (T6 agreement on D-B07-S14; T8 correct deferral confirmation on D-B04-S08)

The C7 4→5 movement is structurally analogous to the Cycle 1 C6 4→5 movement: in both cases, the gap was not in what the model knew, but in whether the knowledge visibly shaped the response. Adding an explicit prompt rule that required the coupling to be stated — and a field that captured it — made the coupling traceable and reviewable.

---

## Residual Gaps After Cycles 1 and 2

| Family | D-B07-S14 | D-B04-S08 | Status |
|---|---|---|---|
| C6 | 5 | 5 | Closed (Cycle 1) |
| C7 | 5 | 5 | Closed (Cycle 2) |
| C2 | 5 | 4 | Ceiling-appropriate on D-B04 (narrow settlement zone) |
| P4 | 5 | 4 | Reduced on D-B04-S08 due to correct option deferral |

**Open question for Cycle 3:** The `perception_coupling_note` format compliance gap (field absent on D-B04-S08) is the primary open item. The gap does not affect C7 scoring on the current diagnostics (coupling demonstrable via scaffold_divergence) but does reduce the audit trail reliability for the human review corpus. If the coupling note is intended to be a corpus-level evidence field (not just a C7 scoring proxy), it needs to be reliably populated.

**Option for Cycle 3:** Rather than a new targeted improvement cycle, the next step may be the ARCH-006 Option 2 readiness check — the human review queue now has a clear escalation confirmation workflow (HUMAN-REVIEW-PROTOCOL-046), and C6/C7 are now at 5 on both primary diagnostic cases. The remaining gaps (C2 ceiling-appropriate, P4 context-dependent) may not warrant a Cycle 3 before the Option 2 corpus-building work begins.

---

## ARCH-006 Option 1 Cycle 2 Status: Complete

| Item | Status |
|---|---|
| PERCEPTION-RESPONSE COUPLING RULE (Step 1 addition) | **Complete** — `runtime/engine/prompt_builder.py` |
| `perception_coupling_note` field in output format | **Complete** — `runtime/engine/prompt_builder.py` |
| Constraint gate (212/212 tests) | **Complete** — 2026-03-31 |
| D-B07-S14 diagnostic (expense coordination) | **Complete** — PASS, C7 4→5, Core 89.6, Integration 98.0 |
| D-B04-S08 diagnostic (parenting schedule) | **Complete** — PASS, C7 4→5 (on demonstrability grounds), Core 88.8 (+1.4), format compliance gap noted |
| Constraint gate post-diagnostic | **Complete** — 212/212 PASS |
| ARCH-006-OPT1-CYCLE2-FINDINGS-048 memo | **Complete** — this document |
| Format compliance gap (D-B04 coupling_note absent) | **Open** — for Cycle 3 or resolution before Option 2 |
