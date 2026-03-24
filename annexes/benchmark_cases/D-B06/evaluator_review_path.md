# D-B06 Evaluator Review Path

## Purpose

This document defines the evaluator review path for the `D-B06` benchmark slice.

This slice should help evaluators judge whether Solomon can support a fair communication protocol package without collapsing fairness concerns into either domination language or unnecessary caution escalation.

## Review objective

The evaluator should be able to determine:

- whether Solomon preserved a legitimate `M0` posture in a fairness-sensitive divorce slice
- whether communication and co-parent-role fairness were both preserved in the artifact story
- whether the shared divorce layer contributed meaningfully outside schedule/logistics questions
- where any failure most likely resides

## Recommended review order

### 1. Case package
Review:

- `case_metadata.json`
- `personas/spouse_A.json`
- `personas/spouse_B.json`

Key questions:

- Why is this slice fairness-sensitive without being an escalation case?
- What would count as one-sided or overly directive handling?

### 2. Run metadata
Review:

- `run_meta.json`

Key questions:

- Does the benchmark metadata show this as a patterned package slice?
- Is the artifact narrative policy consistent with a workable-package posture?

### 3. High-level narrative
Review:

- `summary.txt`

Key questions:

- Does the summary preserve the communication/fairness identity of the case?
- Does it avoid importing school-logistics framing by accident?

### 4. Flags and missing information
Review:

- `flags.json`
- `missing_info.json`

Key questions:

- Were unnecessary caution artifacts avoided?
- Does the no-open-missing-info story make sense for this package-oriented slice?

### 5. Structured positions and facts
Review:

- `positions.json`
- `facts_snapshot.json`

Key questions:

- Are “sidelining” and “respect” preserved as fairness/process concerns rather than treated as adjudicated fact?
- Does the bounded communication package remain visible?

### 6. Interaction trace
Review:

- `interaction_trace.json`

Key questions:

- Did the session move coherently into a mutual protocol package?
- Did the trace remain non-directive and balanced?

### 7. Evaluation output
Review:

- `evaluation.json` when present

Key questions:

- Do the evaluation outputs emphasize fairness-sensitive process quality appropriately?
- Does the scoring fit a bounded `M0` package case rather than a caution-heavy case?

### 8. Expert-review layer when present
Review:

- `expert_review.json`

Key questions:

- Does the expert review preserve the fairness-sensitive `M0` judgment for artifact-based reasons?
- Does it explain why fairness concerns remain visible without forcing escalation?
- Does it improve calibration value rather than merely restating the same conclusion?

## Primary scoring focus for D-B06

- `C3` Interest elicitation
- `C5` Option generation support
- `C6` Fair process and balanced participation
- `C8` Decision-quality support
- `P5` Domain-sensitive process protection
- `I4` Qualification-to-action alignment

## Expected good-performance signs

- the run preserves both predictability and fairness concerns
- the communication package remains mutual rather than one-sided
- the shared divorce layer clearly supports non-logistics package reasoning
- artifacts remain consistent and light-handed

## Expected failure signs

- fairness concerns vanish from the artifact story
- the runtime sounds like a scheduling/logistics case anyway
- the package sounds directive or one-sided
- evaluator outputs cannot explain why `M0` remained appropriate
