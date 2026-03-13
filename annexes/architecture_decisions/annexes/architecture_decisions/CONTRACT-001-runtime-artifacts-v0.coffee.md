Good. We’ll use the checklist as the active driver and start with the first high-leverage incomplete block:

**Section F: Artifact readiness**

The repo already says the evaluation architecture should use **file-based artifacts as the source of truth** and that the first implementation should produce at least `run_meta.json`, `interaction_trace.json`, `positions.json`, `facts_snapshot.json`, `flags.json`, `missing_info.json`, and `summary.txt` . It also says `interaction_trace.json` must be sufficient for evaluation, justification of flags/escalation, continuity review, and later dataset curation, and it gives minimum required fields for both `interaction_trace.json` and `run_meta.json` .

So the right first artifact is:

`annexes/architecture_decisions/CONTRACT-001-runtime-artifacts-v0.md`

This would let you start checking off:

* F1 source-of-truth artifacts defined
* F3 trace semantics concrete
* part of G3 reproducibility contract stable

Here is the repo-ready draft.

````md
# CONTRACT-001: Runtime Artifacts v0

**Status**  
Draft / informative

**Purpose**  
This document defines the minimum runtime artifact contracts for Solomon’s first offline evaluation-phase implementation.

It is intended to make the runtime architecture concrete enough to support:
- repeatable offline runs
- evaluator review
- escalation analysis
- handoff continuity
- debugging and regression comparison
- later schema formalization

This document does **not** supersede the normative specification.  
If there is any conflict between this document and the normative documents or schemas, the normative specification wins.

---

## 1. Scope

This v0 contract defines the minimum expectations for:

- `run_meta.json`
- `interaction_trace.json`

These two artifacts are prioritized first because they anchor:
- reproducibility
- traceability
- evaluation review
- escalation reasoning
- later schema work for additional artifacts

This document also records the expected place of these files within the session artifact layout.

---

## 2. Artifact role summary

### 2.1 `run_meta.json`
`run_meta.json` is the authoritative record of **how a run was produced**.

It exists to answer:
- which case definition was used
- which model and configuration produced the run
- which prompt version was active
- which policy profile controlled persistence
- which code version generated the artifacts

### 2.2 `interaction_trace.json`
`interaction_trace.json` is the authoritative structured record of **what happened during the run**.

It exists to support:
- evaluation when transcripts are not persisted
- justification of flags and escalation decisions
- continuity review
- later dataset curation
- replay-style debugging of structured behavior

---

## 3. Recommended artifact location

Recommended layout:

```text
{case_id}/
  case_file.json
  case_metadata.json
  personas/
    participant_A.json
    participant_B.json
  sessions/
    {session_id}/
      run_meta.json
      interaction_trace.json
      positions.json
      facts_snapshot.json
      flags.json
      missing_info.json
      summary.txt
      evaluation.json                (after evaluation)
      expert_review.json             (optional)
      briefs/
        case_intake_brief.json
        case_intake_brief.txt
        early_dynamics_brief.json
        early_dynamics_brief.txt
        risk_alert_brief.json
        risk_alert_brief.txt
````

---

## 4. Contract: `run_meta.json`

## 4.1 Purpose

`run_meta.json` records the configuration, provenance, and reproducibility context for a single run.

## 4.2 Minimum required fields

```json
{
  "schema_version": "string",
  "case_id": "string",
  "session_id": "string",
  "timestamp": "ISO-8601 datetime string",
  "session_type": "string",
  "policy_profile": "string",
  "runtime": {
    "environment": "string",
    "code_version": "string",
    "git_commit_hash": "string or null"
  },
  "model_config": {
    "provider": "string",
    "model_name": "string",
    "temperature": "number or null",
    "other_decoding_settings": "object"
  },
  "prompting": {
    "prompt_version": "string",
    "prompt_ids": ["string"]
  },
  "randomization": {
    "seed": "integer or null",
    "determinism_note": "string or null"
  },
  "case_context": {
    "plugin_type": "string",
    "participant_context": ["string"]
  }
}
```

## 4.3 Field definitions

### Top-level fields

* `schema_version`
  Version of the artifact contract used to write this file.

* `case_id`
  Stable identifier for the case definition.

* `session_id`
  Stable identifier for the session run.

* `timestamp`
  Timestamp for the run creation event.

* `session_type`
  Short label for the session category, such as:

  * `offline_synthetic_eval`
  * `benchmark_replay`
  * `debug_run`

* `policy_profile`
  Active persistence/redaction profile, such as:

  * `dev_verbose`
  * `sim_minimal`
  * `redacted`

### `runtime`

* `environment`
  Runtime environment marker, such as:

  * `local`
  * `dev`
  * `staging_eval`

* `code_version`
  Human-readable version string for the codebase.

* `git_commit_hash`
  Commit hash if available.

### `model_config`

* `provider`
  Model provider name.

* `model_name`
  Exact model identifier used for the run.

* `temperature`
  Temperature if applicable.

* `other_decoding_settings`
  Any additional decode settings relevant to replay or comparison.

### `prompting`

* `prompt_version`
  Single version label for the active prompt bundle.

* `prompt_ids`
  Array of prompt, template, or instruction identifiers used in the run.

### `randomization`

* `seed`
  Seed used for system-controlled randomization, if any.

* `determinism_note`
  Free-text note describing replay expectations or nondeterministic elements.

### `case_context`

* `plugin_type`
  Primary plugin/domain for the run, such as `divorce`.

* `participant_context`
  Labels for participants or perspectives represented in the session.

## 4.4 Required invariants

`run_meta.json` must be sufficient to answer:

* which case definition was used
* which model/configuration produced the behavior
* which prompt version was active
* which policy profile governed writes
* which code version generated the run

## 4.5 Example v0 instance

```json
{
  "schema_version": "run_meta.v0",
  "case_id": "DIV-BMK-0007",
  "session_id": "DIV-BMK-0007-S01",
  "timestamp": "2026-03-12T15:10:22Z",
  "session_type": "offline_synthetic_eval",
  "policy_profile": "sim_minimal",
  "runtime": {
    "environment": "local",
    "code_version": "0.1.0",
    "git_commit_hash": "abc123def456"
  },
  "model_config": {
    "provider": "openai",
    "model_name": "gpt-x",
    "temperature": 0.2,
    "other_decoding_settings": {
      "max_output_tokens": 1200
    }
  },
  "prompting": {
    "prompt_version": "mediation_prompt_bundle_v3",
    "prompt_ids": [
      "system_core_v3",
      "divorce_plugin_v1",
      "trace_writer_v1"
    ]
  },
  "randomization": {
    "seed": 42,
    "determinism_note": "Synthetic participant variation seeded; model output not guaranteed fully deterministic."
  },
  "case_context": {
    "plugin_type": "divorce",
    "participant_context": [
      "participant_A",
      "participant_B"
    ]
  }
}
```

---

## 5. Contract: `interaction_trace.json`

## 5.1 Purpose

`interaction_trace.json` is the minimum structured record of the session’s turn-by-turn development.

It is authoritative even when transcripts are not stored.

## 5.2 Top-level shape

```json
{
  "schema_version": "string",
  "case_id": "string",
  "session_id": "string",
  "policy_profile": "string",
  "trace_created_at": "ISO-8601 datetime string",
  "turns": [],
  "final_state_summary": {},
  "trace_notes": "string or null"
}
```

## 5.3 Minimum required top-level fields

* `schema_version`
* `case_id`
* `session_id`
* `policy_profile`
* `trace_created_at`
* `turns`

## 5.4 Turn contract

Each item in `turns` must include at least:

```json
{
  "turn_index": 0,
  "timestamp": "ISO-8601 datetime string",
  "role": "assistant or client",
  "phase": "info_gathering | interest_exploration | option_generation | agreement_building",
  "state_delta": {},
  "risk_check": {}
}
```

## 5.5 Field definitions for each turn

### `turn_index`

Zero-based or one-based index, but must be consistent within the trace.

### `timestamp`

Timestamp for when the turn was committed to the trace.

### `role`

Allowed v0 values:

* `assistant`
* `client`

Future versions may expand this to support evaluator or human mediator turns.

### `phase`

Allowed v0 values:

* `info_gathering`
* `interest_exploration`
* `option_generation`
* `agreement_building`

If a run uses narrower internal phases, they should be normalized into one of these values for trace portability.

### `state_delta`

Structured record of what changed during the turn.

Minimum supported contents:

```json
{
  "facts_added": [],
  "facts_revised": [],
  "positions_added_or_updated": [],
  "open_questions_added": [],
  "open_questions_resolved": [],
  "issue_map_updates": [],
  "option_state_updates": [],
  "escalation_state_updates": []
}
```

### `risk_check`

Structured record of safety and escalation-relevant observations for the turn.

Minimum supported contents:

```json
{
  "triggered": false,
  "signals": [],
  "severity": 1,
  "notes": "string"
}
```

Field meanings:

* `triggered`
  Whether any safety, escalation, or high-conflict threshold-relevant cue was triggered on this turn.

* `signals`
  List of short signal class labels, such as:

  * `power_imbalance_cue`
  * `coercion_concern`
  * `communication_breakdown`
  * `role_boundary_pressure`
  * `trust_breakdown`
  * `domain_complexity_warning`

* `severity`
  Integer severity scale from 1 to 5.

* `notes`
  Short rationale for the risk assessment.

## 5.6 Optional supported turn fields

The following are optional in v0 but recommended:

```json
{
  "message_summary": "string",
  "interaction_observations_delta": [],
  "candidate_escalation_category": "string or null",
  "candidate_escalation_mode": "string or null",
  "confidence_note": "string or null"
}
```

### `message_summary`

Short neutral summary of the turn’s content.

### `interaction_observations_delta`

Descriptive, non-clinical observations or references to observation objects.

### `candidate_escalation_category`

Candidate category label such as:

* `E1`
* `E2`
* `E3`
* `E4`
* `E5`
* `E6`

### `candidate_escalation_mode`

Candidate mode label such as:

* `M0`
* `M1`
* `M2`
* `M3`
* `M4`
* `M5`

These are not authoritative routing decisions in v0; they are traceable intermediate indicators.

### `confidence_note`

Short note about uncertainty or confidence in the turn interpretation.

## 5.7 Top-level optional fields

### `final_state_summary`

Recommended summary object for quick evaluator review.

Suggested contents:

```json
{
  "current_phase": "string",
  "issues_identified": [],
  "open_questions_remaining": [],
  "active_flags": [],
  "current_escalation_state": "string or null",
  "continuation_recommendation": "string or null"
}
```

### `trace_notes`

Free-text note about trace conditions, omissions, or policy-driven limitations.

## 5.8 Required invariants

`interaction_trace.json` must be sufficient to support:

* evaluation without transcript persistence
* justification of flags
* justification of escalation decisions
* continuity review
* later structured analysis

If transcript storage is disabled, the trace must still preserve enough state change and risk signal information for an evaluator to reconstruct the session’s important developments.

## 5.9 Example v0 instance

```json
{
  "schema_version": "interaction_trace.v0",
  "case_id": "DIV-BMK-0007",
  "session_id": "DIV-BMK-0007-S01",
  "policy_profile": "sim_minimal",
  "trace_created_at": "2026-03-12T15:28:10Z",
  "turns": [
    {
      "turn_index": 1,
      "timestamp": "2026-03-12T15:11:05Z",
      "role": "assistant",
      "phase": "info_gathering",
      "message_summary": "System explains role, boundaries, and opening process structure.",
      "state_delta": {
        "facts_added": [],
        "facts_revised": [],
        "positions_added_or_updated": [],
        "open_questions_added": ["primary parenting dispute", "housing transition"],
        "open_questions_resolved": [],
        "issue_map_updates": ["initialized issue clusters"],
        "option_state_updates": [],
        "escalation_state_updates": []
      },
      "risk_check": {
        "triggered": false,
        "signals": [],
        "severity": 1,
        "notes": "No threshold-relevant concern at opening."
      }
    },
    {
      "turn_index": 2,
      "timestamp": "2026-03-12T15:12:21Z",
      "role": "client",
      "phase": "info_gathering",
      "message_summary": "Participant reports pressure around temporary parenting schedule and last-minute threats.",
      "state_delta": {
        "facts_added": ["temporary parenting schedule dispute"],
        "facts_revised": [],
        "positions_added_or_updated": ["participant_A wants a fixed weekday schedule"],
        "open_questions_added": ["threat context", "prior schedule adherence"],
        "open_questions_resolved": [],
        "issue_map_updates": ["parenting_schedule cluster expanded"],
        "option_state_updates": [],
        "escalation_state_updates": ["monitoring trust and coercion signals"]
      },
      "risk_check": {
        "triggered": true,
        "signals": ["power_imbalance_cue", "trust_breakdown"],
        "severity": 3,
        "notes": "Possible coercive dynamics; continue with caution pending more evidence."
      },
      "candidate_escalation_category": "E1",
      "candidate_escalation_mode": "M1",
      "confidence_note": "Moderate confidence; insufficient evidence for handoff yet."
    }
  ],
  "final_state_summary": {
    "current_phase": "info_gathering",
    "issues_identified": ["parenting_schedule", "housing_transition"],
    "open_questions_remaining": ["threat context", "prior schedule adherence"],
    "active_flags": ["monitor_power_asymmetry"],
    "current_escalation_state": "caution",
    "continuation_recommendation": "continue_with_caution"
  },
  "trace_notes": null
}
```

---

## 6. Normalization rules

### 6.1 Authoritative-over-convenience rule

Structured fields are authoritative.
Narrative summaries are convenience aids and must not replace structured state.

### 6.2 Policy-profile rule

The active persistence profile may control whether transcript-like text is written, but it must not prevent the required structured trace from being written.

### 6.3 Minimal portability rule

Artifact fields should remain stable across benchmarks and plugins unless a strong reason exists to specialize them.

### 6.4 Extension rule

Future versions may add fields, but should avoid breaking the v0 minimum semantics.

---

## 7. Immediate follow-on contracts

After this document, the next artifacts to define are:

* `flags.json`
* `positions.json`
* `facts_snapshot.json`
* `missing_info.json`
* `summary.txt`
* continuity packet
* optional briefs

These should be designed to align with `interaction_trace.json` rather than duplicate it unnecessarily.

---

## 8. Readiness checklist impact

Completing and adopting this document should allow partial progress against:

### Section F. Artifact readiness

* source-of-truth artifacts defined
* trace semantics concrete

### Section G. Reproducibility and policy readiness

* required metadata fields drafted
* seed/version/profile handling partly stabilized

This document alone does not complete those sections, but it establishes the minimum contract anchor needed for the next steps.

---

## 9. Open questions

* Should `turn_index` be zero-based or one-based across all artifacts?
* Should `role` remain normalized to `assistant` and `client`, or expand earlier?
* Should `risk_check.signals` use a fixed controlled vocabulary in v1?
* Should `state_delta` entries be plain strings, typed objects, or both?
* Should `final_state_summary` become mandatory in v1?
* How tightly should `interaction_trace.json` align with future evaluator schemas?

```

This is the right first pass because it turns the most architecture-shaping spec language into something developers can actually build against.

The next checklist-driven step should be either:
- `CONTRACT-002-flags-positions-facts-missing-summary-v0.md`, or
- `plugin_interface_v0.md`

The stronger of the two is probably `plugin_interface_v0.md`, because it closes one of the biggest boundary gaps.
```
