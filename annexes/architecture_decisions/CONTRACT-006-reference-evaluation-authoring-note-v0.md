# Contract 006 — Reference evaluation.json Authoring Note v0

## Purpose

This note defines how to author a worked reference `evaluation.json` example without guessing field conventions.

It is for:

- new worked evaluator anchors
- updated reference examples after rubric changes
- future slice additions once breadth resumes

## Authoring rule

A worked `evaluation.json` example should be authored from artifacts outward, not from impression inward.

Recommended evidence order:

1. `case_metadata.json`
2. `flags.json`
3. `summary.txt`
4. `interaction_trace.json`
5. any relevant briefs
6. only then the scored record

## Minimum discipline

Every worked reference evaluation should:

- match `case_id`, `benchmark_id`, and `plugin` to `case_metadata.json`
- use `policy_profile = sim_minimal` unless there is an explicit reason not to
- list the reviewed artifacts explicitly
- keep score families and weighted-score blocks aligned with the schema weights
- set escalation posture fields to the posture the worked example is meant to anchor
- keep the final rationale compact and artifact-based

## Reference posture rule

Before writing the score blocks, decide which posture family the example is meant to anchor:

- caution-centered `M1`
- bounded-package `M0`
- fairness-sensitive `M0`
- another explicitly named posture if later added

That posture should remain consistent across:

- `escalation_review`
- `final_judgment`
- `evaluation_summary.txt`

## Notes discipline

Use notes where they add calibration value, especially:

- scores of `1`, `2`, or `5`
- the key plugin-domain family for the slice
- the strongest integration family for the slice
- escalation-review fields when used

Do not turn the worked example into a transcript retelling.

## Minimal authoring checklist

- confirm metadata alignment with `case_metadata.json`
- confirm score-family keys match schema expectations
- confirm weighted family values are mathematically correct
- confirm total weighted scores are mathematically correct
- confirm `observed_mode`, `evaluator_preferred_mode`, and primary escalation category match the intended anchor posture
- confirm `artifact_links` point to the authoritative session files
- run:
  - `python tools\validate_reference_evaluator_artifacts.py`

## Good authoring style

Good worked examples:

- make the main scoring theory of the slice obvious
- use brief notes only where calibration value is high
- make it easy for a later reviewer to tell why this example exists

Weak worked examples:

- use generic praise instead of artifact-based rationale
- drift away from the schema weights
- mix a caution narrative with an `M0` posture
- describe a slice as richer or safer than the actual artifacts support
