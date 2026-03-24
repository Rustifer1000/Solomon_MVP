# Next-Phase Execution Tasklist 005

Focus: strengthen the divorce path by making slice policy more declarative, reducing central branching, and making new slice creation safer.

## Priority Order

### Required
- [ ] Add a benchmark-owned divorce policy descriptor seam.
Done when:
- [ ] Benchmark simulations can expose divorce-policy inputs without relying on central `case_id` branching.
- [ ] Shared plugin logic can consume those policy inputs through a stable interface.

- [ ] Refactor `runtime/plugins/divorce_policy.py` to consume slice-provided policy descriptors.
Done when:
- [ ] `D-B04`, `D-B05`, and `D-B06` each declare their own policy descriptor or equivalent slice-owned policy payload.
- [ ] The central policy file is no longer a growing switchboard of case ids.

- [ ] Add a light artifact narrative-policy seam.
Done when:
- [ ] Benchmarks can provide limited narrative posture hints without pushing slice-specific language back into shared artifact code.
- [ ] Shared artifact generation remains generic and readable.

- [ ] Add a benchmark scaffold utility or skeleton pattern.
Done when:
- [ ] Creating a new divorce slice requires less manual boilerplate than the current three-slice pattern.
- [ ] The creation path is clear enough that slice growth is less likely to drift.

### Very Helpful
- [ ] Add explicit tests proving slice-owned policy is honored across `D-B04`, `D-B05`, and `D-B06`.
- [ ] Add tests for any new artifact narrative-policy seam.
- [ ] Add a fourth divorce slice after the policy refactor lands.

### Nice But Not Necessary
- [ ] Replace manual registry edits with a more automated registration pattern.
- [ ] Add a benchmark scaffold CLI command.

### Unnecessary Right Now
- [ ] A second plugin family.
- [ ] Cross-domain runtime expansion beyond divorce.
- [ ] Production-grade automation around benchmark generation.

## Execution Rule

Work top to bottom. Do not add a fourth divorce slice until benchmark-owned divorce policy and the light narrative-policy seam are in place.
