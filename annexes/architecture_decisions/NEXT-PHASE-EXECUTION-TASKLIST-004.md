# Next-Phase Execution Tasklist 004

## Priority Rule

Preserve plugin neutrality while reducing future drift. Prefer changes that strengthen the new abstraction boundaries and make future slice/plugin additions safer.

## Strategy Lock

Near-term focus: continue with additional divorce slices until the divorce path is robust and trustworthy. Do not prioritize a second plugin family before the divorce benchmark path is more complete.

## Required

- [x] Make run metadata plugin-neutral as well as runtime-neutral
  - Target file:
    - `runtime/artifacts.py`
  - Done when:
    - [x] prompt ids do not hardcode `divorce_plugin_*` in generic metadata generation
    - [x] plugin-facing metadata can come from the plugin runtime or plugin type

- [x] Add plugin-registry failure-path tests
  - Done when:
    - [x] unknown `plugin_type` produces a clear failure
    - [x] plugin registry behavior is tested independently of the orchestrator

- [x] Add a benchmark creation checklist/template
  - Done when:
    - [x] required files, registration points, tests, and policy hooks are captured in one short repo doc
    - [x] a future slice can be added without repo archaeology

## Very Helpful

- [x] Add a plugin creation checklist/template parallel to the benchmark template
  - Done when:
    - [x] a second plugin family has a clear path into the repo
    - [x] required interface, registry, policy, and test steps are documented

- [ ] Make plugin choice visible in benchmark-facing contracts
  - Done when:
    - [ ] benchmark interfaces or registry data explicitly reflect plugin family, not just case metadata convention

- [ ] Add a third divorce slice that stresses a different issue cluster than the first two

## Nice But Not Necessary

- [ ] Add plugin-aware artifact phrasing hooks
- [ ] Add orchestrator-level tests that assert direct plugin imports do not reappear
- [ ] Add helper scaffolds/scripts for new benchmark or plugin skeletons

## Unnecessary Right Now

- [ ] Production deployment concerns
- [ ] UI work
- [ ] Large-scale plugin proliferation before templates and metadata cleanup are done

## Suggested Execution Order

1. Make metadata fully plugin-neutral.
2. Add plugin-registry failure-path tests.
3. Write the benchmark creation template.
4. Write the plugin creation template.
5. Then add a third divorce slice.
