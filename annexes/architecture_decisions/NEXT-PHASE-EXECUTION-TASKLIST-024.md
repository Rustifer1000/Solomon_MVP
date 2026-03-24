# Next Phase Execution Tasklist 024

## Purpose

This tasklist follows the first full review of the now family-complete divorce corpus.

Priority rule:

- do not add more divorce slices
- turn the completed corpus into a more symmetric and trial-ready evaluator package
- reduce the remaining quality debt before practical validation

---

## 1. Expand Higher-Mode Evaluator Anchors

- [x] Add the full evaluator reference package for `D-B13`:
  - [x] `evaluation.json`
  - [x] `evaluation_summary.txt`
  - [x] `expert_review.json`
- [x] Add the committed support-artifact reference set for `D-B13`.
- [x] Add at least the evaluator reference package for `D-B12`.

Done when:

- [x] the critical higher-mode safety/escalation slices are no longer anchored unevenly.

---

## 2. Clean Up Persona Recommended-Field Warnings

- [x] Update the older persona profiles that still emit recommended-field warnings:
  - [x] `D-B05`
  - [x] `D-B06`
  - [x] `D-B07`
  - [x] `D-B08`
  - [x] `D-B09`
- [x] Keep the persona schema stable while normalizing the older slice corpus upward.

Done when:

- [x] `python tools\\validate_persona_profiles.py` reports no recommended-field warnings.

---

## 3. Run A First Practical Trial / Validation Pass

- [x] Decide the practical-trial protocol for the complete divorce corpus.
- [x] Define:
  - [x] which slices are in the first trial set
  - [x] what outputs are reviewed
  - [x] what counts as success, caution, or redesign
- [x] Record the trial procedure in repo docs.

Done when:

- [x] the divorce corpus is ready for a real validation pass rather than only internal benchmark execution.

---

## 4. Then Reassess Post-Corpus Priorities

- [ ] Reassess whether the next work should be:
  - [ ] practical-trial follow-up
  - [ ] evaluator anchor deepening
  - [ ] or beginning preparation for a second plugin family

Done when:

- [ ] the repo has a clear post-divorce-completion direction.

---

## Recommended Execution Order

1. Expand higher-mode evaluator anchors.
2. Clean up persona recommended-field warnings.
3. Run a first practical trial / validation pass.
4. Then reassess post-corpus priorities.
