# Solomon MVP Spec Package

## Purpose

This repository contains the working specification package for the **MVP evaluation-phase architecture** of **Solomon**, an expert-in-the-middle AI mediation platform.

The package is designed for developers, technical architects, evaluator-tooling builders, and research/ops collaborators who need a clear, implementation-relevant understanding of:

- what Solomon is
- what the MVP evaluation phase is intended to prove
- how the core and plugin architecture should be separated
- how offline synthetic evaluation should be structured
- how scoring, escalation, and review artifacts should work
- which files are normative versus illustrative

This repository is **not** the final production architecture for Solomon. It is the developer-ready specification package for the **evaluation phase of the MVP**.

---

## What Solomon is

Solomon is an **expert-in-the-middle AI mediation system**.

For MVP purposes, Solomon should be understood as:

- a **core mediation component** that handles domain-general mediation process functions
- a **plugin/domain layer** that supplies issue structure, vocabulary, constraints, and domain-specific evaluation extensions
- a system that treats **human mediator involvement as a normal success mode**, not merely a fallback failure path

The first domain plugin specified here is **divorce mediation**.

---

## Repository reading order

If you are new to the project, read in this order:

1. **`docs/01_foundations_and_architecture.md`**  
   System definition, design principles, core/plugin boundary, scoring model, escalation model, synthetic evaluation architecture.

2. **`docs/02_Operations and Evaluator Workflow`**  
   Benchmarks, evaluator workflow, score sheet, evaluator instructions, template families, and operational evaluation structure.

3. **`docs/03_MVP Eval Intent Lock.md`**  
   Short normative purpose lock for the current phase so architecture and implementation stay aligned with the MVP evaluation target.

4. **`schema/evaluation.schema.json`**  
   Primary evaluator output contract.

5. **`schema/expert_review.schema.json`**  
   Expert adjudication / calibration / second-level review contract.

6. **`examples/evaluation.example.json`**  
   Example evaluator record.

7. **`examples/expert_review.example.json`**  
   Example expert review record.

8. **`annexes/`**  
   Supporting libraries and reference materials such as benchmark scenario collections and template-family sets.

If you need only the high-level conceptual model, start with Part I.  
If you are implementing evaluator tooling or artifact pipelines, read both Parts I and II before touching schemas.

---

## Normative vs informative files

This repository distinguishes between **normative** files and **informative** files.

### Normative
These define the intended MVP evaluation-phase requirements.

- `docs/01_foundations_and_architecture.md`
- `docs/02_Operations and Evaluator Workflow`
- `docs/03_MVP Eval Intent Lock.md`
- `schema/evaluation.schema.json`
- `schema/expert_review.schema.json`

### Informative
These help interpret, test, or implement the normative documents, but do not supersede them.

- `examples/*`
- `annexes/*`
- archived drafts
- working notes
- scenario libraries used for calibration or illustration

If there is any conflict between an example and a normative spec, the **normative spec wins**.
annexes/architecture_decisions/ is the bridge from spec to implementation

---

## Spec Completion Status

Current repo state at a glance:

- **Normative foundation:** present in `docs/` and `schema/`
- **Examples:** present in `examples/`
- **Architecture-input drafts:** materially present in `annexes/architecture_decisions/`
- **Pending specification artifacts:** materially drafted in `pending/`

Still unresolved or not yet fully normalized:

- final reproducibility / persistence framing and runtime-architecture translation
- final promotion of the architecture-input pack from draft bridge into the next-phase runtime baseline

If you are starting work now:

1. Read the normative docs and schemas first.
2. Use `annexes/architecture_decisions/` as the current bridge into implementation planning.
3. Treat `pending/` as draft-but-substantive follow-on specification material rather than placeholders.
4. Treat archived snapshots as historical references rather than active sources of truth.

---

## Repository structure

Recommended structure:

```text
solomon-mvp-spec/
  README.md
  docs/
    01_foundations_and_architecture.md
    02_Operations and Evaluator Workflow
  schema/
    evaluation.schema.json
    expert_review.schema.json
  examples/
    evaluation.example.json
    expert_review.example.json
  annexes/
    benchmark_scenarios_divorce.md
    divorce_template_families.md
  archive/
    legacy_tracker.md
    integrated_draft_snapshot.md
    99_full_spec_snapshot.md
