# Next Phase Execution Tasklist 022

## Purpose

This tasklist follows the post-`D-B13` boundary audit.

Priority rule:

- preserve plugin neutrality in shared layers while continuing the divorce-first strategy
- fix the smallest remaining leaks before they harden into assumptions that make later plugin expansion expensive

---

## 1. Remove Divorce-Specific Package Vocabulary From Shared Artifacts

- [x] Stop importing `PACKAGE_ELEMENT_LABELS` directly into `runtime/artifacts.py`.
- [x] Stop importing `PACKAGE_ELEMENT_LABELS` directly into `runtime/support_artifacts.py`.
- [x] Move package-element labels behind:
  - [x] a plugin-owned descriptor
  - [ ] or a benchmark-owned descriptor
- [x] Keep the shared artifact layer responsible for structure, not domain vocabulary.

Done when:

- [x] `runtime/artifacts.py` no longer imports from `runtime.plugins.divorce_shared`.
- [x] `runtime/support_artifacts.py` no longer imports from `runtime.plugins.divorce_shared`.

---

## 2. Make Fairness/Evaluator Helpers Plugin-Aware

- [x] Review `runtime/fairness_checks.py`.
- [x] Review `runtime/evaluator_operations.py`.
- [x] Decide which assumptions should move behind plugin-aware hooks or descriptors.
- [x] Keep current divorce behavior unchanged while removing silent divorce-only assumptions from shared helper design.

Done when:

- [x] evaluator helper logic is clearly shared-plus-plugin-aware rather than shared-but-secretly-divorce-shaped.

---

## 3. Audit Shared Artifact Vocabulary

- [x] Review summary/support-artifact wording for places where shared layers still assume divorce-specific issue/package idioms.
- [x] Push any remaining domain vocabulary into plugin or benchmark descriptors where reasonable.
- [x] Do not over-abstract stable shared process language.

Done when:

- [x] shared artifact wording is mostly structural/process-oriented and domain vocabulary is supplied from the domain side.

---

## 4. Then Reassess `TF-DIV-11`

- [x] After the boundary cleanup pass, reassess whether the repo is ready for the final remaining hard-trigger family.
- [x] Use that review to decide whether `TF-DIV-11` should be implemented immediately or preceded by any small evaluator/safety-artifact adjustments.

Done when:

- [x] the final remaining family is sequenced from a cleaner shared/core boundary.

---

## Recommended Execution Order

1. Remove divorce-specific package vocabulary from shared artifacts.
2. Make fairness/evaluator helpers plugin-aware.
3. Audit shared artifact vocabulary.
4. Then reassess `TF-DIV-11`.
