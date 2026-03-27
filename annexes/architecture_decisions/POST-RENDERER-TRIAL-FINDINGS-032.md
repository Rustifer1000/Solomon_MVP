# Post-Renderer Trial Findings 032

## Purpose

This memo closes [NEXT-PHASE-EXECUTION-TASKLIST-028](./NEXT-PHASE-EXECUTION-TASKLIST-028.md) by recording the findings of the reviewer transcript renderer trial and rendering a verdict on the current prototype.

It also formally records the decision on whether to invest further in the renderer before pivoting to the next architectural priority.

---

## What was trialed

The current prototype is `prototype_local_v0`: a deterministic, rule-based renderer that rewrites structured trace entries into more natural-reading reviewer-facing text without using an LLM.

Two of the three cases specified in TASKLIST-028 were trialed:

- `D-B08`: repeated interruption, procedural domination, co-handling escalation (E2 / M3)
- `D-B12`: severe emotional flooding with failed repair, co-handling after stabilization failure (E2 / M3)

`D-B13` (coercive control and compromised voluntariness, M4/M5 protected handoff) was **not trialed**.

---

## Per-case findings

### D-B08 — useful improvement

The deterministic renderer produced a materially better reviewer experience for D-B08 compared to the unrendered transcript.

What worked:
- The interruption and airtime pattern became more perceptible in the rendered version
- Solomon's repair attempts read as deliberate mediation moves rather than generic system turns
- The shift from repair attempt to escalation decision was legible as a narrative progression
- Evaluators could track the process-breakdown story through the rendered text

Assessment: **the renderer is useful for this challenge type.** Process-breakdown cases with visible turn-by-turn dynamics translate reasonably well through rule-based rewriting because the key signal (who controls pace, when repair is attempted, when it fails) is already present at the turn level.

---

### D-B12 — insufficiently strong

The deterministic renderer failed to make the D-B12 challenge type reliably legible.

What went wrong:
- Emotional flooding is a **cumulative arc**, not a turn-level signal. Each individual turn can be rewritten to read more naturally, but the arc — flooding builds, repair is attempted, repair fails, flooding resumes — requires a reader to perceive how the session evolved across turns, not just what happened within each one
- The rendered transcript improved individual turn naturalness but did not help reviewers perceive the repair-failure pattern
- The result still read too much like a case note about what happened rather than interaction evidence that lets the reviewer feel what happened
- The critical evaluator challenge for D-B12 — distinguishing this flooding-with-failed-repair from ordinary emotional heat — was not served by the rendering

The limitation here is **structural**, not a matter of tuning. Rule-based rewriting operates on individual turns. Conveying arc and nuance requires a renderer that can read context across turns and modulate language accordingly. That is the LLM rendering path described in [MEMO-011](./MEMO-011-reviewer-transcript-rendering-architecture.md) and specified in [CONTRACT-011](./CONTRACT-011-reviewer-transcript-rendering-prompt-v0.md).

---

## D-B13 assessment (untrialed)

`D-B13` was not trialed during this pass. Its challenge type makes the assessment straightforward enough to record without a trial run:

D-B13 tests whether a reviewer can perceive subtle coercive control dynamics — not acute threat, but the kind of constrained participation where one party does not feel free to disagree openly. The evaluator must distinguish this from ordinary asymmetry or ordinary assertiveness.

That distinction requires the reviewer to **feel the coercive pressure through the transcript** — to notice that one party's engagement is constrained rather than cooperative, and to perceive that the other party is exploiting that constraint without necessarily naming it.

A deterministic renderer cannot do this. The signals are cumulative, subtle, and require modulated language to convey. Beyond weakness, this is the case where renderer failure would be most consequential: if the rendered transcript smooths over the coercive dynamics or reads as ordinary power asymmetry, the reviewer loses the evidence they most need to call this case correctly.

Verdict without trial: **D-B13 would perform worse than D-B12, and failure there is higher-stakes.**

---

## Structural diagnosis

The trial confirms a capability boundary for the deterministic prototype:

**The renderer works where the challenge is visible at the turn level.**

Process-breakdown cases (D-B08) fit this profile: domination and repair attempts are discrete turn-level events that rule-based rewriting can make more legible.

**The renderer fails where the challenge is a cross-turn arc.**

Emotional flooding (D-B12), repair failure as a pattern, and coercive constraint (D-B13) all require the reviewer to perceive something that builds and unfolds across turns. Deterministic rendering cannot convey this because it operates per-turn without arc awareness.

This is not a bug to fix in `prototype_local_v0`. It is the inherent limit of rule-based, per-turn text rewriting.

---

## Verdict on the current prototype

**Park at current capability level.**

The current renderer is:

- **useful** for process-breakdown cases where turn-level signals are the primary reviewer challenge (D-B08 family)
- **not sufficient** for emotional arc cases (D-B12 family) or subtle safety cases (D-B13 family)
- **not ready** for generalization across the benchmark corpus

The correct next investment if reviewer-transcript generalization becomes a priority is the LLM-assisted constrained rendering path described in MEMO-011 and CONTRACT-011. That path was always the recommended architecture — the current prototype was a deliberately narrow test of whether rule-based rewriting could reach useful quality before committing to LLM rendering. The answer for the harder challenge types is no.

The current prototype remains available via `--review-transcript-renderer prototype_local_v0` and is appropriate for D-B08-family runs. It should not be extended further at this stage.

---

## Decision

Do not invest further in `prototype_local_v0` before Stage 0 diagnostic work is complete.

Reason: Stage 0 will produce a failure mode map that may change the prioritization of the LLM rendering investment. If Stage 0 reveals that perception quality is the primary system limitation (likely), the LLM rendering path becomes more valuable sooner. If Stage 0 reveals that the current rendering is sufficient for the evaluation patterns that actually matter, the investment may remain low priority. Either way, the Stage 0 evidence should inform the decision.

The renderer investment decision is deferred to post-Stage-0.

---

## Tasklist-028 status

| Item | Status |
|---|---|
| 1. Define rendering contract | Complete — CONTRACT-010 |
| 2. Define minimal prompt and output shape | Complete — CONTRACT-011 |
| 3. Add prototype rendering path | Complete — `runtime/reviewer_transcript_rendering.py`, `--review-transcript-renderer` flag |
| 4. Trial on narrow contrast set | Partial — D-B08 and D-B12 trialed; D-B13 not trialed |
| 5. Compare deterministic vs rendered | Complete for D-B08 and D-B12 |
| 6. Write findings memo | **This document** |

TASKLIST-028 is closed. The D-B13 gap is recorded and does not require a separate trial run given the structural assessment above.

---

## Bottom line

The renderer trial served its purpose: it established where the deterministic prototype adds value (process-breakdown cases) and confirmed the limit that MEMO-011 already anticipated (arc and nuance cases require LLM-assisted rendering). The right next move is Stage 0 diagnostic work, not further renderer investment.
