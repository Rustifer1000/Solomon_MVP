# Drift Watchlist: Level 1 Alignment

**Status**  
Active working guardrail for the evaluation-phase build.

**Purpose**  
This watchlist is a short recurring check to prevent Levels 2-5 work from drifting away from the Level 1 intent lock in `docs/03_MVP Eval Intent Lock.md`.

It is not a replacement for the normative spec.  
It is a practical reminder set for architecture, runtime, artifact, and eval changes.

---

## When to use this watchlist

Use this check whenever one of the following changes:

- runtime boundaries
- artifact contracts
- evaluator scoring or review flow
- plugin qualification behavior
- escalation logic
- benchmark slice design
- prompts or model-output normalization

---

## Drift watch questions

### 1. Are we still building an evaluation runtime rather than a disguised production product?

Check:

- Does the change primarily help evaluator review, artifact quality, benchmark execution, or architecture validation?
- Or does it mainly optimize for product polish, scale, deployment shape, or live-user convenience?

Drift signal:

- production concerns start driving decisions before the eval target is proven

---

### 2. Are we still treating human involvement as a success mode rather than a fallback embarrassment?

Check:

- Does the change preserve review, co-handling, handoff, and escalation as legitimate good outcomes?
- Does scoring still recognize correct escalation as successful behavior?

Drift signal:

- the system is rewarded mainly for staying autonomous longer

---

### 3. Are we preserving the core/plugin/platform/evaluator boundary?

Check:

- Does the core still own mediation process?
- Does the plugin still own domain qualification and domain warnings?
- Does the platform/runtime still own authoritative state, routing, and artifact authority?
- Does the evaluator layer remain outside the live runtime loop?

Drift signal:

- model or plugin output silently becomes authoritative without explicit normalization and commit rules

---

### 4. Are we rewarding caution, qualification, and explicit uncertainty rather than polished overconfidence?

Check:

- Do artifacts keep positions, facts, flags, and missing information distinct?
- Does the system explicitly record what is unresolved before stronger optioning?
- Do tests and scoring penalize overclaiming feasibility or authority?

Drift signal:

- fluent output starts counting as success even when uncertainty is hidden

---

### 5. Are we preserving Solomon’s anti-authoritarian posture?

Check:

- Does the change avoid turning Solomon into a judge, arbitrator, therapist, or legal decision-maker?
- Does it avoid optimizing for persuasive closure or settlement-rate theater?

Drift signal:

- the runtime starts sounding or behaving like it should decide outcomes for the parties

---

## Quick decision labels

When reviewing a change, label each question:

- `Preserved`
- `Watch`
- `At risk`

If any item is `At risk`, pause implementation and reconcile the change against:

- `docs/03_MVP Eval Intent Lock.md`
- `docs/01_foundations_and_architecture.md`
- `docs/02_Operations and Evaluator Workflow`

---

## Current main watchpoints

At the current repo stage, the highest-risk drift areas are:

- evaluator logging richness becoming a proxy for quality instead of correct caution and traceability
- runtime convenience gradually outranking evaluation-phase narrowness
- architecture or prompts implying more authority than the intent lock allows
- stronger option generation outrunning plugin qualification and missing-information handling

---

## Maintenance note

This file should stay short.

If it grows into a broad review checklist, split detailed guidance elsewhere and keep this page as the recurring “are we still building the right thing?” prompt.
