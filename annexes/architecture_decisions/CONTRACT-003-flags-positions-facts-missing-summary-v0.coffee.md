## 2)

```
# CONTRACT-003: Flags, Positions, Facts, Missing Info, and Summary v0

**Status**  
Draft / informative

**Purpose**  
This document defines the minimum v0 contracts for the remaining core runtime artifacts in Solomon’s first offline evaluation-phase implementation:

- `flags.json`
- `positions.json`
- `facts_snapshot.json`
- `missing_info.json`
- `summary.txt`

These artifacts complement `run_meta.json` and `interaction_trace.json` and help make the runtime evaluable, inspectable, and architecture-ready.

This document does **not** supersede the normative specification.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. Framing

The Solomon specification requires structured artifacts as the source of truth for offline evaluation.  
This contract defines the minimum shapes for the remaining required artifacts beyond `run_meta.json` and `interaction_trace.json`.

These artifacts should:
- support evaluator review
- support escalation analysis
- preserve separation between structured state and convenience narratives
- avoid forcing evaluators to rely on transcripts alone

---

## 2. Artifact overview

### `flags.json`
Authoritative list of active, cleared, and historical flags relevant to risk, escalation, process quality, or domain concerns.

### `positions.json`
Structured representation of participant positions, stated preferences, proposals, red lines, and position changes.

### `facts_snapshot.json`
Structured snapshot of facts the system is currently treating as known, disputed, uncertain, or incomplete.

### `missing_info.json`
Structured record of unresolved information gaps that materially limit responsible progress.

### `summary.txt`
Human-readable narrative summary for quick review.  
It is a convenience artifact and must not override structured artifacts.

---

## 3. Contract: `flags.json`

### 3.1 Purpose
`flags.json` records conditions that matter for:
- safety
- process quality
- domain risk
- escalation reasoning
- evaluator review

### 3.2 Top-level shape

```json
{
  "schema_version": "string",
  "case_id": "string",
  "session_id": "string",
  "active_flags": [],
  "cleared_flags": [],
  "flag_notes": "string or null"
}
3.3 Flag item shape
{
  "flag_id": "string",
  "flag_type": "string",
  "status": "active | cleared | historical",
  "severity": 1,
  "source": "model | plugin | platform | evaluator_seeded",
  "first_detected_turn": 1,
  "last_updated_turn": 1,
  "hard_trigger": false,
  "related_categories": ["E1", "E2"],
  "title": "string",
  "note": "string"
}
3.4 Minimum flag types in v0

Suggested controlled labels:

safety_concern

coercion_concern

power_imbalance

trust_breakdown

process_breakdown

domain_complexity

decision_quality_risk

role_boundary_pressure

plugin_low_confidence

insufficient_information

3.5 Invariants

flags.json is authoritative for currently recognized flags.

A flag may originate from model or plugin signals, but the platform owns authoritative status.

Hard-trigger status must be represented explicitly.

4. Contract: positions.json
4.1 Purpose

positions.json records what each participant appears to want, resist, propose, or conditionally accept.

4.2 Top-level shape
{
  "schema_version": "string",
  "case_id": "string",
  "session_id": "string",
  "participants": [],
  "position_notes": "string or null"
}
4.3 Participant item shape
{
  "participant_id": "string",
  "current_positions": [],
  "proposals": [],
  "red_lines": [],
  "soft_preferences": [],
  "open_to_discussion": [],
  "last_updated_turn": 1
}
4.4 Position item shape
{
  "position_id": "string",
  "issue_id": "string",
  "statement": "string",
  "status": "current | revised | withdrawn | unclear",
  "confidence": "high | medium | low",
  "source_turns": [1, 2]
}
4.5 Proposal item shape
{
  "proposal_id": "string",
  "issue_id": "string",
  "statement": "string",
  "status": "proposed | discussed | tentative | rejected | parked",
  "source_turns": [3]
}
4.6 Invariants

positions.json records participant-facing negotiation posture, not objective fact.

A position should be distinguishable from a fact claim.

Revisions should remain traceable.

5. Contract: facts_snapshot.json
5.1 Purpose

facts_snapshot.json records what the system currently treats as known, disputed, uncertain, or pending verification.

5.2 Top-level shape
{
  "schema_version": "string",
  "case_id": "string",
  "session_id": "string",
  "facts": [],
  "facts_notes": "string or null"
}
5.3 Fact item shape
{
  "fact_id": "string",
  "category": "string",
  "statement": "string",
  "status": "accepted | disputed | uncertain | incomplete",
  "source_turns": [1, 2],
  "related_issues": ["string"],
  "note": "string or null"
}
5.4 Suggested categories in v0

family_structure

parenting_schedule

housing

finances

support

property

debt

timeline

communication_history

safety_or_power_context

5.5 Invariants

Facts must be distinguishable from positions.

Disputed or uncertain facts must not be silently promoted to accepted.

The artifact should support evaluator review of decision-quality and escalation reasoning.

6. Contract: missing_info.json
6.1 Purpose

missing_info.json records unresolved information gaps that materially constrain safe or responsible progress.

6.2 Top-level shape
{
  "schema_version": "string",
  "case_id": "string",
  "session_id": "string",
  "missing_items": [],
  "missing_info_notes": "string or null"
}
6.3 Missing-item shape
{
  "missing_id": "string",
  "question": "string",
  "importance": "low | medium | high",
  "reason_type": "fact_gap | feasibility_gap | risk_gap | process_gap | domain_gap",
  "related_issues": ["string"],
  "first_identified_turn": 1,
  "status": "open | partially_resolved | resolved",
  "note": "string or null"
}
6.4 Invariants

Missing information should be explicit when it affects feasibility, fairness, or escalation.

The platform should be able to relate missing information to E4 and E5 escalation logic when appropriate.

7. Contract: summary.txt
7.1 Purpose

summary.txt is a convenience artifact for humans.

It should provide a concise narrative overview of:

what the session covered

what issues were identified

where the parties appear to stand

what risks or flags are active

whether escalation/caution is relevant

what remains unresolved

7.2 Minimum structure

Recommended headings:

Session Summary
Issues Identified
Participant Positions
Facts and Uncertainties
Active Flags / Concerns
Missing Information
Current Escalation Posture
Recommended Next Step
7.3 Invariants

summary.txt must not override structured artifacts.

If a conflict exists between summary.txt and structured artifacts, the structured artifacts win.

The summary should be readable by evaluators without requiring transcript access.

8. Cross-artifact consistency rules
8.1 Positions vs facts

positions.json records what participants want or claim.

facts_snapshot.json records what the system currently treats as factual state and with what confidence.

8.2 Flags vs missing info

flags.json records concerns or active conditions.

missing_info.json records unresolved information gaps.

A missing item may support a flag, but the two artifacts should remain distinct.

8.3 Structured vs narrative

Structured artifacts are authoritative.

summary.txt is a convenience layer.

8.4 Turn trace linkage

These artifacts should be traceable back to:

interaction_trace.json

source turns where possible

9. Example compact instances
9.1 flags.json
{
  "schema_version": "flags.v0",
  "case_id": "DIV-BMK-0007",
  "session_id": "DIV-BMK-0007-S01",
  "active_flags": [
    {
      "flag_id": "flag-001",
      "flag_type": "power_imbalance",
      "status": "active",
      "severity": 3,
      "source": "plugin",
      "first_detected_turn": 2,
      "last_updated_turn": 5,
      "hard_trigger": false,
      "related_categories": ["E1", "E3"],
      "title": "Potential bargaining pressure",
      "note": "Housing dependence may be shaping negotiation freedom."
    }
  ],
  "cleared_flags": [],
  "flag_notes": null
}
9.2 positions.json
{
  "schema_version": "positions.v0",
  "case_id": "DIV-BMK-0007",
  "session_id": "DIV-BMK-0007-S01",
  "participants": [
    {
      "participant_id": "participant_A",
      "current_positions": [
        {
          "position_id": "pos-001",
          "issue_id": "parenting_schedule",
          "statement": "Wants fixed weekday schedule.",
          "status": "current",
          "confidence": "high",
          "source_turns": [2]
        }
      ],
      "proposals": [],
      "red_lines": [],
      "soft_preferences": [],
      "open_to_discussion": [],
      "last_updated_turn": 2
    }
  ],
  "position_notes": null
}
9.3 facts_snapshot.json
{
  "schema_version": "facts_snapshot.v0",
  "case_id": "DIV-BMK-0007",
  "session_id": "DIV-BMK-0007-S01",
  "facts": [
    {
      "fact_id": "fact-001",
      "category": "parenting_schedule",
      "statement": "There is an active dispute over temporary parenting schedule.",
      "status": "accepted",
      "source_turns": [2],
      "related_issues": ["parenting_schedule"],
      "note": null
    }
  ],
  "facts_notes": null
}
9.4 missing_info.json
{
  "schema_version": "missing_info.v0",
  "case_id": "DIV-BMK-0007",
  "session_id": "DIV-BMK-0007-S01",
  "missing_items": [
    {
      "missing_id": "miss-001",
      "question": "What school transportation constraints affect weekday exchanges?",
      "importance": "high",
      "reason_type": "feasibility_gap",
      "related_issues": ["parenting_schedule"],
      "first_identified_turn": 2,
      "status": "open",
      "note": null
    }
  ],
  "missing_info_notes": null
}
10. Readiness checklist impact

Completing and adopting this document should advance:

Section F. Artifact readiness

source-of-truth artifacts defined

required optional/adjacent artifacts clarified

trace-linked semantics closer to completion

Section G. Reproducibility and policy readiness

evaluable state representation improved

This document, together with CONTRACT-001, should give the architecture phase a usable artifact contract base.

11. Open questions

Should positions.json distinguish positions from interests in v1, or keep interests elsewhere?

Should facts and missing information use typed enums or remain lightly controlled in v0?

Should summary.txt be partly machine-generated and partly platform-authored?

Should flags.json maintain complete flag history or only active/cleared states in v0?