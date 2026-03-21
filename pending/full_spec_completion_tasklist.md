# Full Specification Completion Tasklist

## Current reading of the intended workflow

Based on the normative docs and architecture-decision files, the repo's intended flow is:

1. Define the evaluation-phase foundations and operating model in `docs/`.
2. Lock the model/core/plugin/evaluator boundary and readiness criteria in `annexes/architecture_decisions/`.
3. Translate the spec into architecture inputs, runtime contracts, benchmark pressure maps, and a first end-to-end benchmark slice.
4. Complete the remaining scoring, testing, schema, and evaluator-tooling artifacts in `pending/`.
5. Use that package to draft the first concrete runtime architecture for the offline evaluation-phase implementation.

## Completed or materially drafted already

- [x] Core normative spec exists in `README.md`, `docs/01_foundations_and_architecture.md`, and `docs/02_Operations and Evaluator Workflow`.
- [x] Evaluator output schemas exist in `schema/evaluation.schema.json` and `schema/expert_review.schema.json`.
- [x] Example evaluator and expert-review records exist in `examples/`.
- [x] Core boundary and readiness documents exist:
  - `annexes/architecture_decisions/ADR-001-model-core-plugin-evaluator-boundary.md`
  - `annexes/architecture_decisions/READINESS-001-pre-architecture-checklist.md`
  - `annexes/architecture_decisions/SPEC-TO-ARCH-INPUTS.md`
  - `annexes/architecture_decisions/SLICE-001-first-end-to-end-benchmark.md`
  - `annexes/architecture_decisions/benchmark_to_capability_matrix.md`
  - `annexes/architecture_decisions/escalation_authority_matrix.md`
  - `annexes/architecture_decisions/CONTRACT-002-plugin-interface-v0.md`
  - `annexes/architecture_decisions/CONTRACT-003-flags-positions-facts-missing-summary-v0.md`
  - `annexes/architecture_decisions/CONTRACT-004-continuity-packet-v0.md`
  - `annexes/architecture_decisions/competency_to_artifact_matrix.md`
- [x] A first benchmark case package exists for `D-B04` under `annexes/benchmark_cases/D-B04/`.
- [x] Canonical benchmark and template source material exists in `annexes/`.

## Gaps that still block a "full specification"

- [x] `pending/evaluator_console_requirements.md` is drafted.
- [x] `pending/fairness_checks.md` is drafted.
- [x] `pending/flags.schema.json` is drafted.
- [x] `pending/integration_scoring.md` is drafted.
- [x] `pending/plugin_domain_scoring.md` is drafted.
- [x] `pending/regression_test_protocol.md` is drafted.
- [x] `pending/synthetic_user_role_profile_schema.md` is drafted.
- [x] `pending/trigger_class_test_table.md` is drafted.
- [x] `STATUS-001-spec-to-architecture-plan.md` has been partially reconciled with the files now present in the repo.
- [ ] Example/schema alignment and active-pack promotion still need one final consistency pass before the repo should be treated as fully locked.

## Priority tasklist

### Phase 1: Reconcile repo status and structure

- [x] Update `annexes/architecture_decisions/STATUS-001-spec-to-architecture-plan.md` so it reflects the documents that now exist.
- [x] Normalize path references where the repo currently disagrees with itself.
- [x] Rename draft architecture docs from `.coffee.md` to stable `.md` names and update references.
- [x] Move `CONTRACT-001-runtime-artifacts-v0` into the main `annexes/architecture_decisions/` folder.
- [x] Replace the placeholder content in `pending/trigger_class_test_table.md` and fix the apparent typo.
- [x] Archive the stale full-spec snapshot so it stops competing with the live spec layer.

### Phase 2: Finish the minimum missing contract pack

- [x] Complete `pending/flags.schema.json`.
  - It should align with the runtime-artifact contract and the evaluator workflow.
- [x] Complete `pending/synthetic_user_role_profile_schema.md`.
  - It should cover goals, private concerns, red lines, communication style, emotional triggers, disclosure tendencies, compromise willingness, and reactions to bias/pressure.
- [x] Review `CONTRACT-001`, `CONTRACT-002`, and `CONTRACT-003` together and normalize them into clean publishable markdown.
- [x] Review `CONTRACT-001` through `CONTRACT-004` together and resolve the main overlap before treating them as the baseline contract set.

### Phase 3: Complete the remaining evaluator and scoring specifications

- [x] Draft `pending/plugin_domain_scoring.md`.
  - This closes the missing divorce-plugin score layer called out in the operational spec.
- [x] Draft `pending/integration_scoring.md`.
  - This closes the missing core/plugin integration score layer.
- [x] Draft `pending/evaluator_console_requirements.md`.
  - This should match the score sheet, review flow, required notes, and schema outputs already defined elsewhere.

### Phase 4: Complete the testing and governance package

- [x] Draft `pending/fairness_checks.md`.
  - This should define first-pass fairness review dimensions and when expert review is required.
- [x] Draft `pending/trigger_class_test_table.md`.
  - This should map trigger classes to expected detection, thresholds, artifacts, and escalation outcomes.
- [x] Draft `pending/regression_test_protocol.md`.
  - This should define benchmark rerun cadence, comparison rules, failure triage, and how regressions are attributed.

### Phase 5: Close the loop on the first end-to-end slice

- [x] Expand the `D-B04` slice so the benchmark package is complete enough to serve as the reference run.
- [x] Ensure the slice has a clearly linked set of:
  - case metadata
  - personas
  - expected runtime artifacts
  - evaluator review order
  - expected escalation posture
  - likely failure attribution paths
- [x] Add or finalize executed example artifacts for the first end-to-end slice if they are intended to be part of the full spec package.

### Phase 6: Final consistency pass before runtime architecture work

- [ ] Cross-check that all examples conform to the current schemas.
- [ ] Cross-check that the pending docs use the same terminology for modes, categories, thresholds, artifacts, and score layers as the normative docs.
- [x] Add a short repo-level "spec completion status" summary in `README.md` or a dedicated status file so new contributors can tell what is authoritative, drafted, placeholder, or missing.
- [ ] Decide which architecture-decision documents are stable enough to treat as the active locked input pack for the next phase.
- [x] Remove generated temp artifacts and add ignore rules so future reviews stay signal-rich.

## Recommended execution order

1. Clean up repo structure and stale status tracking.
2. Complete the `D-B04` end-to-end executed reference-run package.
3. Cross-check examples against schemas.
4. Run a final consistency review across docs, schemas, examples, and architecture-decision drafts.
5. Begin runtime architecture drafting against the locked package.
6. Add rerun and comparison coverage against the reference baseline.

## Definition of done for the full specification

The repo can reasonably be treated as a full evaluation-phase specification package when:

- [x] All files in `pending/` are replaced with real content.
- [x] The contract pack for runtime artifacts, plugin interface, and escalation authority is internally consistent and reflected by one canonical executed reference run.
- [x] The scoring model is complete across core, plugin, and integration layers.
- [x] The evaluator workflow, fairness checks, trigger tests, and regression protocol are all specified.
- [x] At least one end-to-end benchmark slice is fully specified as a reference implementation target.
- [x] Status, paths, and filenames are consistent enough that a new architect or tooling builder can navigate the repo without guesswork.
