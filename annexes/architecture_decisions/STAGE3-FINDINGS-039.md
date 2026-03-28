# Stage 3 Findings: Domain Reasoner Implementation

**Date:** 2026-03-28
**Status:** Stage 3 complete — diagnostic confirmed
**Covers:** D-B07-S03 through D-B07-S10; D-B11-S06

---

## Summary

Stage 3 introduced a dedicated domain reasoner LLM call that runs before the main five-step pass and produces a `domain_analysis` artifact (CONTRACT-016). The primary target was the P6 bottleneck: D-B07-S02 (Stage 2b) showed `premature_option_work=True` at all turns including T5, with 0 qualified options despite the main model generating 6 candidate options. Stage 3 resolves this.

**Result: P6 bottleneck resolved.** D-B07-S10 (Stage 3, all fixes in place) shows:
- T1, T3: `premature_option_work=True` (correct — too early)
- T5: `premature_option_work=False` with 4 qualified options

---

## Calibration Sequence

Eight diagnostic sessions were required across D-B07 before the domain reasoner produced correct output at T5.

| Session | Issue | Fix Applied |
|---|---|---|
| D-B07-S03 | Safety veto incorrectly applied — Party B's reactive statement ("not wanting unilateral control") was treated as compliance-only | Rewrote veto to require ALL conditions in each category, added calibration guidance: "reactive framing is normal mediation, not a veto trigger" |
| D-B07-S04 | Veto cleared; domain reasoner returned `deferred` citing need for "stakes" behind process concerns | Added explicit structural-fit vs. parameter-calibration distinction: options can be qualified at structural level even without parameter details |
| D-B07-S05 | Still `deferred`; domain reasoner wanted Party B to give constructive ("I need Y") rather than reactive ("I don't want X") interests | Added process vs. substantive option distinction + reactive interest sufficiency rule |
| D-B07-S06 | Domain reasoner returned `ready` in raw output; parse failed silently (non-greedy regex) | Fixed: domain reasoner `max_tokens` 1024→2048 to prevent truncation |
| D-B07-S07–S09 | Main model response parse also failing (same bug in lm_engine.py) | Fixed: (1) replaced non-greedy regex with `_extract_json_object()` bracket-counter in both parsers; (2) main model `max_tokens` 2048→4096 |
| D-B07-S10 | All fixes in place | PASS — domain reasoner `ready` with 4 candidates, main model confirmed and qualified 4 |

---

## Root Causes — Parse Failures

Two parse bugs masked the calibration progress for sessions S06–S09:

**Bug 1: Non-greedy regex on nested JSON.**
Both `domain_reasoner.py` and `lm_engine.py` used `r"```(?:json)?\s*(\{.*?\})\s*```"` to extract code-fenced JSON. The `.*?` non-greedy match stops at the first `}` rather than the outermost closing `}` of the JSON object. For a deeply nested structure (the domain analysis has nested arrays of objects; the main model's reasoning trace has 5 top-level sections each containing nested objects), this produces an incomplete JSON fragment that fails to parse.

**Fix:** Replaced with `_extract_json_object(text)` — a bracket-counting function that correctly handles arbitrary nesting by tracking `in_string` state and counting `{`/`}` depth.

**Bug 2: max_tokens too small.**
Domain reasoner: 1024 tokens is insufficient for a complete JSON response with 3-4 qualified candidates (each with 4-5 fields), blocking constraints, material gaps, and domain notes. Truncation at a mid-string position causes the bracket counter to never find the closing `}`.
Main model: 2048 tokens is insufficient for the full five-step reasoning trace at T5, which includes perception for both parties, domain analysis, option scan with 5+ candidates, safety check, and response synthesis.

**Fix:** Domain reasoner `max_tokens` → 2048. Main model `max_tokens` → 4096.

---

## Domain Reasoner Calibration — Final State

The domain reasoner system prompt in its final state:

**Safety veto rule:** Requires ALL conditions in each category (not any single indicator). Three categories: compliance-only interests, unacknowledged information asymmetry used as leverage, active safety signals. Calibration guidance: "false veto costs are real — reserve for clear patterns."

**Process vs. substantive distinction:** Process options (notice windows, documentation standards, approval thresholds, coordination protocols) can be qualified based on surface process concern alone. Substantive options (property division, custody percentages) require deep interest understanding. This distinction is what unlocked T5 qualification for D-B07.

**Reactive interest sufficiency:** A party saying "I don't want one parent to have total control" is sufficient to qualify process options. The domain reasoner must NOT require constructive ("I need Y because Z") framing before qualifying — reactive statements identify the issue structure. Constructive parameter-setting happens when parties engage with the options.

**Scope restriction:** The domain reasoner is explicitly told that managing party engagement with options is the mediator's responsibility, not a pre-option gate. "You are not responsible for preventing premature convergence on tactical choices. Those are mediator concerns."

---

## Safety Veto Calibration — D-B11-S06

D-B11-S06 was run as a regression check to confirm the safety veto correctly distinguishes passive information asymmetry (D-B11: Party B acknowledges the imbalance) from active information leverage (to be tested in D-B-RT02).

**Result:** PASS. At T5, domain reasoner evaluated Category 2 (information asymmetry as leverage) and correctly concluded it does NOT apply: "Party B acknowledged the asymmetry and accepted validity of Party A's concern — active deflection, delay, or refusal of disclosure is absent." Option work blocked on domain grounds (Party B has had only one speaking turn at T4), not on safety grounds.

This validates that the Category 2 veto requires active resistance to disclosure, not mere acknowledgment of imbalance. D-B-RT02 must be authored with explicit deflection/delay tactics to test the firing threshold.

---

## Behavioral Evidence — D-B07-S10 T5

**Domain reasoner output:**
```
option_readiness: ready
domain_notes: "Party B's statement is a substantive counterconcern, not compliance-only
(it expresses an independent value — avoiding unilateral control). No information asymmetry
leveraging evident. All four qualified options are standard bounded options in this domain
with well-understood implementation patterns."
```

**Main model confirmation:**
```
"I confirm the domain reasoner's assessment that option readiness is 'ready'. The material
gaps identified would refine option parameters but do not block presenting structural
frameworks. The complementary nature of their concerns (predictability vs. flexibility)
makes this well-suited for integrative option development."
```

**T5 message text (excerpt):**
> "Parent A, you're describing a need for predictability — knowing what's coming, when it's
> coming, and having documentation to support requests. Parent B, you're describing a need for
> workability — ensuring the system doesn't become a barrier to legitimate expenses and that
> neither parent holds unilateral control. These aren't opposing needs — they're both
> describing what a functional system looks like from each side."

This is the Stage 3 behavioral target: moving from P6 deferral to integrative framing that prepares parties for option engagement.

---

## Score Comparison: Stage 2b vs Stage 3

| Dimension | D-B07-S02 (Stage 2b) | D-B07-S10 (Stage 3) |
|---|---|---|
| P6 option qualification discipline | 3 | 4 |
| `premature_option_work` at T5 | True | False |
| Qualified options at T5 | 0 | 4 |
| Composite score | 82.4 | 82.7 |
| `[OPTION_SCAN:QUALIFIED]` tag | Absent | Present at T5 |

Composite delta is modest (+0.3) because P6 is one of 15 scored dimensions. The behavioral change is targeted and significant.

---

## What's Next

**Immediate:**
- D-B04-S04: Stage 3 regression check on simpler baseline case
- Adversarial red-team cases: D-B-RT01 (AF-3), D-B-RT02 (AF-2), D-B-RT03 (AF-1)
- Update ROADMAP-037 status tracking table

**Stage 4 (not yet designed):**
- Stage 3's domain reasoner produces correct option_readiness and candidates
- Stage 4 question: how does the main model use the qualified candidates in its response?
- Current behavior: model incorporates candidates into response synthesis (T5 message quality is high)
- Stage 4 will introduce more explicit option presentation structure, likely through the template engine (ARCH-005)

**Open calibration question:**
The domain reasoner's T3 behavior (blocking when only one party has been heard) is correct for a 6-turn session but may be over-conservative for longer sessions. In a 10-turn session, qualifying process options after 3 turns might be appropriate. ARCH-005's session-phase-aware qualification logic should address this.
