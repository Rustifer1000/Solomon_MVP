# Next-Phase Execution Tasklist 011

Focus: decide whether evaluator reference coverage is sufficient before adding a fifth divorce slice.

## Priority Order

### Required
- [x] Decide whether the current worked evaluator contrast pair is enough.
Done when:
- [x] The repo explicitly records either:
  - `D-B04` + `D-B05` are sufficient for now, or
  - one more worked `M0` evaluator example is required before slice expansion.

- [x] If one more worked evaluator example is required, choose exactly one slice: `D-B06` or `D-B07`.
Done when:
- [x] The selection is recorded in repo guidance.
- [x] The reason is tied to evaluator calibration value, not just completeness.

- [ ] Add a reusable validation helper for `evaluation.json` example consistency.
Done when:
- [ ] Reference evaluation examples are checked in one reusable place rather than only through ad hoc assertions.
- [ ] Weight-band and key-field alignment are covered.

### Very Helpful
- [ ] Add a light template/contract note for `evaluation_summary.txt`.
- [ ] Add one worked `expert_review.json` example after evaluator-example policy is settled.

### Nice But Not Necessary
- [ ] Add calibration notes for common `M0` vs `M1` disagreements across current slices.
- [ ] Add a tiny script that validates reference evaluator examples against the schema files.

### Unnecessary Right Now
- [ ] A fifth divorce slice before the evaluator-coverage decision is made.
- [ ] A second plugin family.
- [ ] Evaluator-console implementation.

## Execution Rule

Do not add a fifth divorce slice yet. The repo now has three evaluator anchors: `D-B04` (`M1` caution), `D-B05` (`M0` package), and `D-B06` (`M0` fairness-sensitive package). Next improve reusable evaluator-example validation before expanding breadth again.
