# Post-D-B12 Spec Review 022

## Purpose

This review reassesses the repo after `D-B12` against the developer-ready evaluation specification, with a narrow focus on deciding the next family between:

- `TF-DIV-10` coercive-control / safety-compromised participation
- `TF-DIV-11` participation-capacity impairment

The question is not simply which family is still missing. It is which family the current corpus and runtime are now most ready to represent honestly.

---

## What The Repo Now Covers Well

The current corpus now includes:

- low-conflict package work
- narrow-settlement-zone caution
- financial confusion / unequal understanding
- emotional intensity that remains bounded
- asymmetry-sensitive caution
- domination / process-breakdown escalation
- legitimacy-sensitive escalation
- domain-complexity review
- emotional flooding with co-handling
- no-agreement-yet as a legitimate outcome

This is a strong evaluation-phase corpus. It now has meaningful contrast across:

- `M0`
- `M1`
- `M2`
- `M3`

and across several important divorce-specific failure modes.

---

## What The Spec Still Emphasizes

The specification continues to put strong weight on:

- fair participation
- self-determination
- safety and escalation
- honest source-of-truth artifacts
- evaluator-legible rationale for higher-mode handling

The remaining uncovered families are both hard-trigger families that push toward:

- `M4`
- possibly `M5`

So the next choice should go to the family the current architecture can represent with the least ambiguity and the highest evaluator legibility.

---

## Family Comparison

### `TF-DIV-10` Coercive-control or safety-compromised participation

This family is the stronger next move.

Why:

- The spec repeatedly treats compromised voluntariness and unsafe continuation as first-order evaluation concerns.
- The repo already has strong process, fairness, and escalation infrastructure.
- The missing major gap is not more escalation variety in general; it is a true hard-trigger safety family where continued mediation itself may be illegitimate.
- The current corpus already covers:
  - process domination
  - emotional flooding
  - informational asymmetry

What it does **not** yet cover is:

- a case where apparent participation is not meaningfully voluntary
- a case where calmness or compliance may itself be misleading
- a case where the system must prefer safety/handoff over continued mediation logic

Why the repo is ready enough:

- escalation modes beyond `M3` already exist
- continuity/support artifacts already exist
- evaluator-anchor infrastructure is mature
- synthetic persona profiles can now carry hidden fear / control dynamics more explicitly than before

Main implementation risk:

- this family is easy to under-model if it becomes just “severe conflict”
- it must preserve constrained agency, fear cues, and non-voluntary participation, not just hostility

Conclusion:

- highest-value next family
- most spec-aligned next move

### `TF-DIV-11` Participation-capacity impairment

This family should follow `TF-DIV-10`, not precede it.

Why:

- It is also high-stakes, but it is more vulnerable to ambiguous interpretation and overreach.
- It risks pulling the evaluation corpus toward quasi-clinical inference unless the artifact and evaluator guidance are very carefully bounded.
- The current repo does not yet have a strong dedicated layer for “meaningful participation impairment” cues that avoids diagnostic drift.

This family remains important, but sequencing it second has clear benefits:

- after a real safety/voluntariness slice is anchored, the repo can turn to capacity/competence boundaries with a cleaner hard-trigger comparison set
- evaluator guidance for `TF-DIV-11` will likely need to be more explicit than for `TF-DIV-10`

Conclusion:

- important
- but not the next slice

---

## Selection

The next family should be:

- `TF-DIV-10` coercive-control or safety-compromised participation

Recommended target posture:

- primary posture: `M4`
- category centered on safety / voluntariness loss
- with support artifacts oriented toward protected handoff rather than continued bounded mediation

---

## Why This Ordering Fits The Spec

This choice best reflects the spec’s priorities:

- safety and coercion should not remain abstract in a developer-ready evaluation corpus
- correct escalation to human handling is a success mode
- the system must not mistake constrained compliance for legitimate mediated participation

`TF-DIV-10` is therefore the clearest remaining missing anchor in the current corpus.

---

## Recommendation

Implement the next slice as `TF-DIV-10`, then add:

1. a worked evaluator anchor package
2. committed higher-mode support artifacts if appropriate
3. only then reassess `TF-DIV-11` as the final remaining hard-trigger family
