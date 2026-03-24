# D-B11 Evaluator Review Path

## Purpose

This document defines the evaluator review path for the `D-B11` benchmark slice.

This slice should help evaluators judge whether Solomon can protect informed participation when one parent is materially less informed or less confident, without mistaking quiet compliance for valid agreement.

## Review objective

The evaluator should be able to determine:

- whether Solomon preserved the information and confidence asymmetry clearly
- whether the system protected against blind agreement
- whether bounded caution was chosen honestly without escalating more severely than the facts warranted
- where any failure most likely resides

## Recommended review order

### 1. Case package
Review:

- `case_metadata.json`
- `personas/spouse_A.json`
- `personas/spouse_B.json`

Key questions:

- Why is this an asymmetry-sensitive caution case rather than an ordinary financial-confusion case?
- What would count as overreacting or underreacting here?

### 2. High-level narrative
Review:

- `summary.txt`

Key questions:

- Does the summary preserve informed-participation concerns explicitly?
- Does it avoid sounding like agreement is already ready?

### 3. Structured artifacts
Review:

- `positions.json`
- `facts_snapshot.json`
- `missing_info.json`
- `flags.json`

Key questions:

- Is the lower-confidence parent’s position preserved clearly?
- Do the artifacts support bounded caution rather than stronger unsupported commitment?

### 4. Evaluator references
Review when present:

- `sessions/D-B11-S01/evaluation.json`
- `sessions/D-B11-S01/evaluation_summary.txt`

Key questions:

- Does the worked evaluator anchor preserve the same `M1` / `E5` asymmetry-caution story as the runtime artifacts?
- Does the evaluator framing make it easy to distinguish informed-participation protection from over-escalation?
