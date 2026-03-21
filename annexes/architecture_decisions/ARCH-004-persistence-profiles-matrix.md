# ARCH-004: Persistence Profiles Matrix

**Status**  
Draft / informative

**Purpose**  
This document defines the first implementation-facing persistence/profile matrix for Solomon's offline evaluation-phase runtime.

It is intended to make policy-controlled persistence concrete enough to support:

- runtime write decisions
- artifact visibility rules
- evaluator expectations
- future redaction hooks
- reproducibility planning

This document is aligned to the current contract pack and the `D-B04-S01` baseline.
It should also be read as inheriting the phase scope in `docs/03_MVP Eval Intent Lock.md`: preserve enough evaluator-reviewable evidence for bounded synthetic evaluation without pretending to define the full production data model.

---

## 1. Role of this matrix

This matrix turns the profile names already present in the specification into operational write rules.

It should answer:

- which artifacts are written under each profile
- which artifacts are forbidden
- which artifacts may be redacted
- which outputs are evaluator-visible
- which enforcement decisions belong to the platform

It is intentionally scoped to MVP evaluation evidence handling, not enterprise-wide retention design.

---

## 2. Profiles in scope

The first runtime should recognize three named profiles:

- `dev_verbose`
- `sim_minimal`
- `redacted`

These are policy profiles, not environment names.

---

## 3. Matrix

| Artifact / output | dev_verbose | sim_minimal | redacted | Notes |
|---|---|---|---|---|
| `run_meta.json` | Required | Required | Required | Always written for traceability |
| `interaction_trace.json` | Required | Required | Required | Always authoritative, even without transcript |
| `positions.json` | Required | Required | Required | Authoritative state artifact |
| `facts_snapshot.json` | Required | Required | Required | Authoritative state artifact |
| `flags.json` | Required | Required | Required | Authoritative risk/escalation artifact |
| `missing_info.json` | Required | Required | Required | Authoritative feasibility/decision-quality artifact |
| `summary.txt` | Required | Required | Required | Convenience artifact derived from state |
| `transcript.json` | Allowed | Forbidden | Optional redacted form only | Not required for the baseline architecture |
| raw prompt/message history | Optional if explicitly enabled | Forbidden | Forbidden | Keep outside default evaluator path |
| raw tool traces | Optional if explicitly enabled | Forbidden | Forbidden | Not part of baseline evaluator contract |
| continuity packet | Required when mode is `M2-M5` | Required when mode is `M2-M5` | Required when mode is `M2-M5`, redacted if needed | Conditional on escalation mode |
| risk alert brief | Required when policy trigger is met | Required when policy trigger is met | Required when policy trigger is met, redacted if needed | Trigger-driven |
| intake / early dynamics briefs | Allowed or required by workflow | Allowed or required by workflow | Allowed in redacted form | Depends on slice/workflow |
| `evaluation.json` | Allowed | Allowed | Allowed | Usually written after runtime completion |
| `expert_review.json` | Allowed | Allowed | Allowed | Evaluator-plane artifact, not live runtime output |

---

## 4. Enforcement rules

### 4.1 Platform ownership

Profile enforcement belongs to the platform/runtime layer, not to:

- the model
- plugin prompts
- evaluator tooling

This keeps persistence policy aligned with the intent lock's guardrail that structured artifacts and platform-owned policy remain authoritative.

### 4.2 Write-decision rule

For each artifact candidate, the platform should determine:

- required
- optional
- forbidden
- required in redacted form

before the write occurs.

### 4.3 Redaction rule

If an artifact is allowed only in redacted form:

- redaction must happen before persistence
- the artifact writer should receive already-approved content or a redaction instruction
- the runtime should not write the unredacted version first and clean it up later

---

## 5. D-B04-S01 baseline interpretation

For `D-B04-S01`, the profile assumptions are:

- policy profile: `sim_minimal`
- transcript not written
- structured artifacts required
- evaluation output allowed
- continuity packet not written because the run ends at `M1`

That makes `D-B04-S01` the baseline example of how `sim_minimal` should behave.

---

## 6. Artifact visibility classes

The first runtime should distinguish three visibility classes.

### 6.1 Evaluator-visible authoritative artifacts

These should be visible to evaluator tooling when present:

- `run_meta.json`
- `interaction_trace.json`
- `positions.json`
- `facts_snapshot.json`
- `flags.json`
- `missing_info.json`
- `summary.txt`
- continuity packet when required

### 6.2 Evaluator-visible optional artifacts

These may be visible when policy and workflow allow:

- redacted transcript
- intake brief
- early dynamics brief
- risk alert brief
- evaluation outputs
- expert review outputs

### 6.3 Runtime-only or restricted artifacts

These should be treated as restricted unless explicitly enabled:

- raw prompt history
- raw tool traces
- internal debugging payloads
- unredacted transcript content in restricted profiles

---

## 7. Recommended enforcement interface

The first implementation should expose a simple policy decision structure to the artifact writer.

Suggested conceptual shape:

```json
{
  "profile_name": "sim_minimal",
  "artifact_policy": {
    "run_meta.json": "required",
    "interaction_trace.json": "required",
    "positions.json": "required",
    "facts_snapshot.json": "required",
    "flags.json": "required",
    "missing_info.json": "required",
    "summary.txt": "required",
    "transcript.json": "forbidden",
    "continuity_packet": "conditional_required"
  }
}
```

This does not need to be the final schema, but the architecture should support an equivalent enforcement decision.

---

## 8. Redaction hook points

The runtime should support redaction hooks at least at the following points:

- before transcript persistence
- before brief persistence
- before continuity-packet persistence
- before evaluator-facing narrative excerpt persistence

For the first implementation, these hooks may be no-ops in `sim_minimal`, but the architecture should reserve the boundary now.

---

## 9. Reproducibility interaction

Persistence profiles interact with reproducibility in two ways:

### 9.1 Required reproducibility metadata

Regardless of profile, the runtime should preserve:

- case ID
- session ID
- timestamp
- model/provider configuration
- prompt version identifiers
- policy profile name
- code version
- seed if applicable

### 9.2 Reduced evidence profiles

Profiles like `sim_minimal` reduce raw evidence, so the runtime must compensate by ensuring that:

- `interaction_trace.json` is sufficiently rich
- state artifacts are complete enough for evaluator reconstruction
- summary text does not replace authoritative state

---

## 10. Minimal implementation guidance

Implement profile handling in this order:

1. define profile names as constants or config entries
2. define artifact-level required/optional/forbidden rules
3. enforce those rules in the artifact writer path
4. record the active profile in `run_meta.json`
5. add redaction hooks for future use

This is enough for the first runtime architecture pass.

---

## 11. Risks to avoid

- letting prompt text decide what gets persisted
- writing forbidden artifacts and deleting them later
- allowing summary text to compensate for missing trace content
- treating redaction as a manual post-process rather than a platform responsibility
- allowing profile behavior to vary implicitly by environment without being recorded

---

## 12. Immediate follow-on

After this matrix, the next useful follow-on would be:

- a concrete runtime policy config example
- artifact writer interface sketch
- redaction-hook responsibility table
