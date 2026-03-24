# Practical Trial Protocol 001

## Purpose

This protocol defines the first practical trial / validation pass for the complete divorce corpus after family-completion and higher-mode anchoring.

The goal is not to add more breadth. The goal is to validate whether the existing corpus is coherent, reviewable, and calibration-usable as a developer-ready evaluation set.

## Trial Scope

Use the full divorce corpus:

- `D-B04`
- `D-B05`
- `D-B06`
- `D-B07`
- `D-B08`
- `D-B09`
- `D-B10`
- `D-B11`
- `D-B12`
- `D-B13`
- `D-B14`

## Trial Set Structure

Review the corpus in three grouped passes.

### Pass A: bounded / caution calibration

- `D-B04`
- `D-B05`
- `D-B06`
- `D-B07`
- `D-B10`
- `D-B11`

Purpose:

- confirm that workable, caution, and asymmetry-sensitive cases do not drift upward into unnecessary escalation
- confirm that package-bearing slices remain distinguishable from one another in summary and evaluator artifacts

### Pass B: higher-mode co-handling calibration

- `D-B08`
- `D-B12`

Purpose:

- confirm that `E2 / M3` higher-mode cases remain distinct by cause
- distinguish fairness/process breakdown from emotional flooding

### Pass C: hard-trigger handoff calibration

- `D-B13`
- `D-B14`
- `D-B09`

Purpose:

- confirm that `E1 / M4` handoff cases remain distinct by trigger family
- keep `D-B09` in the pass as a contrast case for domain complexity that should not be flattened into hard-trigger logic

## Required Outputs To Review

For every slice in the trial set, review:

- `summary.txt`
- `flags.json`
- `run_meta.json`
- `interaction_trace.json`

When present, also review:

- `evaluation.json`
- `evaluation_summary.txt`
- `expert_review.json`
- `briefs/case_intake_brief.json`
- `briefs/early_dynamics_brief.json`
- `briefs/risk_alert_brief.json`
- `continuity/continuity_packet.json`

## Trial Questions

For every slice, answer:

1. Is the final posture still the right one for this family?
2. Are the reason-for-posture and the family identity visible without transcript dependence?
3. Do the evaluator artifacts and support artifacts tell the same story as the trace?
4. Does this slice remain meaningfully distinct from its nearest contrast slice?

## Success / Caution / Redesign Criteria

### Success

A slice is a success when:

- its posture is still defensible
- its family identity is visible in summary, flags, and evaluator artifacts
- its nearest contrast slice remains clearly distinguishable
- support artifacts, when present, preserve the same escalation or caution story as the main artifacts

### Caution

A slice is in caution when:

- the posture is probably right but the rationale is too lossy or too transcript-dependent
- evaluator artifacts are valid but not yet sharp enough for reliable comparison
- support artifacts exist but add little practical review value

### Redesign

A slice should be redesigned when:

- its final posture looks wrong for the family
- its nearest contrast slice is no longer meaningfully distinguishable
- support artifacts or evaluator anchors materially contradict the trace or summary
- the slice depends on hidden assumptions that an external reviewer could not recover from the emitted artifacts

## Nearest Contrast Pairs

Use these pairs explicitly during the trial:

- `D-B10` vs `D-B12`
- `D-B08` vs `D-B12`
- `D-B13` vs `D-B14`
- `D-B11` vs `D-B13`
- `D-B09` vs `D-B13`

## Trial Procedure

1. Run the full automated checks:
   - `python -m unittest discover -s tests -p "test_end_to_end.py"`
   - `python tools\validate_reference_evaluator_artifacts.py`
   - `python tools\validate_persona_profiles.py`
   - `python tools\report_divorce_template_family_coverage.py`
2. Review Pass A and record any posture drift or package indistinguishability.
3. Review Pass B and record any co-handling family conflation.
4. Review Pass C and record any hard-trigger conflation or false hard-trigger behavior.
5. Summarize findings in one repo memo before changing slice content.

## Expected Outcome

If this trial passes cleanly, the divorce corpus should be treated as:

- family-complete
- evaluator-usable
- support-artifact-usable
- ready for first practical use and comparison against real validation feedback
