# Contract 007 — Reference expert_review.json Authoring Note v0

## Purpose

This note defines when and how to author a worked `expert_review.json` example.

It is for:

- calibration anchors
- adjudication examples
- fairness or safety review examples

## When a worked expert review is worth adding

Add a worked `expert_review.json` example when at least one of these is true:

- the slice is an anchor benchmark
- the evaluator judgment is likely to become a recurring calibration question
- the case shows how a primary evaluation should be confirmed or corrected
- the case demonstrates expert handling of escalation, overlay, or fairness review

Do not add expert-review examples just for coverage symmetry.

## Minimum discipline

Every worked expert review should:

- match `case_id`, `benchmark_id`, and `plugin` to the underlying session
- reference at least one worked `evaluation.json` source record
- make the review reason explicit
- make the agreement/disagreement level explicit
- explain why the expert review confirms, corrects, or escalates the case
- keep `final_review_outcome` aligned with the actual review theory

## Review-type guidance

Use:

- `calibration`
  - when the example is mainly meant to stabilize evaluator interpretation
- `adjudication`
  - when the primary evaluation is being materially corrected
- `quality_audit`, `fairness_review`, or `safety_review`
  - only when that narrower review lens is the point of the example

## Agreement rule

If `case_status = confirmed_as_scored`, the review should not claim `substantial_disagreement`.

If the review materially changes scores, overlays, or escalation posture, the final disposition should say so directly.

## Minimal authoring checklist

- confirm alignment with the primary `evaluation.json`
- confirm reviewed-artifact list includes the actual evidence used
- confirm `review_reason.trigger` matches why the expert review exists
- confirm `expert_findings` explain the key expert question, not just the final answer
- confirm `final_review_outcome` matches the actual level of agreement or correction
- run:
  - `python tools\validate_reference_evaluator_artifacts.py`

## Good authoring style

Good worked expert reviews:

- make the calibration or adjudication value obvious
- explain the decisive artifact pattern briefly
- preserve a clear difference between confirming and correcting

Weak worked expert reviews:

- merely restate the original evaluation
- add expert-review ceremony without a real review question
- imply disagreement while still marking the case as fully confirmed
