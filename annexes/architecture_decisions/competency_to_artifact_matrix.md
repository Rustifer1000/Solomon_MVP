# Competency-to-Artifact Matrix

**Status**  
Draft / informative

**Purpose**  
This document maps Solomon's core competency families to observable runtime behaviors and evaluator-visible artifacts.

It is intended to reduce one of the key pre-architecture ambiguities:

- what each competency family must actually produce or preserve in the runtime

This document does **not** supersede the normative specification in `docs/`.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. How to use this matrix

For each competency family, ask:

- what runtime behavior should exist if the competency is functioning
- what artifacts should preserve evidence of it
- what kinds of failure should evaluators be able to see

This matrix should be used by:

- runtime architects
- evaluator-tooling builders
- plugin designers
- benchmark authors

---

## 2. Matrix columns

### Competency family
The core family from C1 through C10.

### Observable runtime behavior
What the runtime should be able to do, preserve, or explain if the competency is present.

### Primary artifact evidence
Which artifacts should most clearly preserve evidence of the competency.

### Common failure evidence
What artifact pattern would commonly indicate the competency is failing.

---

## 3. First-pass matrix

| Competency family | Observable runtime behavior | Primary artifact evidence | Common failure evidence |
|---|---|---|---|
| C1 Process framing | role and limits are explained; session structure is initialized; party authority is preserved | interaction trace, summary, evaluation notes | summary lacks role/limits; trace shows no usable framing |
| C2 Issue clarification | issues become organized into workable clusters; accusations are translated into issue structure | interaction trace, positions, facts snapshot, summary | issue map remains muddy; positions and facts blur together |
| C3 Interest elicitation | underlying concerns, constraints, and priorities are surfaced beneath positions | interaction trace, summary, positions, continuity packet if escalated | options appear without clear interests; repeated positions only |
| C4 Communication management | neutral summaries, turn management, reframing, interruption response | interaction trace, summary, flags if process strain rises | repeated interruption or inflammatory language persists without meaningful intervention |
| C5 Option generation support | multiple options, tradeoffs, sequencing, and contingencies are explored responsibly | interaction trace, summary, missing info, plugin qualification outputs | optioning is premature, directive, or detached from constraints |
| C6 Fair process and balanced participation | participation imbalance is noticed; self-determination is protected; domination is addressed | interaction trace, flags, summary, fairness checks | one party fades out; pressure or one-sidedness is visible but unaddressed |
| C7 Emotional and relational regulation | emotional content is acknowledged; de-escalation supports rather than replaces substance | interaction trace, summary | soothing language appears but conflict dynamics remain unmanaged |
| C8 Decision-quality support | facts and assumptions are distinguished; uncertainty is made explicit; missing info is tracked | facts snapshot, missing info, interaction trace, summary | false certainty; important unknowns stay implicit |
| C9 Safety, escalation, and boundary handling | risks are detected; thresholds are assessed; mode choice is recorded; handoff occurs when needed | flags, interaction trace, continuity packet, summary | unsafe continuation, opaque escalation rationale, missed hard triggers |
| C10 Explainability and auditability | procedural moves and state changes remain evaluator-visible and attributable | run meta, interaction trace, structured artifacts, evaluation outputs | evaluators cannot reconstruct what happened or why |

---

## 4. Architecture implications

### 4.1 Core families are not just transcript qualities
Most competencies need structured artifact evidence, not only conversational evidence.

### 4.2 C6, C8, C9, and C10 are especially artifact-dependent
These families rely heavily on:

- `flags.json`
- `missing_info.json`
- `facts_snapshot.json`
- `interaction_trace.json`
- continuity packet or review artifacts when escalation occurs

### 4.3 Plugin qualification intersects but does not replace core evidence
For C5, C8, and C9 especially, plugin signals may enrich the evidence path, but the core family still needs evaluator-visible preservation.

---

## 5. D-B04 anchor interpretation

For `D-B04`, the matrix implies:

- `C3` should appear in surfaced interests around child stability and fairness
- `C5` should appear in phased or contingent optioning rather than immediate directive solutioning
- `C6` should appear in balanced treatment of both parents' concerns
- `C8` should appear in explicit tracking of unresolved school and logistics questions

The most diagnostic artifacts for this slice are:

- `interaction_trace.json`
- `positions.json`
- `facts_snapshot.json`
- `missing_info.json`
- `flags.json`
- `summary.txt`

---

## 6. Definition of done for v0

This matrix is sufficiently useful for the architecture phase when:

- each competency has at least one observable runtime behavior
- each competency has at least one primary artifact path
- common failure evidence is concrete enough to guide implementation and evaluation
