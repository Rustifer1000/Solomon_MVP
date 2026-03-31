# Codebase Review 045

**Date:** 2026-03-30
**Scope:** Full review following Stages 3–6 and ARCH-006 Option 1
**Status:** Findings confirmed — awaiting fix pass

This is the first structured review since Stage 4 (Track 1-5 fixes). Four agents have been added or significantly modified since then: `safety_monitor.py`, `perception_agent.py`, plus wiring across `orchestrator.py`, `lm_engine.py`, `domain_reasoner.py`, `option_generator.py`, `prompt_builder.py`, `artifacts.py`.

Findings are presented by track, each with file + line, severity, description, and fix.

---

## Track 1 — Stage 3 Fallback: Option Label Field Name Mismatch

**File:** `runtime/engine/prompt_builder.py:303`
**Severity:** Major

**What it is:**

The domain analysis context section in the prompt has two code paths. The Stage 4 path (lines 293–295) calls `_render_option_pool()` when `option_pool_qualification` is present. The Stage 3 fallback path (lines 297–306) renders `qualified_candidates` directly, used when the brainstormer pool was empty or the domain reasoner ran in Stage 3 mode.

Line 303:
```python
f"  [{c.get('confidence','?')}] {c.get('option_label','?')}: "
```

`domain_reasoner._normalize_candidate()` (lines 507–516) unconditionally normalizes `option_label → label` on every candidate before returning. By the time candidates reach `prompt_builder.py`, the field is named `label`, not `option_label`. The Stage 3 path therefore always renders the label column as `?`.

This matters for any session where the brainstormer is not active: T1 (prior_party_state is None), turns where the brainstormer failed silently (D-B04-S05 case documented in STAGE4-FINDINGS-041), or any future session where the Stage 3 fallback is intentionally triggered. The main model then receives `?` as the option label in its domain analysis prior.

**Fix:**

```python
# prompt_builder.py line 303
f"  [{c.get('confidence','?')}] {c.get('label','?')}: "
```

---

## Track 2 — `compliance_only_pattern` Flag Unhandled in determine_escalation()

**File:** `runtime/escalation.py` (no handler) vs `runtime/engine/safety_monitor.py:511–519` (flag registered T2/E1)
**Severity:** Major

**What it is:**

The safety monitor registers `compliance_only_pattern` with `threshold_band: "T2"` and `related_categories: ["E1"]` in `_FLAG_TYPE_METADATA` (lines 512–519). When CATEGORY 1 is detected, this flag is raised and merged into `state["flags"]` via `build_safety_monitor_flag_templates()` and `merge_flag_templates()`.

`determine_escalation()` in `escalation.py` reads `active_flag_types` from `state["flags"]` and has explicit handlers for: `irrecoverable_breakdown`, `acute_safety_concern`, `coercion_or_intimidation`, `participation_incapacity`, `fairness_breakdown`, `repeated_process_breakdown`, `explicit_human_request`, `domain_complexity_overload`, `role_boundary_pressure`, `decision_quality_risk`, `insufficient_information`.

There is no handler for `compliance_only_pattern`. A session where the safety monitor detects sustained CATEGORY 1 pattern and raises this flag will see the flag land in `state["flags"]` with `threshold_band T2` and then fall straight through `determine_escalation()` to `M0`.

The structural option-blocking veto — the safety monitor's primary protection — still works correctly via `party_state_signals → domain_reasoner → option_readiness="blocked"`. But the session escalation mode does not reflect the detected compliance pattern. A reviewer examining the session state will see M0 alongside an active `compliance_only_pattern` flag, which is inconsistent: the flag metadata says T2/E1 but the escalation is M0.

**Fix:**

Add a handler in `escalation.py` for `compliance_only_pattern`, mapping it to at least M1 with a specific rationale. Placement: after the `role_boundary_pressure` handler, before the `caution_reasons` block:

```python
if "compliance_only_pattern" in active_flag_types:
    return {
        "category": "E1",
        "threshold_band": "T2",
        "mode": "M1",
        "rationale": (
            "Elevated caution is warranted because the safety monitor detected a sustained "
            "compliance-only pattern: one party has not independently articulated their own "
            "interests across multiple turns. Continued autonomous handling requires care to "
            "ensure genuine consent."
        ),
    }
```

Note: M1 (elevated caution) rather than M2+ is the correct starting point — CATEGORY 1 is a pattern concern, not an active coercion event. The test cases (D-B-RT01) confirm that CATEGORY 1 should not trigger a hard veto when the pattern is a false positive; M1 preserves that distinction.

---

## Track 3 — `_last_option_readiness()` Defined but Never Called

**File:** `runtime/engine/lm_engine.py:646–663`
**Severity:** Minor

**What it is:**

`_last_option_readiness()` reads the prior turn's `option_readiness` from the reasoning trace to allow the brainstormer guard to skip generation when the domain analysis previously said `"blocked"`. The function is correctly implemented — it iterates the trace buffer in reverse, finds the last assistant turn's `pre_computed_domain_analysis`, and returns its `option_readiness`.

It is never called. The brainstormer guard at lines 146–157 only checks `prior_party_state is not None`. As a result, the brainstormer runs on every turn where party state exists, including turns where the previous domain analysis applied a safety veto (`option_readiness="blocked"`). The domain reasoner then re-applies the veto immediately, correctly blocking options — but only after the brainstormer has already made an API call and generated candidates.

This is confirmed by D-B-RT02 and D-B-RT03 diagnostics: the brainstormer generates candidates at T9 which the domain reasoner correctly blocks via safety veto. The correctness is maintained; the efficiency is not.

**Fix:**

Call `_last_option_readiness(state)` in the brainstormer guard:

```python
# lm_engine.py lines 146–157 — replace with:
if prior_party_state is not None and _last_option_readiness(state) != "blocked":
    brainstormer_pool = generate_option_pool(...)
else:
    brainstormer_pool = []
```

The guard comment should be updated to explain both conditions.

---

## Track 4 — Perception Notes Not Injected into Domain Reasoner Context

**File:** `runtime/engine/domain_reasoner.py:348–363`
**Severity:** Minor

**What it is:**

`generate_domain_analysis()` accepts `perception_agent_result` and extracts individual party-level signals from it (lines 348–363): `inferred_interests`, `inferred_concerns`, `unsaid_signals` for each party. These are injected into the domain context so the domain reasoner can reference them during option qualification.

The perception agent also produces a `perception_notes` list — the most important synthesized observations the perception agent identified, representing items the mediator must hold before responding. These notes are injected into the main LM's prompt (via `prompt_builder.py` lines 365–373) but are NOT injected into the domain reasoner's context.

The domain reasoner therefore has access to the raw party signals (inferred interests, concerns) but not the perception agent's synthesis judgment (what matters most this turn). For option qualification, the synthesis sometimes carries signals that the raw party fields don't express directly — for example, "engagement_quality=compliant_only is present at T9 but only confirmed across three prior turns" is a `perception_note` that is not captured in any individual party field.

**Fix:**

In `domain_reasoner.py`, after the existing party signal injection block (around line 363), add:

```python
perception_notes = (
    perception_agent_result.get("perception_notes", [])
    if perception_agent_result and not perception_agent_result.get("_null_result")
    else []
)
if perception_notes:
    parts.append("PERCEPTION AGENT KEY OBSERVATIONS:")
    for note in perception_notes:
        parts.append(f"  - {note}")
    parts.append("")
```

---

## Track 5 — Silent Exception Swallow in Orchestrator min_phase Fallback

**File:** `runtime/orchestrator.py:89`
**Severity:** Minor

**What it is:**

The orchestrator calls `simulation.generate_runtime_assistant_turn()` to get the reference simulation's expected phase (used as a minimum floor for the LM-generated turn). This is wrapped in a broad `except Exception:` with no logging (line 89):

```python
except Exception:
    min_phase = "info_gathering"
```

If the simulation raises for any unexpected reason — not just "this turn isn't scripted" but also import errors, state corruption, or API failures — the exception is silently swallowed, the phase floor is dropped, and the session continues. No log entry is produced, making it impossible to diagnose from session artifacts alone.

The phase floor is a safety mechanism (prevents the LM from lagging behind scripted client turn progression). Silent failure here means LM phase regression can occur without any observable diagnostic signal.

**Fix:**

```python
except Exception as e:
    import sys
    print(f"[orchestrator] T{plan_entry.turn_index} min_phase fallback: {e}", file=sys.stderr)
    min_phase = "info_gathering"
```

---

## Track 6 — Test Coverage Gaps for Stage 5 and Stage 6 Integration

**File:** `tests/test_end_to_end.py`
**Severity:** Major

**What it is:**

The test file has solid unit-level coverage for the safety monitor (lines 3683–3836) and perception agent (lines 3852–4036) in isolation — null result shapes, schema validity, flag template construction, action derivation. What is absent is integration-level coverage: tests that verify the agents operate correctly when wired together through the pipeline.

**Gap 1 — Safety monitor → domain reasoner signal path:**

No test verifies that `party_state_signals` from the safety monitor result are extracted and passed to `generate_domain_analysis()`. This is the primary structural guarantee (ARCH-007 §3): the safety monitor's veto signals must reach the domain reasoner. The unit tests confirm signal derivation in isolation but do not confirm the signal path through `lm_engine.py:165–168`.

**Gap 2 — `compliance_only_pattern` → escalation:**

No test verifies the escalation cascade behaviour when `compliance_only_pattern` is in `state["flags"]`. This is especially relevant given Track 2 above: the flag currently falls through to M0 with no handler in `determine_escalation()`. Adding the handler in Track 2 will need a test to cover it.

**Gap 3 — Brainstormer skip when option_readiness="blocked":**

After the Track 3 fix is applied, a test should verify that `_last_option_readiness()` causes the brainstormer to return `[]` when the prior domain analysis blocked options. Currently there is no such test.

**Gap 4 — Perception agent notes injection into main prompt:**

No test verifies that `perception_notes` from a non-null perception agent result appear in the turn prompt passed to the main LM. The extraction via `extract_perception_notes()` is tested (lines 4007–4019) but not the downstream injection via `build_turn_prompt()`.

**Gap 5 — Agent failure graceful degradation:**

No tests verify what happens when any single agent raises an exception: safety monitor failure (should proceed with null result, no crash), perception agent failure (should proceed with scaffold perception), domain reasoner failure (should use fallback). The except-and-return pattern in each agent is correct per code inspection, but no test exercises these paths.

**Recommended additions:**

| Test | Class | What it verifies |
|---|---|---|
| `test_safety_monitor_signals_passed_to_domain_reasoner` | existing unit test class | Construct a mock safety_monitor_result with a non-empty `party_state_signals`; call `generate_lm_assistant_turn` with it mocked; verify `safety_signals` appears in the domain_reasoner call |
| `test_compliance_only_flag_triggers_m1_escalation` | `TestDetermineEscalation` or new | Add `compliance_only_pattern` flag to state; verify `determine_escalation()` returns M1 |
| `test_brainstormer_skipped_when_prior_blocked` | new `TestOptionGeneratorGuard` | Construct state with prior assistant turn showing `option_readiness="blocked"`; verify brainstormer returns `[]` after Track 3 fix |
| `test_perception_notes_in_turn_prompt` | new | Call `build_turn_prompt()` with a non-null perception_agent_result containing perception_notes; verify notes appear in the returned messages |
| `test_safety_monitor_failure_does_not_crash_session` | new | Pass a safety_monitor_result that raises on `.get()`; verify session completes with null safety context |

---

## Summary

| # | Track | File | Severity | Fix |
|---|---|---|---|---|
| 1 | Stage 3 fallback: option_label vs label | `prompt_builder.py:303` | **Major** | Change `option_label` → `label` |
| 2 | `compliance_only_pattern` unhandled in escalation | `escalation.py` | **Major** | Add M1 handler for compliance_only_pattern flag |
| 3 | `_last_option_readiness()` never called | `lm_engine.py:146` | Minor | Call in brainstormer guard |
| 4 | Perception notes not injected into domain reasoner | `domain_reasoner.py:363` | Minor | Inject perception_notes into domain context |
| 5 | Silent exception swallow, min_phase fallback | `orchestrator.py:89` | Minor | Log exception before fallback |
| 6 | Test gaps: Stages 5/6 pipeline integration | `test_end_to_end.py` | **Major** | Add 5 integration tests |

Findings 1, 2, 6 are actionable now. Findings 3 and 4 are correct-direction improvements that carry small risk (both are additive). Finding 5 is a one-line diagnostic improvement.

No findings affect the constraint gate results (the constraint gate runs source="runtime", not source="lm_runtime", so Stages 5/6 agents are not exercised by it). The Stage 3 fallback bug (Finding 1) would have been visible if any constraint gate session hit the Stage 3 path with a null brainstormer pool.
