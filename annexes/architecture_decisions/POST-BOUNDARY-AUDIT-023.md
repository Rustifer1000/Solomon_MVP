# Post-Boundary Audit 023

## Purpose

This memo records a focused audit of the core/plugin boundary after the `D-B13` slice landed.

The question was not whether the repo is already multi-plugin complete. It was whether the current divorce-first build is still preserving the architectural separation needed for later plugin families.

---

## Short Answer

Yes, mostly.

The runtime spine is respecting the core/plugin boundary much better than earlier in the project. The main remaining leaks are not in the orchestrator. They are in shared artifact and evaluator helper layers that still know a bit too much about current divorce vocabulary.

---

## What Is Healthy

### 1. The orchestrator seam is real

`runtime/orchestrator.py` resolves plugin behavior through the plugin registry and plugin interface rather than importing divorce logic directly.

That is the most important architectural seam, and it is holding.

### 2. The benchmark layer owns slice policy

Benchmark simulations now own:

- plugin policy descriptors
- artifact narrative policy
- support-artifact policy
- benchmark descriptors
- runtime turn plans

That keeps slice-specific behavior out of shared runtime logic.

### 3. The plugin registry is the right shape

`runtime/plugins/base.py` and `runtime/plugins/__init__.py` define a clean minimal runtime hook surface:

- `qualify_case`
- `assess_state`
- `sync_flags_for_turn`

That is a healthy starting point for later plugin expansion.

---

## Remaining Boundary Leaks

### 1. Shared artifacts still import divorce-specific package labels

`runtime/artifacts.py` imports `PACKAGE_ELEMENT_LABELS` from `runtime.plugins.divorce_shared`.

This is the clearest remaining core/plugin leak.

Why it matters:

- the shared artifact layer should not depend directly on a divorce plugin module
- a second plugin would either inherit the wrong vocabulary path or require shared-layer changes

### 2. Evaluator helpers are still effectively divorce-shaped

`runtime/fairness_checks.py` and `runtime/evaluator_operations.py` are useful and valid, but they still encode current fairness and review assumptions in a divorce-first way.

Why it matters:

- these helpers should eventually become plugin-aware rather than silently plugin-specific
- otherwise later plugin families will look like exceptions instead of first-class citizens

### 3. Shared artifact narration is generic in structure but still narrow in vocabulary

The artifact layer is much better than before, but it still assumes the current issue/package idiom more than a fully plugin-owned narrative vocabulary.

Why it matters:

- this is manageable while divorce is the only plugin
- but it is still a watch point for future plugin-neutrality

---

## Bottom Line

The repo is maintaining the boundary where it matters most:

- core runtime loop
- benchmark/plugin registration
- slice-owned policy

The remaining cleanup is about:

- shared artifact vocabulary
- shared evaluator vocabulary

not about major architecture reversal.

That is a good state for a divorce-first MVP.
