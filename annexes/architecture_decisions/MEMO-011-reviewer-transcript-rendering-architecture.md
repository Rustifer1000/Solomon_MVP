# Reviewer Transcript Rendering Architecture

## Purpose

This memo defines the recommended architecture for improving reviewer-facing transcript realism without weakening the core evaluation scaffold.

The target use case is:

- practical dry-run review
- mediation-aware human reviewers
- technically light reviewers such as students

The key question is:

How should the system produce more natural and evaluator-useful transcripts without moving core judgment into an LLM?

## Decision

The recommended path is:

**deterministic structured core + optional LLM-assisted reviewer transcript rendering**

This means:

1. the runtime and evaluation layers remain deterministic and structured
2. `interaction_trace.json` remains the canonical session record
3. a separate rendering layer may use an LLM to produce a more natural reviewer-facing transcript
4. the rendered transcript is presentation-only, not source-of-truth

## What Must Remain Canonical

The following remain authoritative:

- `interaction_trace.json`
- `run_meta.json`
- `flags.json`
- `facts_snapshot.json`
- `positions.json`
- `summary.txt`
- evaluator artifacts such as `evaluation.json` and `expert_review.json`

These artifacts support:

- auditability
- validation
- rerun comparison
- evaluator consistency

The reviewer transcript must not replace them.

## Why Not Pure Templates Alone

A pure-template upgrade is still possible, but it is not the preferred next move.

Reasons:

- realistic dialogue requires large authoring effort
- speaker voice becomes labor-intensive to maintain
- interruption, repair failure, and emotional nuance are hard to keep natural through deterministic phrase assembly alone
- reviewer-facing realism is now a practical-use requirement, not just an internal polish concern

Pure templates remain useful for the canonical trace.
They are not the best sole mechanism for the reviewer-facing rendering layer.

## Why Not LLM In The Core Loop

The LLM should not:

- decide escalation
- decide posture
- introduce new facts
- reinterpret the case independently of the trace
- become the canonical record of what happened

Doing so would weaken:

- reproducibility
- validation discipline
- evaluator trust
- traceability between runtime behavior and reviewer artifacts

## Recommended Split

### Layer 1: Structured runtime and evaluator core

This layer already exists.

It should continue to produce:

- state-stable turn records
- state deltas
- risk signals
- escalation outcomes
- support artifacts
- evaluator artifacts

This layer is used for correctness, validation, and audit.

### Layer 2: Reviewer-facing rendering layer

This layer is new or expanded.

It should produce:

- `review_transcript.txt`
- possibly later `review_cover_sheet.txt` and `review_outcome_sheet.txt` refinements

This layer is used for:

- readability
- practical review
- reviewer orientation
- student-facing evaluation use

This layer may use an LLM, but only under constrained rendering rules.

## Constraints On LLM Rendering

If an LLM is used, the rendering prompt must enforce:

- no new facts
- no omitted turns that matter to posture
- no changed speaker identity
- no changed order of events
- no altered escalation outcome
- no re-judging of the case
- no smoothing away of process failure that the evaluator should still be able to see

The renderer should be instructed to:

- preserve sequence
- preserve who said what in substance
- improve naturalness of wording
- make mediation moves legible to a human reviewer
- make repair attempts and failures easier to perceive

## Recommended Minimal Data Contract For Rendering

The renderer should take as input:

- `case_metadata.json`
- selected persona fields from `personas/*.json`
- `interaction_trace.json`
- optionally `summary.txt`

The renderer should not need:

- evaluator scoring outputs
- weighted score blocks
- expert review conclusions

The transcript should arise from the interaction, not from the later evaluation layer.

## Optional Trace Enrichment

The current trace is already sufficient for a first hybrid pass.

However, the following optional fields would make rendering more reliable later:

- `interaction_move`
  - example: `interrupts`, `repair_attempt`, `withdraws`, `requests_human_help`
- `speaker_intent`
  - example: `regain_control`, `protect_airtime`, `slow_process`
- `repair_stage`
  - example: `pre_repair`, `repair_attempt`, `repair_failed`
- `tone_hint`
  - example: `defensive`, `overwhelmed`, `steady`, `directive`

These fields should remain optional and should support rendering only.

## Output Labeling

The reviewer transcript should be labeled clearly as:

**reviewer-facing rendered transcript derived from the structured interaction trace**

This matters because:

- reviewers should understand it is a presentation layer
- evaluators should know where to go for the canonical source
- the system should not imply that the rendered transcript is a verbatim record

## Recommended First Implementation

The first implementation should be deliberately narrow:

1. keep the current deterministic transcript generator in place
2. add an optional LLM rendering path for `review_transcript.txt`
3. keep the deterministic trace as fallback and source-of-truth
4. compare deterministic vs rendered transcript on a small contrast set such as:
   - `D-B08`
   - `D-B12`
   - `D-B13`

Evaluation criteria for that comparison:

- realism
- readability
- distinct speaker voice
- preservation of escalation evidence
- reviewer confidence

## Recommendation

Proceed with the hybrid architecture when reviewer-facing usability becomes the next active implementation target.

Do not move the LLM into:

- escalation logic
- evaluation logic
- expert review logic

Use it only where it adds the most value with the least architectural risk:

- reviewer-facing transcript rendering

## Bottom Line

The right architectural move is not:

- pure deterministic dialogue templating everywhere

and not:

- LLM-centered core evaluation

It is:

**structured deterministic core, with optional constrained LLM rendering at the reviewer presentation layer**

That gives the project the best balance of:

- realism
- evaluator usefulness
- auditability
- safety
- maintainability
