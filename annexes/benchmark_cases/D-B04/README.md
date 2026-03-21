# D-B04 Reference Slice Package

## Purpose

This folder is the current reference package for the first end-to-end benchmark slice used to validate Solomon's offline evaluation-phase architecture.

`D-B04` is the anchor case for:

- parenting-schedule conflict
- narrow settlement zone handling
- missing-information tracking
- plugin qualification
- caution-capable continuation

## Included artifacts

- `case_metadata.json`
  - benchmark record and architecture-facing expectations
- `personas/spouse_A.json`
  - Parent A synthetic role profile
- `personas/spouse_B.json`
  - Parent B synthetic role profile
- `runtime_flow.md`
  - expected first-pass runtime sequence for the slice
- `evaluator_review_path.md`
  - fixed evaluator review path for the slice
- `sessions/D-B04-S01/`
  - first worked reference session artifact set aligned to the current contracts

## Intended use

Use this package when:

- validating the minimum runtime architecture
- testing whether the core/plugin split is coherent
- testing whether `M1` caution handling is placed correctly
- checking whether evaluators can score one run end-to-end without guessing

## Current reference posture

- preferred initial posture: `M1`
- acceptable observed mode range: `M0` or `M1`
- immediate comparator benchmark: `D-B05`

## Current reference-run status

- `D-B04-S01` is now the first worked reference-run artifact set for this slice.
- It should be treated as a reference package aligned to the current spec and contracts.
- It is suitable for evaluator walkthroughs, schema/example checks, and architecture translation.

## What is still out of scope here

This folder does not yet contain multiple reruns, calibration disagreement examples, or a runtime-emitted continuity packet for an escalated variant of `D-B04`.
