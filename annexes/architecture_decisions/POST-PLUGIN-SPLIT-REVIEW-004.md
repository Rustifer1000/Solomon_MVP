# Post-Plugin-Split Review 004

## Findings

### [P1] The plugin seam is cleaner, but the orchestrator is still plugin-specific

`runtime/orchestrator.py` still imports and calls the divorce plugin directly:

- `qualify_case(...)`
- `assess_state(...)`
- `sync_flags_for_turn(...)`

That means benchmarks are registered through the simulation layer, but the runtime still assumes a single plugin family. The current architecture is therefore "multi-slice within one plugin" rather than "plugin-neutral runtime".

### [P1] Shared divorce analysis still carries logistics-heavy assumptions as default shared behavior

`runtime/plugins/divorce_shared.py` is a useful split, but its shared layer still centers:

- logistics keywords
- logistics-related missing info
- logistics-related uncertain facts

That may be acceptable for the current two slices, but it means the shared divorce layer is still closer to "divorce scheduling/process cases" than a broader divorce-plugin foundation.

### [P2] Case policy is explicit now, but still encoded as hardcoded `case_id` branching

`runtime/plugins/divorce_policy.py` currently uses `_default_policy(case_id)` with explicit `D-B04` and `D-B05` branches.

This is a good transitional step, but the next layer of maturity is to let benchmark simulations provide policy descriptors rather than growing a central `if case_id == ...` table.

### [P2] Artifact notes remain generic, but are not yet policy-aware

`runtime/artifacts.py` is much better than before, but its note generation still infers narrative from state alone rather than consulting benchmark/plugin policy.

That means:

- it avoids hardcoded `D-B04` narration
- but it also has no clean way to express slice-specific narrative preferences except by indirect state interpretation

The current approach is fine for now, but the next evolution is probably a small narrative-policy surface rather than pushing more nuance into generic string-building logic.

### [P2] Benchmark creation is still repetitive enough to invite drift

Adding `D-B05` proved the architecture works, but it still required:

- case files
- authored module
- runtime module
- simulation module
- facade export
- registry update
- tests

That is manageable today, but the repo is now ready for a benchmark template/checklist so new slices do not depend on memory.

### [P3] The runtime still has no concept of plugin selection independent of benchmark selection

Benchmarks currently imply plugin choice through case metadata plus the hardwired divorce plugin path. That works with one plugin family, but a future non-divorce slice would currently require runtime-level edits rather than only benchmark/plugin registration.

## What Is Healthy Here

- The divorce plugin split is real and useful.
- Shared analysis vs case-policy is now visible in code.
- The benchmark layer, policy layer, artifact layer, and tests are all materially cleaner than they were a few iterations ago.
- The current system is now a credible multi-slice executable eval prototype for one plugin family.

## MVP Readiness Update

The main architectural question has shifted again. The repo no longer looks blocked by slice-level cleanup. The next important question is whether the runtime should stay "divorce-plugin-first" for the MVP, or whether it should now introduce a proper plugin abstraction boundary before adding more slice breadth.

If the MVP scope remains divorce-only for now, the next best work is benchmark/template discipline plus a third slice. If the MVP is meant to demonstrate domain-pluggability, the next best work is making the runtime plugin-neutral.
