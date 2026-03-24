# Next-Phase Execution Tasklist 010

Focus: evaluator artifacts and scoring consistency before a fifth divorce slice.

## Priority Order

### Required
- [x] Add evaluator review-path coverage for `D-B05`, `D-B06`, and `D-B07`.
Done when:
- [x] Each active divorce slice has an `evaluator_review_path.md`.
- [x] Each slice README points evaluators to that path.

- [x] Add guardrail checks for evaluator-side consistency.
Done when:
- [x] The reference `D-B04` `evaluation.json` is covered by repo tests at the shape/alignment level.
- [x] Slice metadata and evaluator artifact expectations are checked for the active divorce slices.

- [ ] Decide whether to add one or more additional reference `evaluation.json` examples before a fifth slice.
Done when:
- [ ] The team explicitly chooses whether `D-B05`, `D-B06`, or `D-B07` should gain a worked evaluator example next.
- [ ] That decision is captured in repo guidance.

### Very Helpful
- [ ] Add a small evaluator template for `evaluation_summary.txt` if that artifact should remain recommended.
- [ ] Add a schema/example validation helper outside the unit test file.

### Nice But Not Necessary
- [ ] Add a worked `expert_review.json` example.
- [ ] Add evaluator calibration notes for common `M0` vs `M1` disagreements across the divorce slices.

### Unnecessary Right Now
- [ ] A fifth divorce slice.
- [ ] A second plugin family.
- [ ] Evaluator-console implementation work beyond current schema and workflow consistency.

## Execution Rule

Do not add another divorce slice yet. First decide whether the current evaluator layer needs additional worked reference evaluations for the existing `M0` package slices.
