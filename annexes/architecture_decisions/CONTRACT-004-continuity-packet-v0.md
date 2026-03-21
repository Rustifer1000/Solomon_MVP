# CONTRACT-004: Continuity Packet v0

**Status**  
Draft / informative

**Purpose**  
This document defines the minimum continuity packet contract for Solomon's first offline evaluation-phase implementation.

It is intended to make review, co-handling, and handoff transitions:

- structured
- evaluator-visible
- domain-qualified
- usable by a human mediator or reviewer

This document does **not** supersede the normative specification in `docs/` or the runtime artifact contracts.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. Why this artifact exists

Part I requires that when Solomon chooses `M2` through `M5`, it produces a continuity packet containing at least:

- case ID
- plugin type
- escalation category
- threshold band
- concise rationale
- issue map
- identified interests / concerns
- unresolved questions
- risk flags
- interventions already attempted
- current option-generation state
- confidence / uncertainty notes
- recommended next human role

This contract turns that requirement into a concrete v0 packet shape.

---

## 2. Continuity packet role

The continuity packet is not merely a summary. It is the minimum structured bridge between:

- autonomous handling
- human review in the loop
- co-handling
- full handoff
- stop-and-redirect decisions

It should let a human quickly understand:

- what happened
- why Solomon changed posture
- what remains unresolved
- what the human should look at next

---

## 3. Top-level shape

Recommended v0 JSON shape:

```json
{
  "schema_version": "continuity_packet.v0",
  "case_id": "string",
  "session_id": "string",
  "plugin": "string",
  "escalation": {},
  "current_state": {},
  "human_handoff_guidance": {},
  "artifact_links": {},
  "packet_notes": "string or null"
}
```

---

## 4. Required sections

### 4.1 `escalation`
Must include:

- authoritative category
- threshold band
- selected mode
- hard-trigger status
- concise rationale

Suggested shape:

```json
{
  "category": "E1 | E2 | E3 | E4 | E5 | E6 | none",
  "threshold_band": "T0 | T1 | T2 | T3 | T4",
  "selected_mode": "M2 | M3 | M4 | M5",
  "hard_trigger_present": false,
  "short_rationale": "string"
}
```

### 4.2 `current_state`
Must include enough structured state for a human to continue responsibly.

Suggested shape:

```json
{
  "issue_map": ["string"],
  "identified_interests_and_concerns": ["string"],
  "unresolved_questions": ["string"],
  "risk_flags": ["string"],
  "interventions_already_attempted": ["string"],
  "option_generation_state": "string",
  "confidence_and_uncertainty_notes": ["string"]
}
```

### 4.3 `human_handoff_guidance`
Must indicate what kind of human involvement is being requested.

Suggested shape:

```json
{
  "recommended_next_human_role": "reviewer | co_handler | mediator_takeover | redirect_receiver",
  "priority": "low | medium | high",
  "recommended_next_step": "string",
  "plugin_annotations": ["string"]
}
```

### 4.4 `artifact_links`
Should point to the main supporting evidence.

These links should point to the authoritative artifacts defined in `CONTRACT-001` and `CONTRACT-003`. Plugin-local annotations should remain additive and must not replace the core packet structure.

Suggested shape:

```json
{
  "interaction_trace": "string",
  "flags": "string",
  "summary": "string",
  "missing_info": "string or null",
  "positions": "string or null",
  "facts_snapshot": "string or null",
  "risk_alert_brief": "string or null"
}
```

---

## 5. Field meanings

### `issue_map`
Compact list of the active issue clusters or issue IDs the human should orient to first.

### `identified_interests_and_concerns`
High-value participant motivations, constraints, fears, or process concerns already surfaced.

### `unresolved_questions`
Questions that materially limit safe or legitimate progress.

### `risk_flags`
Compact list of current flags that matter for handoff, ideally aligned with `flags.json`.

### `interventions_already_attempted`
Short record of the main repair or management moves Solomon already tried.

### `option_generation_state`
Short description of whether option work is:

- not yet started
- exploratory
- narrowed
- blocked by missing information
- inappropriate to continue autonomously

### `confidence_and_uncertainty_notes`
Human-facing explanation of where Solomon or the plugin lacked confidence.

---

## 6. Invariants

The continuity packet should obey these rules:

- it must not contradict authoritative structured artifacts
- it must be concise enough for fast human uptake
- it must preserve why the selected mode was chosen
- it must include enough context to continue without re-reading the full run first
- plugin-specific annotations may enrich the packet but must not replace the core packet structure

---

## 7. When the packet is required

The packet should be required for:

- `M2` human review in the loop
- `M3` co-handling
- `M4` full handoff
- `M5` stop-and-redirect

It may optionally be written for serious `M1` cases, but that is not required in v0.

---

## 8. D-B04 reference example

Example compact instance:

```json
{
  "schema_version": "continuity_packet.v0",
  "case_id": "D-B04",
  "session_id": "D-B04-S01",
  "plugin": "divorce",
  "escalation": {
    "category": "E5",
    "threshold_band": "T2",
    "selected_mode": "M2",
    "hard_trigger_present": false,
    "short_rationale": "Important parenting-schedule option work remains under-specified because school logistics and exchange feasibility are unresolved."
  },
  "current_state": {
    "issue_map": ["parenting_schedule", "school_logistics", "communication_protocol"],
    "identified_interests_and_concerns": [
      "child stability during the school week",
      "meaningful parenting role",
      "fairness and predictability"
    ],
    "unresolved_questions": [
      "What school transportation constraints affect weekday exchanges?",
      "What reliability conditions would make phased schedule changes workable?"
    ],
    "risk_flags": ["insufficient_information", "decision_quality_risk"],
    "interventions_already_attempted": [
      "neutral reframing of parenting positions",
      "interest elicitation around stability and fairness",
      "early exploration of phased options"
    ],
    "option_generation_state": "exploratory but blocked by unresolved logistics",
    "confidence_and_uncertainty_notes": [
      "plugin qualification is limited until schedule logistics are clarified"
    ]
  },
  "human_handoff_guidance": {
    "recommended_next_human_role": "reviewer",
    "priority": "medium",
    "recommended_next_step": "Review whether bounded continued handling is appropriate after missing logistics are clarified.",
    "plugin_annotations": [
      "Parenting-sensitive schedule qualification remains incomplete."
    ]
  },
  "artifact_links": {
    "interaction_trace": "sessions/D-B04-S01/interaction_trace.json",
    "flags": "sessions/D-B04-S01/flags.json",
    "summary": "sessions/D-B04-S01/summary.txt",
    "missing_info": "sessions/D-B04-S01/missing_info.json",
    "positions": "sessions/D-B04-S01/positions.json",
    "facts_snapshot": "sessions/D-B04-S01/facts_snapshot.json",
    "risk_alert_brief": null
  },
  "packet_notes": null
}
```

---

## 9. Definition of done for v0

The continuity packet contract is sufficiently specified when:

- a developer can implement one packet shape without guessing the minimum fields
- evaluators can review handoff quality consistently
- plugin annotations have a defined place
- the packet is usable for `M2` through `M5`
