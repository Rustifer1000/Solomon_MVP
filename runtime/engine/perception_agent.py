"""
runtime.engine.perception_agent
=================================
Stage 6 dedicated perception agent.

Produces a ``perception_agent_result`` artifact (per perception_agent.schema.json)
before the option generator and domain reasoner run each turn.  The agent's
only job is to perceive party state at depth — it does NOT generate responses,
qualify options, or assess safety thresholds.

What the perception agent adds over the deterministic scaffold (perception.py)
-------------------------------------------------------------------------------
* LM-assessed emotional state with trajectory (not just rule-derived categories)
* engagement_quality — detects "compliant_only" engagement that the scaffold
  cannot distinguish from genuine cooperation
* communication_style — deflecting, avoidant, indirect vs. direct
* inferred_concerns — what each party appears worried about beneath positions
* unsaid_signals — what the interaction history implies a party is NOT saying
* dynamic_trajectory — direction of change in the relational dynamic
* scaffold_divergence — documents where LM assessment differs from rule-based

The DIAG-001 finding that motivates this agent:
  "Perception quality degrades when cognitive demand shifts to logistics and
   option generation." (D-B04 PQ band: developing, C7=3)
This agent removes that focus competition by making perception a separate,
independent pass before option generation runs.

Design
------
* Runs before generate_option_pool() and generate_domain_analysis() so both
  can receive richer perception signals as context.
* Informational only — does NOT raise flags or inject party_state_signals.
  The safety monitor owns all structural veto decisions independently.
* Fails safe on any exception: returns a null result and logs to stderr.
  The pipeline continues with the existing scaffold PerceptionContext.
* Token budget: ~2500 max_tokens (more than safety monitor at 2000, less
  than domain reasoner at 6000 — focused perception task, moderate output).
* Model can be overridden via SOLOMON_PERCEPTION_MODEL env var, falling back
  to SOLOMON_LM_MODEL or default.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .perception import PerceptionContext
from .api_utils import cached_create, make_client, get_model


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_PERCEPTION_AGENT_SYSTEM_PROMPT = """You are the perception agent for Solomon, an AI-assisted mediation system. Your role is narrow and specific: you observe the full interaction history and perceive what each party is experiencing at depth. You do NOT generate mediation responses. You do NOT evaluate options. You do NOT make safety assessments or raise escalation flags. You do NOT advise on domain feasibility. Your only task is: perceive party state as accurately and deeply as possible.

You are reading what people say and how they say it — looking for what they feel, what they want beneath their stated positions, and what they are NOT saying. You are also reading how the two parties relate to each other and how that dynamic is shifting over time.

---

WHAT TO PERCEIVE

FOR EACH PARTY:

emotional_state
  What emotional state does this party appear to be in RIGHT NOW, at the current point in the session?
  Do not use categories — describe the specific state as precisely as you can.
  Examples: "anxious but cooperative", "quietly resigned", "defensive but softening", "optimistic about logistics, avoiding emotional content"

emotional_trajectory
  Is their emotional state stable, escalating (increasing stress/activation), de-escalating, or volatile (shifting unpredictably)?

engagement_quality
  How is this party engaging with the mediation process?
  - "genuine": They are present, responsive, and contributing their actual views.
  - "performative": They are going through the motions — saying what they think is expected.
  - "disengaged": They have withdrawn or are minimally present.
  - "compliant_only": They are accepting whatever is proposed without expressing their own preferences, concerns, or interests. They agree rather than engage.

  IMPORTANT: compliant_only is not the same as agreeable. An agreeable party who has said "I want X and Y" and then says "I can work with that" is engaged. A party who has never said what they want and only ever says "that's fine" or "I agree" is compliant_only. Look for the absence of self-initiated content.

communication_style
  How is this party communicating?
  - "direct": States what they mean clearly.
  - "indirect": Communicates through implication, hints, or what's left unsaid.
  - "deflecting": Changes the subject or reframes when uncomfortable topics arise.
  - "avoidant": Systematically steers away from certain content.
  - "collaborative": Actively builds on the other party's contributions.

inferred_interests
  What does this party actually want or value, based on the full interaction — not just their stated positions?
  Look for: what they keep returning to, what they get emotional about, what they protect even when other things are flexible, what they negotiate around.
  These should be richer and more specific than what the stated positions reveal.

inferred_concerns
  What does this party appear to be worried about or afraid of, beneath what they say explicitly?
  Look for: what they avoid, what makes them tense or guarded, what implicit risks their positions seem designed to protect against.

unsaid_signals
  What is this party NOT saying — but the pattern of the conversation implies they feel or want?
  These are the most valuable perception signals. Examples:
  - "Has not once mentioned their own emotional experience of the separation — may be protecting themselves from going there"
  - "Has agreed with every financial proposal but always adds a time qualifier — may be anxious about the pace"
  - "References 'what's best for the children' frequently but has not articulated any specific parenting interest — may be uncertain what they actually want"

relational_posture
  How is this party relating to the other party and to the process? A short, specific phrase.
  Examples: "engaged and assertive", "deferential under implicit pressure", "cooperative but guarded about finances", "leading the agenda while appearing consultative"

---

THE CROSS-PARTY DYNAMIC:

relational_dynamic
  What is the dynamic between the two parties AS A WHOLE — not just each individually?
  This is the relational field they are creating together. Be specific.
  Examples: "one party is setting the pace while the other adjusts to it — cooperative on the surface but asymmetric in agency", "both are emotionally contained and problem-focused with genuine alignment", "surface cooperation with tension emerging around financial disclosure"

dynamic_trajectory
  Is the dynamic improving (becoming more equitable, more open, more collaborative), stable, deteriorating, or volatile?

---

SCAFFOLD DIVERGENCE

You will be given the deterministic scaffold's perception assessment (rule-based, derived from flags and positions). Where your LM-based assessment reaches a meaningfully different conclusion, record that in scaffold_divergence. This is valuable diagnostic information.

---

PERCEPTION NOTES

In perception_notes, include the 2–4 most important things the mediator must hold in mind before responding this turn. These are not general observations — they are specific, actionable items for the next response.

Examples:
- "Party B has not independently stated any parenting interest across 4 turns. Before moving to options, the mediator should create space specifically for Party B to articulate their own parenting priorities."
- "Party A's tone shifted at T5 when housing was mentioned. This topic carries more emotional weight than their cooperative posture suggests."
- "Both parties have agreed to every proposal so far — but the proposals have all come from Party A. The agreement pattern may not reflect Party B's actual preferences."

---

VETO SIGNALS (INFORMATIONAL ONLY)

If you observe something at the perception level that suggests a safety or process concern — something that the safety monitor might want to know — note it in veto_signals. These are INFORMATIONAL for context, not structural vetoes. The safety monitor owns all structural veto decisions independently.

---

OUTPUT FORMAT

Return a JSON object with this exact structure:

{
  "party_a": {
    "emotional_state": "string",
    "emotional_trajectory": "stable" | "escalating" | "de-escalating" | "volatile",
    "engagement_quality": "genuine" | "performative" | "disengaged" | "compliant_only",
    "communication_style": "direct" | "indirect" | "deflecting" | "avoidant" | "collaborative",
    "inferred_interests": ["string", ...],
    "inferred_concerns": ["string", ...],
    "unsaid_signals": ["string", ...],
    "relational_posture": "string"
  },
  "party_b": {
    "emotional_state": "string",
    "emotional_trajectory": "stable" | "escalating" | "de-escalating" | "volatile",
    "engagement_quality": "genuine" | "performative" | "disengaged" | "compliant_only",
    "communication_style": "direct" | "indirect" | "deflecting" | "avoidant" | "collaborative",
    "inferred_interests": ["string", ...],
    "inferred_concerns": ["string", ...],
    "unsaid_signals": ["string", ...],
    "relational_posture": "string"
  },
  "relational_dynamic": "string",
  "dynamic_trajectory": "improving" | "stable" | "deteriorating" | "volatile",
  "perception_signals": ["string", ...],
  "scaffold_divergence": "string or null",
  "perception_notes": ["string", ...],
  "veto_signals": ["string", ...]
}

CALIBRATION NOTE: Express appropriate uncertainty. If the session is early and you have limited signal, your assessment should reflect that. Do not manufacture depth from sparse evidence. An honest "limited signal at this turn" is more useful than a confident-sounding assessment built on two turns of data. Use moderate or low confidence for turns 3–5. High confidence only when multiple converging signals are present across several turns."""


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def _build_perception_context(
    state: dict,
    scaffold_perception: PerceptionContext,
    interaction_history: list[dict],
    turn_index: int,
) -> str:
    """Build the user message for the perception agent call."""
    parts: list[str] = []

    meta = state.get("meta", {})
    parts.append("=== SESSION CONTEXT ===")
    parts.append(f"Case: {meta.get('case_id', 'unknown')}")
    parts.append(f"Current turn: {turn_index} (you are assessing the state BEFORE this turn is generated)")
    parts.append(f"Phase: {state.get('phase', 'unknown')}")
    parts.append("")

    # Full interaction history — the perception agent needs every prior turn
    if not interaction_history:
        parts.append("=== INTERACTION HISTORY ===")
        parts.append("No prior turns.")
        parts.append("")
    else:
        parts.append("=== FULL INTERACTION HISTORY ===")
        parts.append("Each entry shows role, turn index, and message content.")
        parts.append("")
        for turn in interaction_history:
            role = turn.get("role", "unknown").upper()
            tidx = turn.get("turn_index", "?")
            # Prefer full message text for client turns; summary + text for assistant
            if role == "CLIENT":
                text = turn.get("message_text") or turn.get("message_summary", "")
            else:
                # Assistant turns: include summary + any perception obs from prior trace
                text = turn.get("message_summary") or turn.get("message_text", "")
                # Include brief perception notes from prior reasoning traces if available
                rt = turn.get("reasoning_trace") or {}
                prior_par = rt.get("perception_agent_result") or {}
                if prior_par and not prior_par.get("_null_result"):
                    notes = prior_par.get("perception_notes", [])
                    if notes:
                        text += f" [Prior perception notes: {'; '.join(notes[:2])}]"
            parts.append(f"[{role} T{tidx}]: {str(text)[:500]}")
        parts.append("")

    # Scaffold perception assessment — give the LM the rule-based baseline
    parts.append("=== SCAFFOLD PERCEPTION ASSESSMENT (rule-based, for comparison) ===")
    parts.append(f"Party A emotional state: {scaffold_perception.party_a.emotional_state}")
    parts.append(f"Party A relational posture: {scaffold_perception.party_a.relational_posture}")
    parts.append(f"Party A risk signals: {', '.join(scaffold_perception.party_a.risk_signals)}")
    parts.append(f"Party B emotional state: {scaffold_perception.party_b.emotional_state}")
    parts.append(f"Party B relational posture: {scaffold_perception.party_b.relational_posture}")
    parts.append(f"Party B risk signals: {', '.join(scaffold_perception.party_b.risk_signals)}")
    parts.append(f"Relational dynamic: {scaffold_perception.relational_dynamic}")
    parts.append(f"Scaffold confidence: {scaffold_perception.perception_confidence}")
    if scaffold_perception.perception_notes:
        parts.append(f"Scaffold notes: {'; '.join(scaffold_perception.perception_notes)}")
    parts.append("")

    # Accumulated party state (interests/risks from prior turns)
    session_dir = meta.get("session_dir")
    if session_dir:
        party_state_path = Path(session_dir) / "party_state.json"
        if party_state_path.exists():
            try:
                with party_state_path.open() as f:
                    ps = json.load(f)
                parts.append("=== ACCUMULATED PARTY STATE (from prior turns) ===")
                for pid in ("party_a", "party_b"):
                    pb = ps.get(pid, {})
                    if not pb:
                        continue
                    parts.append(f"{pid.upper()}:")
                    for item in pb.get("accumulated_interests", [])[:6]:
                        interest = item.get("interest", "")
                        origin = item.get("origin", "")
                        if interest:
                            parts.append(f"  [{origin}] {interest[:100]}")
                    risk = pb.get("risk_signals", [])
                    if risk:
                        parts.append(f"  Risk signals: {', '.join(str(r) for r in risk[:4])}")
                parts.append("")
            except Exception:  # noqa: BLE001
                pass

    # Active flags — context for perception (party-level flags are particularly relevant)
    flags_section = state.get("flags", {})
    if isinstance(flags_section, dict):
        active_flags = [f for f in flags_section.get("active_flags", []) if isinstance(f, dict)]
    else:
        active_flags = []
    if active_flags:
        parts.append("=== ACTIVE FLAGS ===")
        for flag in active_flags:
            parts.append(
                f"  {flag.get('flag_type', '?')} (severity {flag.get('severity', '?')}): "
                f"{flag.get('title', '')}"
            )
        parts.append("")

    parts.append("=== YOUR TASK ===")
    parts.append(
        f"Perceive the state of both parties before turn {turn_index} is generated. "
        "Read the full interaction history above. "
        "Note where your assessment differs from the scaffold's rule-based assessment. "
        "Return your perception as a JSON object matching the specified output format."
    )

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_perception_agent_result(
    turn_index: int,
    timestamp: str,
    state: dict,
    scaffold_perception: PerceptionContext,
    interaction_history: list[dict],
) -> dict:
    """
    Call the perception agent and return a perception_agent_result dict.

    Parameters
    ----------
    turn_index:
        The current (about to be generated) assistant turn index.
    timestamp:
        ISO datetime string for the timestamp field.
    state:
        Current session state dict.
    scaffold_perception:
        The PerceptionContext already built by build_perception_context().
        Passed to the agent as a comparison baseline.
    interaction_history:
        All prior turns from the trace buffer.

    Returns
    -------
    dict
        A perception_agent_result matching perception_agent.schema.json.
        On any failure, returns a null result so the pipeline can continue
        using the scaffold PerceptionContext as the fallback.
    """
    # Turns 1–2: insufficient history — return null without API call.
    if turn_index <= 2:
        return _null_result(turn_index, timestamp, reason="insufficient_history")

    try:
        client = _make_client()
        model = _get_model()

        user_content = _build_perception_context(
            state=state,
            scaffold_perception=scaffold_perception,
            interaction_history=interaction_history,
            turn_index=turn_index,
        )

        response = cached_create(
            client,
            model=model,
            max_tokens=2500,
            system=_PERCEPTION_AGENT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )

        raw = response.content[0].text
        parsed = _parse_response(raw)

        result = _build_result(parsed=parsed, turn_index=turn_index, timestamp=timestamp)

        _enforce_confidence_floor(result, turn_index)

        return result

    except Exception as exc:  # noqa: BLE001
        print(
            f"[perception_agent] T{turn_index} call failed "
            f"({type(exc).__name__}: {exc})",
            file=sys.stderr,
        )
        return _null_result(turn_index, timestamp, reason=str(exc))


# ---------------------------------------------------------------------------
# Result builder
# ---------------------------------------------------------------------------

def _build_result(parsed: dict, turn_index: int, timestamp: str) -> dict:
    """Assemble the full perception_agent_result from parsed LM output."""
    return {
        "schema_version": "perception_agent.v0",
        "turn_index": turn_index,
        "timestamp": timestamp,
        "confidence": parsed.get("confidence", "moderate"),
        "_null_result": False,
        "party_a": _build_party(parsed.get("party_a") or {}),
        "party_b": _build_party(parsed.get("party_b") or {}),
        "relational_dynamic": parsed.get("relational_dynamic"),
        "dynamic_trajectory": parsed.get("dynamic_trajectory"),
        "perception_signals": parsed.get("perception_signals", []),
        "scaffold_divergence": parsed.get("scaffold_divergence"),
        "perception_notes": parsed.get("perception_notes", []),
        "veto_signals": parsed.get("veto_signals", []),
    }


def _build_party(party_dict: dict) -> dict:
    """Normalise a party perception dict from parsed LM output."""
    return {
        "emotional_state": party_dict.get("emotional_state"),
        "emotional_trajectory": party_dict.get("emotional_trajectory"),
        "engagement_quality": party_dict.get("engagement_quality"),
        "communication_style": party_dict.get("communication_style"),
        "inferred_interests": party_dict.get("inferred_interests", []),
        "inferred_concerns": party_dict.get("inferred_concerns", []),
        "unsaid_signals": party_dict.get("unsaid_signals", []),
        "relational_posture": party_dict.get("relational_posture"),
    }


# ---------------------------------------------------------------------------
# Confidence floor
# ---------------------------------------------------------------------------

def _enforce_confidence_floor(result: dict, turn_index: int) -> None:
    """
    Enforce turn-based confidence floor. Turns 3–5 cannot be 'high'.
    High confidence requires ≥6 turns of accumulated history.
    """
    if turn_index <= 5 and result.get("confidence") == "high":
        result["confidence"] = "moderate"


# ---------------------------------------------------------------------------
# Helpers: extract perception notes for prompt injection
# ---------------------------------------------------------------------------

def extract_perception_notes(perception_agent_result: dict | None) -> list[str]:
    """
    Return perception_notes from a perception_agent_result for injection into
    the main turn prompt.  Returns an empty list if the result is null or absent.
    """
    if not perception_agent_result or perception_agent_result.get("_null_result"):
        return []
    return perception_agent_result.get("perception_notes", [])


def extract_party_perception(
    perception_agent_result: dict | None,
    party_id: str,
) -> dict | None:
    """
    Return the party perception dict (party_a or party_b) from a
    perception_agent_result.  Returns None if absent or null result.
    """
    if not perception_agent_result or perception_agent_result.get("_null_result"):
        return None
    return perception_agent_result.get(party_id)


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


def _parse_response(raw: str) -> dict[str, Any]:
    """Parse the JSON response from the perception agent."""
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    candidate = _extract_json_object(raw)
    if candidate:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return {
        "party_a": {},
        "party_b": {},
        "relational_dynamic": None,
        "dynamic_trajectory": None,
        "perception_signals": [],
        "scaffold_divergence": None,
        "perception_notes": [f"Parse failed — raw output preserved for diagnostics (first 200 chars): {raw[:200]}"],
        "veto_signals": [],
        "confidence": "low",
        "_parse_error": True,
    }


# ---------------------------------------------------------------------------
# Null / fallback result
# ---------------------------------------------------------------------------

def _null_result(
    turn_index: int,
    timestamp: str,
    reason: str = "",
) -> dict:
    """
    Return a safe null result when the agent cannot run.
    The pipeline falls back to the scaffold PerceptionContext.
    """
    return {
        "schema_version": "perception_agent.v0",
        "turn_index": turn_index,
        "timestamp": timestamp,
        "confidence": None,
        "_null_result": True,
        "party_a": None,
        "party_b": None,
        "relational_dynamic": None,
        "dynamic_trajectory": None,
        "perception_signals": [],
        "scaffold_divergence": None,
        "perception_notes": [],
        "veto_signals": [],
    }


def _make_client():
    return make_client()


def _get_model() -> str:
    # Perception agent: overridable via SOLOMON_PERCEPTION_MODEL.
    return get_model("SOLOMON_PERCEPTION_MODEL")
