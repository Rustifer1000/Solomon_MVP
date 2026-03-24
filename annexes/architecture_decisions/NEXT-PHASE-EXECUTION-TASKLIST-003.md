# Next-Phase Execution Tasklist 003

## Priority Rule

Choose one of two directions explicitly:

- If the MVP remains divorce-only, prioritize slice breadth and benchmark discipline.
- If the MVP is meant to prove domain-pluggability, prioritize a plugin-neutral runtime boundary before adding more slices.

## Required

- [ ] Decide and encode the next architectural scope
  - Done when:
    - [ ] The repo states whether the near-term MVP is `divorce-plugin-first` or `plugin-neutral runtime`
    - [ ] The next tasks follow that choice explicitly

- [ ] Remove divorce-plugin assumptions from the generic orchestrator if plugin-neutral runtime is the goal
  - Target file:
    - `runtime/orchestrator.py`
  - Done when:
    - [ ] The orchestrator no longer imports a specific plugin module directly
    - [ ] Plugin qualification, state assessment, and flag sync are resolved through a plugin-facing interface

- [ ] Add a benchmark creation template/checklist
  - Done when:
    - [ ] A single short doc captures required files, registration steps, tests, and policy hooks
    - [ ] A new slice can be added by following that checklist without repo archaeology

## Very Helpful

- [ ] Introduce a small plugin interface/registry parallel to the benchmark registry
  - Done when:
    - [ ] Benchmarks can declare which plugin family they use
    - [ ] Runtime can call plugin hooks through a stable interface

- [ ] Add a third benchmark slice
  - If staying divorce-only:
    - [ ] Prefer a slice that stresses different issues than scheduling/logistics
  - If moving toward plugin-neutral runtime:
    - [ ] Add the third slice only after the plugin seam is cleaned up

- [ ] Add a benchmark policy surface for artifact phrasing
  - Done when:
    - [ ] Benchmarks can provide lightweight narrative hints without taking over generic artifact generation

## Nice But Not Necessary

- [ ] Split artifact narrative policy out from generic string builders
- [ ] Add explicit plugin-level tests separate from end-to-end tests
- [ ] Add a helper for generating new benchmark skeletons

## Unnecessary Right Now

- [ ] Broad multi-plugin generalization before deciding the MVP direction
- [ ] Production deployment or UI work
- [ ] More phrasing diversity work

## Suggested Execution Order

1. Record whether the next milestone is `divorce-only breadth` or `plugin-neutral runtime`.
2. If `divorce-only breadth`, write the benchmark creation template and add a third slice.
3. If `plugin-neutral runtime`, add a plugin interface/registry and remove direct plugin imports from the orchestrator.
4. Only then expand slice count or plugin count further.
