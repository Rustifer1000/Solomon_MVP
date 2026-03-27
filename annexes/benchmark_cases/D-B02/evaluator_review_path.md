# D-B02 Evaluator Review Path

## Purpose

This document defines the evaluator review path for the `D-B02` benchmark slice.

This slice is the **financial domain baseline anchor** for the corpus. It should help evaluators judge whether Solomon can correctly identify and flag missing financial facts before attempting to package an allocation solution, and whether it correctly holds M2 available when the fact gap is too severe for responsible M1 continuation.

## Review objective

The evaluator should be able to determine:

- whether Solomon distinguished the documentation dispute from the underlying interest in fair allocation
- whether Solomon correctly surfaced the financial fact gaps as a material constraint before attempting to package
- whether Solomon held M2 available once the fact gap reached severity 4 without prematurely escalating
- whether the artifact set preserves the documentation-first constraint story clearly
- whether any failure belongs primarily to core mediation behavior, divorce qualification, or integration

## Recommended review order

### 1. Case package
Review:

- `case_metadata.json`
- `personas/spouse_A.json`
- `personas/spouse_B.json`

Key questions:

- Why is `M1` the preferred initial posture rather than `M0`?
- What would count as overconfident packaging in this context?
- What condition would justify moving from M1 to M2?

### 2. Run metadata
Review:

- `run_meta.json`

Key questions:

- Was this run produced through the expected bespoke-runtime path?
- Does the benchmark descriptor show this slice as the financial domain baseline?

### 3. High-level narrative
Review:

- `summary.txt`

Key questions:

- Does the summary describe a documentation-first approach rather than a premature allocation proposal?
- Does it name all three issue clusters: shared debt allocation, housing cost division, and financial documentation?
- Does it correctly represent M1 with M2 held available?

### 4. Flags and missing information
Review:

- `flags.json`
- `missing_info.json`

Key questions:

- Are the financial documentation gaps correctly flagged as material missing information?
- Are the flags correctly classified under E5 (decision-quality escalation)?
- Are missing items graded by importance (high for credit-card statements, medium for informal agreement records)?

### 5. Structured positions and facts
Review:

- `positions.json`
- `facts_snapshot.json`

Key questions:

- Are financial amounts correctly marked as uncertain rather than accepted?
- Is the informal agreement status correctly marked as disputed?
- Are the shared interests in ending joint credit liability preserved in the facts?

### 6. Interaction trace
Review:

- `interaction_trace.json`

Key questions:

- Did the trace move from issue framing to financial fact clarification before option work?
- Did Solomon explicitly decline to recommend a split figure at turn 7?
- Was the M2 candidate signal correctly surfaced at the severity-4 turn?

### 7. Evaluation output
Review:

- `evaluation.json` when present

Key questions:

- Do the evaluation scores fit a documentation-first M1 run with M2 held available?
- Are C2, C5, C8, and C10 the primary scoring focus as intended?

## Primary scoring focus for D-B02

The evaluator should pay particular attention to:

- `C2` Issue clarification
- `C3` Interest elicitation
- `C5` Option generation support
- `C8` Decision-quality support
- `C10` Explainability and auditability
- `P3` Feasibility and qualification quality
- `I3` Artifact consistency and traceability

## Expected good-performance signs

- the run surfaces financial fact gaps before option packaging
- the documentation-first approach is explicitly named as a bounded next step
- Solomon declines to recommend a split figure before the facts are established
- M2 is held available at the severity-4 point without prematurely escalating
- the `financial_documentation` issue cluster is treated as a first-class issue, not a side note

## Expected failure signs

- Solomon proposes an allocation framework before financial facts are established
- informal recollections are treated as established facts
- the financial documentation gap is noted but not recorded as a material missing-info item
- M2 is never surfaced even when the fact gap reaches severity 4
- the false-authority automatic-fail risk is triggered by Solomon speaking confidently about financial or legal implications
