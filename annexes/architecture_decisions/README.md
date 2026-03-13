# Architecture Decisions and Readiness Notes

## Purpose

This folder contains **informative implementation-planning documents** that help translate the Solomon MVP specification package into concrete technical decisions.

These files do **not** replace the normative specification documents in `docs/` or the JSON schemas in `schema/` / `schemas/`.  
They exist to make architecture work, planning, sequencing, and boundary decisions more explicit and easier to maintain.

---

## What belongs here

This folder is intended for documents such as:

- architecture decision records (ADRs)
- readiness checklists
- implementation boundary memos
- planning notes that clarify how to translate the evaluation-phase specification into runtime architecture
- cross-cutting decisions about model, platform, plugin, evaluator, and artifact responsibilities

Examples:

- `ADR-001-model-core-plugin-evaluator-boundary.md`
- `READINESS-001-pre-architecture-checklist.md`

---

## What does not belong here

This folder should **not** contain:

- the authoritative MVP evaluation-phase spec
- evaluator schemas
- example records that define contract shape
- ad hoc brainstorming notes with no decision value
- historical drafts that belong in `archive/`

Those materials should remain in their existing locations unless the repository structure is later revised.

---

## Normative vs informative

### Normative
The current normative sources of truth are the core specification and schema files, including:

- `docs/01_foundations_and_architecture.md`
- `docs/02_operations_and_evaluator_workflow.md`
- evaluation and expert-review schemas

If an ADR or readiness note conflicts with a normative spec, the **normative spec wins**.

### Informative
Files in this folder are informative.  
They are intended to:

- interpret the normative spec
- support planning and implementation
- make boundary decisions explicit
- reduce ambiguity during development
- prepare future architecture documents

---

## How to use this folder

Use these documents when you need to answer questions like:

- What should live in the model?
- What should live in the core platform?
- What should live in the plugin layer?
- What should live in the evaluator/control plane?
- What must be stable before architecture translation begins?
- Which design choices are provisional versus settled?

These files should help developers, architects, and evaluators move from “what the system is supposed to do” to “how the system should actually be structured.”

---

## Document types

### ADR files
ADR files capture a concrete architecture or boundary decision.

Recommended format:
- title
- status
- purpose
- decision
- implications
- open questions if any

ADR naming convention:

`ADR-###-short-kebab-case-title.md`

Example:

`ADR-001-model-core-plugin-evaluator-boundary.md`

### Readiness files
Readiness files define thresholds that should be met before a next phase of work begins.

Recommended format:
- purpose
- readiness principle
- checklist sections
- exit conditions
- final go / no-go criteria

Readiness naming convention:

`READINESS-###-short-kebab-case-title.md`

Example:

`READINESS-001-pre-architecture-checklist.md`

---

## Current intended use in Solomon

At the current stage of the repository, this folder is expected to serve as the bridge between:

1. the evaluation-phase specification
2. the offline synthetic evaluation workflow
3. the future runtime architecture

In particular, this folder should help the team avoid:

- prematurely freezing production architecture
- hiding unresolved system design inside the model
- collapsing core and plugin responsibilities
- losing traceability between evaluation evidence and architecture decisions

---

## Relationship to future architecture documents

If repeated evaluation and implementation work stabilizes a decision recorded here, that decision may later be:

- incorporated into `docs/01_foundations_and_architecture.md`
- incorporated into `docs/02_operations_and_evaluator_workflow.md`
- promoted into a future normative runtime architecture document such as `docs/03_runtime_architecture.md`

Until then, the files here should be treated as working implementation guidance.

---

## Maintenance guidance

A document in this folder should be updated when:

- a boundary decision changes
- evaluation evidence invalidates a prior assumption
- a readiness threshold is revised
- a provisional implementation decision becomes stable enough to promote elsewhere

A document in this folder should be retired or archived when:

- it has been superseded by a newer ADR
- it has been folded into a normative spec
- it no longer reflects the active implementation direction

---

## Suggested initial contents

- `README.md`
- `ADR-001-model-core-plugin-evaluator-boundary.md`
- `READINESS-001-pre-architecture-checklist.md`

---

## Working principle

Use this folder to make architecture thinking explicit before architecture is finalized.