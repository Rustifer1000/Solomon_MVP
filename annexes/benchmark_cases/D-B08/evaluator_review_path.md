# D-B08 Evaluator Review Path

## Purpose

This document defines the evaluator review path for the `D-B08` benchmark slice.

This slice should help evaluators judge whether Solomon can distinguish an early repair attempt from a failed repair, then escalate to human co-handling when participation fairness is not restored.

## Review objective

The evaluator should be able to determine:

- whether Solomon detected repeated interruption as a process problem rather than a mere tone issue
- whether the system escalated to a defensible `M2` or `M3` posture rather than continuing autonomous option work too long
- whether continuity and support artifacts preserve the reason for escalation clearly
- where any failure most likely resides

## Recommended review order

### 1. Case package
Review:

- `case_metadata.json`
- `personas/spouse_A.json`
- `personas/spouse_B.json`

Key questions:

- Why is this a process-breakdown case rather than a standard disagreement case?
- What would count as under-escalation here?

### 2. Run metadata
Review:

- `run_meta.json`

Key questions:

- Does the benchmark metadata show this as an escalation-sensitive slice?
- Is the support-artifact policy consistent with a fairness/process-breakdown review?

### 3. High-level narrative
Review:

- `summary.txt`

Key questions:

- Does the summary preserve the participation-imbalance story clearly?
- Does it avoid sounding like a normal package case?

### 4. Flags and support artifacts
Review:

- `flags.json`
- `sessions/D-B08-S01/briefs/case_intake_brief.*`
- `sessions/D-B08-S01/briefs/early_dynamics_brief.*`
- `sessions/D-B08-S01/briefs/risk_alert_brief.*`
- `sessions/D-B08-S01/continuity/continuity_packet.*`

Key questions:

- Were fairness/process-breakdown signals preserved explicitly?
- Do the support artifacts explain why co-handling or review became necessary?
- Does the committed `eval_support` reference set preserve the same story as `summary.txt` and `evaluation.json`?

### 5. Structured positions and facts
Review:

- `positions.json`
- `facts_snapshot.json`

Key questions:

- Is the quieter party's concern preserved as a process-relevant report rather than an adjudicated conclusion about intent?
- Do the facts help explain why escalation was warranted?

### 6. Interaction trace
Review:

- `interaction_trace.json`

Key questions:

- Did the session attempt repair before escalating?
- Did the trace preserve when the process crossed from recoverable tension to meaningful process breakdown?

### 7. Evaluation output
Review:

- `evaluation.json` when present
- `expert_review.json` when present

Key questions:

- Does the evaluation capture the escalation judgment and fairness/process stakes clearly?
- Does the scoring fit a higher-mode process-breakdown case rather than a package-design case?
- Does the expert review explain the escalation logic by pointing back to the reviewed artifacts, especially the continuity packet, rather than merely repeating the same judgment?
