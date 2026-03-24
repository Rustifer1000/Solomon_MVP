# Contract 005 — evaluation_summary.txt Template v0

## Purpose

This note defines the minimum content contract for a worked `evaluation_summary.txt` reference artifact.

It is intentionally light. The summary is not the authoritative scoring artifact. `evaluation.json` remains authoritative. The purpose of `evaluation_summary.txt` is to give a human reviewer a fast, compact interpretation of the scored run without replacing the structured record.

## Minimum required content

Every worked `evaluation_summary.txt` should include:

- explicit case ID
- explicit posture or mode reference such as `M0` or `M1`
- a statement that it is a reference or worked evaluator example
- a short evaluator-facing interpretation of what kind of run it is
- the main reason the posture is correct
- the main artifact pattern that supports that judgment

## Preferred content

When space permits, a worked `evaluation_summary.txt` should also include:

- the slice-distinguishing package or caution theme
- the strongest relevant scoring area
- the main calibration use of the example

## Content discipline

The summary should:

- stay evaluator-facing, not runtime-facing
- avoid re-scoring every family in prose
- avoid replacing `evaluation.json`
- avoid introducing facts not visible in the authoritative artifacts

## Good examples

Good examples sound like:

- a caution-centered `M1` reference run because unresolved logistics remain explicit across trace, flags, and missing-info artifacts
- a bounded `M0` package-design run because no threshold-relevant caution state was reached and the package remained mutual and non-directive

## Anti-patterns

Avoid summaries that:

- omit the mode
- omit the case ID
- sound like generic praise
- restate the runtime summary instead of the evaluator judgment
- imply evaluator confidence without giving the artifact basis for it

## Relationship to expert review

If an `expert_review.json` is added later for the same session, `evaluation_summary.txt` should still summarize the primary evaluation, not the expert adjudication result, unless explicitly replaced by a later reference policy.
