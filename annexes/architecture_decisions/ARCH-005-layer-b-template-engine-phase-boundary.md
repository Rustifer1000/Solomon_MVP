# ARCH-005: Layer B Template Engine — Phase Boundary Decision

**Status**
Stable / v0 approved

**Purpose**
This document records the scope decision for G-10 (Layer B template instantiation engine): Phase 1 delivers a contract-anchor stub only; full case generation is explicitly deferred to Phase 2.

---

## 1. Context

The Solomon synthetic evaluation architecture specifies a three-layer pipeline:

| Layer | Description | Phase 1 Status |
|---|---|---|
| A | Hand-authored canonical benchmark set (D-B01 – D-B14) | Complete |
| B | Template-based variation engine | Stub only (this decision) |
| C | Free-form synthetic generator | Deferred to later phase |

Layer B was designed to enable controlled scenario generation from reusable template families, providing auditable variation beyond the fixed Layer A set. The 12 divorce template family definitions (`annexes/divorce_template_families.md`) are complete and normative. The machine-readable JSON form (`annexes/divorce_template_families.json`) was produced as part of Phase 1 stub work.

**The question decided here:** should the full Layer B instantiation engine be built before the first real evaluation run?

---

## 2. Decision

**Phase 1 scope: loader stub only. Full instantiation deferred to Phase 2.**

Phase 1 delivers:

- `annexes/divorce_template_families.json` — machine-readable canonical source for all 12 families
- `runtime/templates/loader.py` — loader with `TemplateFamilyRecord` dataclass, `load_all_template_families()`, and `get_template_family(id)`
- 8 tests confirming all 12 families parse, all required fields are non-empty, focal competency IDs are valid, and the dataclass is frozen

Phase 2 scope (not built in Phase 1):

- Variable sampler
- Case instantiation factory
- Generation CLI
- Integration with `run_benchmark.py` discovery

---

## 3. Rationale

**Layer B is not needed for the first real evaluation run.** All 14 Layer A cases are authored, runnable, and validated. The evaluation pipeline (schemas, artifacts, scoring, escalation engine, CLI, batch runner) is complete. Building a case generation engine before the evaluation has run once would be building ahead of a validated need.

**The stub serves as a Phase 2 contract anchor.** Any future instantiation engine calls `get_template_family(id)` to retrieve a structured `TemplateFamilyRecord` and builds from there. The loader validates that the source data is parseable and structurally complete before any generation code is written against it.

**Deferral cost is low.** The template family definitions are stable. The loader is the only interface point between the definitions and any future generation code. Adding the instantiation engine in Phase 2 requires no changes to Phase 1 code — it slots entirely above the existing `run_benchmark.py` / `loaders.py` layer.

---

## 4. Phase 2 Build Plan

When Layer B generation is prioritised, the following components should be built in order:

### 4.1 Variable sampler (`runtime/templates/sampler.py`)

Responsible for sampling values from the variable ranges defined in each `TemplateFamilyRecord.primary_variables`. Must support:

- deterministic seeding (`--seed` argument, consistent with existing `run_benchmark.py` pattern)
- optional per-variable overrides for targeted stress-testing
- typed variable definitions (categorical, ordinal, boolean) — currently defined in prose in `annexes/divorce_template_families.md`; should be formalised as structured variable specs in a schema before this module is written

### 4.2 Case factory (`runtime/templates/factory.py`)

Responsible for instantiating a runnable case bundle from a template family record and sampled variable values. Generates:

- `case_metadata.json` — including `template_family_id` as a first-class field (not in `working_slice_notes`)
- `personas/spouse_A.json` and `personas/spouse_B.json` — from the party profile skeleton + sampled variable values
- `case_file.json` — scenario description derived from the base scenario and variable instantiation

Output must be loadable by the existing `runtime/loaders.py` without modification.

### 4.3 Generation CLI (`runtime/cli/generate_from_template.py`)

Entry point:

```
python -m runtime.cli.generate_from_template \
  --family TF-DIV-01 \
  --count 3 \
  --seed abc123 \
  --output-dir /path/to/generated-cases
```

Produces N case folders, each immediately runnable with the existing `run_benchmark.py`. Should register as a `[project.scripts]` entry point in `pyproject.toml` as `solomon-generate`.

### 4.4 Batch integration

The existing `run_all_benchmarks.py` batch runner should be able to discover and execute generated cases alongside Layer A cases. No changes to the runner itself are expected — it uses `discover_case_dirs()` which finds any directory containing `case_metadata.json`.

### 4.5 Template family variable schema

Before writing the sampler, formalise variable definitions in a JSON schema (`schema/template_family_variable.schema.json`). Each variable should carry: type (categorical/ordinal/boolean), allowed values or range, default, and a note on how it affects challenge type or escalation posture.

---

## 5. Interface contract

The loader module (`runtime/templates/loader.py`) is the Phase 1 / Phase 2 boundary. Everything in Phase 2 goes through this interface:

```python
from runtime.templates.loader import get_template_family, TemplateFamilyRecord

record: TemplateFamilyRecord = get_template_family("TF-DIV-01")
# Phase 2: pass record to sampler, then factory, then write case bundle
```

The `TemplateFamilyRecord` dataclass is frozen and versioned. If field additions are needed for Phase 2 (e.g., structured variable definitions), they should be added to both `divorce_template_families.json` and `TemplateFamilyRecord`, and the loader tests updated to cover the new fields.

---

## 6. Files affected by this decision

| File | Change | Phase |
|---|---|---|
| `annexes/divorce_template_families.json` | Created — machine-readable source | Phase 1 |
| `runtime/templates/__init__.py` | Created — package with scope docstring | Phase 1 |
| `runtime/templates/loader.py` | Created — contract-anchor loader | Phase 1 |
| `pyproject.toml` | `runtime.templates` added to packages | Phase 1 |
| `runtime/templates/sampler.py` | To be created | Phase 2 |
| `runtime/templates/factory.py` | To be created | Phase 2 |
| `runtime/cli/generate_from_template.py` | To be created | Phase 2 |
| `schema/template_family_variable.schema.json` | To be created | Phase 2 |
