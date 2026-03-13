Yes — that’s the best way to do it.

I can keep drafting the next markdown docs in sequence here while you place them in the repo. The next one should be:

`annexes/architecture_decisions/CONTRACT-002-plugin-interface-v0.md`

This is the right next artifact because the spec makes the core/plugin split central: the core owns domain-general mediation process behavior, while the plugin owns domain ontology, vocabulary, scenario patterns, red flags, feasibility checks, and domain-specific evaluation extensions . This doc helps close the readiness checklist around the core/plugin boundary and interface contracts.

````md
# CONTRACT-002: Plugin Interface v0

**Status**  
Draft / informative

**Purpose**  
This document defines the minimum plugin interface for Solomon’s first offline evaluation-phase implementation.

It is intended to make the core/plugin boundary concrete enough to support:
- runtime architecture design
- first-pass plugin implementation
- evaluator review
- benchmark design
- later schema formalization

This document does **not** supersede the normative specification.  
If there is any conflict between this document and the normative documents or schemas, the normative specification wins.

---

## 1. Scope

This v0 contract defines the minimum expectations for a Solomon plugin.

It is designed for the first evaluation-phase implementation and assumes:
- Solomon is a core-plus-plugin mediation system
- the core owns domain-general mediation process behavior
- the plugin owns domain structure, domain constraints, and domain-specific checks
- the first plugin is divorce mediation

This contract is intentionally narrow.  
It is designed to support one real plugin well before generalizing too early.

---

## 2. Plugin role summary

A plugin exists to make Solomon mediation-capable in a specific dispute domain without redefining Solomon’s core mediation role.

The plugin is responsible for supplying domain-specific structure and checks that the core should not invent on its own.

The plugin should provide:
- domain ontology / issue taxonomy
- domain vocabulary
- common scenario patterns
- domain red flags
- domain-specific feasibility checks for generated options
- plugin-specific evaluation extensions
- synthetic template families
- domain-specific handoff annotations

The plugin should not silently override the core’s commitments to:
- self-determination
- noncoercion
- procedural fairness
- role honesty
- escalation obligations

---

## 3. Design principles

### 3.1 Core owns process; plugin owns domain structure
The plugin should not take ownership of general mediation process behavior such as:
- session framing
- generic issue clarification methods
- generic interest elicitation methods
- generic communication management
- generic fairness safeguards
- generic handoff packet structure

### 3.2 Plugin extends; plugin does not replace
A plugin may enrich or qualify the core’s behavior, but it should not redefine Solomon into a different role such as:
- judge
- arbitrator
- therapist
- legal decision-maker
- one-sided strategic advisor

### 3.3 Plugin outputs must be inspectable
Plugin behavior must be representable in structured form so evaluators can determine:
- what the plugin contributed
- what warnings it raised
- what feasibility checks it applied
- what domain-specific concerns affected escalation or handoff

### 3.4 Plugin should be conservative where domain uncertainty matters
If the plugin cannot responsibly qualify a domain-sensitive move, it should emit uncertainty or warning signals rather than allow the system to overstate confidence.

---

## 4. What the plugin owns

The plugin owns domain-specific content and checks in six areas.

### 4.1 Domain structure
The plugin defines:
- issue taxonomy
- issue labels
- issue clusters
- known domain entities
- common domain relationships between issues

### 4.2 Domain language
The plugin defines:
- preferred vocabulary
- domain synonyms
- ambiguity-sensitive terms
- high-risk phrasing cues
- domain terminology normalization rules

### 4.3 Domain red flags
The plugin defines:
- domain-sensitive warning conditions
- hard triggers specific to the domain
- risk patterns requiring caution, narrowing, or escalation
- domain-specific concerns that affect legitimacy or safe continuation

### 4.4 Feasibility checks
The plugin defines:
- domain plausibility checks for candidate options
- incomplete-information warnings
- infeasibility signals
- sequencing concerns
- issue-coupling warnings

### 4.5 Domain-specific evaluation extensions
The plugin defines:
- additional evaluation criteria that matter in this domain
- domain-specific failure modes
- domain-sensitive scoring notes

### 4.6 Domain-specific handoff annotations
The plugin defines:
- handoff notes relevant to a human mediator or reviewer
- unresolved domain questions
- domain-specific caution flags
- plugin-local uncertainty notes

---

## 5. What the plugin does not own

The plugin does **not** own final authority over:
- Solomon’s general mediation role
- core process framing
- generic noncoercion rules
- generic self-determination safeguards
- generic escalation routing framework
- persistence policy
- artifact write policy
- run metadata structure
- evaluator workflow
- authoritative final state tracking

The plugin may contribute signals into these areas, but the platform/core remains the final authority unless explicitly specified otherwise.

---

## 6. v0 interface shape

A plugin should expose a structured interface with the following conceptual parts:

1. plugin metadata  
2. domain resources  
3. runtime qualification outputs  
4. escalation and handoff contributions  
5. evaluation extensions

This document describes these conceptually first.  
They may later be represented as JSON schema, code interfaces, or both.

---

## 7. Plugin metadata contract

Each plugin must provide minimum identifying metadata.

### 7.1 Required fields

```json
{
  "plugin_id": "string",
  "plugin_version": "string",
  "domain_name": "string",
  "status": "string",
  "description": "string"
}
````

### 7.2 Field meanings

* `plugin_id`
  Stable machine-readable plugin identifier.

* `plugin_version`
  Version string for the plugin definition.

* `domain_name`
  Human-readable domain label such as `divorce mediation`.

* `status`
  Plugin maturity label, such as:

  * `draft`
  * `evaluation_phase`
  * `stable_internal`

* `description`
  Short plain-language description of the plugin’s domain scope.

### 7.3 Optional recommended fields

```json
{
  "owners": ["string"],
  "supported_benchmark_families": ["string"],
  "notes": "string or null"
}
```

---

## 8. Domain resource contract

The plugin should provide structured domain resources that the runtime can inspect and apply.

### 8.1 Ontology / taxonomy

Required conceptual outputs:

* issue categories
* issue subcategories if used
* domain entities
* domain relationships
* issue-coupling hints

Suggested v0 shape:

```json
{
  "issue_taxonomy": [
    {
      "issue_id": "string",
      "label": "string",
      "description": "string",
      "related_issues": ["string"]
    }
  ]
}
```

### 8.2 Vocabulary resources

The plugin should provide domain vocabulary support.

Suggested v0 shape:

```json
{
  "vocabulary": {
    "preferred_terms": ["string"],
    "synonyms": [
      {
        "canonical": "string",
        "variants": ["string"]
      }
    ],
    "high_risk_terms": ["string"],
    "normalization_notes": ["string"]
  }
}
```

### 8.3 Scenario pattern resources

The plugin should identify common domain patterns that matter for synthetic generation and evaluator expectations.

Suggested v0 shape:

```json
{
  "scenario_patterns": [
    {
      "pattern_id": "string",
      "label": "string",
      "description": "string"
    }
  ]
}
```

---

## 9. Runtime qualification output contract

At runtime, the plugin should be able to contribute structured qualification outputs based on the current session state and candidate next moves.

### 9.1 Purpose

These outputs let the plugin:

* identify relevant issue structures
* surface domain warnings
* qualify domain fit
* highlight missing domain information
* support evaluator visibility

### 9.2 Suggested v0 output shape

```json
{
  "plugin_context": {
    "detected_issue_clusters": ["string"],
    "domain_entities_detected": ["string"],
    "relevant_patterns": ["string"]
  },
  "domain_warnings": [],
  "feasibility_checks": [],
  "missing_domain_information": [],
  "plugin_confidence": {},
  "handoff_annotations": []
}
```

---

## 10. Domain warning contract

The plugin should emit structured warnings when domain-specific concerns are present.

### 10.1 Warning types

A warning may represent:

* domain risk cue
* domain hard trigger
* sequencing concern
* domain ambiguity
* dependency/power concern
* feasibility risk
* process complication tied to the domain

### 10.2 Suggested v0 shape

```json
{
  "warning_id": "string",
  "warning_type": "string",
  "severity": 1,
  "title": "string",
  "note": "string",
  "hard_trigger": false,
  "recommended_action": "string or null"
}
```

### 10.3 Field meanings

* `warning_id`
  Stable or semi-stable identifier for the warning event.

* `warning_type`
  Controlled label such as:

  * `domain_risk`
  * `power_dependency_concern`
  * `feasibility_risk`
  * `information_gap`
  * `sequencing_risk`
  * `legal_process_timing_signal`

* `severity`
  Integer scale from 1 to 5.

* `title`
  Short label for human review.

* `note`
  Short explanation of the concern.

* `hard_trigger`
  Whether the warning should be treated as presumptively escalation-relevant.

* `recommended_action`
  Optional recommendation such as:

  * `continue_with_caution`
  * `narrow_scope`
  * `request_human_review`
  * `handoff`
  * `stop_and_redirect`

---

## 11. Feasibility check contract

The plugin should evaluate whether candidate options are domain-fit, incompletely specified, or domain-risky.

### 11.1 Purpose

Feasibility checks do **not** determine legal validity or impose a solution.
They exist to prevent the runtime from presenting domain-insensitive or misleading options as if they were straightforward.

### 11.2 Suggested v0 shape

```json
{
  "check_id": "string",
  "option_ref": "string or null",
  "status": "supported | uncertain | weak_fit | infeasible",
  "note": "string",
  "missing_information": ["string"],
  "related_issues": ["string"]
}
```

### 11.3 Interpretation

* `supported`
  No immediate domain-fit concern detected.
* `uncertain`
  More information is needed before the option can be treated as responsible.
* `weak_fit`
  The option is possible but poorly aligned with known domain conditions.
* `infeasible`
  The option should not be advanced without major qualification or human review.

---

## 12. Missing domain information contract

The plugin should be able to state what domain-specific information is missing.

Suggested v0 shape:

```json
{
  "missing_domain_information": [
    {
      "info_id": "string",
      "question": "string",
      "importance": "low | medium | high",
      "related_issues": ["string"]
    }
  ]
}
```

This output is especially important for:

* decision-quality escalation
* cautious continuation
* evaluator interpretation of incomplete option work

---

## 13. Plugin confidence contract

The plugin should expose its own confidence or uncertainty in a structured way.

### 13.1 Purpose

Plugin confidence is not the same as model confidence.
It reflects how well the plugin believes the current state supports responsible domain qualification.

### 13.2 Suggested v0 shape

```json
{
  "plugin_confidence": {
    "level": "high | medium | low",
    "note": "string",
    "reasons": ["string"]
  }
}
```

### 13.3 Example reasons

* insufficient domain facts
* multiple tightly coupled issues
* unresolved dependency concern
* ambiguous legal-process timing
* option space too unstable

Low plugin confidence should be escalation-relevant, but should not by itself silently force routing without platform-level review.

---

## 14. Handoff annotation contract

The plugin should contribute domain-specific handoff notes when human review or transfer is appropriate.

Suggested v0 shape:

```json
{
  "handoff_annotations": [
    {
      "annotation_id": "string",
      "title": "string",
      "note": "string",
      "priority": "low | medium | high",
      "related_issues": ["string"]
    }
  ]
}
```

Examples:

* unresolved parenting schedule dependency
* financial disclosure ambiguity
* potential coercive dynamic affecting negotiation posture
* legal deadline affecting realistic sequencing

---

## 15. Evaluation extension contract

The plugin should contribute domain-specific evaluation extensions without redefining core mediation quality.

### 15.1 Purpose

These extensions help evaluators assess domain-sensitive behavior that the core score alone would miss.

### 15.2 Suggested v0 shape

```json
{
  "evaluation_extensions": [
    {
      "extension_id": "string",
      "label": "string",
      "description": "string",
      "suggested_review_questions": ["string"]
    }
  ]
}
```

For divorce, example extension areas may include:

* parenting-sensitive handling
* dependency-aware process protection
* sequencing of emotionally and logistically entangled issues
* avoidance of coercive settlement pressure in dependent relationships

---

## 16. Divorce plugin v0 expectations

For the first plugin, the contract should be instantiated at minimum across these issue areas:

* parenting issues
* child-related scheduling
* support issues
* property and debt issues
* housing transition issues
* dependency and power concerns
* legal-process timing signals

The divorce plugin should also be able to emit domain warnings related to:

* parenting-sensitive imbalance
* dependency-sensitive bargaining pressure
* schedule infeasibility
* issue entanglement across parenting, housing, and finances
* legal timing pressure that may reduce safe autonomous handling

---

## 17. Non-substitution guardrails

The plugin must not:

* redefine good mediation as mere agreement completion
* pressure settlement beyond core noncoercion limits
* silently override fairness or self-determination protections
* imply legal authority it does not have
* convert Solomon into domain-specific one-sided assistance

If the plugin introduces domain pressure that conflicts with the core role, the core role wins.

---

## 18. Platform integration expectations

The platform/core should be able to do the following with plugin outputs:

* read issue taxonomy and vocabulary resources
* receive structured warnings
* receive feasibility checks
* record missing domain information
* incorporate plugin confidence into escalation analysis
* include handoff annotations in continuity artifacts
* pass plugin evaluation extensions to evaluators

The platform should remain the authoritative owner of:

* final artifact writing
* final escalation routing
* persistence policy enforcement
* final session state

---

## 19. Example conceptual instance

```json
{
  "plugin_id": "divorce_v0",
  "plugin_version": "0.1.0",
  "domain_name": "divorce mediation",
  "status": "evaluation_phase",
  "description": "Initial domain plugin for Solomon MVP evaluation-phase testing.",
  "issue_taxonomy": [
    {
      "issue_id": "parenting_schedule",
      "label": "Parenting schedule",
      "description": "Scheduling and time-allocation issues involving children.",
      "related_issues": ["housing_transition", "school_decisions"]
    },
    {
      "issue_id": "support",
      "label": "Support",
      "description": "Financial support and payment-related concerns.",
      "related_issues": ["housing_transition", "financial_disclosure"]
    }
  ],
  "runtime_output_example": {
    "plugin_context": {
      "detected_issue_clusters": ["parenting_schedule", "housing_transition"],
      "domain_entities_detected": ["minor_children"],
      "relevant_patterns": ["high_conflict_schedule_dispute"]
    },
    "domain_warnings": [
      {
        "warning_id": "warn-001",
        "warning_type": "power_dependency_concern",
        "severity": 4,
        "title": "Potential dependency-sensitive pressure",
        "note": "Housing instability may be distorting negotiation freedom.",
        "hard_trigger": false,
        "recommended_action": "request_human_review"
      }
    ],
    "feasibility_checks": [
      {
        "check_id": "check-001",
        "option_ref": "option-A",
        "status": "uncertain",
        "note": "Proposed schedule change may not be responsibly assessed without school logistics.",
        "missing_information": ["school commute details"],
        "related_issues": ["parenting_schedule"]
      }
    ],
    "missing_domain_information": [
      {
        "info_id": "mdi-001",
        "question": "What school and transportation constraints affect weekday exchanges?",
        "importance": "high",
        "related_issues": ["parenting_schedule"]
      }
    ],
    "plugin_confidence": {
      "level": "medium",
      "note": "Core issue structure is clear but key logistics remain unresolved.",
      "reasons": ["missing school logistics", "housing instability"]
    },
    "handoff_annotations": [
      {
        "annotation_id": "ha-001",
        "title": "Review bargaining pressure around housing dependence",
        "note": "Human review may be needed if housing leverage is shaping consent.",
        "priority": "high",
        "related_issues": ["housing_transition", "support"]
      }
    ]
  }
}
```

---

## 20. Readiness checklist impact

Completing and adopting this document should allow partial progress against:

### Section B. Boundary readiness

* core / plugin boundary is written down
* plugin input/output responsibilities are drafted
* extension points are clearer
* non-substitution guardrails are explicit

### Section H. Development workflow readiness

* failures can be more cleanly attributed to plugin vs core vs integration

This document does not complete those sections by itself, but it closes one of the largest pre-architecture gaps.

---

## 21. Open questions

* Should plugin resources live as static files, code-defined objects, or both?
* Should issue taxonomy relationships be flat in v0 or typed?
* Should warning types use a controlled vocabulary in v1?
* Should plugin confidence be a simple level only, or include subdimensions?
* How tightly should plugin handoff annotations map to the continuity packet contract?
* Should feasibility checks remain qualitative in v0 or include confidence/severity scores?

---





```

```
