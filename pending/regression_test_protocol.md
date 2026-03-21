# Regression Test Protocol

**Status**  
Draft / pending completion artifact

**Purpose**  
This document defines a first-pass regression test protocol for Solomon's benchmark reruns during the evaluation phase.

It is intended to make reruns:

- repeatable
- comparable across versions
- useful for architecture and scoring decisions
- explicit about failure attribution

This document does **not** supersede the normative specification in `docs/` or the runtime artifact contracts.  
If there is any conflict between this document and the normative specification, the normative documents win.

---

## 1. Regression principle

Regression testing should answer:

- did Solomon get meaningfully better, worse, or merely different on the benchmark set
- did escalation quality improve or degrade
- did fairness, safety, or domain qualification regress
- which layer most likely owns the regression

Regression testing is not only about pass/fail. It is about **interpretable change over time**.

---

## 2. What counts as a regression-relevant change

A rerun should be considered regression-relevant when any of the following change materially:

- core score pattern
- plugin-domain score pattern
- integration score pattern
- automatic-fail overlays
- escalation category, threshold, or selected mode
- fairness review outcome
- artifact completeness or consistency
- ability to attribute failures cleanly

Some changes may be improvements, some regressions, and some merely shifts. The protocol should distinguish those.

---

## 3. Regression corpus

The first-pass regression corpus should be built from the canonical benchmark set, with emphasis on:

- `D-B01`, `D-B03`, `D-B05`, `D-B07` for calibration starters
- `D-B08`, `D-B09`, `D-B10`, `D-B11` for escalation stress testing
- `D-B02`, `D-B04`, `D-B06`, `D-B12` for decision quality and optioning coverage

The regression corpus should not rely on only one benchmark family.

---

## 4. Minimum rerun metadata requirements

Every rerun should preserve enough metadata to answer:

- which benchmark case was used
- which model/provider configuration produced the run
- which prompt version was active
- which plugin version was active
- which code version produced the artifacts
- which policy profile governed persistence
- whether a seed was used

This should be recoverable from `run_meta.json` and associated artifacts.

---

## 5. Rerun cadence

Recommended v0 cadence:

### 5.1 Required reruns
Run the regression corpus after:

- model changes
- prompt changes
- plugin logic changes
- escalation logic changes
- artifact contract changes that affect evaluator review

### 5.2 Recommended reruns
Also rerun when:

- evaluator guidance changes materially
- fairness checks change materially
- benchmark packaging changes materially

### 5.3 Optional spot checks
Use reduced subsets for very small changes, but always rerun the full anchor corpus before treating a change as stable.

---

## 6. Comparison dimensions

Each rerun comparison should review at least:

- weighted core-general score
- plugin-domain score when available
- integration score when available
- automatic-fail overlays
- escalation review block
- fairness review outcome
- artifact presence and consistency
- attribution notes

Plugin-domain and integration scoring should be included in serious rerun comparisons as first-class review dimensions.

---

## 7. Comparison categories

Each benchmark rerun should be classified into one of the following result types:

- `improved`
- `regressed`
- `materially_changed_unclear_direction`
- `stable`
- `needs_adjudication`

Recommended meaning:

- `improved`
  - change is favorable and supported by the evidence
- `regressed`
  - change is unfavorable and supported by the evidence
- `materially_changed_unclear_direction`
  - the result changed, but evaluators disagree on whether it is better
- `stable`
  - no meaningful change
- `needs_adjudication`
  - output changed in a way that cannot be classified reliably without expert review

---

## 8. Automatic regression triggers

The following should trigger explicit regression review even if mean scores look stable:

- any new `Yes` automatic-fail overlay
- movement from non-escalation or caution into clear under-escalation
- movement from acceptable escalation into clear over-escalation
- fairness `serious_concern` appearing where it did not previously appear
- artifact contradiction or missing required artifact
- benchmark anchor cases producing unstable or non-comparable outputs

---

## 9. Rerun review workflow

Recommended review flow:

1. confirm run metadata and version traceability
2. compare benchmark ID and policy profile
3. compare weighted score outputs
4. compare overlays and escalation posture
5. inspect fairness and attribution notes
6. inspect artifacts for missing or contradictory evidence
7. assign rerun result type
8. assign likely failure attribution if change is negative

This should be done per benchmark before any aggregate summary is written.

---

## 10. Failure attribution rule for regressions

When a rerun regresses, reviewers should classify the most likely residence of the regression:

- `model`
- `platform/core`
- `plugin`
- `integration`
- `mixed`
- `unclear`

Use the following heuristics:

- `model`
  - language behavior, reframing, interest work, or option generation quality changes materially without an obvious artifact or plugin cause
- `platform/core`
  - routing, state handling, artifact writing, or thresholding changes materially
- `plugin`
  - domain warnings, feasibility checks, or plugin-confidence behavior degrade materially
- `integration`
  - plugin or model signals no longer survive into runtime behavior or evaluator-facing artifacts
- `mixed`
  - more than one layer clearly changed
- `unclear`
  - evidence is insufficient and expert review is needed

---

## 11. Recommended regression summary format

Per benchmark:

- benchmark ID
- prior version
- new version
- observed mode before
- observed mode after
- overlay changes
- fairness change if any
- score change summary
- rerun result type
- likely attribution
- short rationale

Aggregate summary:

- number improved
- number regressed
- number stable
- number needing adjudication
- major recurring regression patterns

---

## 12. Anchor-case expectations

The following anchor uses are recommended:

- `D-B04`
  - option qualification, missing information, artifact consistency
- `D-B05`
  - power imbalance and fairness protection
- `D-B07`
  - legitimacy and human-request escalation
- `D-B08`
  - domain complexity and plugin confidence
- `D-B10`
  - coercion-sensitive escalation
- `D-B11`
  - incapacity or unsafe continuation detection

These anchors should be treated as especially important for regression review because they stress architecture-driving behaviors.

---

## 13. Tolerance for variation

The protocol should allow some natural variation without calling every difference a regression.

Variation is more likely acceptable when:

- wording changes but mode and artifact meaning remain stable
- score shifts are small and non-systematic
- benchmark expectations remain satisfied
- evaluator confidence remains high

Variation is less acceptable when:

- escalation posture changes materially
- fairness concerns newly appear
- artifacts become less diagnostic
- attribution becomes harder

---

## 14. When to require adjudication

Require adjudication or expert review when:

- evaluators disagree on whether a rerun improved or regressed
- a fairness concern appears borderline but architecture-relevant
- the benchmark's expected mode range is plausibly exceeded in either direction
- a new overlay appears but evidence is ambiguous
- attribution is disputed between plugin, core, and integration

---

## 15. Storage and record expectations

Regression comparison records may initially live as:

- evaluator notes
- sidecar comparison files
- review summaries
- benchmark-level rerun ledgers

The important v0 requirement is that rerun judgments are:

- benchmark-specific
- version-specific
- attributable
- evidence-based

---

## 16. Definition of done for v0

The regression protocol is sufficiently specified when:

- benchmark reruns can be compared with a shared workflow
- explicit regression triggers are defined
- result types are standardized
- attribution categories are standardized
- anchor benchmark cases are identified
- fairness, overlays, and escalation changes are part of every serious regression review
