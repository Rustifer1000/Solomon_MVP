# Template 001: Benchmark Creation Checklist

Use this checklist when adding a new benchmark slice.

## Goal

Add a benchmark without relying on repo archaeology or hidden assumptions.

## Required Files

Create a new folder under:

- `annexes/benchmark_cases/<CASE_ID>/`

Include at minimum:

- `case_metadata.json`
- `personas/spouse_A.json` and `personas/spouse_B.json` or equivalent participant files
- `README.md`
- `sessions/<SESSION_ID>/.gitkeep` if no reference artifacts exist yet

## Runtime Files

Add benchmark modules under `runtime/benchmarks/`:

- `<case_id_lower>_authored.py`
- `<case_id_lower>_runtime.py`
- `<case_id_lower>_simulation.py`
- `<case_id_lower>.py` as a thin facade

Prefer using the shared scaffold in `runtime/benchmarks/scaffold.py`:

- `BenchmarkSourceBuilders`
- `BenchmarkRuntimeBuilders`
- `ConfiguredBenchmarkSimulation`

That keeps new slices mostly declarative instead of requiring a bespoke simulation class.

## Registration Steps

1. Register the simulation in `runtime/benchmarks/__init__.py`
2. Ensure `case_metadata.json` has the correct `case_id` and `plugin_type`
3. Ensure the simulation provides:
   - `default_session_id()`
   - `reference_session_dir(...)`
   - `build_turns(...)`
   - `plugin_policy_descriptor(...)`
   - `artifact_narrative_policy(...)`
   - `build_runtime_turn_plan(...)`
   - `generate_runtime_assistant_turn(...)`
   - `generate_runtime_client_turn(...)`
   - `finalize_next_step(...)`

## Design Checks

Before calling the slice complete, confirm:

- the runtime turn plan shape is owned by the benchmark, not the orchestrator
- structured deltas are used wherever practical
- the benchmark does not require new benchmark-specific logic in shared runtime/state code
- summary/flag/missing-info behavior reads plausibly for the slice

## Test Checklist

Add or update tests in `tests/test_end_to_end.py` for:

- benchmark registry lookup
- end-to-end runtime execution
- expected turn count
- expected closing posture (`M0`/`M1`)
- expected artifact family
- narrative coherence specific to the slice

## Final Review Question

`Did I add a new benchmark, or did I quietly hardcode a new exception into shared runtime code?`
