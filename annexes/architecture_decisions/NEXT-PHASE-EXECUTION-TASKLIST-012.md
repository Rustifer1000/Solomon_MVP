# Next-Phase Execution Tasklist 012

Focus: improve quality and depth across the four existing divorce slices before adding more slice breadth.

## Priority Order

### Required
- [x] Increase artifact depth for package-bearing slices.
Done when:
- [x] `summary.txt` preserves more than one generic package sentence when a slice closes around a bounded package.
- [x] `D-B05`, `D-B06`, and `D-B07` remain distinguishable in evaluator-facing summaries without reading raw turns.
- [x] Added detail still remains downstream of authoritative state, not handcrafted prose.

- [x] Deepen shared divorce package reasoning from family-level to element-level.
Done when:
- [x] The shared plugin can reason over structured package elements, not only package family names or old option markers.
- [x] At least one package-quality assessment changes because an expected element is missing, incomplete, or only partially qualified.
- [x] Tests prove the shared plugin is using structured package elements across non-logistics slices.

- [x] Choose one patterned non-anchor slice to carry more real runtime synthesis.
Done when:
- [x] One of `D-B05`, `D-B06`, or `D-B07` exercises more live runtime-generated behavior rather than only authored-turn reuse.
- [x] `D-B04` remains the bespoke anchor slice by policy.
- [x] The chosen slice still stays clean enough to serve as a reusable pattern rather than becoming a second giant bespoke outlier.

### Very Helpful
- [x] Add a reusable repo utility for validating worked evaluator examples.
Done when:
- [x] Reference `evaluation.json` examples can be validated outside the unit-test suite.
- [x] The utility checks both schema compatibility and the repo's stronger reference-example consistency rules.

- [x] Add a light contract note for `evaluation_summary.txt`.
Done when:
- [x] The repo explains what minimum content a worked `evaluation_summary.txt` should preserve.
- [x] The current worked evaluator anchors can be checked against that note.

- [x] Add one worked `expert_review.json` example.
Done when:
- [x] At least one active reference session has a worked expert-review artifact.
- [x] The example stays aligned with the current schema and the primary worked evaluation.

### Nice But Not Necessary
- [ ] Reduce or explicitly fence the remaining fallback defaults in [state.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/state.py).
- [ ] Add one more direct plugin-depth test for mixed-package or partially qualified package cases.

### Unnecessary Right Now
- [ ] A fifth divorce slice.
- [ ] A second plugin family.
- [ ] Broad evaluator-console implementation.

## Execution Rule

Do not add more slice breadth yet. The next gain in trust will come from making the current four slices deeper, more evaluator-legible, and more faithfully represented end to end.

## Update

`D-B06` is now the patterned slice carrying additional live runtime synthesis on the assistant side, while `D-B04` remains the deliberate bespoke anchor slice.

The evaluator plane now has a reusable validation utility, a worked `expert_review.json` example for `D-B04`, and a contract note for `evaluation_summary.txt`.
