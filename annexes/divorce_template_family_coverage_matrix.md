# Divorce Template Family Coverage Matrix

## Purpose

This matrix links the currently implemented divorce benchmark slices to the first-pass divorce template families.

It is intended to support:

- next-slice selection by coverage need
- evaluator calibration planning
- regression corpus planning

---

## Current Slice Coverage

| Slice | Primary family | Secondary family links | Notes |
| --- | --- | --- | --- |
| `D-B04` | `TF-DIV-04` Narrow parenting settlement zone | `TF-DIV-01` Cooperative co-parenting scheduling | Bespoke anchor slice stressing school-week logistics, fairness, and phased trial caution. |
| `D-B05` | `TF-DIV-01` Cooperative co-parenting scheduling | `TF-DIV-04` Narrow parenting settlement zone | Patterned `M0` package slice focused on school-break process design and bounded packaging. |
| `D-B06` | `TF-DIV-01` Cooperative co-parenting scheduling | `TF-DIV-04` Narrow parenting settlement zone | Communication/fairness package slice with extracurricular decision protocol stress. |
| `D-B07` | `TF-DIV-02` Financial confusion and unequal understanding | `TF-DIV-12` No-agreement-yet is the correct result | Child-expense coordination and reimbursement workflow slice. |
| `D-B08` | `TF-DIV-06` Repeated interruption and procedural domination | `TF-DIV-07` Legitimacy/trust challenge to AI-only handling | Escalation-sensitive slice stressing repeated interruption, fairness breakdown, and human co-handling. |
| `D-B09` | `TF-DIV-08` Domain complexity beyond safe autonomy | `TF-DIV-02` Financial confusion and unequal understanding | Escalation-sensitive slice stressing issue coupling, human review, and bounded-autonomy limits without process collapse. |
| `D-B10` | `TF-DIV-03` Emotionally charged but still workable divorce | `TF-DIV-04` Narrow parenting settlement zone | Emotionally intense but still bounded slice proving that strong heat does not automatically justify escalation. |
| `D-B11` | `TF-DIV-05` High asymmetry / dependent spouse | `TF-DIV-02` Financial confusion and unequal understanding | Asymmetry-sensitive caution slice stressing informed participation, confidence imbalance, and document access. |
| `D-B12` | `TF-DIV-09` Severe emotional flooding with possible co-handling need | `TF-DIV-03` Emotionally charged but still workable divorce | Escalation-sensitive slice stressing emotional flooding, repeated failed repair, and dignity-preserving transition to human co-handling. |
| `D-B13` | `TF-DIV-10` Coercive-control or safety-compromised participation | `TF-DIV-05` High asymmetry / dependent spouse | Hard-trigger safety slice stressing constrained voluntariness, fear-based participation, and protected human handoff. |
| `D-B14` | `TF-DIV-11` Participation-capacity impairment | `TF-DIV-03` Emotionally charged but still workable divorce | Hard-trigger capacity slice stressing impaired reliability, unstable orientation, and the need to stop autonomous mediation without coercion framing. |

---

## Covered Families

- `TF-DIV-01`
- `TF-DIV-02`
- `TF-DIV-04`
- `TF-DIV-06`
- `TF-DIV-07` (secondary coverage via `D-B08`)
- `TF-DIV-08`
- `TF-DIV-09`
- `TF-DIV-10`
- `TF-DIV-11`
- `TF-DIV-03`
- `TF-DIV-05`
- `TF-DIV-12` (light partial coverage only)

## Families Not Yet Represented By An Executable Slice

- None

---

## Recommended Use

- Treat `D-B04` through `D-B07` as the current broad-but-limited calibration core.
- Use the current set as the first family-complete divorce slice corpus, while still expecting evaluator and artifact anchors to deepen over time.
