# Template 002: Plugin Creation Checklist

Use this checklist when adding a new plugin family.

## Goal

Add a plugin without re-hardcoding plugin-specific behavior into shared runtime code.

## Required Runtime Files

Add plugin modules under `runtime/plugins/`:

- `<plugin_name>.py` as the stable facade/runtime implementation
- optional `<plugin_name>_shared.py` for shared analysis helpers
- optional `<plugin_name>_policy.py` for slice- or case-policy overlays

## Interface Requirements

A plugin runtime should satisfy `runtime/plugins/base.py`:

- `plugin_type`
- `qualify_case(case_bundle)`
- `assess_state(state)`
- `sync_flags_for_turn(state, turn)`

## Registration Steps

1. Register the plugin runtime in `runtime/plugins/__init__.py`
2. Ensure benchmarks using the plugin declare the correct `plugin_type` in `case_metadata.json`
3. Ensure plugin-owned metadata and flag behavior do not require orchestrator edits

## Design Checks

Before calling the plugin integration complete, confirm:

- the orchestrator still resolves through `get_plugin_runtime(...)`
- shared runtime/state/artifact code does not import the plugin directly
- plugin-specific flags or caution logic live in the plugin layer, not shared state
- plugin assumptions are visible in plugin code or policy, not hidden in generic helpers

## Test Checklist

Add or update tests for:

- plugin registry lookup
- unknown `plugin_type` failure behavior
- plugin-specific state assessment behavior
- plugin-specific flag sync behavior
- at least one end-to-end benchmark using the plugin

## Final Review Question

`Did I add a new plugin family, or did I just move plugin-specific assumptions into generic runtime code?`
