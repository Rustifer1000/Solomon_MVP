# Next Phase Execution Tasklist 019

## Purpose

This tasklist follows the post-`D-B10` spec-conformance review.

Priority rule:

- align the repo more closely with the synthetic-generation and fairness-review parts of the developer-ready evaluation spec
- do not jump straight into the highest-risk remaining slice families without those artifacts in place

---

## 1. Add A Synthetic User Role-Profile Schema

- [x] Create a committed schema/contract artifact for synthetic user role profiles.
- [x] Make sure it covers at least:
  - [x] goals
  - [x] private concerns
  - [x] red lines
  - [x] communication style
  - [x] emotional triggers
  - [x] disclosure tendencies
  - [x] compromise willingness
  - [x] response to perceived bias or pressure
- [x] Check current divorce persona files against the new schema expectations.

Done when:

- [x] The persona layer is a reusable generation contract, not just a set of good examples.

---

## 2. Add First-Pass Fairness Checks

- [x] Create a first-pass fairness-check artifact or contract note.
- [x] Define what fairness-sensitive evaluators should inspect across:
  - [x] positions
  - [x] facts
  - [x] flags
  - [x] summaries
  - [x] escalation behavior
- [x] Connect the fairness checks to the current fairness-sensitive slices:
  - [x] `D-B06`
  - [x] `D-B08`
  - [x] `D-B10`

Done when:

- [x] Fairness review is more operational than implicit.

---

## 3. Implement The Next Slice As TF-DIV-05

- [x] Create a new benchmark slice for `TF-DIV-05` high asymmetry / dependent spouse.
- [x] Use it to test fair-process protection, domination detection, and escalation calibration.
- [x] Prefer the lightest posture that remains honest; do not force a severe posture unless the facts justify it.

Done when:

- [x] The corpus includes an explicit asymmetry/dependency slice before the highest-stakes safety families.

---

## 4. Add The Matching Evaluator Reference Package For TF-DIV-05

- [x] Add `evaluation.json`.
- [x] Add `evaluation_summary.txt`.
- [x] Validate with the existing evaluator validator.

Done when:

- [x] The new asymmetry slice is represented in the evaluator anchor set.

---

## 5. Reassess The Remaining High-Stakes Families

- [x] Re-run coverage after `TF-DIV-05` lands.
- [x] Reassess the next gap among:
  - [x] `TF-DIV-09`
  - [x] `TF-DIV-10`
  - [x] `TF-DIV-11`

Done when:

- [x] The next move is chosen from the updated vulnerability / safety coverage picture.

---

## Recommended Execution Order

1. Add the synthetic user role-profile schema.
2. Add first-pass fairness checks.
3. Implement `TF-DIV-05`.
4. Add its evaluator reference package.
5. Then reassess the highest-stakes remaining families.
