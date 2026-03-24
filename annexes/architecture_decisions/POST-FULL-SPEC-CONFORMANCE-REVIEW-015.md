# Post Full-Spec Conformance Review 015

## Purpose

This review checks the current repository against the broader **Developer-Ready Evaluation Specification Draft**, not just against the narrower runtime-remediation and divorce-slice work completed so far.

The goal is to identify the most important gaps between:

- the current executable evaluation runtime
- the broader evaluation-phase architecture the full specification expects

---

## Findings

### 1. Policy profiles are present in metadata, but not yet implemented as real runtime behavior.

Severity: High

The full specification treats policy profiles as architecture-shaping, especially for persistence, redaction, and which artifacts are allowed to exist in a given run. The current runtime carries `policy_profile` through metadata and artifact headers, but does not yet change behavior by profile.

Current state:

- [runtime/cli/run_benchmark.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/cli/run_benchmark.py) accepts `--policy-profile`
- [runtime/orchestrator.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/orchestrator.py) carries that state through execution
- [runtime/artifacts.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/artifacts.py) records it in emitted artifacts

What is missing:

- no profile-driven artifact suppression
- no profile-driven redaction
- no profile-driven transcript/brief/continuity branching
- no validation that emitted artifacts match the selected policy profile

Why it matters:

Right now `policy_profile` is informative, not authoritative. Under the full spec, it should become a control surface.

### 2. Briefs and continuity-packet outputs are still mostly contractual, not executable.

Severity: High

The full specification expects evaluator-facing briefs and continuity artifacts to be part of the evaluation runtime, especially when escalation rises above ordinary autonomous handling. The current artifact writer emits the core runtime set well, but it does not yet emit:

- `briefs/`
- continuity packets
- escalation-triggered handoff artifacts

Current state:

- [runtime/artifacts.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/artifacts.py) writes:
  - `run_meta.json`
  - `interaction_trace.json`
  - `positions.json`
  - `facts_snapshot.json`
  - `flags.json`
  - `missing_info.json`
  - `summary.txt`
- [annexes/architecture_decisions/CONTRACT-004-continuity-packet-v0.md](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/annexes/architecture_decisions/CONTRACT-004-continuity-packet-v0.md) exists as design guidance

What is missing:

- no continuity packet generator
- no risk-alert brief generation
- no intake / early-dynamics brief generation
- no runtime contract that says when those artifacts become required

Why it matters:

The current system is strong at summarizing completed runs, but it is not yet strong at preserving a structured handoff package when the process needs human review, co-handling, or takeover.

### 3. The escalation framework is still materially narrower than the full spec.

Severity: High

The full specification frames escalation as a first-class feature with meaningful differences between `M0` through `M5`, and between categories `E1` through `E6`. The current runtime still behaves like a focused MVP scaffold centered on `M0` and `M1`.

Current state:

- [runtime/escalation.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/escalation.py) effectively resolves to:
  - `M0`
  - `M1`
  - mostly `E5`
- [runtime/session_validation.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/session_validation.py) validates session coherence well, but it does not yet pressure-test higher escalation modes

Why it matters:

The repo currently demonstrates bounded caution well. It does not yet demonstrate:

- human review in the loop
- co-handling
- full handoff
- stop-and-redirect
- broader ethical / fairness / safety escalation families

That is a major gap under the full spec, even if it is understandable for the current slice set.

### 4. Divorce template families are documented, but not yet operationalized as a generation system.

Severity: Medium

The repository now has four strong divorce slices, which is a real achievement. But the full specification asks for more than slices; it asks for a reusable generation and calibration model tied to template families.

Current state:

- [annexes/divorce_template_families.md](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/annexes/divorce_template_families.md) defines first-pass families
- [runtime/benchmarks](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/benchmarks) contains four executable slices

What is missing:

- no family-driven scenario generator
- no explicit coverage matrix tying implemented slices back to template families
- no calibration corpus builder or near-neighbor generation flow

Why it matters:

Right now the benchmark set is well-structured, but still hand-authored and selectively broad. The spec envisions a more systematic generation strategy.

### 5. Fairness, calibration, and regression are better specified than operationalized.

Severity: Medium

The spec emphasizes evaluator calibration, fairness checks, regression discipline, and disagreement handling. The repository now has good evaluator validation for worked examples, but those broader evaluator operations remain mostly documentary.

Current state:

- [pending/fairness_checks.md](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/pending/fairness_checks.md) exists
- [pending/regression_test_protocol.md](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/pending/regression_test_protocol.md) exists
- [runtime/evaluator_artifact_validation.py](/C:/Users/RussellCollins/Solomon_MVP/Solomon_MVP/runtime/evaluator_artifact_validation.py) validates worked evaluator examples

What is missing:

- no fairness-check execution helper
- no calibration workflow utility
- no regression rerun comparison tool
- no adjudication-support artifact flow beyond the single worked `expert_review.json`

Why it matters:

The evaluator plane is now credible, but still not fully operationalized in the way the full spec imagines.

### 6. The current repo is strongest where it has already concentrated effort: runtime authority chain, benchmark structure, evaluator artifact discipline, and plugin neutrality.

Severity: Healthy

This review found substantial conformance strength in the following areas:

- benchmark registry and benchmark-owned runtime planning
- plugin-neutral orchestrator seam
- authoritative state mutation and structured normalization
- evaluator artifact validation and worked examples
- slice-owned policy descriptors and artifact narrative policy
- a real multi-slice divorce benchmark stack

This matters because it means the current repo is not broadly off-track. The main gaps are in the broader evaluation-phase surfaces the full spec includes beyond the narrow runtime MVP.

---

## Open Questions / Assumptions

- I am assuming the immediate goal is still evaluation-phase maturity, not end-user productization.
- I am assuming persistence profiles are intended to shape actual artifact behavior soon, not remain metadata only.
- I am assuming the next escalation work should still be evaluation-driven and synthetic-first, rather than tied to live deployment behavior.

---

## What Is Healthy Here

- The current runtime is far more executable and trustworthy than a design-only scaffold.
- The authority chain from normalized turn -> state -> plugin assessment -> escalation -> artifacts is now meaningfully real.
- The benchmark and plugin seams are healthier than many first-phase systems at this stage.
- The evaluator plane has improved enough that the next gaps are no longer “write a schema,” but “operationalize the evaluator workflow the spec describes.”

---

## Conformance Judgment

The repository is now **strongly aligned with the core runtime spine of the evaluation-phase specification**, but only **partially aligned with the broader evaluation-phase operating model** described in the full draft.

In plain terms:

- the runtime core is ahead of the surrounding evaluation infrastructure
- the repo is credible as an executable divorce evaluation runtime
- it is not yet fully conformant with the complete draft because several spec-critical surfaces remain mostly documentary:
  - policy profiles
  - briefs
  - continuity packets
  - richer escalation modes
  - calibration/fairness/regression operations

---

## Next Bottlenecks

The next bottlenecks under the full specification are:

1. Policy-profile enforcement and persistence/redaction behavior
2. Brief and continuity-packet generation
3. Broader escalation-mode implementation and test coverage
4. Operational evaluator tooling for fairness/calibration/regression
5. Template-family operationalization and coverage mapping

---

## Recommendation

Do not treat the next phase as “add another divorce slice.”

The strongest next phase under the full specification is:

1. make `policy_profile` behavior real
2. add brief / continuity artifacts
3. widen escalation handling beyond `M0` / `M1`
4. then operationalize evaluator-side fairness / calibration / regression tooling

That sequence follows the full spec much more closely than more benchmark breadth would.
