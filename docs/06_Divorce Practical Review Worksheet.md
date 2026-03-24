# Divorce Practical Review Worksheet

## Purpose

Use this worksheet during structured dry-run usage with side-by-side human review.

This worksheet is designed to make practical review:

- easy to run
- consistent across reviewers
- comparable across slices
- useful for deciding whether a change is actually needed

This worksheet is for **offline evaluator-centered practical review**, not live end-user deployment.

---

## Session Header

- Review date:
- Reviewer:
- Review mode:
  - internal evaluator walkthrough
  - side-by-side human review
  - structured dry-run artifact review
- Slice or set:
- Compared against:
- Session artifact folder(s):

---

## Recommended Review Order

Review these in order when available:

1. `case_metadata.json`
2. `run_meta.json`
3. `summary.txt`
4. `flags.json`
5. `facts_snapshot.json`
6. `positions.json`
7. `interaction_trace.json`
8. `evaluation.json`
9. `evaluation_summary.txt`
10. `expert_review.json`
11. `briefs/*`
12. `continuity/continuity_packet.json`

Do not start with the transcript even if one exists. The point is to test whether the artifact set is sufficient.

---

## Part 1: Fast Judgment

### 1. Final posture

- Observed posture:
- Did the final posture feel right?
  - yes
  - probably yes but thinly justified
  - no

### 2. Next step usefulness

- Did the recommended next step feel practically useful?
  - yes
  - partially
  - no

### 3. Artifact sufficiency

- Could you explain the posture and next step from the artifact set alone?
  - yes
  - mostly
  - no

### 4. Family identity

- Did this slice remain clearly distinct from its nearest contrast slice?
  - yes
  - mostly
  - no

---

## Part 2: Practical Success / Caution / Concern

Choose one:

- useful practical success
- caution but acceptable
- material concern requiring remediation

Short reason:

---

## Part 3: Core Review Questions

### A. Posture clarity

- What artifact most strongly justified the final posture?
- What artifact was least helpful?
- Did any artifact materially conflict with another?

### B. Role and legitimacy

- Did Solomon stay within a legitimate mediation role?
- Did the system avoid sounding directive, adjudicative, or falsely authoritative?
- If escalation occurred, did it feel like good performance rather than failure-by-default?

### C. Practical usability

- Did the support artifacts help?
  - yes clearly
  - somewhat
  - no
- If they helped, what did they clarify?
- If they did not help, what felt redundant or confusing?

### D. Reviewer friction

- What was the main friction point in this review?
- Was the friction mainly:
  - navigation
  - artifact thinness
  - unclear posture rationale
  - slice indistinguishability
  - evaluator wording
  - other

---

## Part 4: Contrast Judgment

If reviewing a contrast pair or set, answer:

- Which slice was easiest to understand?
- Which slice was hardest to distinguish?
- Did any two slices feel closer together than they should?
- If yes, which pair and why?

Suggested contrast pairs:

- `D-B10` vs `D-B12`
- `D-B08` vs `D-B12`
- `D-B13` vs `D-B14`
- `D-B11` vs `D-B13`
- `D-B09` vs `D-B13`

---

## Part 5: Actionability

### If the review was a success

- What should remain unchanged?

### If the review was cautionary

- What is the smallest change that would reduce friction?

### If the review found a material concern

- What concrete remediation is suggested?
- Which artifact or layer should change first?

---

## Part 6: Boundary Watch

Answer only if something felt boundary-relevant.

- Did anything in this review suggest the shared/core layers still behave too much like a divorce-only system?
- Did anything suggest the plugin boundary is unclear in practice?
- Is this a real repeated concern, or just a one-off impression?

Only treat this as second-plugin-relevant if it appears repeatedly across practical reviews.

---

## Reviewer Close-Out

- Final label:
  - useful practical success
  - caution but acceptable
  - material concern requiring remediation
- Main finding in one sentence:
- Smallest next step, if any:
- Did this review increase pressure for a second plugin?
  - no
  - slightly
  - materially

If yes, why:

---

## Suggested Use

Use one worksheet per:

- single-slice review
- contrast pair
- contrast set

Then summarize multiple worksheets into one short memo after a practical-use round.
