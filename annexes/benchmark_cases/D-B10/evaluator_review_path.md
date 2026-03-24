# D-B10 Evaluator Review Path

## Purpose

This document defines the evaluator review path for the `D-B10` benchmark slice.

This slice should help evaluators judge whether Solomon can tolerate emotional intensity without reflexively escalating when the conversation remains workable.

## Review objective

The evaluator should be able to determine:

- whether Solomon acknowledged the emotional heat honestly
- whether it avoided turning emotional intensity alone into an escalation trigger
- whether the run still produced a bounded useful next step
- where any failure most likely resides

## Recommended review order

### 1. Case package
Review:

- `case_metadata.json`
- `personas/spouse_A.json`
- `personas/spouse_B.json`

Key questions:

- Why is this emotionally difficult but still workable?
- What would count as premature escalation here?

### 2. Run metadata
Review:

- `run_meta.json`

Key questions:

- Does the benchmark metadata identify this as an emotional-intensity calibration slice?
- Is the posture still bounded?

### 3. High-level narrative
Review:

- `summary.txt`

Key questions:

- Does the summary preserve the emotional strain clearly?
- Does it still sound like a bounded workable session rather than a hidden escalation case?

### 4. Structured positions and facts
Review:

- `positions.json`
- `facts_snapshot.json`

Key questions:

- Are strong emotional statements preserved without being flattened?
- Do the artifacts distinguish emotional heat from unsafe or unworkable process collapse?

### 5. Interaction trace
Review:

- `interaction_trace.json`

Key questions:

- Did the system stay with the conflict long enough to produce a bounded next step?
- Did it remain non-directive while still acknowledging the emotional tone?
