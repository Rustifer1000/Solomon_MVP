# STAGE5-DESIGN-042: Safety Monitor as Dedicated Agent

**Date:** 2026-03-28
**Status:** Design — not yet implemented
**Supersedes:** ARCH-007 §5 (sketch only)
**Authored by:** Design session following Stage 3/4 completion and codebase review

---

## 1. Context

Stages 3 and 4 completed the option generation architecture: domain_reasoner qualifies options, option_generator brainstorms unconstrained pools, and escalation.py routes sessions via a rule-based priority cascade. The full pipeline is:

```
orchestrator
  → plugin.assess_state(state)        → plugin_assessment
  → escalation.determine_escalation() → escalation_result
  → domain_reasoner.run()             → pre_computed_domain_analysis
  → option_generator.run()            → brainstormer_pool   [Stage 4]
  → lm_engine.run_turn()              → CandidateTurn
```

The adversarial red-team corpus (D-B-RT01/02/03) exposed a structural gap: none of the three failure modes tested (AF-1, AF-2, AF-3) are detectable by the current rule-based flag/escalation layer. All three require cross-turn pattern synthesis that a stateless cascade cannot perform.

Stage 5 introduces the **safety monitor** as a dedicated agent to fill this gap.

---

## 2. What Stage 5 Adds

### 2.1 The Gap

`escalation.py` operates on flags that are *already set*. `build_case_flag_templates()` fires on per-turn signals. No component currently observes the interaction history across turns to detect structural adversarial patterns.

The three adversarial patterns require cross-turn observation:

| Case | Failure Mode | Required Detection |
|------|-------------|-------------------|
| D-B-RT01 | AF-3: Premature option pressure | Party B's accumulated interests contain no independently-stated entries — detectable only by reviewing all of Party B's prior turns together |
| D-B-RT02 | AF-2: Deflection as leverage | Party A deflected the *same disclosure request* across T5 and T7 using different tactics — detectable only by tracking the request across turns |
| D-B-RT03 | AF-1: Coercion masking cooperation | Party B's T6 discordant signal was suppressed by Party A's T7 reframe — detectable only by comparing Party B's T6 statement against Party B's T8 compliance |

### 2.2 What the Safety Monitor Does

The safety monitor is a dedicated LM agent that:

1. **Observes the full interaction history** at each assistant turn
2. **Detects structural adversarial patterns** that per-turn flag logic cannot see
3. **Writes safety signals to party_state** before the domain_reasoner runs
4. **Raises flags** that the escalation cascade can act on
5. **Produces a structured output** (SafetyMonitorResult) stored in `reasoning_trace`

The escalation cascade and domain_reasoner remain unchanged. The safety monitor is additive — it feeds inputs to existing components rather than replacing them.

---

## 3. Proposed Pipeline Position

The safety monitor runs **before** plugin assessment so its flags are visible to the escalation cascade:

```
orchestrator
  → safety_monitor.run(state, interaction_history)  → SafetyMonitorResult   [NEW Stage 5]
      (writes flags to state, writes signals to party_state)
  → plugin.assess_state(state)                       → plugin_assessment
  → escalation.determine_escalation()                → escalation_result
  → domain_reasoner.run(state)                       → pre_computed_domain_analysis
  → option_generator.run(state)                      → brainstormer_pool
  → lm_engine.run_turn()                             → CandidateTurn
```

**Rationale for this position:**
- Safety monitor outputs (flags) must be visible to `determine_escalation()` — so it must precede `plugin.assess_state()`
- Safety monitor outputs (party_state signals) must be visible to `domain_reasoner` — so it must precede `domain_reasoner.run()`
- Safety monitor reads `state` and `interaction_history` only — it has no dependency on prior pipeline stages

---

## 4. Input/Output Contract

### 4.1 Inputs

```python
class SafetyMonitorInput:
    state: dict                    # current session state (summary_state, flags, missing_info, etc.)
    interaction_history: list      # all prior turns in interaction_trace format
    turn_index: int                # current turn being evaluated
    case_id: str
    session_id: str
```

### 4.2 Output: SafetyMonitorResult

```python
@dataclass
class SafetyMonitorResult:
    schema_version: str            # "safety_monitor.v0"
    case_id: str
    session_id: str
    turn_index: int
    generated_at: str              # ISO datetime

    # Pattern detection
    compliance_pattern: CompliancePattern | None
    deflection_pattern: DeflectionPattern | None
    discordant_signals: list[DiscordantSignal]

    # Actions
    flags_raised: list[str]        # flag_types to add to state.flags
    party_state_signals: list[str] # signals to write to party_state.signals
    veto_recommendation: str | None  # None | "CATEGORY 1" | "CATEGORY 2" | "CATEGORY 3"
    veto_reason: str | None

    # Diagnostic
    monitor_confidence: str        # "low" | "moderate" | "high"
    monitor_notes: str
```

### 4.3 Sub-structures

```python
@dataclass
class CompliancePattern:
    detected: bool
    party: str                     # "A" | "B" | "both"
    evidence_turns: list[int]
    pattern_type: str              # "reactive_only" | "acceptance_only" | "reactive_with_independent"
    severity: str                  # "low" | "moderate" | "high"

@dataclass
class DeflectionPattern:
    detected: bool
    deflecting_party: str
    target_request_turn: int       # turn where the original request was made
    deflection_turns: list[int]
    deflection_tactics: list[str]  # "complexity_reframe" | "timing_deflection" | "urgency_pressure"
    pattern_confirmed: bool        # True when ≥2 distinct deflection tactics observed

@dataclass
class DiscordantSignal:
    party: str
    signal_turn: int
    signal_summary: str
    was_reframed: bool
    reframe_turn: int | None
    reframe_party: str | None
    return_to_compliance: bool
    compliance_turn: int | None
```

---

## 5. Veto Category Mapping

The CATEGORY 1/2/3 veto logic currently lives implicitly in the domain_reasoner's system prompt. Stage 5 makes it explicit in the safety monitor:

| Category | Pattern | Trigger Condition |
|----------|---------|-----------------|
| CATEGORY 1 | Compliance-only party | `compliance_pattern.detected=True` AND `pattern_type="acceptance_only"` OR `pattern_type="reactive_only"` with `severity="high"` |
| CATEGORY 2 | Information asymmetry used as leverage | `deflection_pattern.detected=True` AND `deflection_pattern.pattern_confirmed=True` (≥2 distinct tactics) |
| CATEGORY 3 | Discordant signal suppressed | `len(discordant_signals) > 0` AND any `DiscordantSignal.was_reframed=True` AND `return_to_compliance=True` |

The safety monitor writes `safety_veto_applied=True` and `safety_veto_reason=<category>` to party_state signals when a category is triggered. The domain_reasoner reads these and sets `option_readiness="blocked"`.

---

## 6. Persistence: SafetyMonitorResult in reasoning_trace

The SafetyMonitorResult is persisted inside `interaction_trace.json` under `reasoning_trace.safety_monitor_result` per turn — analogous to `reasoning_trace.pre_computed_domain_analysis`. It is **not** emitted as a standalone artifact.

Schema stub for validation purposes will be at `schema/safety_monitor.schema.json`.

---

## 7. Relationship to Existing Components

### 7.1 escalation.py — No changes required

The escalation cascade operates on `state.flags`. The safety monitor raises flags before the cascade runs. No changes to `determine_escalation()`.

### 7.2 domain_reasoner.py — Minimal change

The domain_reasoner's system prompt currently contains CATEGORY 1/2 veto descriptions that ask the LM to detect these patterns directly. In Stage 5, the safety monitor does this detection. The domain_reasoner system prompt should be updated to:
- Trust `safety_veto_applied` signal from party_state when present
- Remove its own CATEGORY 1/2 detection obligation (it will still receive the signal)
- Remain the owner of `option_readiness` determination

This prevents double-detection and removes complexity from the domain_reasoner prompt.

### 7.3 plugin layer — No changes required

The plugin's `build_case_flag_templates()` operates on per-turn risk signals from `CandidateTurn.risk_check.signals`. The safety monitor operates on interaction history. These are orthogonal.

The safety monitor's raised flags are structured the same way as plugin flags and merged via the existing `merge_flag_templates()` utility. No plugin changes needed.

### 7.4 option_generator.py — No changes required

The brainstormer is safety-agnostic. It runs after the safety monitor outputs are already in state.

---

## 8. When Does the Safety Monitor Make an LM Call?

The safety monitor makes an LM call every assistant turn (like the domain_reasoner). However, unlike the domain_reasoner, pattern detection is primarily backward-looking (history scan) rather than forward-looking (option readiness). This means:

- **Turn 1**: No interaction history — safety monitor returns null/low-confidence result
- **Turn 2-3**: Limited history — can detect early compliance signals but low confidence
- **Turn 4+**: Sufficient history for pattern detection — confidence increases

The safety monitor's LM call is cheaper than the domain_reasoner call: it does not need to enumerate qualified candidates, just detect patterns and raise signals.

**Proposed token budget:** 1500-2000 tokens for the safety monitor output (vs. 6000 for domain_reasoner). Total per-turn LM spend increases from ~2 calls to ~3 calls for Stage 5 sessions.

---

## 9. Open Design Questions

### 9.1 Prompt architecture
Should the safety monitor use a dedicated system prompt (like domain_reasoner) or a structured JSON-output prompt? Recommendation: dedicated system prompt with JSON output instruction — consistent with domain_reasoner pattern.

### 9.2 Cross-turn state summary
The safety monitor receives full interaction history. Should it also receive a pre-summarized "party narrative" (e.g., "Party B's expressed interests across all turns") or process raw turns? Recommendation for v0: raw turns with a compact summary prefix. Revisit if prompt size becomes an issue.

### 9.3 False positive risk
CATEGORY 1 could over-fire on sessions where one party genuinely agrees with the other's proposal. The trigger condition must require multiple turns of the pattern, not a single acceptance turn. The `severity` field is the control: only `severity="high"` (≥3 turns of reactive-only) triggers the veto.

### 9.4 Safety monitor failure mode
If the safety monitor LM call fails (like option_generator), it must fail safe: return a null result with `monitor_confidence="low"`, log to stderr, and let the pipeline continue with existing escalation behavior. It must NOT block the session.

### 9.5 Audit trail
When the safety monitor raises a flag or veto, the evaluator needs to see *why*. The `evidence_turns`, `deflection_tactics`, and `veto_reason` fields in SafetyMonitorResult serve this purpose. The reviewer transcript renderer (Stage 3) should include safety monitor output in the review packet.

---

## 10. Adversarial Validation Plan

Stage 5 adversarial validation runs the three existing RT sessions through the Stage 5 pipeline and verifies:

| Session | Expected Change from Stage 3 baseline |
|---------|--------------------------------------|
| D-B-RT01-S01 | CATEGORY 1 veto fires at T5 (currently relies on domain_reasoner behavioral catch — Stage 5 makes it structural) |
| D-B-RT02-S02 | CATEGORY 2 veto fires at T7 (one turn earlier than Stage 3 baseline T9, since pattern is confirmed after 2nd deflection) |
| D-B-RT03-S01 | CATEGORY 3 veto fires at T9 after discordant signal suppression detected |

All three should remain PASS. The delta is that the veto mechanism fires structurally rather than behaviorally.

---

## 11. Implementation Sequence

Stage 5 work items (in order):

1. **schema/safety_monitor.schema.json** — write schema stub based on §4.2/4.3 above
2. **runtime/engine/safety_monitor.py** — implement SafetyMonitorResult dataclass + system prompt + LM call
3. **runtime/orchestrator.py** — insert safety_monitor.run() before plugin.assess_state()
4. **runtime/artifacts.py** — persist SafetyMonitorResult in reasoning_trace
5. **runtime/engine/domain_reasoner.py** — update system prompt to trust party_state veto signals, remove own CATEGORY 1/2 detection obligation
6. **runtime/engine/reviewer_transcript_rendering.py** — add safety monitor section to review packet
7. **tests/test_end_to_end.py** — add TestSafetyMonitor unit tests (null result, CATEGORY 1 trigger, CATEGORY 2 trigger, CATEGORY 3 trigger, failure-safe behavior)
8. **RT adversarial validation** — run D-B-RT01/02/03 through Stage 5 pipeline and evaluate

---

## 12. Success Criteria

Stage 5 is complete when:

- SafetyMonitorResult is produced per turn and stored in reasoning_trace
- CATEGORY 1 veto fires structurally on D-B-RT01 (not relying on domain_reasoner behavioral detection)
- CATEGORY 2 veto fires at or before T7 on D-B-RT02 (confirmed deflection pattern)
- CATEGORY 3 fires structurally on D-B-RT03 (discordant signal + reframe suppression)
- Safety monitor failure (LM exception) is fail-safe — pipeline continues
- All existing Stage 3/4 benchmarks remain PASS (non-adversarial sessions unaffected)
- Composite scores for non-adversarial cases do not regress
