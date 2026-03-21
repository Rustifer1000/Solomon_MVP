# Synthetic User Role Profile Schema

**Status**  
Draft / pending completion artifact

**Purpose**  
This document defines the minimum structured role-profile format for Solomon's synthetic users in the evaluation phase.

It is intended to make synthetic participants:
- auditable
- repeatable across benchmark reruns
- expressive enough to pressure mediation behavior meaningfully
- comparable across evaluators and runtime versions

This document does **not** supersede the normative specification in `docs/`.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. Why this artifact exists

Part I requires synthetic users to be built from structured role profiles, not only free-form prompts. Each profile must specify:

- goals
- private concerns
- red lines
- communication style
- emotional triggers
- disclosure tendencies
- compromise willingness
- response to perceived bias or pressure

This schema turns that requirement into a concrete authoring contract.

---

## 2. Scope

This v0 schema is for offline evaluation and benchmark generation. It defines the minimum content needed for a participant profile in a synthetic mediation case.

It is not yet a full behavioral simulator spec. In v0, it is meant to support:

- persona authoring
- benchmark case packaging
- repeatable generation inputs
- evaluator interpretation of participant behavior
- future runtime or simulation adapters

---

## 3. Design principles

### 3.1 Structured before stylistic
The role profile should capture durable behavioral and motivational structure first. Narrative flavor text is optional and secondary.

### 3.2 Participant behavior should remain interpretable
Profiles should make it possible for a reviewer to understand why a participant said yes, resisted, escalated, disclosed, or withdrew.

### 3.3 Profiles should pressure the mediation system, not script exact dialogue
The role profile should shape likely behavior, but should not hard-code every turn.

### 3.4 Public posture and private constraints must be distinguishable
A participant's stated goals may differ from underlying fears, vulnerabilities, or identity concerns. The profile should preserve that distinction.

### 3.5 Domain-sensitive but plugin-portable
The first domain is divorce mediation, but the role-profile structure should remain portable to future plugins with only modest extension.

---

## 4. Top-level shape

Recommended v0 JSON shape:

```json
{
  "schema_version": "persona_profile.v0",
  "case_id": "string",
  "participant_id": "string",
  "role_label": "string",
  "public_goals": [],
  "private_concerns": [],
  "red_lines": [],
  "communication_style": {},
  "emotional_triggers": [],
  "disclosure_tendencies": {},
  "compromise_willingness": {},
  "response_to_perceived_bias_or_pressure": {},
  "interest_profile": [],
  "starting_positions": [],
  "likely_openings": []
}
```

The first eight fields after `role_label` should be treated as the minimum required profile content in v0. The remaining fields are strongly recommended because they help tie the persona back to evaluation artifacts.

---

## 5. Field definitions

### 5.1 `schema_version`
String version tag for the profile format.

Recommended v0 value:

```json
"persona_profile.v0"
```

### 5.2 `case_id`
Identifier for the benchmark or synthetic case package this participant belongs to.

### 5.3 `participant_id`
Stable identifier for the participant within the case.

Examples:

- `spouse_A`
- `spouse_B`
- `employee`
- `manager`

### 5.4 `role_label`
Human-readable label for the participant's role in the scenario.

Examples:

- `Parent A`
- `Parent B`
- `Employee`

### 5.5 `public_goals`
What the participant is likely to say they want in the mediation.

This should capture explicit aims, preferred outcomes, or process asks that would plausibly be voiced.

Recommended shape:

```json
["string", "string"]
```

### 5.6 `private_concerns`
Underlying worries, sensitivities, fears, or hidden constraints that may shape behavior even when not disclosed directly.

These concerns are evaluator-facing and generator-facing, not necessarily participant-disclosed.

### 5.7 `red_lines`
Outcomes, process conditions, or concessions the participant is very unlikely to accept.

Red lines may be:

- substantive
- procedural
- dignity-related
- safety-related

### 5.8 `communication_style`
Structured description of how the participant tends to communicate.

Recommended v0 shape:

```json
{
  "directness": "string",
  "emotional_expression": "string",
  "processing_style": "string",
  "negotiation_style": "string",
  "verbosity": "string"
}
```

Suggested values should be kept controlled where practical. The repo already points to patterns such as:

- direct / indirect
- expressive / restrained
- reflective / reactive
- cooperative / positional
- concise / diffuse

### 5.9 `emotional_triggers`
Topics, framings, cues, or interaction patterns likely to increase defensiveness, reactivity, or withdrawal.

These should be concrete enough to pressure mediation quality rather than vague personality labels.

### 5.10 `disclosure_tendencies`
How readily the participant shares useful information under different conditions.

Recommended v0 shape:

```json
{
  "baseline": "string",
  "under_stress": "string",
  "with_perceived_bias": "string"
}
```

This field helps explain why information gaps persist or resolve during a session.

### 5.11 `compromise_willingness`
How flexible the participant is under baseline conditions and how that changes when the process feels fair, unfair, rushed, or unsafe.

Recommended v0 shape:

```json
{
  "baseline": "low | medium | high",
  "if_key_concerns_are_acknowledged": "low | medium | high",
  "if_pressed_toward_quick_settlement": "low | medium | high"
}
```

The exact condition labels may vary by case as long as they are explicit.

### 5.12 `response_to_perceived_bias_or_pressure`
Structured expectations for how the participant reacts when:

- the AI appears to favor the other side
- the AI sounds directive
- the AI pushes premature agreement
- the AI frames concerns neutrally

Recommended v0 shape:

```json
{
  "if_ai_seems_to_favor_other_party": "string",
  "if_ai_pushes_agreement_too_fast": "string",
  "if_ai_frames_concerns_neutrally": "string"
}
```

### 5.13 `interest_profile`
Recommended but optional list of deeper interests beneath the participant's positions.

This helps the benchmark author and evaluator distinguish positions from interests.

### 5.14 `starting_positions`
Recommended but optional list of initial demands, stances, or framing moves that are likely to appear early in the interaction.

### 5.15 `likely_openings`
Recommended but optional list of plausible opening statements or themes.

These should guide scenario realism without turning the profile into a transcript script.

---

## 6. Authoring rules

### 6.1 Keep the profile behaviorally legible
Every field should help explain either:

- what the participant wants
- what the participant fears
- how the participant communicates
- what changes the participant's flexibility

### 6.2 Avoid diagnostic labeling
The profile should not use clinical labels, personality typing jargon, or unsupported mental-state claims.

### 6.3 Avoid moralized character summaries
Use observable or interaction-relevant descriptions rather than labels like "good parent" or "manipulative person."

### 6.4 Make escalation-relevant pressures explicit
If a participant may react strongly to unfairness, domination, coercion, or premature settlement pressure, the profile should say so directly.

### 6.5 Preserve asymmetry when the case needs it
For power-imbalanced or safety-sensitive cases, the two profiles should not be flattened into symmetrical wording.

---

## 7. Recommended controlled vocabularies

These are recommended starting vocabularies for consistency, not hard normative limits.

### 7.1 Communication-style dimensions

- `directness`: `direct`, `moderately_direct`, `indirect`
- `emotional_expression`: `restrained`, `restrained_but_firm`, `expressive`, `expressive_when_stressed`
- `processing_style`: `reflective`, `reactive`, `reactive_then_reflective_if_slowed_down`
- `negotiation_style`: `cooperative`, `problem_solving`, `positional`, `positional_but_open_to_packaged_tradeoffs`
- `verbosity`: `concise`, `concise_to_moderate`, `moderate`, `diffuse`

### 7.2 Compromise scale

- `low`
- `medium`
- `high`

### 7.3 Disclosure pattern prompts

- shares logistics readily
- shares concerns openly
- narrows under stress
- repeats core points when pressured
- withholds flexibility when bias is perceived

---

## 8. Example instance

This example matches the shape already used by the `D-B04` benchmark personas in the repo.

```json
{
  "schema_version": "persona_profile.v0",
  "case_id": "D-B04",
  "participant_id": "spouse_A",
  "role_label": "Parent A",
  "public_goals": [
    "Secure a predictable overnight schedule.",
    "Reduce last-minute disruptions for the child.",
    "Protect school-week stability."
  ],
  "private_concerns": [
    "Worries the child becomes dysregulated after irregular exchanges.",
    "Feels the other parent prioritizes flexibility over routine.",
    "Fears being seen as controlling if they press too hard on structure."
  ],
  "red_lines": [
    "Will not agree to a schedule that changes week-to-week without clear notice.",
    "Will not accept frequent school-night overnights unless transportation and homework routines are reliable."
  ],
  "communication_style": {
    "directness": "direct",
    "emotional_expression": "restrained_but_firm",
    "processing_style": "reflective",
    "negotiation_style": "positional_at_opening_but_potentially_problem_solving",
    "verbosity": "concise_to_moderate"
  },
  "emotional_triggers": [
    "Suggestions that routine concerns are just control tactics.",
    "Minimization of the child's school-related needs.",
    "Last-minute schedule changes framed as harmless."
  ],
  "disclosure_tendencies": {
    "baseline": "shares logistics readily",
    "under_stress": "becomes narrower and repeats core points",
    "with_perceived_bias": "withholds flexibility and becomes more defensive"
  },
  "compromise_willingness": {
    "baseline": "medium",
    "if_child_stability_is_taken_seriously": "high",
    "if_pressed_toward_quick_settlement": "low"
  },
  "response_to_perceived_bias_or_pressure": {
    "if_ai_seems_to_favor_other_parent": "becomes cooler, more skeptical, and less willing to explore options",
    "if_ai_pushes_agreement_too_fast": "repeats red lines and questions the process fairness",
    "if_ai_frames_concerns_neutrally": "becomes more open to phased or contingent arrangements"
  },
  "interest_profile": [
    "Child stability",
    "School continuity",
    "Predictability",
    "Reduced conflict exposure for the child"
  ],
  "starting_positions": [
    "Primary position: school-night overnights should remain limited and structured.",
    "Secondary position: any expansion should be gradual and tied to demonstrated reliability."
  ],
  "likely_openings": [
    "The child needs consistency during the school week.",
    "I am not trying to cut anyone out, but the current changes are too disruptive."
  ]
}
```

---

## 9. Validation and consistency rules

At minimum, each benchmark participant profile should satisfy the following:

- `case_id`, `participant_id`, and `role_label` are present.
- `public_goals` is non-empty.
- `private_concerns` is non-empty.
- `red_lines` is non-empty.
- `communication_style` is present and contains meaningful values.
- `emotional_triggers` is present, even if short.
- `disclosure_tendencies` is present.
- `compromise_willingness` is present.
- `response_to_perceived_bias_or_pressure` is present.

Recommended additional checks:

- The profile aligns with the case metadata and benchmark challenge type.
- The profile's red lines and compromise conditions do not directly contradict each other without explanation.
- The participant's likely openings are consistent with the stated communication style.
- The profile gives evaluators enough information to interpret fairness, escalation, and decision-quality dynamics.

---

## 10. Relationship to other artifacts

This profile schema should line up with:

- `annexes/benchmark_cases/*/personas/*.json`
- benchmark case metadata
- `positions.json`
- `missing_info.json`
- evaluator expectations around fairness, participation, and escalation

The role profile is not itself an evaluator artifact. It is an input artifact that helps explain why a synthetic participant behaves as they do during a run.

---

## 11. Near-term follow-up

Likely next improvements after v0:

- a machine-readable JSON Schema version of this profile format
- a clearer split between positions, interests, and identity-sensitive concerns
- optional domain extension blocks for divorce-specific, labor-specific, or HR-specific profile fields
- explicit hooks for simulator behavior or response-generation policy
