"""
runtime.engine.perception
=========================
Builds an explicit PerceptionContext from the current session state and
plugin assessment.

This is the Stage 1 perception pass — the first cognitive step that must
complete before option generation or response synthesis can begin.  In the
deterministic scaffold the perception was implicit inside each
generate_runtime_assistant_turn() function.  Here it is a first-class
computation with a well-defined output that is:

  1. Passed into the prompt as structured context (Stage 1)
  2. Written to the party_state artifact (Stage 2)
  3. Used by the safety monitor agent (Stage 5)

Design notes
------------
* All fields are derived from existing runtime state — no new data is
  required.  The perception pass is an interpretation layer, not a
  data-collection layer.
* party_id values match whatever keys the state["positions"] dict uses.
  Typically "party_a" and "party_b" but the builder is key-agnostic.
* Risk signals are drawn from active flags + risk_check history in the
  trace buffer.  The safety monitor (Stage 5) will own this more deeply;
  for Stage 1 it is a read-only summary.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PartyPerception:
    """Perception model for a single party at the current turn."""

    party_id: str

    # What emotional/psychological state does this party appear to be in?
    # Derived from: flags, position volatility, trace buffer language cues.
    emotional_state: str

    # What do we believe their underlying interests and concerns are,
    # beneath their stated positions?
    # Derived from: positions, open questions, missing_info entries.
    inferred_interests: list[str]

    # Risk and vulnerability signals observed for this party.
    # Derived from: active flags with party-relevant flag types, risk_checks.
    risk_signals: list[str]

    # How is this party relating to the process and the other party?
    # e.g. "engaged_and_assertive", "deferential", "withdrawn",
    #      "emotionally_escalating", "strategically_guarded"
    relational_posture: str


@dataclass(frozen=True)
class PerceptionContext:
    """
    Full perception snapshot at a given turn.

    Produced once per assistant turn before any other cognitive step.
    """

    turn_index: int

    party_a: PartyPerception
    party_b: PartyPerception

    # The cross-party dynamic observed so far — the relational pattern
    # as a whole, not just each party individually.
    # e.g. "cooperative_with_latent_tension",
    #      "one_party_dominating_other_deferring",
    #      "mutual_escalation", "stable_and_productive"
    relational_dynamic: str

    # How confident are we in this perception?
    # high   — multiple converging signals
    # moderate — some signals, some inference
    # low    — limited signal data, early in session
    perception_confidence: str

    # Free-text notes for the prompt — key things the model should hold
    # in mind about party state before generating a response.
    perception_notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

# Flag types that indicate party-A-specific risk
_PARTY_A_RISK_FLAGS: frozenset[str] = frozenset({
    "coercion_or_intimidation",
    "participation_incapacity",
    "acute_safety_concern",
    "fairness_breakdown",
})

# Flag types that indicate party-B-specific risk (same set — flags are
# symmetric by default; asymmetry is captured in flag notes)
_PARTY_B_RISK_FLAGS: frozenset[str] = _PARTY_A_RISK_FLAGS

# Flag types that indicate process-level risk (not party-specific)
_PROCESS_RISK_FLAGS: frozenset[str] = frozenset({
    "repeated_process_breakdown",
    "domain_complexity_overload",
    "irrecoverable_breakdown",
    "explicit_human_request",
})


def build_perception_context(
    state: dict,
    plugin_assessment: dict,
    turn_index: int,
) -> PerceptionContext:
    """
    Derive a PerceptionContext from the current session state.

    Parameters
    ----------
    state:
        The live session state dict (positions, flags, trace_buffer, etc.)
    plugin_assessment:
        The plugin's current assessment dict (open_missing_items,
        active_flag_types, plugin_confidence, etc.)
    turn_index:
        The turn about to be generated.
    """
    positions: dict = state.get("positions", {})
    active_flags: list[dict] = _get_active_flags(state)
    trace: list[dict] = state.get("trace_buffer", [])
    missing_info: list[dict] = state.get("missing_info", [])
    escalation: dict = state.get("escalation", {})

    party_ids = _infer_party_ids(state)
    party_a_id = party_ids[0] if party_ids else "party_a"
    party_b_id = party_ids[1] if len(party_ids) > 1 else "party_b"

    party_a = _build_party_perception(
        party_id=party_a_id,
        positions=positions,
        active_flags=active_flags,
        missing_info=missing_info,
        trace=trace,
        plugin_assessment=plugin_assessment,
        is_primary=True,
    )

    party_b = _build_party_perception(
        party_id=party_b_id,
        positions=positions,
        active_flags=active_flags,
        missing_info=missing_info,
        trace=trace,
        plugin_assessment=plugin_assessment,
        is_primary=False,
    )

    relational_dynamic = _infer_relational_dynamic(
        party_a=party_a,
        party_b=party_b,
        active_flags=active_flags,
        escalation=escalation,
        plugin_assessment=plugin_assessment,
    )

    perception_confidence = _infer_confidence(
        turn_index=turn_index,
        trace=trace,
        active_flags=active_flags,
    )

    perception_notes = _build_notes(
        party_a=party_a,
        party_b=party_b,
        relational_dynamic=relational_dynamic,
        active_flags=active_flags,
        plugin_assessment=plugin_assessment,
        escalation=escalation,
    )

    return PerceptionContext(
        turn_index=turn_index,
        party_a=party_a,
        party_b=party_b,
        relational_dynamic=relational_dynamic,
        perception_confidence=perception_confidence,
        perception_notes=perception_notes,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_active_flags(state: dict) -> list[dict]:
    flags_section = state.get("flags", {})
    if isinstance(flags_section, dict):
        return [
            f for f in flags_section.get("active_flags", [])
            if isinstance(f, dict) and f.get("status") == "active"
        ]
    return []


def _infer_party_ids(state: dict) -> list[str]:
    """Return party IDs in a stable order from positions or meta."""
    meta = state.get("meta", {})
    parties = meta.get("parties", [])
    if parties:
        return [p.get("party_id", f"party_{i}") for i, p in enumerate(parties)]
    # Fall back to keys in positions
    pos = state.get("positions", {})
    return sorted(pos.keys())[:2]


def _build_party_perception(
    party_id: str,
    positions: dict,
    active_flags: list[dict],
    missing_info: list[dict],
    trace: list[dict],
    plugin_assessment: dict,
    is_primary: bool,
) -> PartyPerception:
    party_positions = positions.get(party_id, {})

    # --- Emotional state ---
    emotional_state = _infer_emotional_state(
        party_id=party_id,
        active_flags=active_flags,
        trace=trace,
        plugin_assessment=plugin_assessment,
    )

    # --- Inferred interests ---
    inferred_interests = _infer_interests(
        party_positions=party_positions,
        missing_info=missing_info,
        plugin_assessment=plugin_assessment,
    )

    # --- Risk signals ---
    risk_signals = _infer_risk_signals(
        party_id=party_id,
        active_flags=active_flags,
        plugin_assessment=plugin_assessment,
    )

    # --- Relational posture ---
    relational_posture = _infer_relational_posture(
        party_id=party_id,
        party_positions=party_positions,
        active_flags=active_flags,
        trace=trace,
        is_primary=is_primary,
    )

    return PartyPerception(
        party_id=party_id,
        emotional_state=emotional_state,
        inferred_interests=inferred_interests,
        risk_signals=risk_signals,
        relational_posture=relational_posture,
    )


def _infer_emotional_state(
    party_id: str,
    active_flags: list[dict],
    trace: list[dict],
    plugin_assessment: dict,
) -> str:
    flag_types = {f.get("flag_type", "") for f in active_flags}
    risk_checks = [
        t.get("risk_check", {}) for t in trace
        if t.get("role") == "assistant"
    ]
    all_signals: list[str] = []
    for rc in risk_checks:
        if isinstance(rc, dict):
            all_signals.extend(rc.get("signals", []))

    if "acute_safety_concern" in flag_types or "coercion_or_intimidation" in flag_types:
        return "acutely_distressed_or_unsafe"
    if "participation_incapacity" in flag_types:
        return "potentially_incapacitated_or_overwhelmed"
    if "fairness_breakdown" in flag_types:
        return "experiencing_unfair_process"
    if "emotional_distress_noted" in all_signals or "emotional_flooding" in all_signals:
        return "emotionally_activated"
    if "pace_tension" in all_signals:
        return "experiencing_pace_or_pressure_stress"
    if not active_flags and not all_signals:
        return "apparently_stable"
    return "moderately_stressed"


def _infer_interests(
    party_positions: dict,
    missing_info: list[dict],
    plugin_assessment: dict,
) -> list[str]:
    interests: list[str] = []

    # Pull from explicit proposals
    proposals = party_positions.get("proposals", [])
    for prop in proposals[:3]:  # limit to avoid noise
        if isinstance(prop, dict):
            stmt = prop.get("statement") or prop.get("summary", "")
            if stmt:
                interests.append(f"Proposes: {stmt[:80]}")

    # Surface open missing-info items as revealed interest areas
    for item in missing_info[:3]:
        if isinstance(item, dict) and item.get("importance") in ("high", "critical"):
            topic = item.get("topic") or item.get("item", "")
            if topic:
                interests.append(f"Needs clarity on: {topic[:60]}")

    # Plugin issue families as interest proxies
    issue_families = plugin_assessment.get("issue_families", [])
    if isinstance(issue_families, dict):
        issue_families = [k for k, v in issue_families.items() if v]
    if issue_families and not interests:
        interests = [f"Active concern: {f}" for f in issue_families[:3]]

    return interests or ["(insufficient signal to infer — early session)"]


def _infer_risk_signals(
    party_id: str,
    active_flags: list[dict],
    plugin_assessment: dict,
) -> list[str]:
    signals: list[str] = []
    for flag in active_flags:
        ft = flag.get("flag_type", "")
        if ft in _PARTY_A_RISK_FLAGS or ft in _PROCESS_RISK_FLAGS:
            sev = flag.get("severity", 1)
            signals.append(f"{ft} (severity {sev})")
    if not signals:
        signals.append("no_active_risk_signals")
    return signals


def _infer_relational_posture(
    party_id: str,
    party_positions: dict,
    active_flags: list[dict],
    trace: list[dict],
    is_primary: bool,
) -> str:
    flag_types = {f.get("flag_type", "") for f in active_flags}

    if "coercion_or_intimidation" in flag_types:
        return "dominating" if is_primary else "deferential_under_pressure"
    if "fairness_breakdown" in flag_types:
        return "disengaging_due_to_unfair_process"
    if "participation_incapacity" in flag_types:
        return "struggling_to_participate"

    proposals = party_positions.get("proposals", [])
    confidence_levels = [
        p.get("confidence", "") for p in proposals if isinstance(p, dict)
    ]
    if "high" in confidence_levels:
        return "assertive_and_confident"
    if "low" in confidence_levels or "uncertain" in confidence_levels:
        return "hesitant_or_uncertain"

    return "engaged_and_cooperative"


def _infer_relational_dynamic(
    party_a: PartyPerception,
    party_b: PartyPerception,
    active_flags: list[dict],
    escalation: dict,
    plugin_assessment: dict,
) -> str:
    flag_types = {f.get("flag_type", "") for f in active_flags}
    mode = escalation.get("mode", "M0")

    if "coercion_or_intimidation" in flag_types:
        return "one_party_dominating_other_deferring"
    if "fairness_breakdown" in flag_types:
        return "process_fairness_at_risk"
    if "repeated_process_breakdown" in flag_types:
        return "process_breakdown_recurring"
    if "acute_safety_concern" in flag_types:
        return "safety_concern_present"

    if mode in ("M3", "M4", "M5"):
        return "escalated_requiring_human_involvement"
    if mode == "M2":
        return "process_stressed_advisory_active"
    if mode == "M1":
        return "cautious_but_workable"

    # Both emotionally activated
    if (party_a.emotional_state == "emotionally_activated"
            and party_b.emotional_state == "emotionally_activated"):
        return "mutual_emotional_activation_workable"

    # Asymmetric postures
    assertive_postures = {"assertive_and_confident", "dominating"}
    deferential_postures = {"deferential_under_pressure", "hesitant_or_uncertain"}
    if (party_a.relational_posture in assertive_postures
            and party_b.relational_posture in deferential_postures):
        return "asymmetric_one_assertive_one_deferential"
    if (party_b.relational_posture in assertive_postures
            and party_a.relational_posture in deferential_postures):
        return "asymmetric_one_assertive_one_deferential"

    return "cooperative_and_stable"


def _infer_confidence(
    turn_index: int,
    trace: list[dict],
    active_flags: list[dict],
) -> str:
    if turn_index <= 2:
        return "low"
    if turn_index >= 5 or len(trace) >= 4:
        return "high" if active_flags else "moderate"
    return "moderate"


def _build_notes(
    party_a: PartyPerception,
    party_b: PartyPerception,
    relational_dynamic: str,
    active_flags: list[dict],
    plugin_assessment: dict,
    escalation: dict,
) -> list[str]:
    notes: list[str] = []

    # Emotional asymmetry note
    if party_a.emotional_state != party_b.emotional_state:
        notes.append(
            f"Emotional asymmetry: {party_a.party_id} is "
            f"'{party_a.emotional_state}', {party_b.party_id} is "
            f"'{party_b.emotional_state}'. Hold both states before responding."
        )

    # Posture asymmetry note
    if party_a.relational_posture != party_b.relational_posture:
        notes.append(
            f"Posture asymmetry: {party_a.party_id} is "
            f"'{party_a.relational_posture}', {party_b.party_id} is "
            f"'{party_b.relational_posture}'. Protect the less-assertive party."
        )

    # Risk signal note
    all_risk = [
        s for s in party_a.risk_signals + party_b.risk_signals
        if s != "no_active_risk_signals"
    ]
    if all_risk:
        notes.append(f"Active risk signals: {', '.join(set(all_risk))}.")

    # Relational dynamic note
    if relational_dynamic not in ("cooperative_and_stable", "cautious_but_workable"):
        notes.append(f"Relational dynamic: {relational_dynamic}.")

    # Plugin confidence note
    plugin_conf = plugin_assessment.get("plugin_confidence", "moderate")
    if plugin_conf == "low":
        notes.append(
            "Plugin confidence is low — option work is constrained. "
            "Do not generate options beyond what the information supports."
        )

    return notes
