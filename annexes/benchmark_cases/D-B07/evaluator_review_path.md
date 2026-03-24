# D-B07 Evaluator Review Path

## Purpose

This document defines the evaluator review path for the `D-B07` benchmark slice.

This slice should help evaluators judge whether Solomon can support a bounded reimbursement-process package without drifting into directive judgments about who is right on the expense dispute.

## Review objective

The evaluator should be able to determine:

- whether Solomon preserved a legitimate `M0` posture in an expense-coordination slice
- whether notice, documentation, and reimbursement timing remain explicit in the artifact story
- whether the shared divorce layer handles expense-package meaning clearly
- where any failure most likely belongs

## Recommended review order

### 1. Case package
Review:

- `case_metadata.json`
- `personas/spouse_A.json`
- `personas/spouse_B.json`

Key questions:

- Why is this an expense-coordination process case rather than a caution case?
- What would count as false authority or hidden judgment here?

### 2. Run metadata
Review:

- `run_meta.json`

Key questions:

- Does the benchmark descriptor show the patterned package structure clearly?
- Does the runtime metadata preserve the slice’s own narrative descriptor?

### 3. High-level narrative
Review:

- `summary.txt`

Key questions:

- Does the summary preserve receipts, notice, and response timing as the leading package details?
- Does it avoid turning process structure into a judgment about who is correct?

### 4. Flags and missing information
Review:

- `flags.json`
- `missing_info.json`

Key questions:

- Were caution flags avoided appropriately?
- Does the artifact set support a bounded `M0` close without hiding unresolved blame narratives?

### 5. Structured positions and facts
Review:

- `positions.json`
- `facts_snapshot.json`

Key questions:

- Are reimbursement frustrations preserved as positions/process concerns rather than adjudicated wrongdoing?
- Is the reimbursement package visible in structured state, not just summary prose?

### 6. Interaction trace
Review:

- `interaction_trace.json`

Key questions:

- Did the runtime move coherently from expense frustration into a documented coordination package?
- Did the trace stay non-directive and process-owned?

### 7. Evaluation output
Review:

- `evaluation.json` when present

Key questions:

- Do the evaluator outputs reflect the slice’s expense-coordination emphasis?
- Is scoring grounded in artifact evidence rather than transcript feel?

## Primary scoring focus for D-B07

- `C3` Interest elicitation
- `C5` Option generation support
- `C6` Fair process and balanced participation
- `C8` Decision-quality support
- `P3` Feasibility and qualification quality
- `P5` Domain-sensitive process protection
- `I3` Artifact consistency and traceability

## Expected good-performance signs

- the summary preserves reimbursement-package detail clearly
- the package stays bounded and documented
- the runtime avoids directive blame language
- evaluator artifacts make the `M0` posture easy to justify

## Expected failure signs

- expense-package detail disappears from the artifacts
- the runtime drifts into deciding who is right
- the slice inherits caution-heavy language from other cases
- evaluator outputs are too vague to compare against future reruns
