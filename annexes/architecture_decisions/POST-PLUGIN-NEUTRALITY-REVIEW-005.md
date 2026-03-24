# Post-Plugin-Neutrality Review 005

## Findings

### [P1] The runtime is plugin-neutral at the orchestrator seam, but not yet plugin-neutral in generated metadata

`runtime/orchestrator.py` now resolves plugin hooks through the registry, which is a real architectural win. However, `runtime/artifacts.py` still hardcodes prompt ids like:

- `divorce_plugin_mock_v0`
- `divorce_plugin_runtime_v0`

That means the runtime control flow is plugin-neutral, but the provenance metadata still assumes the divorce plugin as the only plugin family.

### [P1] Benchmarks still do not declare plugin family explicitly through a benchmark-facing contract

The plugin registry resolves from `case_metadata.plugin_type`, which works. But the benchmark protocol in `runtime/benchmarks/base.py` still has no explicit plugin-facing hook or plugin declaration. So the plugin-neutral seam exists, but benchmarks and plugins are still connected indirectly through shared metadata conventions rather than a clearer contract.

### [P2] The current plugin registry is real, but only lightly tested as an abstraction

The code now routes through `runtime/plugins/__init__.py`, and tests cover retrieval of the divorce plugin runtime. But there are not yet tests that:

- assert the orchestrator remains free of direct plugin imports over time
- validate behavior when an unknown `plugin_type` is encountered
- prove multiple plugin implementations can coexist cleanly in the registry

### [P2] Shared divorce analysis is still narrower than the neutrality milestone might suggest

The runtime is plugin-neutral, but the only plugin family still assumes scheduling/logistics-heavy mediation. That is not a bug; it just means "plugin-neutral runtime" has been achieved sooner than "domain-broad plugin ecosystem."

### [P2] Benchmark creation discipline is now the most obvious missing operational tool

At this point the architecture is modular enough that the biggest friction is procedural: adding slices and future plugin families is still too dependent on memory and pattern-matching across the repo.

### [P3] Artifact phrasing is state-aware, but not yet plugin-aware

The artifact layer no longer tells a `D-B04`-only story, which is good. But if a future non-divorce plugin wanted different narrative emphasis, there is not yet a formal plugin-aware phrasing hook. This is not urgent, but it is the next abstraction frontier after plugin-neutral orchestration.

## What Is Healthy Here

- Plugin neutrality is no longer just a memo; it is now embodied in the runtime seam.
- The orchestrator no longer imports a specific plugin module directly.
- The plugin registry/interface is small, understandable, and sufficient for the current runtime.
- The repo now has coherent benchmark, plugin, and runtime seams all at once.

## MVP Readiness Update

The architecture is now in a noticeably stronger state. The next bottleneck is no longer "remove divorce assumptions from the orchestrator." That is done. The next highest-value work is:

1. strengthen the plugin-neutral contract around metadata and failure cases
2. reduce future development drift by documenting how to add new slices/plugins
3. decide whether the next proof point is a third divorce slice or a second plugin family
