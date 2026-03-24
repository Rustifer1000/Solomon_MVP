# Post-Complete Divorce Corpus Review 025

## Purpose

This review was conducted after `D-B14` landed and the divorce corpus reached full template-family coverage.

The question was no longer whether the architecture can support the family set. The question was what the most important remaining gap is now that the divorce benchmark layer is family-complete.

---

## Short Answer

The divorce corpus is now structurally complete and impressively well anchored, but the next bottleneck is **evaluator-anchor asymmetry across the highest-stakes slices**, not missing slice breadth.

The repo is ready to stop adding divorce families.

The next best move is to make the committed evaluator/support-artifact layer more even across the most important higher-mode cases before shifting into practical trial work.

---

## What Is Strong

### 1. The divorce corpus is now family-complete

`TF-DIV-01` through `TF-DIV-12` are all represented by executable slices.

That is a major milestone. The corpus now includes:

- bounded package slices
- caution slices
- higher-mode co-handling slices
- hard-trigger handoff slices

### 2. The final hard-trigger distinctions are now visible

The current higher-mode cluster is meaningfully differentiated:

- `D-B08`: fairness/process breakdown
- `D-B12`: emotional flooding
- `D-B13`: coercion or safety-compromised participation
- `D-B14`: participation-capacity impairment

This is a much better evaluation set than a single generic “higher-mode” bucket.

### 3. The boundary work held

The shared/core boundary is in a materially better place than earlier in the project:

- artifact vocabulary no longer imports divorce package labels directly
- evaluator helpers are plugin-aware
- runtime/plugin/benchmark ownership is clear

### 4. The evaluator plane is now credible

The repo no longer has only runtime outputs. It now has:

- worked `evaluation.json` examples
- worked `evaluation_summary.txt` examples
- worked `expert_review.json` examples
- a standalone evaluator validator
- committed support-artifact references for selected higher-mode slices

That makes the repo much closer to something that can be reviewed, calibrated, and tried in practice.

---

## Main Remaining Gaps

### 1. Higher-mode evaluator anchoring is uneven

This is now the biggest gap.

`D-B14` is fully anchored:

- worked evaluation
- worked expert review
- committed support-artifact set

But the same is not true yet for all of the other high-value higher-mode slices.

Most notably:

- `D-B13` is a critical hard-trigger safety / voluntariness anchor but still lacks the same committed evaluator/support-artifact package depth
- `D-B12` is the emotional-flooding anchor and is still not committed at the same evaluator depth either

Why this matters:

- these are not peripheral slices
- they are part of the safety and escalation spine of the corpus
- practical trial work will be stronger if those anchors are just as reviewable as `D-B14`

### 2. Persona-model maturity is uneven across the corpus

`validate_persona_profiles.py` passes, but it still reports recommended-field warnings for older slices:

- `D-B05`
- `D-B06`
- `D-B07`
- `D-B08`
- `D-B09`

This is not a blocker for correctness right now, but it is the clearest maintenance-quality gap left in the persona layer.

Why it matters:

- later slices are richer and more evaluation-ready than earlier ones
- older slices could drift into “legacy benchmark” status unless the persona model is normalized

### 3. Practical-trial readiness is close, but not fully even

The corpus is now broad and well-tested enough that a first practical trial/validation pass is reasonable soon.

But the repo would be stronger going into that pass if:

- the critical higher-mode anchors were evaluator-complete in a more symmetric way
- the older persona profiles were brought up to the current recommended-field standard

---

## Ranking The Next Three Options

### 1. Evaluator anchor expansion

This is the best next move.

Why:

- it directly strengthens the highest-stakes slice cluster
- it improves trial-readiness
- it increases reviewer consistency where mistakes matter most

### 2. Persona-warning cleanup

This should come next unless it is bundled into trial prep.

Why:

- the warnings are now the most obvious remaining quality inconsistency in the divorce corpus
- they are maintenance debt, not architecture debt

### 3. First practical trial / validation pass

This is now close, but should follow at least one more anchor-strengthening pass.

Why:

- the repo is nearly ready
- but a practical trial will be more valuable if the safety-sensitive anchor set is more symmetric first

---

## Recommendation

Do **not** add more divorce slices.

The next phase should be:

1. expand the evaluator/support-artifact anchor set for the remaining high-value higher-mode slices, starting with `D-B13`
2. then clean up persona-profile recommended-field warnings in older slices
3. then run a first practical trial / validation pass on the complete divorce corpus

That is the best path from “family complete” to “practice ready.”

