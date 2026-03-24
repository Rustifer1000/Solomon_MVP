# Runtime Remediation Tasklist

Purpose: drive the next trust-critical fixes in the MVP evaluation runtime.

Rule of execution: work from the top down unless a lower item is needed to safely complete a higher one.

Status legend:
- `[ ]` not started
- `[~]` in progress
- `[x]` completed

## Priority 1: Correctness And Authority

- [x] Fix `missing_info` lifecycle so question resolution updates authoritative `missing_info` state as well as `open_questions`.
- [x] Update plugin assessment logic to rely on the corrected `missing_info` lifecycle.
- [x] Update escalation logic to rely on the corrected `missing_info` lifecycle.
- [x] Add tests proving resolved questions no longer remain open in `missing_info`.
- [x] Add tests proving plugin/escalation outputs change appropriately after question resolution.

- [x] Remove or repair the broken fact canonicalization in [state.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/state.py).
- [x] Add tests proving inferred fact statements do not reverse the meaning of the source turn.
- [x] Add tests proving uncertain logistics facts remain uncertain rather than being promoted to sufficiency claims.

- [x] Stop injecting participant red lines, soft preferences, open-to-discussion items, and extra facts directly inside `_update_positions`.
- [x] Decide where that information should live instead:
  explicit simulator inputs, plugin-derived annotations, or not at all.
- [x] Refactor state mutation so authoritative participant state is derived only from normalized turn content plus explicit approved derivation paths.
- [x] Add tests proving participant artifacts do not contain state that was never introduced by the runtime authority chain.

## Priority 2: Trustworthy Artifacts And Metadata

- [x] Make `run_meta.json` truthful about actual source and provenance.
- [x] Replace hardcoded deterministic/model metadata with source-aware runtime metadata.
- [x] Distinguish clearly between `reference`, `mock_model`, `varied_mock_model`, and `runtime` runs.
- [x] Add tests proving `run_meta.json` changes correctly by source.

- [x] Add semantic tests for state invariants, not just artifact existence.
- [x] Add invariant tests for trace -> state consistency.
- [x] Add invariant tests for state -> artifact consistency.
- [x] Add invariant tests proving summary claims are supported by authoritative state.
- [x] Add invariant tests proving flags and escalation are supported by `missing_info`, options, and plugin assessment.

## Priority 3: Reusability And Extension

- [x] Finish de-`D-B04`-ing loaders, CLI defaults, and session references so the benchmark layer is a real extension seam.
- [x] Remove hardcoded `D-B04-S01` assumptions from loaders and CLI defaults.
- [x] Make benchmark-specific defaults live in the registered simulation layer instead of generic runtime entry points.
- [x] Add at least one test that demonstrates the runtime can load a benchmark simulation without relying on `D-B04`-named paths in generic code.

- [x] Strengthen contract validation with a few meaning-level invariants.
- [x] Validate timestamp format and basic sequencing assumptions.
- [x] Validate supported escalation category values.
- [x] Validate consistency between `risk_check.triggered`, `signals`, and severity.
- [x] Validate obviously contradictory turn payload combinations where practical.
- [x] Add tests proving invalid semantic combinations are rejected at normalization/validation time.

## Suggested Execution Order

1. Fix `missing_info` lifecycle and its downstream tests.
2. Repair fact canonicalization and add meaning-preservation tests.
3. Remove state-side participant injection and tighten authority boundaries.
4. Make `run_meta.json` truthful.
5. Expand semantic/invariant tests.
6. De-`D-B04` generic runtime surfaces.
7. Strengthen contract semantics.

## Done Criteria

- [x] A resolved question no longer appears open in authoritative state or downstream artifacts.
- [x] No fact inference can invert or overstate the meaning of a source statement.
- [x] Participant artifact content is traceable to normalized turns or explicit approved derivation.
- [x] `run_meta.json` accurately describes how the run was produced.
- [x] Tests check semantic correctness, not only file existence and string presence.
- [x] Generic runtime entry points no longer quietly depend on `D-B04`.
- [x] Invalid turn semantics are rejected before state mutation.

## Remaining Partial Items

- None in this remediation pass.
