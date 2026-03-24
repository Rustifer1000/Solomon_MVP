# Next-Phase Execution Tasklist 013

Focus: improve completeness and edge-case depth across the existing four divorce slices before any further slice expansion.

## Priority Order

### Required
- [ ] Improve evaluator-facing artifact completeness.
Done when:
- [ ] `summary.txt` can preserve more than one package-relevant fact or concern when the slice supports it.
- [ ] Caution-oriented runs expose more than a single warning line when multiple caution reasons are active.
- [ ] Package-oriented runs remain readable while surfacing more than one relevant bounded-package detail.
- [ ] Added completeness still remains downstream of authoritative state and plugin assessment.

- [ ] Deepen shared plugin handling for edge-case package states.
Done when:
- [ ] The shared divorce layer can assess mixed, partial, or competing package signals more explicitly.
- [ ] At least one edge-case package test changes plugin output in a way that would matter to evaluator interpretation.
- [ ] The richer edge-case handling remains shared logic, not slice-specific patching.

- [ ] Add artifact/plugin coherence tests for richer edge cases.
Done when:
- [ ] Tests cover at least one partial-package case and one mixed-package case.
- [ ] Tests confirm that artifact summaries do not overstate package completeness when the plugin marks the package as partial.
- [ ] Tests confirm that caution summaries remain aligned with multiple active caution reasons.

### Very Helpful
- [x] Add a light evaluator authoring note or template for future worked `evaluation.json` examples.
Done when:
- [x] The repo documents how to create a worked reference evaluation without guessing field conventions.

- [x] Add a parallel note or template for future worked `expert_review.json` examples.
Done when:
- [x] The repo documents when expert review is appropriate and what a minimal worked example should include.

### Nice But Not Necessary
- [ ] Reduce or fence the remaining shallow fallback defaults in [state.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/state.py).
- [x] Reduce another safe slice-content duplication seam once the artifact/plugin work is done.

### Unnecessary Right Now
- [ ] A fifth divorce slice.
- [ ] A second plugin family.
- [ ] Evaluator-console implementation.

## Execution Rule

Do not add more slice breadth yet. The next gain in trust will come from making the current artifact set fuller and the shared divorce plugin more honest in edge-case package states.

## Update

The repo now includes authoring notes for future worked `evaluation.json` and `expert_review.json` examples, so evaluator/example creation is less manual and less likely to drift.

The patterned authored slices now share a small message-variant helper for mock and varied-mock turn generation instead of maintaining that override pattern in parallel.
