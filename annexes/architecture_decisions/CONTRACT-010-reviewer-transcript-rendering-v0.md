# Contract 010 — Reviewer Transcript Rendering v0

## Purpose

This note defines the minimum contract for a reviewer-facing rendered transcript prototype.

It exists to support:

- practical dry-run review
- student or technically light reviewers
- improved human readability of session interaction

It does **not** redefine the canonical runtime or evaluator record.

## Canonical-source rule

The canonical source for session interaction remains:

- `interaction_trace.json`

The rendered reviewer transcript is:

- derived
- presentation-layer only
- non-authoritative

If the rendered transcript and the structured trace appear to diverge, the structured trace wins.

## Allowed inputs

A reviewer-transcript renderer may use:

- `case_metadata.json`
- selected persona fields from `personas/*.json`
- `interaction_trace.json`
- optionally `summary.txt`

It may also use narrowly scoped rendering metadata if such fields are later added to the trace, for example:

- `interaction_move`
- `speaker_intent`
- `repair_stage`
- `tone_hint`

## Inputs the renderer must not depend on

The renderer should not depend on:

- `evaluation.json`
- `expert_review.json`
- weighted score blocks
- evaluator scoring conclusions
- post-hoc expert adjudication language

The transcript must be rendered from the interaction layer, not from the later judgment layer.

## Required invariants

Every rendered reviewer transcript must preserve:

- speaker identity
- event order
- the practical substance of each turn
- the practical reason the session changed direction when it did
- the visibility of repair attempts and repair failure when those are central to the case
- the visibility of escalation-relevant interaction cues

## Prohibited behavior

The renderer must not:

- introduce new facts
- invent new turns
- change who said what in substance
- omit turns that materially affect posture
- soften or erase important process failures
- improve the apparent quality of the session beyond what the trace supports
- re-judge the case
- reinterpret escalation independently of the structured record

## Output labeling

Every rendered reviewer transcript should identify itself clearly as:

**a reviewer-facing rendered transcript derived from the structured interaction trace**

It should not be presented as:

- verbatim
- canonical
- the source used for evaluation scoring

## Preferred output style

A good reviewer-facing transcript should:

- sound readable to a mediation-aware human reviewer
- use natural dialogue-like language
- preserve distinct speaker voice where reasonably possible
- make mediation moves legible
- make repair attempts and failures perceptible
- minimize evaluator jargon

It should help a reviewer answer:

- what happened between these people?
- what did Solomon do?
- why did the posture change?

## Anti-patterns

Avoid transcripts that:

- sound like third-person case notes
- flatten all speakers into one generic voice
- smooth over interruption, flooding, coercion, or breakdown cues
- sound more polished than the underlying interaction really was
- quietly encode evaluator conclusions that are not visible in the interaction itself

## Fallback rule

If the rendering layer cannot produce a constrained transcript confidently, the system should fall back to the deterministic transcript rendering path rather than producing a misleading one.

## Minimal prototype discipline

The first prototype should:

- remain optional
- remain isolated from the core runtime path
- be easy to compare against the deterministic transcript
- be trialed on a narrow contrast set before wider use

## Bottom line

The reviewer transcript renderer exists to improve readability, not to create a second judgment system.

Its job is:

- better presentation
- not new adjudication
