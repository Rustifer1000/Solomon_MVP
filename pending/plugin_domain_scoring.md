# Plugin-Domain Scoring

**Status**  
Draft / pending completion artifact

**Purpose**  
This document defines the first-pass plugin-domain score layer for Solomon's evaluation phase.

It is intended to answer:
- what should be scored about a domain plugin beyond the core mediation score
- how divorce-plugin performance should be evaluated without redefining core mediation quality
- how evaluators can distinguish plugin failure from core or integration failure

This document does **not** supersede the normative specification in `docs/` or the current schemas.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. Role of the plugin-domain score

Part I defines three evaluation targets:

- core-general mediation performance
- plugin-domain performance
- core/plugin integration quality

The plugin-domain score exists to measure the second of those three targets.

It should answer:

- Did the plugin provide the right domain structure?
- Did it surface the right domain warnings?
- Did it qualify options responsibly?
- Did it contribute the right domain-sensitive caution, feasibility, and handoff context?

It should **not** answer:

- whether Solomon generally mediated well across all domains
- whether the platform preserved plugin signals correctly
- whether the final artifact pipeline was coherent end-to-end

Those belong to the core and integration layers.

---

## 2. Plugin scoring principle

Score the plugin on how well it supports responsible domain-specific mediation in the active benchmark or case.

For v0, the plugin-domain score should focus on whether the plugin:

- adds usable domain structure
- supplies domain-relevant warnings
- qualifies feasibility responsibly
- identifies domain-specific missing information
- supports domain-sensitive escalation or handoff
- extends evaluation in the right places

The plugin should be judged as a **qualifying layer**, not as a substitute mediator.

---

## 3. Scope for the first plugin

The first domain plugin is divorce mediation.

The divorce plugin is expected to contribute at least in the following areas:

- parenting issues
- child-related scheduling issues
- support issues
- property and debt issues
- housing transition issues
- dependency and power concerns
- legal-process timing signals

The v0 plugin-domain score should therefore be written around divorce-specific evaluation needs while staying structurally portable to later domains.

---

## 4. Plugin-domain scoring families

The recommended first-pass plugin-domain score uses six families.

### P1. Domain issue structuring
How well the plugin identifies and organizes the active domain issue map.

Focus on:

- whether issue categories match the case
- whether issue coupling is recognized
- whether domain terminology is normalized helpfully
- whether the plugin avoids flattening materially distinct issue clusters

### P2. Domain warning and red-flag quality
How well the plugin surfaces domain-sensitive warnings, hard triggers, and caution conditions.

Focus on:

- whether the plugin notices relevant domain risks
- whether warning severity is proportionate
- whether hard triggers are surfaced when appropriate
- whether the warnings are specific enough to support evaluator review

### P3. Feasibility and qualification quality
How well the plugin qualifies candidate options or discussion moves for domain fit.

Focus on:

- whether proposed options are checked against domain realities
- whether incomplete-information warnings are surfaced
- whether sequencing risks are identified
- whether weak-fit or infeasible options are flagged rather than presented as straightforward

### P4. Missing-information detection
How well the plugin identifies missing domain information that materially limits responsible progress.

Focus on:

- whether missing facts are identified explicitly
- whether the missing information is tied to issues or feasibility constraints
- whether the importance of the gap is calibrated reasonably
- whether domain-complexity or decision-quality concerns are surfaced early enough

### P5. Domain-sensitive process protection
How well the plugin supports process legitimacy in domain-specific contexts.

Focus on:

- parenting-sensitive handling
- dependency-aware protection
- recognition of bargaining pressure tied to domain realities
- avoidance of domain-insensitive pressure to settle

This family is domain-sensitive, but it should still remain subordinate to the core's ownership of generic fairness and noncoercion.

### P6. Handoff and review contribution quality
How well the plugin contributes domain annotations when human review, co-handling, or handoff becomes relevant.

Focus on:

- whether handoff notes identify the right domain questions
- whether plugin confidence or uncertainty is legible
- whether domain-specific cautions are preserved in a way humans can act on

---

## 5. Scoring scale

Each plugin-domain family should use the same 1–5 scale as the core score:

- `5` = strong / exemplary
- `4` = good
- `3` = adequate
- `2` = weak
- `1` = poor

The same notes discipline should apply:

- notes are required for scores of `1`, `2`, or `5`
- notes are encouraged whenever domain-specific reasoning would otherwise be ambiguous

---

## 6. Proposed weights

Recommended v0 family weights:

| Family | Weight |
|---|---:|
| P3. Feasibility and qualification quality | 24 |
| P2. Domain warning and red-flag quality | 20 |
| P4. Missing-information detection | 18 |
| P5. Domain-sensitive process protection | 16 |
| P1. Domain issue structuring | 12 |
| P6. Handoff and review contribution quality | 10 |

Total = 100

### Weighting logic

Top weight goes to:

- feasibility qualification
- domain warnings
- explicit recognition of missing information

This reflects the plugin's main job: making the system domain-responsible rather than merely domain-fluent.

Lower but still meaningful weight goes to:

- issue structure
- process-sensitive protections
- handoff contribution quality

---

## 7. Aggregation rule

Use the same formula style as the core score:

**Weighted family score = (family score / 5) x family weight**

Then sum all weighted family scores to obtain a plugin-domain score out of 100.

Recommended interpretation bands:

- `85-100`: strong domain qualification
- `70-84`: useful but materially improvable
- `55-69`: weak domain qualification
- `below 55`: unsafe or insufficient domain support

These bands should be treated as guidance, not a deployment decision by themselves.

---

## 8. Divorce-plugin scoring guidance by family

### P1. Domain issue structuring
Score highly when the plugin cleanly distinguishes issues such as:

- parenting schedule
- school logistics
- support or cost burdens
- housing transition
- communication protocol

Common failure:
- treating a parenting conflict as a single generic fairness dispute without preserving schedule or child-stability structure

### P2. Domain warning and red-flag quality
Score highly when the plugin notices concerns such as:

- dependency-sensitive bargaining pressure
- parenting-sensitive instability
- legal timing pressure
- domain complexity that exceeds responsible autonomous handling

Common failure:
- obvious domain warning signs exist, but the plugin remains silent or vague

### P3. Feasibility and qualification quality
Score highly when the plugin flags that an option depends on facts like:

- school commute realities
- childcare logistics
- support or housing constraints
- timing interactions across issue clusters

Common failure:
- options are treated as domain-fit without checking practical constraints

### P4. Missing-information detection
Score highly when the plugin turns unresolved gaps into structured missing information rather than leaving them implicit.

Common failure:
- the system keeps advancing option generation while domain-critical unknowns remain unstated

### P5. Domain-sensitive process protection
Score highly when the plugin helps guard against:

- subtle coercive settlement pressure in dependent relationships
- routine or parenting arguments being used as unexamined authority
- domain conditions that distort negotiation freedom

Common failure:
- domain structure is present, but process risks tied to dependency or parenting sensitivity are not surfaced

### P6. Handoff and review contribution quality
Score highly when the plugin produces domain annotations that would genuinely help a human reviewer continue responsibly.

Common failure:
- the plugin suggests caution or low confidence but does not explain what the human should look at next

---

## 9. Plugin-domain review block

Recommended evaluator form section:

### Plugin-domain family scores
- P1 Domain issue structuring: __ / 5
- P2 Domain warning and red-flag quality: __ / 5
- P3 Feasibility and qualification quality: __ / 5
- P4 Missing-information detection: __ / 5
- P5 Domain-sensitive process protection: __ / 5
- P6 Handoff and review contribution quality: __ / 5

### Plugin-domain final fields
- plugin-domain score: __ / 100
- plugin-domain judgment: Strong / Useful but improvable / Weak / Poor
- plugin-confidence handling quality: High / Medium / Low
- plugin-specific rationale:

---

## 10. Plugin-specific failure overlays

The operational spec notes that plugin-specific failure overlays may be needed.

Recommended first-pass divorce-plugin overlays:

- `PD1 domain_blindness`
  - the plugin fails to surface obviously relevant domain structure
- `PD2 weak_feasibility_guarding`
  - the plugin allows unrealistic or under-specified options to appear well qualified
- `PD3 missed_domain_trigger`
  - the plugin misses a domain-specific hard trigger or major warning
- `PD4 dependency_insensitivity`
  - the plugin fails to recognize dependency- or power-shaped bargaining distortion

These should initially be treated as optional evaluator callouts rather than schema-required fields.

---

## 11. Attribution guidance

A low plugin-domain score should be used when the failure is primarily domain-resident.

Likely plugin-resident failures include:

- missing issue taxonomy
- weak domain warning logic
- failure to mark missing domain information
- lack of domain feasibility checks
- poor plugin-confidence signaling

Do **not** assign plugin blame when:

- the plugin emitted the right signal, but the platform ignored it
- the plugin qualified an option correctly, but the final artifacts lost that information
- the evaluator problem is actually generic mediation behavior rather than domain support

Those are more likely integration or core failures.

---

## 12. Relationship to the core and integration scores

The plugin-domain score should be read together with:

- the core-general score
- the integration score

Common patterns:

- Strong core + weak plugin:
  generic mediation is decent, but domain qualification is unsafe or thin

- Strong plugin + weak integration:
  the plugin emitted useful signals, but they were not preserved or acted on correctly

- Weak core + strong plugin:
  the domain layer is structurally sound, but Solomon still mediated poorly

---

## 13. Recommended next step

Once this document is adopted, the next scoring artifact should be the core/plugin integration score layer so evaluators can distinguish:

- plugin failure
- integration failure
- mixed failure
