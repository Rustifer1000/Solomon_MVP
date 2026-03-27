# CONTRACT-012: Session Meta v0

**Status**
Draft / informative

**Purpose**
This document defines the contract for `session_meta.json`, the stable identity document written at the start of every benchmark session.

---

## 1. Role

`session_meta.json` captures what is **constant across all runs of a given session**: case identity, plugin type, source mode, and human-readable labels.

It is distinct from `run_meta.json`, which captures per-run provenance (timestamps, model config, git hash, policy profile). `session_meta.json` is stable across reruns; `run_meta.json` changes each time the session is run.

---

## 2. Required fields

```json
{
  "schema_version": "session_meta.v0",
  "case_id": "string",
  "session_id": "string",
  "plugin_type": "string",
  "source": "string",
  "created_at": "ISO-8601 datetime string"
}
```

## 3. Optional fields

```json
{
  "title": "string or null",
  "scenario_summary": "string or null"
}
```

---

## 4. Field definitions

`schema_version`
: Must be `"session_meta.v0"`.

`case_id`
: Stable identifier for the case definition. Must match the `case_id` in `case_metadata.json` and all other session artifacts.

`session_id`
: Stable identifier for the session. Typically derived from the benchmark module's `default_session_id()`.

`plugin_type`
: Primary plugin/domain for this session, e.g. `"divorce"`.

`source`
: Turn-output source used for this session. Allowed values: `"runtime"`, `"reference"`, `"mock_model"`, `"varied_mock_model"`, `"lm_runtime"`.

`created_at`
: Timestamp when the session folder was first initialized.

`title`
: Human-readable case title. Drawn from case metadata if available.

`scenario_summary`
: One-sentence scenario description. Drawn from case metadata if available.

---

## 5. Required invariants

- `session_meta.json` must be written as the first artifact in a session output directory.
- Its `case_id` and `session_id` must be identical to those in `run_meta.json` and all other session artifacts.
- It must not contain per-run fields (timestamps of the run, model config, policy profile, git hash). Those belong in `run_meta.json`.

---

## 6. Artifact location

```text
sessions/
  {session_id}/
    session_meta.json    ← written first, stable across reruns
    run_meta.json        ← written per run
    interaction_trace.json
    ...
```

---

## 7. Schema reference

`schema/session_meta.schema.json`
