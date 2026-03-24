# Next-Phase Execution Tasklist 009

Focus: make shared package meaning more explicit and less string-fragile.

## Priority Order

### Required
- [x] Add an explicit marker or contract for `D-B04` as the bespoke anchor slice.
Done when:
- [x] The benchmark layer makes `D-B04` special on purpose, not just by code shape.
- [x] The decision is discoverable without reading all runtime files.

- [x] Introduce a lightweight structured package representation.
Done when:
- [x] Shared divorce reasoning can identify package families without relying only on string markers in `state["options"]`.
- [x] The representation remains simple enough for the current MVP scaffold.

- [x] Add tests for the new package representation across the package-oriented slices.
Done when:
- [x] `D-B05`, `D-B06`, and `D-B07` all exercise the new representation.
- [x] Shared plugin behavior is covered through that representation.

### Very Helpful
- [ ] Extend the content-helper pattern to support light runtime overlays on authored reference turns.
- [ ] Decide whether summary selectivity should remain as-is or become one step richer.

### Nice But Not Necessary
- [ ] Add helper utilities for repeated package metadata in authored slices.
- [ ] Add richer package-aware summary sections.

### Unnecessary Right Now
- [ ] A fifth divorce slice.
- [ ] A second plugin family.
- [ ] Broad runtime architecture changes.

## Execution Rule

Do not add another slice yet. Revisit evaluator artifacts, `evaluation.json`, and evaluator-facing schema/instruction consistency before adding a fifth slice.
