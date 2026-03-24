# Next Phase Execution Tasklist 014

## Purpose

This tasklist turns the full-spec conformance review into the next execution phase.

Priority rule:

- do not add a fifth divorce slice yet
- first operationalize the broader evaluation-phase surfaces the full specification expects

---

## 1. Make Policy Profiles Real

- [x] Define the first executable profile matrix for the current repo.
- [x] Decide which artifacts are allowed, required, optional, or suppressed for at least:
  - [x] `sim_minimal`
  - [x] one richer evaluation profile
- [x] Implement profile-aware artifact emission in [runtime/artifacts.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/artifacts.py).
- [x] Add profile-aware validation so emitted artifact sets match the selected profile.
- [x] Add tests proving profile changes behavior, not just metadata.

Done when:

- [x] `policy_profile` changes runtime artifact behavior in a visible and testable way.
- [x] The artifact set for a run can be validated against the selected profile.

---

## 2. Add Brief / Continuity Artifact Generation

- [x] Implement a first-pass brief writer for evaluator-facing support artifacts.
- [x] Add at least one executable brief family:
  - [x] `case_intake_brief`
  - [x] `early_dynamics_brief` if applicable
  - [x] `risk_alert_brief` if triggered
- [x] Implement a minimal continuity-packet writer for escalated runs.
- [x] Tie continuity artifact generation to escalation mode thresholds.
- [x] Add tests for:
  - [x] no continuity packet in ordinary `M0`
  - [x] continuity packet required in at least one escalated mode

Done when:

- [x] The runtime can emit structured handoff-support artifacts, not just a session summary.
- [x] At least one escalation path produces continuity output automatically.

---

## 3. Widen Escalation Beyond M0 / M1

- [x] Decide the first executable subset of higher escalation modes to support next.
- [x] Recommended first subset:
  - [x] `M2` human review in the loop
  - [x] `M3` co-handling / mediator involvement
- [x] Add at least one additional escalation category beyond current decision-quality caution.
- [x] Extend [runtime/escalation.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/escalation.py) to emit those modes/categories under explicit conditions.
- [x] Add benchmark or synthetic test cases that actually reach those modes.
- [ ] Extend session and artifact validation for higher-mode expectations.

Done when:

- [x] The runtime can produce at least one nontrivial higher escalation mode beyond `M1`.
- [x] The resulting artifacts and rationale differ meaningfully by mode.

---

## 4. Operationalize Evaluator Fairness / Calibration / Regression Tooling

- [x] Add a reusable fairness-check helper tied to evaluator artifacts.
- [x] Add a first-pass regression comparison utility for benchmark reruns.
- [x] Add a calibration-support note or helper for disagreement / borderline cases.
- [x] Decide whether `expert_review.json` needs a second worked example before broader rollout.
- [x] Make these tools operate outside the test suite, not only inside it.

Done when:

- [x] Evaluator operations are not only documented; there is at least one executable helper for each major function:
  - [x] fairness review
  - [x] regression comparison
  - [x] calibration support

---

## 5. Operationalize Divorce Template-Family Coverage

- [x] Add a simple coverage matrix linking active divorce slices to documented template families.
- [x] Identify which first-pass families remain unrepresented by the current `D-B04` to `D-B07` set.
- [x] Decide whether the next slice should be selected by family-gap logic instead of ad hoc topic choice.
- [x] If useful, add a small generator or registry annotation layer for family membership.

Done when:

- [x] It is easy to see which documented families are already covered and which are missing.
- [x] The next slice decision can be made from coverage needs rather than intuition alone.

---

## Recommended Execution Order

1. Make policy profiles real.
2. Add brief / continuity artifact generation.
3. Widen escalation beyond `M0` / `M1`.
4. Operationalize evaluator fairness / calibration / regression tooling.
5. Add template-family coverage mapping.

---

## Stop Rule

Before adding another divorce slice, confirm all of the following:

- [x] `policy_profile` is behaviorally real
- [x] at least one continuity path is executable
- [x] at least one higher escalation mode is executable
- [x] evaluator operations include executable fairness/regression helpers
- [x] current slice coverage is mapped against template families
