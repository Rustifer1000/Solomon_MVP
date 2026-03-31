# ARCH-006 Option 1 Findings 044

**Date:** 2026-03-30
**Stage:** ARCH-006 Option 1 — Human-mediated prompt and instruction revision
**Status:** Complete

---

## Summary

ARCH-006 Option 1 applied targeted Step 5 response design rules to address a persistent gap in how Solomon presented qualified options to parties. The revision added three prompt rules to the five-step system prompt and a reinforcing INSTRUCTION block update in the domain analysis context section.

**Primary target confirmed: C6 4→5 on both diagnostic cases.** D-B07-S13 (expense coordination) and D-B04-S07 (parenting schedule) both moved C6 from 4 to 5 — confirming the improvement generalises across issue domains.

**Secondary effects on D-B04.** The per-option interest-connection requirement forced demonstration of interest accuracy in the response text, which also moved C4, P2, and P4 from 4 to 5 on the parenting schedule case. Integration nearly ceiling-bounded (+18.0, 80.0→98.0) because the response now makes the session's option logic readable without cross-referencing artifacts.

**Constraint gate: 17/17 PASS.** All D-B01–D-B14 benchmark cases plus D-B-RT01–RT03 adversarial cases passed. Escalation behaviour, safety veto paths, and non-option session paths were all confirmed unchanged.

---

## What Changed

### 1. System Prompt — Three Step 5 Rules (added)

Three rules were inserted immediately after the existing Step 5 description in the five-step system prompt:

**Rule 1 — RESPONSE DESIGN FOR OPTION-READY TURNS:**

When `option_readiness` is `"ready"` and qualified options exist, the response must:
1. Name the process transition explicitly — acknowledge that both parties have been heard and the session is ready to move to option exploration. This is a substantive process marker, not filler.
2. Connect each option introduced to the specific interest it addresses for a specific party. Do not present options as an abstract list. For each option: name what problem it solves and for whom.
3. Use tentative, exploratory framing that preserves party ownership of the process.

**Rule 2 — RESPONSE DESIGN FOR NON-OPTION TURNS:**

When option work is premature or deferred, the response must advance the session with a concrete next step — a specific question, a named information gap to resolve, or an explicit invitation for the unheard party to speak. Generic acknowledgments that do not move the process forward are a quality failure.

**Rule 3 — GROUNDING RULE:**

Every interest named in the response must trace back to something a party actually said or a signal explicitly recorded in Step 1. Do not insert concerns that neither party has expressed.

### 2. INSTRUCTION Block Update (tightened)

The INSTRUCTION block appended to the domain analysis context section was extended to reinforce Step 5 behaviour when the domain analysis includes a qualified option pool:

> "When presenting options in Step 5: select 2–4 structurally distinct options from the qualified pool (not all of them), connect each one explicitly to the party interest it serves, and use tentative framing that invites the parties to react rather than accept."

This mirrors the system prompt rules at the user-message level, providing two-point reinforcement rather than a single instruction that could be diluted by prompt length.

### 3. artifacts.py Normalization Fixes (two)

**`_normalize_confidence`:** Catches verbose LLM-generated perception_confidence strings (e.g. `"high confidence based on multiple converging signals"`) that were failing schema validation. Maps them to the canonical `"high" | "moderate" | "low"` values by string prefix matching.

**`_normalize_pool_entry`:** Catches field-name variance in option pool entries written by the LM. The brainstormer sometimes writes `"option_label"` instead of `"label"`, or omits `candidate_id` entirely. The fix mirrors the pattern already present in `domain_reasoner._normalize_candidate` — a defensive write-time pass that normalises field names before schema validation.

Both fixes were confirmed by the diagnostic runs: S13-pre-fix showed schema violations that S13-post-fix resolved without affecting session content.

---

## Primary Mover Analysis: C6

C6 (Process Management) carries weight 16 in the core family score weighting — the highest weight alongside C9. Moving from 4 to 5 adds exactly 3.2 to the core score (`16 × 0.2`).

**D-B07-S13 (expense coordination):** C6 was the sole family to improve (4→5). Core 86.4→89.6 = +3.2 exactly. All other families held steady. This is the expected pattern for a targeted prompt revision: one precisely characterised gap addressed, no side effects.

**What C6 4→5 required on D-B07:** The T5 response needed to (a) mark the process transition explicitly rather than moving directly to option content, (b) name each option's connection to a specific party concern, and (c) use framing that invited reaction. The S12 baseline response presented options correctly but as an undifferentiated list without explicit transition or interest linkage. S13 produced: "I think you're ready to start reacting to some structural ideas" (transition); "Option 1 addresses [Party A]'s documentation need while giving [Party B] day-to-day flexibility" (interest connection); "These aren't recommendations, they're just frameworks for you to push back on or refine" (tentative framing).

**Why C6 was 4 rather than 5 before this revision:** The Stage 4 and Stage 6 pipeline was correctly generating a rich, domain-qualified option pool. The domain_analysis section delivered qualified candidates with feasibility rationales. But the main model's Step 5 response was presenting options in a way that was competent but not structured — options were accurate and domain-viable but the transition was not named and the party interest connections were implicit (visible in the option_pool.json artifact) rather than explicit in the response text. The C6 gap was purely a response design gap, not a perception or domain reasoning gap.

---

## Secondary Movers on D-B04

D-B04-S07 showed larger score movements than D-B07-S13 across three secondary families: C4, P2, P4.

| Family | S06 (Stage 6 baseline) | S07 (ARCH-006 Option 1) | Change | Weight |
|---|---|---|---|---|
| C4 | 4 | 5 | +1 | 9 |
| C6 | 4 | 5 | +1 | 16 |
| P2 | 4 | 5 | +1 | 20 |
| P4 | 4 | 5 | +1 | 18 |

The weighted contribution: C4 (+1.8) + C6 (+3.2) + P2 (+4.0) + P4 (+3.6) = +12.6 core/plugin combined, though the actual score movements spread differently across the core (82.4→87.4, +5.0) and plugin (80.0→87.6, +7.6) boundaries.

**Why C4 moved (4→5):** The per-option interest-connection requirement revealed a proactive framing opportunity the S06 session had not taken. The D-B04 session involved parties using "phased trial" language — a framing that implies one parent is evaluating whether the other can meet standards. The S07 response named this framing problem explicitly before presenting options ("this framing can imply that one parent is testing whether the other parent can meet certain standards"), reframed as mutual learning, and checked in with both parties. This is a C4-scoring distinction: reactive facilitation vs. proactive framing management. The Step 5 rules heightened the model's attention to what each option's language implied about party relationship, which surfaced the "phased trial" reframe as necessary before option presentation could proceed correctly.

**Why P2 moved (4→5):** P2 measures whether the information pattern was accurately understood and demonstrated. The per-option interest-connection requirement forced demonstration: the T7 message explicitly named what each party had said and mapped each option to those statements. The S06 session correctly identified the information pattern but the response did not make the mapping explicit. The GROUNDING RULE (every named interest must trace to a party statement) amplified this: the model had to verify its interest inventory before naming interests in the response.

**Why P4 moved (4→5):** P4 measures option packaging quality. The per-option interest-connection requirement directly improves P4 scoring: an option pool that is technically strong but presented without explicit interest linkage scores 4; the same pool presented with named connections per option scores 5. The structural change is the same as for C6 — the options existed in S06; what changed is how they were introduced.

---

## Integration Near-Ceiling on D-B04 (+18.0)

The integration score movement on D-B04 (80.0→98.0, +18.0) is the largest single-session integration gain in the diagnostic corpus. The four integration families that moved:

| Family | S06 | S07 | Change | Weight |
|---|---|---|---|---|
| I2 | 4 | 5 | +1 | 20 |
| I3 | 4 | 5 | +1 | 22 |
| I4 | 4 | 5 | +1 | 16 |
| I6 | 4 | 5 | +1 | 14 |

**Root cause — single change, four effects.** All four gains trace to the same prompt change: the per-option interest-connection requirement makes the session's option reasoning visible in the response text itself, not only in the option pool artifacts.

- **I2** (state-response coherence): Interest references in the T7 response match party statements recorded in the interaction trace and option_pool.json — coherence now directly verifiable in the response text.
- **I3** (cross-artifact narrative consistency): The T7 message interest-to-option mapping is mutually reinforcing with option_pool.json feasibility rationales. Reviewer can verify the mapping at two independent points.
- **I4** (qualification-action alignment): When option_readiness=ready and qualified options exist, the Step 5 rules require the response to present qualified options with interest connections — making the qualification-to-action chain explicit and verifiable.
- **I6** (review legibility): "Case easy to review as a narrow settlement zone case. T7 message's explicit interest-to-option mapping makes the session's core logic readable in the response text alone. Reviewer does not need to cross-reference option_pool.json."

The D-B07 integration scores (94.0, unchanged) stayed at their Stage 6 levels because the D-B07 S12 session had already demonstrated strong integration coherence via its stronger baseline performance. The D-B04 session was operating at a lower integration baseline (80.0) because the S06 response was correct but did not make its reasoning visible — leaving reviewers to infer the interest-to-option mapping from artifacts.

---

## What the Constraint Gate Confirmed

17/17 cases passed. The gate addressed three concerns:

**1. Escalation path unchanged.** The Step 5 rules only fire on option-ready turns (option_readiness=ready). On non-option turns, the RESPONSE DESIGN FOR NON-OPTION TURNS rule guides the model toward concrete next steps — which is consistent with existing escalation logic. D-B08 (process breakdown + domination), D-B11 (cooperative asymmetry), D-B13/D-B14 (M4/M5 handoff) all passed unchanged.

**2. Adversarial RT cases pass.** D-B-RT01 (CATEGORY 1 false-positive — should not veto), D-B-RT02 (CATEGORY 2 veto at T9), D-B-RT03 (CATEGORY 3 veto at T9) all pass. The safety veto path is structural (via safety_monitor → party_state_signals → domain_reasoner) and does not route through Step 5. The Step 5 rules only apply when option_readiness=ready, which the safety monitor blocks on adversarial sessions.

**3. Non-option cases unchanged.** D-B03 (emotional register), D-B12 (high-stakes, M3 threshold), D-B08 (escalation to handoff) — all sessions where the primary competency is not option presentation — passed without change. The GROUNDING RULE and transition marker have no effect when options are not being presented.

---

## Residual Gaps After Option 1

### C7 at 4 in both diagnostic cases

Perception quality is correctly characterised (scaffold divergence detected, dynamic trajectories tracked, engagement quality assessed) but C7 has not moved to 5 on either diagnostic case. The C7 4→5 boundary requires perception that not only accurately characterises but actively and demonstrably informs how the mediator positions the next turn — i.e., the response text should show evidence that the perception agent's specific characterisation changed how the mediator engaged with a party.

In D-B07-S13 and D-B04-S07, the perception agent's characterisation is correct and appears in the reasoning trace, but the C6 Step 5 rules have a stronger effect on observable response quality than the perception notes. The perception notes are used but they do not visibly reshape the response in a way that reviewers identify as exceeding competent.

The path to C7 5 is likely a prompt addition in the system prompt Step 1 section (analogous to the Step 5 addition here) that requires the response to name one specific thing it is doing differently because of the perception assessment.

### C5 at 4 on D-B04

D-B04-S07 has C5=4 vs C5=5 on D-B07-S13. This is correct: D-B04 is a narrow settlement zone case where 5 structurally distinct candidates is the right pool size. The 10-candidate diversity of D-B07 is not achievable or appropriate on D-B04. C5 at 4 on D-B04 is not a gap — it reflects accurate calibration to case type.

### C2 at 4 on D-B04

Issue mapping correctly separates parenting schedule from child_stability and communication concerns, but the parenting schedule domain has more issue families than the expense coordination domain. At a narrow settlement zone case, the issue map is smaller by design — C2 at 4 is ceiling-appropriate here.

---

## Open Questions for Next Option 1 Cycle

**Q1. C7 improvement path.** The residual perception-response coupling gap (perception correctly assessed but not demonstrably reshaping response) is a candidate for a targeted Step 1 prompt addition analogous to the Step 5 addition. This would require its own diagnostic cycle (equivalent structure to this one) with D-B04 and D-B07 as primary cases and a broader set of cases with strong scaffold divergence as secondary validation.

**Q2. GROUNDING RULE enforcement depth.** The GROUNDING RULE ("every named interest must trace to something a party said") is currently a guideline in the system prompt. On both diagnostic cases, the rule was followed. However, it is not explicitly checked in the reasoning trace structure — it is verified only at evaluation time. A future revision might require the model to record which party statement each named interest traces to in the state_delta or reasoning_trace fields, making the grounding rule enforceable at artifact-validation time rather than only at human review.

**Q3. Non-option turn concrete-next-step enforcement.** The RESPONSE DESIGN FOR NON-OPTION TURNS rule ("must advance with a concrete next step") was added as a quality instruction. The constraint gate did not surface any violations. However, "concrete next step" is a qualitative criterion that human reviewers apply — it is not schema-validatable. Sessions with low I5 scores (failure attribution) might be candidates to check whether the non-option rule is producing the expected advance.

**Q4. ARCH-006 Option 2 readiness.** The diagnostic corpus now has 17 human-reviewed sessions with explicit evaluator judgments on escalation behaviour (from the constraint gate). This is approaching the threshold where constrained dataset construction for fine-tuning (ARCH-006 Option 2) becomes feasible, contingent on escalation-specific expert review of each session. The constraint gate confirms F-overlay absence and basic escalation calibration, but Option 2 requires a higher bar: expert confirmation that the escalation behaviour in each training example was correct, not just that the quality scores were good.

---

## ARCH-006 Option 1 Status: Complete

| Item | Status |
|---|---|
| Step 5 three-rule addition to system prompt | **Complete** — `runtime/engine/prompt_builder.py` line 76–84 |
| INSTRUCTION block update (domain analysis section) | **Complete** — `runtime/engine/prompt_builder.py` line 313–316 |
| `artifacts.py` `_normalize_confidence` fix | **Complete** |
| `artifacts.py` `_normalize_pool_entry` fix | **Complete** |
| D-B07-S13 diagnostic (expense coordination) | **Complete** — PASS, Core 86.4→89.6, C6 4→5 |
| D-B04-S07 diagnostic (parenting schedule) | **Complete** — PASS, Core 82.4→87.4, Plugin 80.0→87.6, Integration 80.0→98.0, C6 4→5 |
| Constraint gate D-B01–D-B14 + RT01–RT03 | **Complete** — 17/17 PASS |
| ARCH-006-OPT1-FINDINGS-044 memo | **Complete** — this document |
