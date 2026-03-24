# Contract 009: First-Pass Fairness Checks v0

## Purpose

This note defines the first-pass fairness checks for Solomon benchmark review.

It is intentionally lightweight. The goal is not a final fairness framework. The goal is to make fairness review more operational than implicit.

## First-pass fairness review questions

Evaluators or tools should inspect whether the reviewed artifact set preserves:

1. fairness-sensitive issue framing
2. one-sidedness, domination, or sidelining signals when present
3. balanced participation concerns in structured positions or facts
4. summary language that matches the fairness-sensitive artifact trail
5. escalation behavior that is proportionate rather than reflexive

## Minimum artifact touchpoints

First-pass fairness checks should look across at least:

- `positions.json`
- `facts_snapshot.json`
- `flags.json`
- `summary.txt`
- escalation posture in `run_meta.json` or `evaluation.json`

## Current fairness-sensitive anchor slices

The first pass should explicitly cover:

- `D-B06`
- `D-B08`
- `D-B10`

## Operational rule

Fairness checks should not assume that every fairness-sensitive slice must escalate.

They should help distinguish between:

- fairness-sensitive but workable sessions
- fairness/process-breakdown sessions that do require escalation

## Why this contract exists

The developer-ready evaluation spec calls out first-pass fairness checks as a recommended next artifact after template families and synthetic user role profiles. This note makes that recommendation concrete enough for tools and tests.
