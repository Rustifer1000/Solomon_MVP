# Evaluator Tool Runbook

## Purpose

This runbook explains how to use the repository's evaluator-side tools during the evaluation phase.

It is intended for:

- reference-example validation
- fairness-sensitive review preparation
- calibration support
- rerun comparison and regression discussion

---

## 1. Validate Worked Reference Evaluator Artifacts

Use:

```powershell
python tools\validate_reference_evaluator_artifacts.py
```

This checks committed reference examples such as:

- `evaluation.json`
- `evaluation_summary.txt`
- `expert_review.json`

Use this after editing any worked evaluator reference artifact.

---

## 2. Build A Fairness Review Seed From A Run Directory

Use:

```powershell
python tools\build_fairness_review_seed.py C:\path\to\run_output
```

This creates a compact fairness-review starting point from:

- `run_meta.json`
- `flags.json`
- `summary.txt`

Use this when:

- the case is fairness-sensitive
- fairness flags are active
- the evaluator wants a short structured prompt for further review

---

## 3. Build A Calibration Review Seed

Use:

```powershell
python tools\build_calibration_review_seed.py C:\path\to\evaluation.json
```

Or with expert review:

```powershell
python tools\build_calibration_review_seed.py C:\path\to\evaluation.json C:\path\to\expert_review.json
```

This helps identify whether a case should be discussed in calibration.

Use this when:

- an evaluator marked the case for calibration
- an expert review disagrees with the primary evaluation
- a benchmark anchor needs re-confirmation after runtime changes

---

## 4. Compare Two Benchmark Runs

Use:

```powershell
python tools\compare_benchmark_runs.py C:\path\to\run_a C:\path\to\run_b
```

This produces a compact comparison of:

- summary change
- open-missing-info delta
- flag-type change
- process-variant change

Use this as the first-pass rerun comparison before a fuller regression discussion.

---

## 5. Check Divorce Template-Family Coverage

Use:

```powershell
python tools\report_divorce_template_family_coverage.py
```

This reports:

- which first-pass divorce template families are currently covered
- which families are still missing

Use this before choosing the next divorce slice.

---

## 6. Suggested Review Order

1. Validate committed evaluator reference artifacts.
2. If a new run is fairness-sensitive, build a fairness review seed.
3. If a case is contested or anchor-like, build a calibration review seed.
4. If comparing reruns, use the benchmark comparison tool first.
5. Before requesting a new slice, check template-family coverage.

---

## 7. Current Worked Evaluator Anchors

- `D-B04`: caution-centered `M1` reference plus expert review
- `D-B05`: bounded-package `M0` reference evaluation
- `D-B06`: fairness-sensitive `M0` reference evaluation plus expert review

These are the current evaluator anchors the tools should be checked against first.
