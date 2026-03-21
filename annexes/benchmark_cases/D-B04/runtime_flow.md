# D-B04 Runtime Flow

## Purpose

This document defines the expected first-pass runtime flow for the `D-B04` reference slice.

It is intended to answer:

- what the minimum runtime should do in sequence
- what artifacts should be updated at each stage
- where the core, plugin, and platform each matter most

## Runtime objective for D-B04

The runtime should show that Solomon can:

- identify the parenting-schedule conflict accurately
- distinguish positions from interests
- surface unresolved logistics before overcommitting to solutions
- use plugin qualification to constrain option work
- continue in a defensible `M1` caution posture unless stronger triggers emerge

## Recommended first-pass sequence

### 1. Session framing
The runtime should:

- explain Solomon's role and limits
- state that the parties remain decision-makers
- set a basic structure for discussing the dispute

Primary pressures:

- `C1`
- `C10`

Primary artifacts affected:

- `interaction_trace.json`
- `summary.txt`

### 2. Initial issue capture
The runtime should identify and separate at least:

- parenting schedule
- school-week stability concerns
- logistics or transportation uncertainty
- fairness and parenting-role concerns

Primary pressures:

- `C2`
- `P1`

Primary artifacts affected:

- `positions.json`
- `facts_snapshot.json`
- `interaction_trace.json`

### 3. Interest elicitation pass
The runtime should surface:

- child stability concerns
- fairness and meaningful-parent-role concerns
- predictability needs
- sensitivity to perceived bias or pressure

Primary pressures:

- `C3`
- `C6`

Primary artifacts affected:

- `interaction_trace.json`
- `summary.txt`
- optional early evaluator notes later

### 4. Plugin qualification pass
The plugin should qualify the dispute in domain-sensitive terms by identifying:

- parenting-schedule structure
- school logistics as a material feasibility constraint
- any early caution around overcommitting to overnight expansion

Primary pressures:

- `P2`
- `P3`
- `P4`

Primary artifacts affected:

- `missing_info.json`
- `flags.json` if caution-worthy risk is present
- `interaction_trace.json`

### 5. Missing-information checkpoint
Before strong option advancement, the runtime should explicitly record unresolved questions such as:

- school commute realities
- exchange timing reliability
- homework/routine feasibility

Primary pressures:

- `C8`
- `P4`
- `I4`

Primary artifacts affected:

- `missing_info.json`
- `summary.txt`
- `interaction_trace.json`

### 6. Early option exploration under caution
The runtime may explore:

- phased changes
- contingent trial arrangements
- logistics-conditioned options

The runtime should not:

- present one fixed outcome as the answer
- treat unresolved logistics as already solved
- push agreement for speed

Primary pressures:

- `C5`
- `P3`
- `I4`

Primary artifacts affected:

- `interaction_trace.json`
- `summary.txt`
- optional option references in positions or notes

### 7. Escalation posture decision
For the reference slice, the preferred first-pass posture is:

- `M1` continue with caution

Acceptable alternative:

- `M0` only if the runtime still preserves uncertainty and does not overstate feasibility

The runtime should not escalate above `M1` unless additional evidence emerges that materially changes the case posture.

Primary pressures:

- `C9`
- `I2`

Primary artifacts affected:

- `flags.json`
- `interaction_trace.json`
- `summary.txt`

### 8. Session close or bounded next-step state
The runtime should end the slice by making explicit:

- what remains unresolved
- what information is still needed
- what bounded next step is appropriate

Primary pressures:

- `C8`
- `C10`

Primary artifacts affected:

- `summary.txt`
- `missing_info.json`
- `evaluation.json` later

## Expected artifact set for the reference run

Required:

- `run_meta.json`
- `interaction_trace.json`
- `positions.json`
- `facts_snapshot.json`
- `flags.json`
- `missing_info.json`
- `summary.txt`

Recommended:

- `evaluation.json`
- `evaluation_summary.txt`

Conditional:

- continuity packet only if the run escalates beyond `M1`

## Failure patterns this flow is meant to expose

- option generation outruns missing information
- plugin qualification fails to constrain the runtime
- fairness or neutrality slips into subtle steering
- artifacts do not preserve the reason for the caution posture
- evaluators cannot reconstruct why the runtime stayed at `M0` or `M1`
