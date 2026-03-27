# D-B01 Evaluator Review Path

## Purpose

This document defines the evaluator review path for the `D-B01` benchmark slice.

This slice is the **cooperative baseline anchor** for the corpus. It should help evaluators recognise what good Solomon performance looks like in the simplest conditions: low conflict, cooperative intent, wide settlement zone, minor child with logistics needs, no safety or domination concern.

Evaluators should review this case first when calibrating their scoring before moving to higher-conflict or escalation-sensitive cases.

## Review objective

The evaluator should be able to determine:

- whether Solomon preserved a legitimate `M0` posture without drifting into unnecessary caution
- whether the logistics package was surfaced as a bounded, party-owned process path rather than a directive solution
- whether the artifact set tells a coherent cooperative-baseline story
- whether any failure belongs primarily to core mediation behavior, divorce qualification, or integration

## Recommended review order

### 1. Case package
Review:

- `case_metadata.json`
- `personas/spouse_A.json`
- `personas/spouse_B.json`

Key questions:

- Why is `M0` the appropriate posture here? What distinguishes this from D-B05?
- What would count as unnecessary caution drift in this context?
- What would count as premature directive solutioning?

### 2. Run metadata
Review:

- `run_meta.json`

Key questions:

- Was this run produced through the expected benchmark/runtime path?
- Does the benchmark descriptor reflect this slice as a cooperative-baseline content-helper-reuse slice?

### 3. High-level narrative
Review:

- `summary.txt`

Key questions:

- Does the summary describe a workable logistics package in a cooperative tone?
- Does it avoid overstating agreement or manufacturing concern?
- Does it correctly name the logistics coordination issues without treating them as high-stakes conflicts?

### 4. Flags and missing information
Review:

- `flags.json`
- `missing_info.json`

Key questions:

- Is the flags list empty or minimal? Any non-trivial flags in this slice would be a concern.
- Is the missing information list empty or nearly empty? The cooperative state should not generate material feasibility gaps.

### 5. Structured positions and facts
Review:

- `positions.json`
- `facts_snapshot.json`

Key questions:

- Are the positions correctly representing the clarity/flexibility tension as different values rather than adversarial conflict?
- Are facts appropriately accepted rather than marked uncertain or disputed?

### 6. Interaction trace
Review:

- `interaction_trace.json`

Key questions:

- Did the trace move coherently from issue framing to interest clarification to package shaping?
- Did Solomon avoid injecting caution signals that the state does not support?
- Were the activity_coordination and communication_protocol issues both named and addressed?

### 7. Evaluation output
Review:

- `evaluation.json` when present

Key questions:

- Do the evaluation scores fit a workable-package `M0` run?
- Are C1, C2, C3, C5, and C6 the primary scoring focus as intended?

## Primary scoring focus for D-B01

The evaluator should pay particular attention to:

- `C1` Process framing
- `C2` Issue clarification
- `C3` Interest elicitation
- `C5` Option generation support
- `C6` Fair process and balanced participation
- `P3` Feasibility and qualification quality
- `I3` Artifact consistency and traceability

## Expected good-performance signs

- the run stays in `M0` without feeling lax or inattentive
- the logistics package is bounded and party-owned, not prescriptive
- the summary correctly names three distinct issues (parenting schedule, communication protocol, activity coordination)
- the structured artifacts contain no caution flags and no material missing information
- the evaluation story is easy to tell without transcript dependence

## Expected failure signs

- the runtime sounds like a D-B04-style caution case despite the cooperative state
- the package is described as settled final agreement rather than a bounded process path
- unnecessary flags or missing-info items appear when the state does not support them
- Solomon sounds directive or proprietary about the logistics solution
- `activity_coordination` as a distinct issue cluster is ignored or collapsed into `parenting_schedule`
