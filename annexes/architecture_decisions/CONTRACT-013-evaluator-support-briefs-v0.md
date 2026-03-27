# CONTRACT-013: Evaluator Support Briefs v0

**Status**
Draft / informative

**Purpose**
This document defines the contracts for the three evaluator support briefs produced under the `eval_support` and `dev_verbose` policy profiles:

- `case_intake_brief.json` — written at session open
- `early_dynamics_brief.json` — written after opening positions emerge
- `risk_alert_brief.json` — written when flags are active or escalation mode is not M0

These briefs are **evaluator-facing** artifacts. They are derived from state and are not authoritative records. The canonical records are `interaction_trace.json`, `flags.json`, `positions.json`, `facts_snapshot.json`, and `missing_info.json`.

---

## 1. Shared invariants across all three briefs

- Briefs are derived from structured state. They must not introduce new facts, positions, or flags not present in the canonical artifacts.
- Briefs are produced only when the policy profile permits (`eval_support`, `dev_verbose`). They are absent under `sim_minimal` and `redacted`.
- Brief content may be redacted under the `redacted` profile (same rules as canonical artifacts).
- Briefs are written to `sessions/{session_id}/briefs/` alongside their plain-text equivalents.

---

## 2. `case_intake_brief.json`

### 2.1 Purpose

Provides a quick evaluator-facing summary of the case setup at session open.

### 2.2 Required fields

```json
{
  "schema_version": "case_intake_brief.v0",
  "case_id": "string",
  "session_id": "string",
  "policy_profile": "string",
  "plugin_type": "string",
  "title": "string",
  "scenario_summary": "string",
  "expected_mode_range": ["M0", "M1"],
  "participant_snapshots": [
    {
      "participant_id": "string",
      "role_label": "string",
      "public_goals": ["string"],
      "interest_profile": ["string"],
      "starting_positions": ["string"]
    }
  ]
}
```

### 2.3 Optional fields

`intended_challenge_type`
: Short label for the type of challenge the benchmark is designed to stress, e.g. `"constrained_voluntariness"` or `"emotional_flooding"`.

### 2.4 Schema reference

`schema/case_intake_brief.schema.json`

---

## 3. `early_dynamics_brief.json`

### 3.1 Purpose

Captures a mid-session snapshot of opening positions, active issues, and early flag state for evaluator reference.

### 3.2 Required fields

```json
{
  "schema_version": "early_dynamics_brief.v0",
  "case_id": "string",
  "session_id": "string",
  "phase": "string",
  "issues": ["string"],
  "opening_positions": [
    {
      "participant_id": "string",
      "statement": "string"
    }
  ],
  "open_missing_info": ["string"],
  "active_flags": ["string"],
  "package_snapshot": null
}
```

`package_snapshot` is null when no package is in play. When present, it records the active package family, status, elements, and related issues.

### 3.3 Schema reference

`schema/early_dynamics_brief.schema.json`

---

## 4. `risk_alert_brief.json`

### 4.1 Purpose

Provides a structured escalation alert for evaluator review when flags are active or mode is not M0. Summarizes the escalation decision and active risk signals.

### 4.2 Required fields

```json
{
  "schema_version": "risk_alert_brief.v0",
  "case_id": "string",
  "session_id": "string",
  "mode": "M0–M5",
  "category": "E1–E6 or null",
  "category_family": "string",
  "recommended_human_role": "string",
  "handoff_focus": "string",
  "support_artifact_policy_descriptor": "string",
  "rationale": "string",
  "active_flags": [
    {
      "flag_type": "string",
      "title": "string",
      "severity": 1
    }
  ],
  "plugin_warnings": ["string"]
}
```

### 4.3 `category_family` allowed values

`"safety_or_coercion"`, `"fairness_or_process_breakdown"`, `"explicit_human_involvement_request"`, `"domain_complexity_review"`, `"decision_quality_caution"`, `"role_boundary_pressure"`, `"none"`

### 4.4 `recommended_human_role` allowed values

`"full_handoff"`, `"co_handling"`, `"human_review"`, `"bounded_review_or_caution"`, `"none"`

### 4.5 Invariants

- `risk_alert_brief.json` is only written when mode is not `M0` or when active flags are present.
- The `rationale` field must reflect the escalation engine's output — it must not introduce new reasoning not present in the canonical escalation state.
- `active_flags` in this brief must be a subset of flags present in `flags.json`.

### 4.6 Schema reference

`schema/risk_alert_brief.schema.json`
