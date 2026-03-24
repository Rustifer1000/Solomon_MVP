# Post-Boundary Cleanup 024

## Purpose

This memo records the results of the boundary-cleanup pass that followed the post-`D-B13` boundary audit.

The goal was to remove the remaining obvious divorce-specific leaks from shared artifact and evaluator helper layers before sequencing the final remaining divorce template family.

---

## What Changed

### 1. Shared artifact layers no longer import divorce package vocabulary directly

`runtime/artifacts.py` and `runtime/support_artifacts.py` no longer import `PACKAGE_ELEMENT_LABELS` from `runtime.plugins.divorce_shared`.

Instead:

- the divorce plugin exposes package-element labels through the plugin runtime surface
- the orchestrator records that vocabulary in session metadata
- shared artifact writers consume plugin-provided vocabulary from state

This is a materially better boundary:

- shared layers keep structural responsibility
- the plugin owns its own vocabulary

### 2. Fairness and evaluator helpers are now plugin-aware

`runtime/fairness_checks.py` and `runtime/evaluator_operations.py` no longer depend on hardcoded case-id sets or shared divorce-only constants.

Instead they now read:

- plugin-owned evaluator helper policy
- benchmark-owned evaluator attention tags

from runtime metadata emitted in `run_meta.json`.

That means the helper design is now:

- shared helper logic
- plugin-provided review vocabulary
- benchmark-provided attention signaling

rather than shared code secretly carrying divorce-corpus assumptions.

### 3. Remaining shared artifact vocabulary is acceptable for now

After removing the direct label leak, the remaining shared artifact vocabulary is mostly structural and process-oriented:

- issues
- positions
- package detail
- escalation posture
- missing information

That still reflects the current scaffold style, but it is not the same kind of boundary problem as a direct import from a domain plugin module.

The remaining phrasing is acceptable while divorce remains the only active plugin family.

---

## Bottom Line

The important boundary cleanup is now done.

The repo is in a better state for later plugin expansion because:

- the core runtime loop remains plugin-neutral
- shared artifact layers are no longer reaching directly into divorce vocabulary
- evaluator helpers now consume plugin and benchmark review metadata rather than hardcoded divorce corpus assumptions

This does not mean the repo is fully multi-plugin proven.

It does mean the last major boundary leaks identified in the post-`D-B13` audit have been reduced enough that the next divorce family decision can be made on evaluation and safety grounds rather than boundary hygiene.

