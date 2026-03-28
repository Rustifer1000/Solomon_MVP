# CONTRACT-016: Domain Analysis Artifact — v0

**Stage:** 3
**Status:** Active
**Date:** 2026-03-28
**Supersedes:** None (new artifact)
**Related:** CONTRACT-014 (reasoning trace), CONTRACT-015 (party state), ROADMAP-037

---

## 1. Purpose

This contract defines the `domain_analysis` artifact produced by the Stage 3 domain reasoner. It specifies:

- The artifact schema and field semantics
- The derivation logic (what the domain reasoner takes as input and how it produces output)
- The safety veto rule (when party state signals override domain feasibility)
- Which policy profiles emit the artifact
- How the artifact integrates with the existing five-step prompt

The `domain_analysis` artifact replaces the self-generated `domain_analysis` block in the lm_runtime five-step reasoning trace. Instead of the main model performing domain analysis as one of five simultaneous tasks, a dedicated domain reasoning call produces this output as a structured prior before the main model runs.

---

## 2. Motivation

**Observed failure mode (diagnostic finding across D-B04, D-B07, D-B11):**

The model consistently generates plausible candidate options but qualifies none of them. `option_readiness` is held at `blocked` or `deferred` even in bounded-package cases where parties have articulated clear interests and the domain constraints are knowable. D-B07-S02 T5: 6 candidate options, 0 qualified, parties reached agreement_building by T6 without the model releasing any options.

**Root cause:** Option qualification requires a domain feasibility judgment ("is this option viable given what we know about this couple's situation?") that is structurally difficult to make when the same inference pass is simultaneously handling perception, safety assessment, and response synthesis. The model defaults to deferral when uncertain — which is appropriate safety behaviour but excessive in bounded-package contexts.

**Stage 3 fix:** A dedicated domain reasoning call makes the feasibility judgment before the main pass runs. The main model receives a pre-qualified option set rather than having to produce one.

---

## 3. Artifact Schema

```
domain_analysis.v0 {
  schema_version: "domain_analysis.v0"
  case_id: string
  session_id: string
  turn_index: int                          // the turn this analysis is for
  generated_at: ISO 8601 timestamp
  source: "domain_reasoner_v0"

  option_readiness: "ready" | "deferred" | "blocked"
  readiness_rationale: string              // why this determination was made
  safety_veto_applied: bool                // true if party_state signals overrode domain feasibility
  safety_veto_reason: string | null        // which signal triggered the veto

  qualified_candidates: [
    {
      option_label: string                 // short name for the option
      option_description: string           // what it proposes
      feasibility_rationale: string        // why it's viable now
      confidence: "low" | "moderate" | "high"
      conditions: [string]                 // any conditions that must hold for viability
    }
  ]

  blocking_constraints: [
    {
      constraint: string                   // what is blocking
      severity: "minor" | "moderate" | "critical"
      what_would_resolve_it: string        // what needs to happen
    }
  ]

  material_gaps: [
    {
      gap: string                          // what is unknown
      importance: "low" | "moderate" | "high"
      what_it_blocks: string               // which options or readiness determination it affects
    }
  ]

  domain_confidence: "low" | "moderate" | "high"
  domain_notes: string                     // practitioner-level read of the current session state
}
```

---

## 4. Field Semantics

### `option_readiness`

The domain reasoner's determination of whether option work can proceed:

- `ready` — domain constraints are understood; at least one option is qualified; presenting options to parties is appropriate now.
- `deferred` — domain constraints are understood but material gaps prevent responsible qualification; option work is appropriate in the next turn or session once gaps are addressed.
- `blocked` — a safety signal, participation barrier, or fundamental information absence prevents option work. Do not advance to option presentation.

**Precedence rule:** If `safety_veto_applied` is `true`, `option_readiness` must be `blocked` regardless of domain feasibility. Safety signals in `party_state.json` are a hard veto on option release.

### `qualified_candidates`

Options the domain reasoner has assessed as feasible given the current session state. This list may be empty even when `option_readiness=ready` if the domain reasoner determines that no pre-specified options fit and the mediator should elicit options from the parties instead.

When `option_readiness` is `deferred` or `blocked`, `qualified_candidates` must be empty.

### `blocking_constraints`

Specific constraints that prevent option release. Each entry includes what would resolve it — this is used by the main model's Step 2 (domain analysis) to inform the facilitation move (what to elicit next).

### `safety_veto_applied`

True when signals in `party_state.json` cause `option_readiness` to be held at `blocked` despite domain feasibility. Specifically:

The domain reasoner applies the veto when `party_state.json` shows any of:
- Active risk signals for either party that are unresolved and of sufficient severity
- `relational_posture` indicating coercion, withdrawal, or participation incapacity
- Information asymmetry that has not been acknowledged or addressed by the party who holds the information
- Conflict avoidance pattern in a party who has not yet been given space to assert their own interests

The veto is not automatically applied for all risk signals — minor signals (e.g., "rehearsed grievance language") do not block option work. The domain reasoner applies judgment about whether the signal pattern indicates that proceeding to option presentation would be unsafe for one of the parties.

### `domain_confidence`

The domain reasoner's confidence in its own assessment:

- `low` — early in session; insufficient party input; domain constraints speculative.
- `moderate` — some domain-relevant information available; assessment grounded but incomplete.
- `high` — domain constraints clearly understood; party interests sufficiently surfaced; assessment is well-grounded.

---

## 5. Derivation Logic

### Inputs to the domain reasoner

```
{
  session_state: {
    case_id, session_id, turn_index,
    current_phase, escalation_mode, escalation_category,
    positions,         // current party positions
    missing_info,      // open information gaps
    facts_snapshot     // accepted facts
  },
  party_state: {       // from party_state.json, prior turns only
    party_a: { current_emotional_state, accumulated_interests, risk_signal_history, relational_posture_progression },
    party_b: { same },
    cross_party: { current_relational_dynamic, relational_dynamic_arc }
  },
  plugin_assessment: { // from existing plugin pipeline
    plugin_confidence, option_posture, active_flag_types, issue_families
  },
  session_history: [   // last 6 turns (same as main prompt)
    { turn_index, role, message_summary, phase }
  ]
}
```

### Domain reasoner system prompt (scope)

The domain reasoner is prompted as a **domain practitioner**, not as a mediator. Its task is:
1. Read the session state and party state
2. Determine whether option work is appropriate now
3. If yes, identify which options from the known option space for this domain are viable given current information
4. If no, identify what specifically is blocking — with enough precision that the mediator knows what to elicit next

The domain reasoner does **not**:
- Generate response text
- Assess party psychology (that's the perception layer's job)
- Make escalation decisions (that's the safety layer's job)
- Know the full five-step sequence — it is a single-purpose tool

### Output contract

The domain reasoner returns a JSON object matching the schema above. The main `lm_engine.py` call then injects this as `pre_computed_domain_analysis` into `build_turn_prompt()`, which renders it as the `=== DOMAIN ANALYSIS (pre-computed) ===` section in the user message — replacing the current `=== PLUGIN ASSESSMENT ===` section (or augmenting it when domain reasoning is unavailable).

---

## 6. Integration with Five-Step Prompt

When `pre_computed_domain_analysis` is available, the user message rendered by `prompt_builder.py` changes:

**Before Stage 3:**
```
=== PLUGIN ASSESSMENT ===
Plugin confidence: moderate
Option posture: conditional
Active flag types: ...
```

**After Stage 3:**
```
=== DOMAIN ANALYSIS (pre-computed by domain reasoner) ===
Option readiness: ready
Readiness rationale: Both parties have articulated clear process interests...
Qualified candidates (2):
  - Tiered notice requirement: feasible given stated interests...
  - Receipt standard with substitute provision: feasible...
Blocking constraints: none
Domain confidence: high

INSTRUCTION: Your Step 2 (Domain Analysis) should confirm, extend, or
challenge this pre-computed assessment based on the session history. Do
not simply repeat it — add any domain observations the reasoner may have
missed. Your Step 3 (Option Scan) should draw from qualified_candidates
above, and may add candidates the reasoner did not identify.
```

The main model's five-step reasoning is not bypassed — it remains intact. The domain reasoner provides a prior, not a final answer. The main model can challenge or extend the pre-computed assessment. This maintains evaluability of the model's reasoning chain while removing the qualification-under-uncertainty bottleneck.

---

## 7. Safety Veto Rule — Design Rationale

The safety veto is the most critical design element in this contract. Without it, Stage 3 introduces a regression risk: the domain reasoner could push `option_readiness` to `ready` in sessions where the party state warrants caution — for example, a D-B11-class case where Party A has a conflict_avoidance pattern and Party B holds information asymmetry as leverage. Presenting options in that session before the asymmetry is resolved would be unsafe, regardless of domain feasibility.

The veto resolves this by making `party_state.json` a gate on option release. The domain reasoner reads the party state before making any `option_readiness` determination. If the party state shows signals that indicate a party cannot safely participate in option evaluation, the veto applies regardless of whether the options themselves are domain-feasible.

This is the correct separation: domain feasibility (what options are viable) is separate from participation safety (whether presenting options now is appropriate). The domain reasoner handles the first; party state handles the second.

---

## 8. Policy Profile Emission

| Profile | `domain_analysis.json` emitted | Notes |
|---|---|---|
| `dev_verbose` | yes | Full domain_analysis artifact written to session dir |
| `eval_support` | yes | Full domain_analysis artifact written to session dir |
| `sim_minimal` | no | Domain reasoner not called; existing plugin assessment used |
| `redacted` | no | Domain reasoning not emitted |

The domain reasoner is only called for `lm_runtime` sessions. `runtime` and `reference` sessions use the existing deterministic plugin pipeline.

---

## 9. Invariants

- `option_readiness == "blocked"` whenever `safety_veto_applied == true`. No exceptions.
- `qualified_candidates` is empty whenever `option_readiness != "ready"`.
- `safety_veto_reason` is non-null whenever `safety_veto_applied == true`.
- `domain_confidence` is `"low"` on turn 1 (no party input yet).
- `schema_version` is always `"domain_analysis.v0"`.
- `source` is always `"domain_reasoner_v0"` for Stage 3 output.

---

## 10. Relationship to Existing Contracts

| Contract | Relationship |
|---|---|
| CONTRACT-014 (reasoning trace) | The main model's per-turn `reasoning_trace.domain_analysis` block is now informed by this artifact. The reasoning trace field is not removed — it still captures the main model's Step 2 output. The domain reasoner output is a separate upstream artifact. |
| CONTRACT-015 (party state) | `party_state.json` is an input to the domain reasoner, not an output. The veto rule reads from it. |
| ARCH-007 Stage 3 | This contract defines the interface that Stage 3 implements. |
| ARCH-007 Stage 4 | Stage 4's option pool artifact extends `qualified_candidates` into a full brainstorming pass. The `option_label` and `option_description` fields in this contract are designed to be forward-compatible with the Stage 4 option pool schema. |
