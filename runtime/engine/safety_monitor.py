"""
runtime.engine.safety_monitor
==============================
Stage 5 safety monitoring agent.

Produces a ``safety_monitor_result`` artifact (per safety_monitor.schema.json)
before plugin assessment runs each turn.  The safety monitor observes the full
interaction history to detect cross-turn adversarial patterns that the
per-turn flag/escalation layer cannot see:

  CATEGORY 1 — Compliance-only party: a party whose accumulated statements
    contain no independently-initiated content, only reactive modifications
    to the other party's proposals.

  CATEGORY 2 — Deflection as leverage: the party holding an information
    advantage actively deflects disclosure requests using distinct tactics
    across turns (complexity reframe, timing deflection, urgency pressure,
    authority claim, scope minimisation).

  CATEGORY 3 — Discordant signal suppressed: a party briefly surfaces a
    genuine interest that doesn't fit the dominant framing; the dominant
    party reframes it as already solved; the original party returns to
    compliance.

Design
------
* Runs as a separate API call BEFORE plugin.assess_state() so raised flags
  are visible to the escalation cascade.
* Writes safety signals to ``party_state_signals`` which the domain_reasoner
  reads for veto authority.
* Fails safe on any exception: returns a null/low-confidence fallback result
  and logs to stderr.  The pipeline continues with existing escalation
  behavior — the safety monitor never blocks a session by crashing.
* Token budget: ~2000 max_tokens (lighter than domain_reasoner at 6000).

Veto thresholds
---------------
CATEGORY 1 fires when compliance_pattern.severity == "high":
  ≥3 turns of acceptance_only  OR  ≥4 turns of reactive_only.

CATEGORY 2 fires when deflection_pattern.pattern_confirmed == True:
  ≥2 distinct deflection tactics in response to the same disclosure request.

CATEGORY 3 fires when any discordant_signal has:
  was_reframed == True  AND  return_to_compliance == True.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .api_utils import cached_create, make_client, get_model


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SAFETY_MONITOR_SYSTEM_PROMPT = """You are the safety monitor for Solomon, an AI-assisted mediation system. Your role is narrow and specific: you observe the full interaction history and detect structural adversarial patterns that per-turn analysis cannot see. You do NOT generate mediation responses. You do NOT assess option feasibility. You do NOT make procedural suggestions. Your only task is: detect cross-turn safety patterns and report them precisely.

You are looking for three specific patterns. Apply them conservatively — only name a pattern when the evidence across turns is clear. A single suspicious turn is not sufficient.

---

CATEGORY 1 — COMPLIANCE-ONLY PARTY

Signal: A party's statements across the session contain no independently-initiated substantive content. Every statement is a reactive response to, modification of, or acceptance of the other party's proposals. The party has never stated what they want, value, or need without being anchored to the other party's framing first.

Evidence standard: You need ≥3 turns of the reactive pattern before raising this. One or two reactive turns are normal mediation behavior. The pattern must be sustained.

Severity levels:
- "acceptance_only": party accepts without any modification or independent content ("That works for me", "I agree with that"). ≥3 such turns = severity HIGH.
- "reactive_only": party always responds by modifying the other party's proposal, never initiating. ≥4 turns of this = severity HIGH. ≥2 turns = severity MODERATE.
- "reactive_with_independent": party is mostly reactive but has stated at least one independent interest (even if small). This is severity LOW — do NOT raise a veto for this.

What does NOT qualify: One party leading discussions while the other responds and counterproposes is normal mediation. A party who says "I want the same thing Party A described, but with X adjustment" has expressed an independent preference (X). A party who says "I don't want unilateral control" has expressed an independent value. Do not over-classify normal responsiveness as compliance.

---

CATEGORY 2 — DEFLECTION AS LEVERAGE

Signal: A party who holds information the other party needs has responded to a direct disclosure request with deflection tactics across multiple turns. The pattern is not a single refusal — it is a sequence of distinct deflection tactics used to avoid the same underlying request.

Deflection tactics to identify:
- complexity_reframe: "You'd need an accountant to understand these figures", "The business structure is too complicated to explain here"
- timing_deflection: "Let's get the framework settled first, then sort the details", "We can deal with that later"
- urgency_pressure: Manufacturing a time constraint to bypass disclosure ("We have a court window closing", "We need to decide today")
- authority_claim: "I understand these numbers better than anyone", "Trust me on the valuation"
- scope_minimisation: "Those details don't really affect this decision", "That information isn't relevant to what we're discussing"

Evidence standard: Pattern is confirmed when ≥2 DISTINCT tactics have been used in response to the same underlying disclosure request. One tactic = detected but not confirmed. Two different tactics = confirmed.

What does NOT qualify: A party asking to table a topic for later when the topic hasn't been specifically requested yet. A party who is confused about what information is being asked for. A party whose information simply hasn't been requested yet (the asymmetry exists but hasn't been tested).

---

CATEGORY 3 — DISCORDANT SIGNAL SUPPRESSED

Signal: A party briefly surfaces a genuine interest or concern that doesn't fit the dominant party's framing. The dominant party responds by reframing the discordant statement as consistent with their own position ("That's exactly what my proposal addresses"). The original party's next statement accepts the reframe and returns to the compliance pattern.

This is the most subtle pattern. The diagnostic signal is the SEQUENCE: discordant → reframe → return to compliance. All three steps must be present.

What to look for in the discordant turn: The party says something that creates tension with the dominant framing — expresses a need the proposal doesn't fully address, raises a concern that would require modifying the proposal, or names a value that points in a different direction.

What the reframe looks like: The dominant party responds to the discordant statement by claiming it's already solved ("my proposal handles exactly that"), reinterpreting the concern as consistent with their framing ("what you're describing is what I've been saying"), or minimising it ("that's a minor detail we can sort out").

Return to compliance: The original party's next statement accepts the reframe ("Right, okay", "I guess that works", "I was overreacting") and does not develop the original concern further.

Evidence standard: All three elements must be present. A party backing down after pushback without a clear dominant-party reframe is normal dynamics. A party who states a concern and receives a GENUINE response (not a reframe) is not this pattern.

---

OUTPUT FORMAT

Return a JSON object with this exact structure:

{
  "compliance_pattern": {
    "detected": true | false,
    "party": "A" | "B" | "both",
    "evidence_turns": [list of turn indices],
    "pattern_type": "acceptance_only" | "reactive_only" | "reactive_with_independent",
    "severity": "low" | "moderate" | "high"
  },
  "deflection_pattern": {
    "detected": true | false,
    "deflecting_party": "A" | "B",
    "target_request_turn": <integer turn index of original request>,
    "deflection_turns": [list of turn indices],
    "deflection_tactics": ["complexity_reframe", "timing_deflection", ...],
    "pattern_confirmed": true | false
  },
  "discordant_signals": [
    {
      "party": "A" | "B",
      "signal_turn": <integer>,
      "signal_summary": "brief description of what was expressed",
      "was_reframed": true | false,
      "reframe_turn": <integer or null>,
      "reframe_party": "A" | "B" | null,
      "return_to_compliance": true | false,
      "compliance_turn": <integer or null>
    }
  ],
  "veto_recommendation": "CATEGORY 1" | "CATEGORY 2" | "CATEGORY 3" | null,
  "veto_reason": "explicit reasoning citing specific turns" | null,
  "monitor_confidence": "low" | "moderate" | "high",
  "monitor_notes": "practitioner-readable summary of cross-turn observations"
}

If compliance_pattern is not detected or insufficient history exists, set detected=false. You may omit the other compliance_pattern fields or set them to null/empty when detected=false.
If deflection_pattern is not detected, set detected=false.
If no discordant signals, return an empty array.
If no veto condition is met, veto_recommendation=null and veto_reason=null.

CALIBRATION NOTE: Your false-positive cost is high. A CATEGORY 1 veto on a genuinely cooperative session prevents option work unfairly. A CATEGORY 2 veto on a party who is simply less articulate about their finances is a serious error. A CATEGORY 3 veto on a party who genuinely reconsidered their position after hearing a good explanation is wrong. Apply these patterns only when the evidence is clear across multiple turns — not when a single turn looks ambiguous."""


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def _build_monitor_context(
    state: dict,
    interaction_history: list[dict],
    turn_index: int,
) -> str:
    """Build the user message for the safety monitor call."""
    parts: list[str] = []

    meta = state.get("meta", {})
    parts.append("=== SESSION CONTEXT ===")
    parts.append(f"Case: {meta.get('case_id', 'unknown')}")
    parts.append(f"Current turn: {turn_index}")
    parts.append(f"Phase: {state.get('phase', 'unknown')}")
    parts.append("")

    # Full interaction history — the monitor needs all prior turns
    if not interaction_history:
        parts.append("=== INTERACTION HISTORY ===")
        parts.append("No prior turns. Insufficient history for pattern detection.")
        parts.append("")
    else:
        parts.append("=== FULL INTERACTION HISTORY ===")
        parts.append("Each turn shows: role, turn index, and the message or summary.")
        parts.append("")
        for turn in interaction_history:
            role = turn.get("role", "unknown").upper()
            tidx = turn.get("turn_index", "?")
            # Prefer message_text for client turns; message_summary for assistant
            if role == "CLIENT":
                text = turn.get("message_text") or turn.get("message_summary", "")
            else:
                text = turn.get("message_summary") or turn.get("message_text", "")
            text = str(text)[:400]
            parts.append(f"[{role} T{tidx}]: {text}")
        parts.append("")

    # Party state interests (if available) — helps identify reactive vs. independent content
    party_state_path = None
    session_dir = meta.get("session_dir")
    if session_dir:
        candidate = Path(session_dir) / "party_state.json"
        if candidate.exists():
            party_state_path = candidate

    if party_state_path:
        try:
            with party_state_path.open() as f:
                ps = json.load(f)
            parts.append("=== ACCUMULATED PARTY STATE (from prior turns) ===")
            for pid in ("party_a", "party_b"):
                pb = ps.get(pid, {})
                if not pb:
                    continue
                parts.append(f"{pid.upper()}:")
                acc = pb.get("accumulated_interests", [])
                if acc:
                    for item in acc[:8]:
                        interest = item.get("interest", "")
                        origin = item.get("origin", "")
                        if interest:
                            parts.append(f"  [{origin}] {interest[:120]}")
                else:
                    parts.append("  No accumulated interests recorded yet.")
            parts.append("")
        except Exception:  # noqa: BLE001
            pass

    # Active flags (context for the monitor)
    flags = state.get("flags", [])
    if flags:
        parts.append("=== ACTIVE FLAGS ===")
        for flag in flags:
            parts.append(f"  {flag.get('flag_type', '?')}: {flag.get('title', '')}")
        parts.append("")

    parts.append("=== YOUR TASK ===")
    parts.append(
        f"Review the full interaction history above (turns 1 through {turn_index - 1}). "
        "Detect CATEGORY 1, CATEGORY 2, and CATEGORY 3 patterns. "
        "Return your assessment as a JSON object matching the specified output format. "
        "Be conservative — only name a pattern when the evidence across multiple turns is clear."
    )

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_safety_monitor_result(
    turn_index: int,
    timestamp: str,
    state: dict,
    interaction_history: list[dict],
) -> dict:
    """
    Call the safety monitor and return a safety_monitor_result dict.

    Parameters
    ----------
    turn_index:
        The current (about to be generated) assistant turn index.
    timestamp:
        ISO datetime string for the generated_at field.
    state:
        Current session state dict.
    interaction_history:
        All prior turns from interaction_trace (client and assistant).

    Returns
    -------
    dict
        A safety_monitor_result matching safety_monitor.schema.json.
        On any failure, returns a null/low-confidence fallback so the
        pipeline can continue without crashing.
    """
    # Turns 1-2: insufficient history — return low-confidence null result
    # without making an API call.
    if turn_index <= 2:
        return _null_result(turn_index, timestamp, state, reason="insufficient_history")

    try:
        client = _make_client()
        model = _get_model()

        user_content = _build_monitor_context(
            state=state,
            interaction_history=interaction_history,
            turn_index=turn_index,
        )

        response = cached_create(
            client,
            model=model,
            max_tokens=2000,
            system=_SAFETY_MONITOR_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )

        raw = response.content[0].text
        parsed = _parse_response(raw)

        meta = state.get("meta", {})
        result = {
            "schema_version": "safety_monitor.v0",
            "case_id": meta.get("case_id", "unknown"),
            "session_id": meta.get("session_id", "unknown"),
            "turn_index": turn_index,
            "generated_at": timestamp,
            "source": "safety_monitor_v0",
            # Pattern fields from LM output
            "compliance_pattern": parsed.get("compliance_pattern"),
            "deflection_pattern": parsed.get("deflection_pattern"),
            "discordant_signals": parsed.get("discordant_signals", []),
            "veto_recommendation": parsed.get("veto_recommendation"),
            "veto_reason": parsed.get("veto_reason"),
            "monitor_confidence": parsed.get("monitor_confidence", "moderate"),
            "monitor_notes": parsed.get("monitor_notes", ""),
            # Derived action fields — populated by _derive_actions
            "flags_raised": [],
            "party_state_signals": [],
        }

        _enforce_confidence_floor(result, turn_index)
        _derive_actions(result)

        return result

    except Exception as exc:  # noqa: BLE001
        print(
            f"[safety_monitor] T{turn_index} call failed "
            f"({type(exc).__name__}: {exc})",
            file=sys.stderr,
        )
        return _null_result(turn_index, timestamp, state, reason=str(exc))


# ---------------------------------------------------------------------------
# Action derivation
# ---------------------------------------------------------------------------

def _derive_actions(result: dict) -> None:
    """
    Populate flags_raised and party_state_signals from detected patterns.
    These are written to state before plugin.assess_state() runs.
    """
    veto = result.get("veto_recommendation")
    veto_reason = result.get("veto_reason") or ""

    if veto == "CATEGORY 1":
        cp = result.get("compliance_pattern") or {}
        party = cp.get("party", "unknown")
        result["flags_raised"].append("compliance_only_pattern")
        result["party_state_signals"].append(
            f"VETO CATEGORY 1: Party {party} compliance-only pattern detected. "
            f"{veto_reason}"
        )

    elif veto == "CATEGORY 2":
        dp = result.get("deflection_pattern") or {}
        party = dp.get("deflecting_party", "unknown")
        tactics = ", ".join(dp.get("deflection_tactics", []))
        result["flags_raised"].append("decision_quality_risk")
        result["party_state_signals"].append(
            f"VETO CATEGORY 2: Party {party} deflection pattern confirmed "
            f"(tactics: {tactics}). {veto_reason}"
        )

    elif veto == "CATEGORY 3":
        ds_list = result.get("discordant_signals") or []
        confirmed = [ds for ds in ds_list if ds.get("was_reframed") and ds.get("return_to_compliance")]
        if confirmed:
            ds = confirmed[0]
            party = ds.get("party", "unknown")
            signal_turn = ds.get("signal_turn", "?")
            result["flags_raised"].append("compliance_only_pattern")
            result["party_state_signals"].append(
                f"VETO CATEGORY 3: Party {party} discordant signal at T{signal_turn} "
                f"suppressed by reframe; party returned to compliance. {veto_reason}"
            )

    # Non-veto: moderate-severity compliance pattern raises a softer flag
    if veto is None:
        cp = result.get("compliance_pattern") or {}
        if cp.get("detected") and cp.get("severity") == "moderate":
            result["flags_raised"].append("insufficient_information")


# ---------------------------------------------------------------------------
# Confidence floor
# ---------------------------------------------------------------------------

def _enforce_confidence_floor(result: dict, turn_index: int) -> None:
    """
    Enforce turn-based confidence floor. Turns 3-4 cannot be 'high'.
    """
    if turn_index <= 4 and result.get("monitor_confidence") == "high":
        result["monitor_confidence"] = "moderate"


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
        "compliance_pattern": None,
        "deflection_pattern": None,
        "discordant_signals": [],
        "veto_recommendation": None,
        "veto_reason": None,
        "monitor_confidence": "low",
        "monitor_notes": f"Parse failed. Raw (first 300 chars): {raw[:300]}",
        "_parse_error": True,
    }


# ---------------------------------------------------------------------------
# Null / fallback result
# ---------------------------------------------------------------------------

def _null_result(
    turn_index: int,
    timestamp: str,
    state: dict,
    reason: str = "",
) -> dict:
    """
    Return a safe null result when the monitor cannot run or history is
    insufficient.  Pipeline continues unchanged.
    """
    meta = state.get("meta", {})

    if reason == "insufficient_history":
        notes = f"Insufficient interaction history at turn {turn_index}. No pattern assessment performed."
        confidence = "low"
    else:
        notes = f"Safety monitor unavailable — null fallback. Reason: {reason[:200]}" if reason else "Safety monitor call failed."
        confidence = "low"

    return {
        "schema_version": "safety_monitor.v0",
        "case_id": meta.get("case_id", "unknown"),
        "session_id": meta.get("session_id", "unknown"),
        "turn_index": turn_index,
        "generated_at": timestamp,
        "source": "safety_monitor_v0",
        "compliance_pattern": None,
        "deflection_pattern": None,
        "discordant_signals": [],
        "flags_raised": [],
        "party_state_signals": [],
        "veto_recommendation": None,
        "veto_reason": None,
        "monitor_confidence": confidence,
        "monitor_notes": notes,
        "_null_result": True,
    }


# ---------------------------------------------------------------------------
# Flag template builder
# ---------------------------------------------------------------------------

_FLAG_TYPE_METADATA: dict[str, dict] = {
    "compliance_only_pattern": {
        "severity": 3,
        "related_categories": ["E1"],
        "threshold_band": "T2",
        "title": "Compliance-only party pattern detected",
        "note": "Safety monitor detected a sustained cross-turn compliance pattern. A party has not independently articulated their own interests.",
        "signal_classes": ["compliance_only_pattern"],
    },
    "decision_quality_risk": {
        "severity": 2,
        "related_categories": ["E5"],
        "threshold_band": "T1",
        "title": "Option qualification may be ahead of informed consent",
        "note": "Safety monitor raised decision quality concern based on cross-turn pattern.",
        "signal_classes": ["decision_quality_risk", "domain_complexity_warning"],
    },
    "insufficient_information": {
        "severity": 2,
        "related_categories": ["E5"],
        "threshold_band": "T1",
        "title": "Material information gaps remain unresolved",
        "note": "Safety monitor raised caution based on moderate cross-turn compliance signal.",
        "signal_classes": ["insufficient_information", "feasibility_gap"],
    },
}


def build_safety_monitor_flag_templates(
    safety_monitor_result: dict,
    case_id: str,
) -> list[dict]:
    """
    Convert safety_monitor_result.flags_raised into full flag template dicts
    compatible with merge_flag_templates().
    """
    turn_index = safety_monitor_result.get("turn_index", 1)
    flag_types = safety_monitor_result.get("flags_raised", [])
    templates: list[dict] = []

    for i, flag_type in enumerate(flag_types):
        meta = _FLAG_TYPE_METADATA.get(flag_type, {
            "severity": 2,
            "related_categories": ["E5"],
            "threshold_band": "T1",
            "title": f"Safety monitor flag: {flag_type}",
            "note": "Safety monitor raised this flag based on cross-turn pattern detection.",
            "signal_classes": [flag_type],
        })
        templates.append({
            "flag_id": f"{case_id.lower()}-flag-monitor-{flag_type.replace('_', '-')}-t{turn_index}",
            "flag_type": flag_type,
            "severity": meta["severity"],
            "source": "safety_monitor",
            "first_detected_turn": turn_index,
            "last_updated_turn": turn_index,
            "related_categories": meta["related_categories"],
            "threshold_band": meta["threshold_band"],
            "title": meta["title"],
            "note": meta["note"],
            "signal_classes": meta["signal_classes"],
            "related_issues": [],
            "source_turns": [turn_index],
        })

    return templates


def _make_client():
    return make_client()


def _get_model() -> str:
    # Safety monitor: overridable via SOLOMON_SAFETY_MODEL.
    return get_model("SOLOMON_SAFETY_MODEL")
