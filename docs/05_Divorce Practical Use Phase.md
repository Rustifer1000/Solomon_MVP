# Divorce Practical Use Phase

## Purpose

This document defines the first more real-world use phase for the divorce plugin.

It is intentionally still aligned with the evaluation-phase specification:

- offline
- controlled
- evaluator-centered
- artifact-driven
- human-in-the-loop

This is **not** live end-user deployment.

## First Practical Use Mode

The first practical use mode is:

**structured dry-run usage with side-by-side human review**

This means:

- run the divorce corpus or selected divorce slices through the existing runtime/artifact pipeline
- have a human evaluator or mediation-aware reviewer walk through the emitted artifacts in sequence
- compare the system’s posture, artifacts, and escalation choices against human practical judgment

This mode is preferred over immediate live or semi-live use because it preserves:

- confidentiality discipline
- reproducibility
- evaluator calibration
- direct artifact review

## Suggested Session Format

For each dry-run session:

1. select a slice or small contrast pair
2. review the emitted artifacts in the expected order
3. record whether the run feels:
   - useful
   - cautious but acceptable
   - materially concerning
4. record whether the reviewer could explain the posture and next step from the artifacts alone

## Recommended First Use Sets

### Set A: bounded and caution contrasts

- `D-B04`
- `D-B10`
- `D-B11`

Purpose:

- confirm that caution, emotional intensity, and asymmetry remain distinguishable under practical review

### Set B: co-handling contrasts

- `D-B08`
- `D-B12`

Purpose:

- compare fairness/process breakdown against emotional flooding under side-by-side review

### Set C: hard-trigger and complexity contrasts

- `D-B09`
- `D-B13`
- `D-B14`

Purpose:

- compare complexity review, constrained-voluntariness handoff, and participation-capacity handoff

## What Counts As Useful Practical Success

A run is a useful practical success when:

- the reviewer can explain the final posture without relying heavily on the transcript
- the artifact set feels practically sufficient for judgment
- the slice remains clearly distinct from its nearest contrast slice
- the recommended next step feels procedurally legitimate

## What Counts As Caution

A run is cautionary when:

- the posture is probably correct but the rationale still feels thinner than it should
- the reviewer has to lean too heavily on one artifact rather than the artifact set as a whole
- the slice is correct but harder to distinguish from a nearby slice than expected

## What Counts As Material Concern Requiring Remediation

A run requires remediation when:

- the posture looks wrong in practical review
- the artifacts contradict each other materially
- the support-artifact layer adds confusion rather than clarity
- the reviewer cannot reliably distinguish the slice from its nearest contrast case
- the system appears to drift beyond legitimate mediation role boundaries

## Evidence Rule

Only treat a concern as architecture-significant if it is visible in repeated practical review, not just a single uncomfortable impression.

This matters especially for the second-plugin question:

- a second plugin should not be started because of speculative concern
- it should only be started if repeated practical use shows a real unresolved boundary blind spot

## Output Expectation

Every practical-use round should produce:

- a short findings memo
- any concrete remediation candidates
- a clear statement about whether second-plugin pressure actually increased

## Recommended Companion Template

Use:

- [06_Divorce Practical Review Worksheet.md](./06_Divorce%20Practical%20Review%20Worksheet.md)
- [07_Reviewer Packet Format.md](./07_Reviewer%20Packet%20Format.md)

This worksheet is the preferred way to make reviewer judgments comparable across dry-run sessions.
