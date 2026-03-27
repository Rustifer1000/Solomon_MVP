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
a CandidateTurn via the existing normalize_core_output() pipeline.  The
five-step reasoning is preserved in interaction_observations_delta so it
is available for PQ evaluation.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import anthropic
from dotenv import dotenv_values

from .perception import PerceptionContext, build_perception_context
from .prompt_builder import SYSTEM_PROMPT, build_turn_prompt


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

    # Build prompt
    messages = build_turn_prompt(
        state=state,
        plugin_assessment=plugin_assessment,
        perception=perception,
        turn_index=turn_index,
        session_history=session_history,
    )

    # Call the model
    client = _make_client()
    model = _get_model()

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    raw_text = response.content[0].text

    # Parse the structured JSON response
    parsed = _parse_lm_response(raw_text)

    # Convert to CandidateTurn-compatible dict
    return _build_turn_dict(
        parsed=parsed,
        perception=perception,
        turn_index=turn_index,
        timestamp=timestamp,
        raw_text=raw_text,
    )


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

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

    # Try extracting from code fence
    fence_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        raw_text,
        re.DOTALL,
    )
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding the outermost JSON object
    brace_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
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
) -> dict:
    """
    Convert the parsed LM response into a raw turn dict.

    The output is compatible with normalize_core_output() → CandidateTurn.
    The five-step reasoning is captured in interaction_observations_delta.
    """
    response = parsed.get("response", {})
    safety = parsed.get("safety_check", {})
    domain = parsed.get("domain_analysis", {})
    option_scan = parsed.get("option_scan", {})
    lm_perception = parsed.get("perception", {})

    # Build observations from the five-step reasoning for PQ evaluation
    observations = _build_observations(
        lm_perception=lm_perception,
        domain=domain,
        option_scan=option_scan,
        safety=safety,
        scaffold_perception=perception,
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
        "phase": response.get("phase", "unknown"),
        "message_summary": response.get("message_summary", ""),
        "message_text": response.get("message_text", ""),
        "state_delta": state_delta,
        "risk_check": risk_check,
        "candidate_escalation_category": candidate_category,
        "candidate_escalation_mode": candidate_mode,
        "confidence_note": response.get("confidence_note"),
        "interaction_observations_delta": observations,
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


def _build_state_delta(
    lm_perception: dict,
    domain: dict,
    option_scan: dict,
    safety: dict,
) -> dict:
    """Build a minimal state_delta from the LM's reasoning."""
    delta: dict = {}

    # Facts from domain analysis
    key_constraints = domain.get("key_constraints", [])
    if key_constraints:
        delta["facts_added"] = [
            {"statement": c, "category": "domain", "status": "inferred"}
            for c in key_constraints[:2]
        ]

    # Escalation state updates from safety check
    if safety.get("escalation_needed"):
        delta["escalation_state_updates"] = [{
            "mode": safety.get("candidate_mode", "M0"),
            "category": safety.get("candidate_category", "E0"),
            "rationale": safety.get("notes", ""),
            "signals": safety.get("signals", []),
        }]

    # Missing info from domain gaps
    gaps = domain.get("material_gaps", [])
    if gaps:
        delta["open_questions_added"] = [
            {"question": g, "party": "both", "importance": "high"}
            for g in gaps[:2]
        ]

    return delta


def _infer_severity(safety: dict) -> int:
    if not safety.get("escalation_needed"):
        return 1
    mode = safety.get("candidate_mode", "M0")
    severity_map = {"M0": 1, "M1": 2, "M2": 3, "M3": 4, "M4": 5, "M5": 5}
    return severity_map.get(mode, 2)


# ---------------------------------------------------------------------------
# Session history extractor
# ---------------------------------------------------------------------------

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
