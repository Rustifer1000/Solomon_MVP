# Next-Phase Execution Tasklist 028

## Purpose

This tasklist sequences a narrow prototype path for reviewer-facing transcript rendering after:

- [MEMO-011-reviewer-transcript-rendering-architecture.md](./MEMO-011-reviewer-transcript-rendering-architecture.md)

The goal is to improve reviewer usability without moving judgment into the rendering layer.

## Guiding constraint

The rendering prototype must not change:

- escalation logic
- evaluator logic
- expert review logic
- canonical structured runtime artifacts

The prototype is presentation-layer only.

## Ranked worklist

### 1. Define the rendering contract for a reviewer-facing transcript prototype

Create a small contract note that specifies:

- allowed inputs
- required invariants
- prohibited behavior
- required output labeling

The contract should make clear that the rendered transcript is derived from `interaction_trace.json` and is not a verbatim or canonical record.

Status:

- complete via [CONTRACT-010-reviewer-transcript-rendering-v0.md](./CONTRACT-010-reviewer-transcript-rendering-v0.md)

### 2. Define the minimal prompt and output shape for a constrained renderer

Draft the first constrained rendering prompt for:

- `review_transcript.txt`

The prompt should require:

- no new facts
- no changed order
- no changed speaker identity
- no changed escalation meaning
- improved naturalness and legibility for human reviewers

Status:

- complete via [CONTRACT-011-reviewer-transcript-rendering-prompt-v0.md](./CONTRACT-011-reviewer-transcript-rendering-prompt-v0.md)

### 3. Add a prototype rendering path that is optional and isolated

Add a rendering path that can be turned on explicitly and that writes:

- rendered reviewer transcript output

This should remain isolated from the deterministic transcript path so both can be compared side by side.

### 4. Trial the renderer on a narrow contrast set

Use:

- `D-B08`
- `D-B12`
- `D-B13`

These slices should be enough to test:

- fairness/process breakdown
- emotional flooding
- constrained voluntariness / hard-trigger handoff

### 5. Compare deterministic vs rendered reviewer transcripts

For each of the three slices, judge:

- realism
- readability
- speaker distinctiveness
- preservation of escalation evidence
- reviewer usefulness

### 6. Write a short findings memo

Record:

- whether the hybrid transcript materially improves practical review
- whether any drift or over-smoothing appears
- whether the prototype should proceed, be tightened, or be abandoned

## Recommendation

The next concrete move is item 1:

**define the rendering contract for a reviewer-facing transcript prototype**

That is the cleanest way to keep the transcript prototype helpful without letting it quietly become a second judgment system.
