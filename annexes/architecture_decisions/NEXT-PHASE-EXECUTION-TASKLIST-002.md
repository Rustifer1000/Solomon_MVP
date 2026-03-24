# Next-Phase Execution Tasklist 002

## Priority Rule

Work top to bottom. Favor changes that remove benchmark-specific assumptions from generic runtime/state/artifact layers before adding new feature breadth.

## Required

- [ ] Move benchmark-specific next-step policy out of `runtime/state.py`
  - Done when:
    - [ ] Generic state logic no longer contains the `turn_index == 8` D-B04 override
    - [ ] Benchmarks own any slice-specific closing recommendation policy

- [ ] Make artifact narrative builders state-aware instead of D-B04-shaped
  - Target files:
    - `runtime/artifacts.py`
  - Done when:
    - [ ] `_summary_intro(...)` does not always imply fixed-recommendation avoidance
    - [ ] `_summary_positions(...)` does not always imply phased optioning
    - [ ] `_missing_info_note(...)` is not overnight-schedule-specific
    - [ ] `D-B04` and `D-B05` produce equally plausible summaries from the same generic artifact layer

- [ ] Move hardcoded flag templates out of generic state logic
  - Target files:
    - `runtime/state.py`
    - benchmark layer or plugin layer
  - Done when:
    - [ ] Generic state logic no longer carries `flag-db04-*` ids/titles/notes
    - [ ] Flag meaning comes from plugin or benchmark-owned policy
    - [ ] A second slice can emit benchmark-appropriate flags without modifying shared state code

- [ ] Add artifact-narrative coherence tests across both slices
  - Done when:
    - [ ] Tests assert `D-B04` summary language matches caution state
    - [ ] Tests assert `D-B05` summary language does not imply unnecessary caution
    - [ ] Tests assert missing-info/flags/escalation language stays slice-appropriate

## Very Helpful

- [ ] Refactor the divorce plugin into clearer shared-vs-slice-specific logic
  - Done when:
    - [ ] Shared divorce plugin logic is not mostly logistics-keyword logic
    - [ ] Slice-specific caution heuristics can live outside the generic divorce plugin

- [ ] Introduce a benchmark policy surface for artifact phrasing and close-out behavior
  - Done when:
    - [ ] Benchmarks can provide small policy hints without owning the whole artifact layer
    - [ ] Summary/flag/next-step phrasing can vary by slice without duplicating artifact generation

- [ ] Add a benchmark creation checklist/template
  - Done when:
    - [ ] A new slice can be added by following one short pattern doc
    - [ ] Registry, files, tests, and simulation steps are captured in one place

## Nice But Not Necessary

- [ ] Add a third benchmark slice after the generic artifact/flag cleanup
- [ ] Add explicit artifact validation helpers in `runtime/` rather than only test assertions
- [ ] Add schema-version notes or benchmark metadata to summaries for evaluator convenience

## Unnecessary Right Now

- [ ] Broad plugin generalization beyond what the next slice needs
- [ ] Production deployment or UI work
- [ ] More generation diversity before generic artifact/flag cleanup is complete

## Suggested Execution Order

1. Remove the D-B04 next-step override from shared state.
2. Make summary/missing-info/position notes genuinely slice-neutral.
3. Move flag template ownership out of shared state.
4. Add dual-slice artifact narrative tests.
5. Then revisit whether the divorce plugin should split into shared + slice-specific policy.
