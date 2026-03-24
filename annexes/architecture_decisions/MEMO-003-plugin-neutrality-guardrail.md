# Memo 003: Plugin Neutrality Guardrail

Plugin neutrality is a standing architectural priority for Solomon.

## Guardrail

Shared runtime layers should not hardcode domain-plugin imports, names, or behavior when those responsibilities can be resolved through a plugin-facing interface.

In practice, this means:

- `runtime/orchestrator.py` should resolve plugin hooks through the plugin registry/interface, not by importing a specific plugin module directly.
- generic runtime/state/artifact code should not silently assume `divorce` as the only plugin family
- benchmark slices may remain divorce-only for a period of time, but that should not be used as a reason to re-harden divorce-specific assumptions in shared runtime code

## Why This Matters

Without this guardrail, the architecture can appear modular while still letting domain assumptions harden in shared code. That would make later plugin expansion costly and would blur the distinction between:

- a universal core mediation engine
- a divorce-specific runtime with optional abstractions layered on top

## Practical Review Question

When modifying shared runtime code, ask:

`Would this change still make sense if the next benchmark used a different plugin family?`

If the answer is no, the logic probably belongs in the plugin layer or benchmark/policy layer instead.
