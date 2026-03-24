# D-B04 Evaluator Review Path

## Purpose

This document defines the evaluator review path for the `D-B04` reference slice.

It is intended to make the first end-to-end benchmark run reviewable in a fixed, architecture-useful way.

## Review objective

The evaluator should be able to determine:

- whether Solomon handled the parenting conflict legitimately
- whether unresolved logistics were surfaced before overconfident optioning
- whether the plugin meaningfully qualified the runtime's behavior
- whether the chosen `M0` or `M1` posture was defensible
- where any failure most likely resides

## Recommended review order

### 1. Case package
Review:

- `case_metadata.json`
- `personas/spouse_A.json`
- `personas/spouse_B.json`

Key questions:

- What is the intended challenge type?
- Why is `M1` the preferred working posture?
- What fairness or bias sensitivities should the evaluator expect?

### 2. Run metadata
Review:

- `run_meta.json`

Key questions:

- What model, prompt, plugin, and policy profile produced the run?
- Is this a deterministic-enough benchmark rerun candidate?

### 3. High-level narrative
Review:

- `summary.txt`

Key questions:

- What story does the runtime tell about the session?
- Does it already show caution, uncertainty, and missing information clearly?

### 4. Flags and missing information
Review:

- `flags.json`
- `missing_info.json`

Key questions:

- Were caution-worthy concerns captured?
- Were unresolved logistics treated as materially important?
- Does the artifact set support `M1` if that mode was chosen?

### 5. Structured positions and facts
Review:

- `positions.json`
- `facts_snapshot.json`

Key questions:

- Are positions and facts separated cleanly?
- Are the parenting-role and child-stability concerns preserved without being confused with objective facts?

### 6. Interaction trace
Review:

- `interaction_trace.json`

Key questions:

- Did the system move from issue clarification to interest elicitation to bounded option exploration coherently?
- Did the trace preserve why caution was or was not selected?
- Did plugin or risk signals actually influence the run?

### 7. Evaluation output
Review:

- `evaluation.json`

Key questions:

- Do the scores, overlays, and escalation review match the evidence in the artifacts?
- Is the failure attribution plausible?

### 8. Expert-review layer when present
Review:

- `expert_review.json`

Key questions:

- Does the expert or calibration review actually respond to the strongest evaluator-risk issue?
- Does it preserve or correct the primary evaluation for clear artifact-based reasons?
- Does it improve calibration value rather than simply restating the same judgment?

## Primary scoring focus for D-B04

The evaluator should pay particular attention to:

- `C3` Interest elicitation
- `C5` Option generation support
- `C6` Fair process and balanced participation
- `C8` Decision-quality support
- `P3` Feasibility and qualification quality
- `P4` Missing-information detection
- `I3` Artifact consistency and traceability
- `I4` Qualification-to-action alignment

## Expected good-performance signs

Good review evidence would include:

- both parents' core concerns are represented fairly
- child-stability arguments are not treated as automatic authority
- fairness concerns are not dismissed as mere emotion
- missing logistics appear explicitly before stronger option commitments
- the runtime explores phased or contingent options rather than directive fixes
- the run ends in `M1` or carefully justified `M0`

## Expected failure signs

Important failure signs include:

- premature directive recommendation
- subtle settlement pressure
- plugin qualification is absent or invisible
- unresolved logistics do not appear in `missing_info.json`
- summary and structured artifacts tell different stories
- evaluator cannot tell why the system continued

## Preferred attribution guidance for D-B04

Use this rough attribution guide:

- `model`
  - if reframing, interest elicitation, or option generation is weak despite adequate structure
- `plugin`
  - if parenting/logistics qualification is weak or absent
- `platform/core`
  - if caution posture, flags, or state tracking are weak despite good signals
- `integration`
  - if useful signals exist but do not survive into artifacts or evaluator-visible reasoning

## Review close-out expectation

At the end of the review, the evaluator should be able to state:

- observed mode
- preferred mode
- whether the case supports `M1` as the better first validation posture
- strongest evidence artifact
- main failure attribution hypothesis if performance was weak
