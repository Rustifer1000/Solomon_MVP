"""
runtime.engine.lm_engine
=========================
Anthropic API client + output parser for Solomon's LLM turn generator.

Wired into the orchestrator via source="lm_runtime".  The deterministic
benchmark simulation paths (source="runtime", source="reference") are
unaffected.

Model selection
---------------
Default model: claude-sonnet-4-5 (balanced quality/cost for evaluation runs)
Fast model:    claude-haiku-4-5   (for rapid iteration and testing)

Both can be overridden via the SOLOMON_LM_MODEL environment variable.

Output contract
---------------
generate_lm_assistant_turn() returns a raw turn dict that normalises into
a CandidateTurn via the existing normalize_core_output() pipeline.

The five-step reasoning is preserved in two forms:
- interaction_observations_delta: string-tag observations (backward compat)
- reasoning_trace: structured per-turn object per CONTRACT-014 §8

The reasoning_trace field is present only for lm_runtime turns and is
additive — it does not replace any existing turn field.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import anthropic
from dotenv import dotenv_values

from .perception import PerceptionContext, build_perception_context
from .perception_agent import (
    generate_perception_agent_result,
    extract_perception_notes,
    extract_party_perception,
)
from .prompt_builder import SYSTEM_PROMPT, _CANONICAL_PHASES, _PHASE_ORDER, build_turn_prompt
from .domain_reasoner import generate_domain_analysis
from .option_generator import generate_option_pool
from .api_utils import cached_create
from runtime.artifacts import build_party_state


# ---------------------------------------------------------------------------
# Client initialisation
# ---------------------------------------------------------------------------

def _load_api_key() -> str:
    """Load API key from environment or .env file."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    # Try .env in project root (two levels up from this file)
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        vals = dotenv_values(env_path)
        key = vals.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not found in environment or .env file. "
            "Set it before using lm_runtime mode."
        )
    return key


def _make_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=_load_api_key())


def _get_model() -> str:
    return os.environ.get("SOLOMON_LM_MODEL", "claude-sonnet-4-5")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_lm_assistant_turn(
    turn_index: int,
    timestamp: str,
    state: dict,
    plugin_assessment: dict,
    min_phase: str = "info_gathering",
    safety_monitor_result: dict | None = None,
) -> dict:
    """
    Generate a single assistant turn via the Anthropic API.

    Implements the five-step cognitive sequence:
      1. Perception pass
      2. Domain analysis
      3. Option space scan
      4. Safety check
      5. Response synthesis

    Returns a raw turn dict compatible with normalize_core_output().
    """
    # Step 1: build perception context from state (the scaffold-side pass)
    perception = build_perception_context(
        state=state,
        plugin_assessment=plugin_assessment,
        turn_index=turn_index,
    )

    # Build session history for context window
    session_history = _extract_session_history(state)

    # Build accumulated party state from prior lm_runtime turns (CONTRACT-015 feedback loop).
    # Only supplied when at least one prior turn has contributed a reasoning_trace —
    # i.e. this is not the very first assistant turn in the session.
    prior_lm_turns = [
        t for t in state.get("trace_buffer", [])
        if t.get("role") == "assistant" and t.get("reasoning_trace") is not None
    ]
    prior_party_state = build_party_state(state, timestamp) if prior_lm_turns else None

    # Stage 6: perception agent call — dedicated LM-based perception pass
    # before option generator and domain reasoner, so they receive richer
    # interest/concern signals as context. Fails safe to null result on
    # turns 1–2 or any exception; the scaffold PerceptionContext is the fallback.
    perception_agent_result = generate_perception_agent_result(
        turn_index=turn_index,
        timestamp=timestamp,
        state=state,
        scaffold_perception=perception,
        interaction_history=list(state.get("trace_buffer", [])),
    )

    # Stage 4: option generator call before the domain reasoner.
    # Produces a brainstormed candidate pool that the domain reasoner
    # then qualifies alongside its own domain-expert additions (Option B).
    #
    # Guard: skip when party_state is absent (T1, no party input yet) OR
    # when the prior turn's domain analysis applied a safety veto (blocked).
    # A block at T1/T3 due to missing party input must NOT cascade to T5
    # where both parties have spoken and options are ready — _last_option_readiness
    # only returns "blocked" when the domain reasoner applied an explicit veto,
    # not when it returned "deferred" due to informational gaps.
    if prior_party_state is not None and _last_option_readiness(state) != "blocked":
        brainstormer_pool = generate_option_pool(
            turn_index=turn_index,
            timestamp=timestamp,
            state=state,
            party_state=prior_party_state,
            plugin_assessment=plugin_assessment,
            session_history=session_history,
            perception_agent_result=perception_agent_result,
        )
    else:
        brainstormer_pool = []

    # Stage 3: domain reasoner call before the main five-step pass.
    # Stage 4: now also receives the brainstormer pool for qualification.
    # Produces option_readiness + qualified candidates as a structured prior.
    # Fails gracefully — fallback dict used if call fails.
    # Extract party_state_signals from safety monitor (Stage 5) to pass into
    # domain_reasoner context so it can honour CATEGORY 1/2/3 veto signals.
    safety_signals = (
        safety_monitor_result.get("party_state_signals", [])
        if safety_monitor_result else []
    )
    domain_analysis = generate_domain_analysis(
        turn_index=turn_index,
        timestamp=timestamp,
        state=state,
        party_state=prior_party_state,
        plugin_assessment=plugin_assessment,
        session_history=session_history,
        option_pool=brainstormer_pool if brainstormer_pool else None,
        safety_monitor_signals=safety_signals if safety_signals else None,
        perception_agent_result=perception_agent_result,
    )

    # Build prompt — pass perception agent notes as a structured prior.
    # Falls back to scaffold perception_notes when agent result is null.
    perception_agent_notes = extract_perception_notes(perception_agent_result)
    messages = build_turn_prompt(
        state=state,
        plugin_assessment=plugin_assessment,
        perception=perception,
        turn_index=turn_index,
        session_history=session_history,
        party_state=prior_party_state,
        domain_analysis=domain_analysis,
        perception_agent_notes=perception_agent_notes if perception_agent_notes else None,
    )

    # Call the model
    client = _make_client()
    model = _get_model()

    response = cached_create(
        client,
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    raw_text = response.content[0].text

    # Parse the structured JSON response
    parsed = _parse_lm_response(raw_text)

    # Compute the highest phase the session has reached so far.
    # Use trace-buffer max rather than state["phase"] because scripted client
    # turns can set state["phase"] backward (e.g. D-B04 client turn 6 = "info_gathering").
    trace_buffer = state.get("trace_buffer", [])
    max_seen_phase = _max_trace_phase(trace_buffer)

    # Convert to CandidateTurn-compatible dict
    return _build_turn_dict(
        parsed=parsed,
        perception=perception,
        turn_index=turn_index,
        timestamp=timestamp,
        raw_text=raw_text,
        model_id=model,
        current_phase=max_seen_phase,
        min_phase=min_phase,
        domain_analysis=domain_analysis,
        brainstormer_pool=brainstormer_pool,
        safety_monitor_result=safety_monitor_result,
        perception_agent_result=perception_agent_result,
    )


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

def _extract_json_object(text: str) -> str | None:
    """Find the first complete JSON object in text using bracket counting."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape_next = False
    for i, c in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue
        if c == "\\" and in_string:
            escape_next = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _parse_lm_response(raw_text: str) -> dict[str, Any]:
    """
    Extract the JSON object from the model's response.

    The model is instructed to return JSON but may wrap it in markdown
    code fences.  This parser handles both cases.
    """
    # Try direct parse first
    try:
        return json.loads(raw_text.strip())
    except json.JSONDecodeError:
        pass

    # Try finding the first complete JSON object (handles code fences and preamble)
    candidate = _extract_json_object(raw_text)
    if candidate:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Fallback: return a minimal structure with the raw text preserved
    return {
        "perception": {},
        "domain_analysis": {},
        "option_scan": {},
        "safety_check": {"escalation_needed": False, "candidate_mode": "M0", "candidate_category": "E0", "signals": [], "notes": "parse_failed"},
        "response": {
            "phase": "unknown",
            "message_summary": "LM response parse failed — raw text preserved in observations.",
            "message_text": raw_text[:500],
            "confidence_note": "parse_failed",
        },
        "_parse_error": True,
        "_raw": raw_text,
    }


# ---------------------------------------------------------------------------
# Turn dict builder
# ---------------------------------------------------------------------------

def _build_turn_dict(
    parsed: dict,
    perception: PerceptionContext,
    turn_index: int,
    timestamp: str,
    raw_text: str,
    model_id: str = "",
    current_phase: str = "info_gathering",
    min_phase: str = "info_gathering",
    domain_analysis: dict | None = None,
    brainstormer_pool: list[dict] | None = None,
    safety_monitor_result: dict | None = None,
    perception_agent_result: dict | None = None,
) -> dict:
    """
    Convert the parsed LM response into a raw turn dict.

    The output is compatible with normalize_core_output() → CandidateTurn.
    The five-step reasoning is captured in two forms:
    - interaction_observations_delta (string tags, backward compat)
    - reasoning_trace (structured object, CONTRACT-014)
    """
    response = parsed.get("response", {})
    safety = parsed.get("safety_check", {})
    domain = parsed.get("domain_analysis", {})
    option_scan = parsed.get("option_scan", {})
    lm_perception = parsed.get("perception", {})

    # Normalise phase to canonical value, clamped to valid progression.
    # min_phase is the reference simulation's expected phase for this turn —
    # the LM cannot produce a phase lower than the scripted expectation.
    raw_phase = response.get("phase", "info_gathering")
    phase = _normalise_phase(raw_phase, current_phase, min_phase)

    # Build observations from the five-step reasoning for PQ evaluation
    observations = _build_observations(
        lm_perception=lm_perception,
        domain=domain,
        option_scan=option_scan,
        safety=safety,
        scaffold_perception=perception,
    )

    # Build structured reasoning trace (CONTRACT-014)
    reasoning_trace = _build_reasoning_trace(
        parsed=parsed,
        scaffold_perception=perception,
        model_id=model_id,
        domain_analysis=domain_analysis,
        brainstormer_pool=brainstormer_pool,
        safety_monitor_result=safety_monitor_result,
        perception_agent_result=perception_agent_result,
    )

    # Escalation from safety check
    escalation_needed = safety.get("escalation_needed", False)
    candidate_mode = safety.get("candidate_mode", "M0") if escalation_needed else None
    candidate_category = safety.get("candidate_category", "E0") if escalation_needed else None

    # Build state_delta from what the model perceived and proposed
    state_delta = _build_state_delta(
        lm_perception=lm_perception,
        domain=domain,
        option_scan=option_scan,
        safety=safety,
    )

    # Build risk_check from safety step
    risk_check = {
        "triggered": escalation_needed,
        "signals": safety.get("signals", []),
        "severity": _infer_severity(safety),
        "notes": safety.get("notes", ""),
    }

    return {
        "turn_index": turn_index,
        "timestamp": timestamp,
        "role": "assistant",
        "phase": phase,
        "message_summary": response.get("message_summary", ""),
        "message_text": response.get("message_text", ""),
        "state_delta": state_delta,
        "risk_check": risk_check,
        "candidate_escalation_category": candidate_category,
        "candidate_escalation_mode": candidate_mode,
        "confidence_note": response.get("confidence_note"),
        "interaction_observations_delta": observations,
        "reasoning_trace": reasoning_trace,
    }


def _build_observations(
    lm_perception: dict,
    domain: dict,
    option_scan: dict,
    safety: dict,
    scaffold_perception: PerceptionContext,
) -> list[str]:
    """Build the interaction_observations_delta entries from the five-step reasoning."""
    obs: list[str] = []

    # Perception observations (PQ evidence)
    party_a = lm_perception.get("party_a", {})
    party_b = lm_perception.get("party_b", {})
    if party_a:
        obs.append(
            f"[PERCEPTION:PARTY_A] emotional={party_a.get('emotional_state', '?')} "
            f"posture={party_a.get('relational_posture', '?')}"
        )
        interests_a = party_a.get("inferred_interests", [])
        if interests_a:
            obs.append(f"[PERCEPTION:PARTY_A:INTERESTS] {'; '.join(str(i) for i in interests_a[:3])}")
    if party_b:
        obs.append(
            f"[PERCEPTION:PARTY_B] emotional={party_b.get('emotional_state', '?')} "
            f"posture={party_b.get('relational_posture', '?')}"
        )
        interests_b = party_b.get("inferred_interests", [])
        if interests_b:
            obs.append(f"[PERCEPTION:PARTY_B:INTERESTS] {'; '.join(str(i) for i in interests_b[:3])}")

    dynamic = lm_perception.get("relational_dynamic", "")
    if dynamic:
        obs.append(f"[PERCEPTION:DYNAMIC] {dynamic}")

    # Domain observations
    gaps = domain.get("material_gaps", [])
    if gaps:
        obs.append(f"[DOMAIN:GAPS] {'; '.join(str(g) for g in gaps[:3])}")

    # Option scan
    premature = option_scan.get("premature_option_work", False)
    if premature:
        obs.append("[OPTION_SCAN] premature_option_work=True — options deferred")
    else:
        qualified = option_scan.get("qualified_options", [])
        if qualified:
            obs.append(f"[OPTION_SCAN:QUALIFIED] {'; '.join(str(o) for o in qualified[:3])}")

    # Safety
    if safety.get("escalation_needed"):
        obs.append(
            f"[SAFETY] escalation_needed mode={safety.get('candidate_mode')} "
            f"category={safety.get('candidate_category')}"
        )

    # Scaffold vs LM perception comparison (diagnostic)
    scaffold_dynamic = scaffold_perception.relational_dynamic
    lm_dynamic = lm_perception.get("relational_dynamic", "")
    if scaffold_dynamic and lm_dynamic and scaffold_dynamic != lm_dynamic:
        obs.append(
            f"[PERCEPTION:DIVERGENCE] scaffold={scaffold_dynamic} lm={lm_dynamic}"
        )

    return obs


def _build_reasoning_trace(
    parsed: dict,
    scaffold_perception: PerceptionContext,
    model_id: str,
    domain_analysis: dict | None = None,
    brainstormer_pool: list[dict] | None = None,
    safety_monitor_result: dict | None = None,
    perception_agent_result: dict | None = None,
) -> dict:
    """
    Build the per-turn reasoning_trace object from the parsed five-step JSON.

    Preserves the structured model output that _build_observations() converts
    to string tags.  CONTRACT-014 defines the full schema.

    Key mappings from parsed keys to trace keys:
    - parsed["safety_check"]  → reasoning_trace["safety_assessment"]
    - parsed["response"]      → reasoning_trace["response_synthesis"]
    """
    lm_perception = parsed.get("perception", {})
    safety = parsed.get("safety_check", {})

    # Add scaffold_divergence to the perception block
    perception_trace = dict(lm_perception)
    scaffold_dynamic = scaffold_perception.relational_dynamic
    lm_dynamic = lm_perception.get("relational_dynamic", "")
    if scaffold_dynamic and lm_dynamic and scaffold_dynamic != lm_dynamic:
        perception_trace["scaffold_divergence"] = (
            f"scaffold assessed relational_dynamic={scaffold_dynamic!r}; "
            f"model assessed {lm_dynamic!r}"
        )
    else:
        perception_trace.setdefault("scaffold_divergence", None)

    # Add safe_to_proceed_to_synthesis as derived field per CONTRACT-014 §6
    escalation_needed = safety.get("escalation_needed", False)
    safety_assessment = dict(safety)
    safety_assessment["safe_to_proceed_to_synthesis"] = not escalation_needed

    result = {
        "source": "lm_runtime",
        "model_id": model_id,
        "perception": perception_trace,
        "domain_analysis": parsed.get("domain_analysis", {}),
        "option_scan": parsed.get("option_scan", {}),
        "safety_assessment": safety_assessment,
        "response_synthesis": parsed.get("response", {}),
    }
    # Attach pre-computed domain analysis (CONTRACT-016) when available.
    # Stored separately from the model's self-generated domain_analysis block
    # so evaluators can compare what the domain reasoner determined vs what
    # the main model produced in Step 2.
    if domain_analysis is not None:
        result["pre_computed_domain_analysis"] = domain_analysis
    # Attach brainstormer pool (CONTRACT-017) when available.
    # Stored here so artifacts.py can assemble option_pool.json without
    # needing to re-call either engine.
    if brainstormer_pool is not None:
        result["brainstormer_pool"] = brainstormer_pool
    # Attach safety monitor result (Stage 5) when available.
    # Stored alongside pre_computed_domain_analysis so evaluators can read
    # the full pre-turn agent stack in one place.
    if safety_monitor_result is not None:
        result["safety_monitor_result"] = safety_monitor_result
    # Attach perception agent result (Stage 6) when available.
    # Stored alongside safety_monitor_result — completes the pre-turn agent stack.
    if perception_agent_result is not None:
        result["perception_agent_result"] = perception_agent_result
    return result


def _build_state_delta(
    lm_perception: dict,
    domain: dict,
    option_scan: dict,
    safety: dict,
) -> dict:
    """Build a minimal state_delta from the LM's reasoning."""
    delta: dict = {}

    # Facts from domain analysis (list of strings required by normalization)
    key_constraints = domain.get("key_constraints", [])
    if key_constraints:
        delta["facts_added"] = [str(c) for c in key_constraints[:2]]

    # Escalation state updates (list of strings required by normalization)
    if safety.get("escalation_needed"):
        mode = safety.get("candidate_mode", "M0")
        cat = safety.get("candidate_category", "E0")
        delta["escalation_state_updates"] = [f"mode={mode} category={cat}"]

    # Missing info from domain gaps (list of strings required by normalization)
    gaps = domain.get("material_gaps", [])
    if gaps:
        delta["open_questions_added"] = [str(g) for g in gaps[:2]]

    return delta


_PHASE_ALIASES: dict[str, str] = {
    "opening": "info_gathering",
    "opening_and_orientation": "info_gathering",
    "opening_orientation": "info_gathering",
    "framing": "info_gathering",
    "session_framing": "info_gathering",
    "information_gathering": "info_gathering",
    "interest_identification": "interest_exploration",
    "interests": "interest_exploration",
    "options": "option_generation",
    "option_generation_support": "option_generation",
    "agreement": "agreement_building",
    "closing": "agreement_building",
}


def _max_trace_phase(trace_buffer: list[dict]) -> str:
    """Return the highest phase seen in the trace buffer so far."""
    max_idx = 0
    for turn in trace_buffer:
        phase = turn.get("phase", "")
        if phase in _CANONICAL_PHASES:
            idx = _PHASE_ORDER.index(phase)
            if idx > max_idx:
                max_idx = idx
    return _PHASE_ORDER[max_idx]


def _normalise_phase(
    raw: str,
    current_phase: str = "info_gathering",
    min_phase: str = "info_gathering",
) -> str:
    """
    Map any phase label the model may produce to a canonical phase value.

    Clamped with both a floor and ceiling:
    - Floor: max(trace-buffer-max-phase, min_phase). min_phase is the reference
      simulation's expected phase for this turn, ensuring the LM can't lag
      behind the scripted client turn progression.
    - Ceiling: at most one step ahead of the trace-buffer max.

    This prevents LM regression and illegal phase skipping.
    """
    if raw not in _CANONICAL_PHASES:
        raw = _PHASE_ALIASES.get(raw, "info_gathering")

    try:
        current_idx = _PHASE_ORDER.index(current_phase)
    except ValueError:
        current_idx = 0
    try:
        requested_idx = _PHASE_ORDER.index(raw)
    except ValueError:
        requested_idx = 0
    try:
        min_idx = _PHASE_ORDER.index(min_phase)
    except ValueError:
        min_idx = 0

    # Ceiling: at most one step ahead of trace max
    allowed_idx = min(requested_idx, current_idx + 1)
    # Floor: can't go below trace max or reference expected phase
    floor_idx = max(current_idx, min_idx)
    allowed_idx = max(allowed_idx, floor_idx)
    return _PHASE_ORDER[allowed_idx]


def _infer_severity(safety: dict) -> int:
    if not safety.get("escalation_needed"):
        return 1
    mode = safety.get("candidate_mode", "M0")
    severity_map = {"M0": 1, "M1": 2, "M2": 3, "M3": 4, "M4": 5, "M5": 5}
    return severity_map.get(mode, 2)


# ---------------------------------------------------------------------------
# Session history extractor
# ---------------------------------------------------------------------------

def _last_option_readiness(state: dict) -> str:
    """
    Return the option_readiness from the most recent assistant turn's
    pre_computed_domain_analysis, if available.

    Returns "unknown" when no prior domain analysis is present (e.g. T1).
    Used to skip the option generator when the prior turn already blocked
    options via the safety veto.
    """
    for turn in reversed(state.get("trace_buffer", [])):
        if turn.get("role") != "assistant":
            continue
        rt = turn.get("reasoning_trace") or {}
        pda = rt.get("pre_computed_domain_analysis") or {}
        readiness = pda.get("option_readiness")
        if readiness:
            return readiness
    return "unknown"


def _extract_session_history(state: dict) -> list[dict]:
    """Extract turn summaries from the trace buffer."""
    trace = state.get("trace_buffer", [])
    history = []
    for turn in trace:
        if isinstance(turn, dict):
            history.append({
                "turn_index": turn.get("turn_index", "?"),
                "role": turn.get("role", "unknown"),
                "message_summary": turn.get("message_summary", ""),
                "phase": turn.get("phase", ""),
            })
    return history
