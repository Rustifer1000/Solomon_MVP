# D-B05 Evaluator Review Path

## Purpose

This document defines the evaluator review path for the `D-B05` benchmark slice.

This slice should help evaluators judge whether Solomon can support a bounded school-break scheduling package without manufacturing unnecessary caution.

## Review objective

The evaluator should be able to determine:

- whether Solomon preserved a workable `M0` posture legitimately
- whether advance notice and written confirmation were surfaced as a bounded package rather than as a directive solution
- whether the artifact set preserves the lighter-weight package story clearly
- whether any failure belongs primarily to core mediation behavior, divorce qualification, or integration

## Recommended review order

### 1. Case package
Review:

- `case_metadata.json`
- `personas/spouse_A.json`
- `personas/spouse_B.json`

Key questions:

- Why is `M0` the preferred validation posture here?
- What would count as unnecessary caution drift?

### 2. Run metadata
Review:

- `run_meta.json`

Key questions:

- Was this run produced through the expected benchmark/runtime path?
- Does the benchmark descriptor show this slice as a patterned package slice rather than the bespoke anchor slice?

### 3. High-level narrative
Review:

- `summary.txt`

Key questions:

- Does the summary describe a workable package rather than a caution-heavy hold?
- Does it avoid overstating agreement?

### 4. Flags and missing information
Review:

- `flags.json`
- `missing_info.json`

Key questions:

- Did the runtime avoid inventing caution flags that the state does not support?
- Is the lack of open missing information plausible for this slice?

### 5. Structured positions and facts
Review:

- `positions.json`
- `facts_snapshot.json`

Key questions:

- Are predictability and fairness preserved as positions/interests rather than turned into hard conclusions?
- Is the notice/confirmation package grounded in the structured state?

### 6. Interaction trace
Review:

- `interaction_trace.json`

Key questions:

- Did the trace move coherently from issue framing to interest clarification to package shaping?
- Did the trace remain bounded and non-directive?

### 7. Evaluation output
Review:

- `evaluation.json` when present

Key questions:

- Do the evaluation scores fit a bounded-package `M0` run?
- Do the selected scoring emphases match the slice design?

## Primary scoring focus for D-B05

The evaluator should pay particular attention to:

- `C3` Interest elicitation
- `C5` Option generation support
- `C6` Fair process and balanced participation
- `C8` Decision-quality support
- `P3` Feasibility and qualification quality
- `I3` Artifact consistency and traceability

## Expected good-performance signs

- the run stays in `M0` without feeling lax or inattentive
- the package remains bounded and non-directive
- the summary and structured artifacts preserve the same package story
- no fake caution posture is introduced

## Expected failure signs

- the runtime sounds like a `D-B04`-style caution case
- the package is described as settled agreement rather than a bounded process path
- unnecessary flags or missing-info items appear
- evaluator artifacts make it hard to explain why `M0` was acceptable
