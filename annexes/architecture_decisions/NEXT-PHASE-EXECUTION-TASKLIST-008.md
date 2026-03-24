# Next-Phase Execution Tasklist 008

Focus: normalize content architecture and improve package representation before expanding the divorce slice set again.

## Priority Order

### Required
- [ ] Decide and encode the intended status of `D-B04`.
Done when:
- [ ] We explicitly choose whether `D-B04` remains a bespoke runtime slice or moves closer to the content-helper pattern.
- [ ] That decision is reflected in code or memo form, not left implicit.

- [ ] Introduce a stronger shared package representation than raw option-marker strings.
Done when:
- [ ] Shared divorce reasoning can identify package families without relying only on free-form string markers.
- [ ] The representation is still lightweight enough for the current MVP runtime.

- [ ] Add tests that lock in the new package representation and any `D-B04` decision.
Done when:
- [ ] Shared package reasoning is directly tested through the new representation.
- [ ] The chosen `D-B04` path is guarded against silent drift.

### Very Helpful
- [ ] Extend the content-helper pattern to support light overlays on reference content.
- [ ] Decide whether summary selectivity should remain as-is or gain one more small richness step.

### Nice But Not Necessary
- [ ] Unify more authored/runtime slice content under declarative content blocks.
- [ ] Add lightweight helper utilities for repeated package-fact patterns.

### Unnecessary Right Now
- [ ] A fifth divorce slice.
- [ ] A second plugin family.
- [ ] Large runtime architecture changes.

## Execution Rule

Do not add another divorce slice yet. First settle the `D-B04` content pattern question and strengthen shared package representation for the four slices already in the repo.
