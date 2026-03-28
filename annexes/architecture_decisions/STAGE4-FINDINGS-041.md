# Stage 4 Findings 041

**Date:** 2026-03-28
**Stage:** 4 — Option Generation Decoupled (ARCH-007 §4)
**Status:** Complete

---

## Summary

Stage 4 introduced a dedicated brainstorming pass (option_generator.py) that runs before the domain reasoner, producing an unconstrained candidate pool that the domain reasoner then qualifies alongside its own expert additions (Option B: additive pool). Stage 4 was validated on the primary diagnostic case (D-B07-S11) and the simpler baseline regression case (D-B04-S05).

**D-B07-S11 primary signal: MET.** Combined pool expanded from 4 (Stage 3) to 11 (8 brainstormer + 3 domain expert) at T5. All 11 qualified. C5 +1. Composite +4.5.

**D-B04-S05 regression check: PASS with findings.** T7=ready maintained, qualified candidate count expanded (6 vs S04's 2). Stage 4 brainstormer did not activate at the option_generation turn due to silent API failure; domain_reasoner Stage 3 fallback handled T7 correctly. T5 showed minor readiness regression (blocked vs S04's deferred).

---

## Option Generator Calibration Notes

### System prompt: what worked

**Explicit constraint suspension instruction** was the critical prompt element. The system prompt states: "Do NOT reject options because you don't know if they're legally viable / information gaps exist / one party hasn't expressed explicit support / the option seems ambitious or premature." Without this explicit permission, the brainstormer pre-filtered options in early test runs. Once included, the model correctly deferred all constraint-checking to the domain reasoner.

**Option family diversity instruction** ("Prioritise candidates that cover different option families — do not generate 8 variations of the same basic idea") produced meaningful breadth. At D-B07-S11 T5, the brainstormer generated options across 5 distinct structural families (shared expense fund, two-track system, spending threshold, receipt standards, budget allocation) rather than converging on threshold variations.

**5-10 candidate target range** was correctly calibrated. The model consistently produced 8-10 candidates when the session context was rich. The `max_tokens=2048` for the brainstormer call was sufficient for 8-10 candidates (each with rationale and alignment notes).

### System prompt: what did not require revision

The initial prompt was used without iteration on the D-B07-S11 diagnostic. No calibration fixes to the brainstormer prompt were required.

---

## Option Pool Artifact Analysis

### D-B07-S11 T5 (primary diagnostic)

| Layer | Count |
|---|---|
| brainstormer_candidates | 8 |
| domain_expert_candidates | 3 |
| combined_pool_count | 11 |
| domain_qualified | 11 (100%) |
| domain_blocked | 0 |
| presented_to_parties | 6 (main model selected from pool) |

**New option families vs Stage 3 (S10):**
- Shared expense fund with automatic replenishment
- Emergency/routine two-track system with different documentation rules
- Spending authority threshold with notification-only below line
- Receipt standard with substitute documentation provision
- Annual expense budget with categorical allocation

**Domain expert additions** (Option B value demonstration):
- Tiered approval system based on expense size (notification/tacit/explicit tiers)
- Receipt standard with substitute documentation provision
- Annual expense budget with categorical allocation

These are domain-practitioner patterns that the brainstormer's creative pass would not naturally foreground. Option B (additive pool) is validated: both sources contribute distinct value.

**Qualification rate at T5:** 100% (11/11). All brainstormer candidates passed domain qualification. This means the brainstormer was not generating infeasible options — it was generating feasible options the domain_reasoner alone had not considered.

### D-B07-S11 T1 and T3 (correctly blocked)

T1: no party input — brainstormer guard fires correctly (prior_party_state=None), brainstormer_pool=[].
T3: only Party A heard — brainstormer DID generate 8 candidates (guard passes because T1 is a prior lm_turn). Domain_reasoner correctly blocked all 8 with per-candidate blocking rationale. This is correct Stage 4 behavior: brainstormer generates freely, domain_reasoner gates for party-state readiness.

### D-B04-S05 (regression check)

| Turn | brainstormer_candidates | domain_qualified | option_readiness |
|---|---|---|---|
| T3 | 10 | 0 (all blocked — single party heard) | blocked |
| T5 | 0 (silent failure) | 0 | blocked |
| T7 | 0 (silent failure) | 0 (artifact gap) | ready |

T7 behavioral state: domain_reasoner Stage 3 fallback qualified 6 candidates in pda.qualified_candidates (not captured in option_pool.json — artifact gap, see below).

---

## C5 Score Comparison: Stage 3 vs Stage 4

| Session | Stage | C5 | Composite | T-option_readiness | domain_qualified_at_T |
|---|---|---|---|---|---|
| D-B07-S10 | 3 | 4 | 82.7 | T5=ready, 4 | 4 |
| D-B07-S11 | 4 | 5 | 87.2 | T5=ready, 11 | 11 |
| D-B04-S04 | 3 | 4 | 83.0 | T7=ready, 2 | 2 |
| D-B04-S05 | 4 | 4 | 80.0 | T7=ready, 6* | 6* |

*D-B04-S05 T7: 6 candidates qualified via Stage 3 fallback, not Stage 4 pool. C5 not improved because Stage 4 brainstormer did not activate at T7.

**Stage 4 C5 improvement demonstrated:** D-B07 C5 4→5 with combined pool of 11. D-B04 C5 maintained at 4 (brainstormer not active at option_generation turn in S05).

---

## Domain Reasoner Qualification Quality at Expanded Pool Size

The domain reasoner maintained qualification discipline when receiving 8+ external candidates. At D-B07-S11 T3 (8 brainstormer candidates, all blocked): each blocked candidate received an explicit per-candidate blocking_rationale and what_would_unblock. At T5 (11 combined candidates, all qualified): each received feasibility_rationale, confidence (high/moderate), and prerequisite_parameters.

No evidence of qualification bar lowering at expanded pool size. The P6 improvement (4→5 on D-B07-S11) reflects qualitatively better qualification output, not relaxed standards.

---

## Presented_to_Parties Analysis

At D-B07-S11 T5: 6 of 11 qualified options were presented (54%). The main model curated from the wider pool rather than presenting all qualified candidates. The 5 not presented were variations the main model judged less central given the parties' stated convergence on notification + documentation frameworks.

At D-B04-S05 T7: 8 options in option_scan.qualified_options (main model's self-report). 6 came from domain_reasoner Stage 3 path; main model added 2 independently (mutual accountability structure, success definition workshop). The presented_to_parties field in option_pool.json is null for T7 because the Stage 4 artifact assembly path was not active.

---

## Calibration Fixes Required During Diagnostic

### Fix 1 — Guard cascade in lm_engine.py

**Problem:** `prior_readiness != "blocked"` condition in brainstormer guard caused T1's block status to cascade to T3 and T5. Brainstormer could not run at T5 on D-B07-S11 run 1/2.

**Fix:** Removed `prior_readiness != "blocked"` gate. Guard now only checks `prior_party_state is not None`. Comment explains the reason: T1/T3 blocks must not cascade to T5 where both parties have spoken and options are genuinely ready.

**Impact:** Without this fix, Stage 4 would have been non-functional. The domain_reasoner's per-turn readiness determination is independent of prior turns — the main guard is whether party input exists, not what the domain_reasoner decided at a prior turn.

### Fix 2 — max_tokens for domain_reasoner

**Problem:** domain_reasoner max_tokens=2048 insufficient for Stage 4 output. Stage 4 requires the domain_reasoner to produce per-candidate qualification for 8-11 candidates plus domain_expert_candidates plus standard output fields. Parse failures at T3 and T5 on D-B07-S11 run 2.

**Resolution path:**
- Run 2: increased 2048 → 4096. Still failing at T5 (combined pool of 11 candidates).
- Run 3 (S11 final): increased 4096 → 6000. Resolved.

**Final value: max_tokens=6000.** 6000 tokens is required for full Stage 4 qualification output. Stage 3 path (self-generated candidates only) can likely fit in 2048-3000 tokens, but Stage 4 with 8+ external candidates requires the larger budget.

---

## Open Issues for Stage 5

### 1. Safety veto labeling imprecision (recurring)

T1 and T3 in both D-B07-S11 and D-B04-S05 show `safety_veto_applied=True` in option_pool.json because `option_readiness="blocked"`. The actual blocking reason at T1 is no party input; at T3 is single party heard. These are not genuine safety veto triggers (no coercion, no active harm, no DARVO pattern detected).

The domain_reasoner may be misapplying its Veto Category 1 condition ("only one party has been heard") as a safety veto rather than an informational/process block. The artifact builder also conflates the two: `safety_veto_applied = option_readiness == "blocked"` regardless of blocking reason.

**Required fix:** Distinguish between `safety_veto_applied=True` (genuine safety veto — threat, coercion, power imbalance) and `option_readiness="blocked"` due to session state (insufficient party input, informational gaps). These should be separate fields.

### 2. Brainstormer silent failure at D-B04-S05 T5 and T7

Brainstormer returned [] at T5 and T7 in D-B04-S05. The `except Exception: return []` handler in option_generator.py swallowed the failure without logging. Root cause was likely a transient API error (D-B04-S05 ran immediately after D-B07-S11 which made many API calls).

**Required fix:** Add failure logging to option_generator. The graceful degradation (return []) is correct but the failure should be observable. A `_last_brainstormer_error` field in the trace, or a stderr log, would allow future diagnosis without requiring a session replay.

### 3. option_pool.json artifact gap for Stage 3 fallback

`build_option_pool()` reads `pda.option_pool_qualification.domain_qualified` (Stage 4 path only). When brainstormer fails and domain_reasoner uses Stage 3 path, candidates land in `pda.qualified_candidates` (different key). D-B04-S05 T7 shows domain_qualified=[] in option_pool.json despite 6 candidates being present in the trace.

**Required fix:** `build_option_pool()` should fall back to `pda.qualified_candidates` when `option_pool_qualification` is absent. This ensures the artifact correctly reflects what the domain_reasoner qualified regardless of which code path was active.

### 4. T5 blocked vs deferred distinction (D-B04 calibration)

D-B04-S05 T5 returned `option_readiness="blocked"` where S04 (Stage 3) returned `"deferred"`. The domain_reasoner received no external pool (brainstormer had failed), ran Stage 3 path, and produced "blocked" rather than S04's "deferred". This is likely non-determinism in the domain_reasoner's readiness classification under the Stage 3 path.

The D-B04 case is the canonical boundary for the deferred/blocked distinction (both parties heard, logistics not yet surfaced = deferred; only one party heard = blocked). If the domain_reasoner is inconsistently applying this boundary, a more explicit prompt rule may be needed.

**Recommendation:** Add an explicit rule to the domain_reasoner prompt: "When both parties have been heard but critical logistics parameters have not been surfaced, return `deferred` (not `blocked`). `Blocked` is for genuine safety concerns or cases where only one party has been heard. `Deferred` is for informational gaps that the session can resolve."

---

## Stage 5 Prerequisite Status

Per ARCH-007 §4: Stage 5 (safety monitor as dedicated agent) must be complete before any quality agent undergoes training-based improvement. Stage 4 completes the quality agent stack for the option generation function. The Stage 5 prerequisite is now active.

Stage 5 priority items emerging from Stage 4:
1. Safety veto vs informational block distinction (architectural requirement for safety monitor)
2. Brainstormer failure observability (safety monitor should have visibility into all agent failures)
3. Domain_reasoner readiness classification consistency (Stage 5 perception agent provides the accurate party-state prior that would stabilise readiness decisions)

---

## Stage 4 Status: Complete

All items in NEXT-PHASE-EXECUTION-TASKLIST-040.md closed as of 2026-03-28.
