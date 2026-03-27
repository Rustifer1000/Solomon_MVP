# Reviewer Packet Format

## Purpose

This document defines the preferred reviewer-facing packet for practical use rounds.

It is designed for reviewers who may be:

- mediation-aware
- evaluator-capable
- not especially technical

The goal is to let a reviewer judge the session naturally without having to navigate raw JSON first.

This is a presentation-layer specification for review. It does **not** replace the underlying runtime artifacts.

---

## Core Principle

A reviewer should be able to understand the session in this order:

1. what kind of case this is
2. what happened in the session
3. what Solomon concluded
4. why that conclusion was reached
5. where to look deeper if something feels unclear

That means the reviewer should not begin with `evaluation.json`, `flags.json`, or other technical artifacts.

---

## Recommended Reviewer Packet Structure

Each practical-review packet should have three layers.

### Layer 1: Human-readable front packet

This is the default packet for a student reviewer, instructor, or mediation-aware human reviewer.

It should contain:

1. **Case cover sheet**
   - case id
   - short case title
   - case type / contrast purpose
   - review question
   - expected posture at a glance

2. **Session summary**
   - short readable summary of what happened
   - final posture
   - recommended next step

3. **Readable transcript**
   - a plain-language turn-by-turn rendering of the session
   - formatted as:
     - `Solomon:`
     - `Spouse A:`
     - `Spouse B:`

4. **Outcome rationale sheet**
   - why the posture was chosen
   - what the main concern was
   - what distinction matters for this slice

This layer should be enough for an initial judgment.

### Layer 2: Review support packet

This is the second layer when the reviewer wants more support or needs to confirm an impression.

It should contain:

- `expert_review.json`
- `evaluation_summary.txt`
- `briefs/early_dynamics_brief`
- `briefs/risk_alert_brief`
- `continuity/continuity_packet.json`

This layer explains the evaluator logic in a more disciplined way without forcing the reviewer into fully technical artifacts immediately.

### Layer 3: Technical appendix

This is only for deeper checking or disagreement resolution.

It should contain:

- `evaluation.json`
- `flags.json`
- `facts_snapshot.json`
- `positions.json`
- `run_meta.json`
- other structured runtime artifacts as needed

This layer should support audit and calibration, not drive the first impression.

---

## Recommended Review Order

For a technically naive reviewer, the natural order is:

1. case cover sheet
2. session summary
3. readable transcript
4. outcome rationale sheet
5. expert review
6. support briefs
7. technical appendix only if needed

This is different from the evaluator-engineering order.

The evaluator-engineering order tests artifact sufficiency.
The reviewer-packet order tests practical human usability.

Both are valid, but they serve different purposes.

---

## What Is Missing In The Current Repo

The current repository is strong on:

- runtime artifact generation
- evaluator reference packages
- support-artifact anchoring
- schema and consistency validation

But it is still thin on reviewer-facing presentation.

In particular, the current system does not yet reliably provide:

- a plain-language cover sheet per run
- a reviewer-ready readable transcript
- a one-page rationale sheet that sits between summary and expert review

These are the most natural next additions if practical review is going to involve students or other less technical reviewers.

---

## Suggested Generated Reviewer Files

For each practical-use run, the ideal generated reviewer packet would include:

- `review_cover_sheet.txt`
- `review_transcript.txt`
- `review_outcome_sheet.txt`

Optional later additions:

- `review_packet_index.txt`
- `review_packet.pdf`

These should be generated from the existing runtime artifacts, not authored independently.

---

## Minimal First Version

The smallest useful first version is:

1. generate a readable transcript from `interaction_trace.json`
2. generate a short cover sheet from `case_metadata.json`, `run_meta.json`, and `summary.txt`
3. generate a short outcome sheet from `summary.txt`, `evaluation_summary.txt`, and `expert_review.json`

This would make the current system much more usable for real review without requiring a full UI.

---

## Relationship To The Practical Review Worksheet

Use this packet format together with:

- [06_Divorce Practical Review Worksheet.md](./06_Divorce%20Practical%20Review%20Worksheet.md)

The packet format makes review intuitive.
The worksheet makes review comparable across cases and reviewers.

Both are needed.

---

## Recommendation

Before building a UI, prefer:

1. a generated reviewer packet
2. repeated dry-run review with technically light reviewers
3. observation of where navigation or interpretation still breaks down

Only after that should the project decide whether a lightweight review UI is justified.
