# Contract 011 — Reviewer Transcript Rendering Prompt v0

## Purpose

This note defines the first constrained prompt and output shape for a reviewer-facing transcript renderer.

It is a prototype contract only.

It exists to support:

- reviewer readability
- practical dry-run evaluation
- comparison between deterministic and rendered reviewer transcripts

It does not authorize any change to:

- canonical runtime artifacts
- escalation logic
- evaluator logic
- expert review logic

## Rendering target

The initial rendering target is:

- `review_transcript.txt`

The renderer should produce a human-readable transcript that is easier for a mediation-aware reviewer to follow than the deterministic transcript.

## Required inputs

The prototype prompt may use:

- `case_metadata.json`
- selected persona fields from `personas/*.json`
- `interaction_trace.json`
- optionally `summary.txt`

## Prohibited inputs

The prototype prompt should not use:

- `evaluation.json`
- `expert_review.json`
- weighted scores
- final evaluator judgment language

The transcript should be rendered from interaction records, not from later evaluator interpretation.

## Required prompt instructions

The prompt for the renderer should explicitly require:

1. preserve speaker identity
2. preserve turn order
3. preserve the practical substance of each turn
4. preserve repair attempts and repair failure if present
5. preserve escalation-relevant interaction cues
6. improve naturalness and readability for a human reviewer
7. avoid evaluator jargon where possible

The prompt must also explicitly prohibit:

- inventing new facts
- inventing new turns
- changing who said what in substance
- omitting materially important turns
- changing the escalation meaning
- smoothing away process breakdown or coercive cues
- turning the transcript into a summary or analysis

## Suggested prototype prompt skeleton

The following is the prototype prompt shape:

```text
You are rendering a reviewer-facing transcript from a structured mediation interaction trace.

Your job is to improve readability and human realism without changing what happened.

Rules:
- Do not add new facts.
- Do not add new turns.
- Do not change turn order.
- Do not change who said what in substance.
- Do not change the meaning of escalation or repair attempts.
- Do not smooth away interruption, flooding, domination, coercion, or breakdown cues if they are present.
- Use natural, plain language suitable for a mediation-aware human reviewer.
- Keep the transcript readable, but faithful.
- This is not a summary and not an evaluation. It is only a reviewer-facing rendering.

Output format:
- Start with a label stating that this is a reviewer-facing rendered transcript derived from the structured interaction trace.
- Then render each turn in order.
- Use speaker labels exactly as provided or as directly derivable from the trace.
- Keep each rendered turn short and readable.
```

## Output shape

The initial output should be plain text with this shape:

1. label line
2. case id line
3. session id line
4. blank line
5. rendered turns in order

### Required header lines

- `Reviewer Transcript`
- `Source Note: reviewer-facing rendered transcript derived from the structured interaction trace`
- `Case ID: ...`
- `Session ID: ...`

## Turn formatting rules

Each turn should be rendered as:

```text
Turn N [phase]
Speaker: rendered utterance
```

Allowed:

- one or two short sentences per turn
- plain mediation language
- light voice differentiation between speakers

Not allowed:

- bullet points inside turns
- evaluator commentary inside turns
- schema language
- score language
- mode/category labels inside turns unless already present in the underlying interaction

## Preferred style

Good rendered turns should:

- sound like a plausible session
- let a reviewer feel interruption, hesitation, defensiveness, or repair
- keep Solomon sounding like a mediator rather than a system note
- keep spouses sounding like different people where the trace supports that

## Anti-patterns

Avoid outputs that:

- read like narrated case notes
- restate the entire case background in every Solomon line
- flatten all spouses into the same voice
- insert evaluator-style phrases like:
  - `process breakdown`
  - `escalation posture`
  - `state reflects`
  - `interaction moved into option work`

unless those ideas are already present in plain language in the interaction itself

## Fallback behavior

If the renderer cannot produce a faithful natural-language rendering under these constraints, it should fail closed and the system should keep the deterministic transcript.

## Prototype evaluation criteria

The rendered transcript will be judged against the deterministic transcript on:

- realism
- readability
- speaker distinctiveness
- preservation of escalation evidence
- reviewer usefulness

## Bottom line

The prompt should push the renderer toward:

- more natural dialogue
- same underlying interaction

and never toward:

- new judgment
- new facts
- altered meaning
