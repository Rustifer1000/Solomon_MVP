"""
runtime.engine.domain_reasoner
===============================
Stage 3 domain reasoning call.

Produces a `domain_analysis` artifact (CONTRACT-016) before the main
five-step LLM pass runs.  The domain reasoner is a focused single-purpose
call: it determines option_readiness, qualifies candidate options, and
applies the safety veto rule from CONTRACT-016 §7.

Design
------
* Separate from the main five-step pass — a dedicated system prompt
  positions the model as a domain practitioner, not a mediator.
* Reads party_state.json (from prior turns) to apply the safety veto.
* Returns a structured dict matching domain_analysis.schema.json.
* Failures degrade gracefully — if the domain reasoner call fails or
  produces unparseable output, the main pass falls back to the existing
  plugin assessment without crashing the session.

Safety veto rule (CONTRACT-016 §7)
-----------------------------------
The domain reasoner applies the veto when party_state shows:
  - Active unresolved risk signals of sufficient severity
  - Compliance-only interest patterns (Party B's interests are only
    responses to Party A, never independently stated)
  - Unacknowledged information asymmetry held by one party
  - Conflict avoidance pattern in a party not yet given independent space

These are passed as explicit context in the domain reasoner prompt.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import anthropic
from dotenv import dotenv_values


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_DOMAIN_REASONER_SYSTEM_PROMPT = """You are a domain practitioner supporting an AI-assisted mediation system called Solomon. Your role is narrow and specific: you assess whether option work is appropriate at this point in the session, and if so, which options from the known option space are domain-feasible given the current state.

You are NOT the mediator. You do not generate response text. You do not assess party psychology. You do not make escalation decisions. Your only task is: given what is known about this session, what options are viable right now, and are the conditions safe to present them?

SAFETY VETO RULE (mandatory — apply carefully, not broadly)

Before assessing domain feasibility, check for veto conditions in two places:

PRIORITY SOURCE — SAFETY MONITOR SIGNALS (Stage 5):
When a "=== SAFETY MONITOR SIGNALS ===" section is present in the context, read it first. If it contains a VETO CATEGORY directive (CATEGORY 1, CATEGORY 2, or CATEGORY 3), apply the veto immediately — set safety_veto_applied=true, option_readiness="blocked", and copy the veto reason into safety_veto_reason. You do NOT need to re-verify the pattern. The safety monitor has already done the cross-turn analysis. Trust its finding.

FALLBACK SOURCE — PARTY STATE SIGNALS:
When no safety monitor signals are present (earlier sessions, Stage 3/4 path, or safety monitor null result), apply your own veto check against the party state below. Apply the veto only when ALL of the following are true for a given signal category — not when any single indicator is present.

VETO CATEGORY 1: Compliance-only interest pattern
Apply when BOTH: (a) a party's accumulated interests contain NO independent substantive content — every entry is a response to or constraint on the other party's proposal with no original value expression, AND (b) the party has had at least one opportunity to speak and has not initiated any content independently. Do NOT apply when a party's interests contain even one genuine independent value (e.g., "not wanting unilateral control over the process" is an independent interest even if stated reactively).

VETO CATEGORY 2: Unacknowledged information asymmetry used as leverage
Apply when BOTH: (a) one party controls information the other party needs and (b) the controlling party has actively deflected, delayed, or refused disclosure despite a direct request. Do NOT apply when information asymmetry exists but has not been tested (i.e., the party with information has simply not been asked yet).

VETO CATEGORY 3: Active safety signals in party_state
Apply when party_state shows unresolved risk signals indicating: explicit fear of the mediation outcome, conflict avoidance under active pressure (not just a deferential style), or stated participation incapacity. Do NOT apply for signals indicating frustration, defensiveness, or reactive posture — these are normal mediation dynamics and do not prevent safe option evaluation.

CALIBRATION GUIDANCE: The safety veto is for situations where proceeding to option work would actively harm a party. Normal mediation patterns — one party leads, the other responds and counterproposes; one party is more assertive than the other; parties use reactive framing — do NOT meet the veto threshold. Apply the veto conservatively. A false veto (blocking option work when it's safe) has real costs: parties cannot move forward, and the mediator loses credibility. Reserve the veto for clear patterns, not ambiguous ones.

OPTION READINESS DETERMINATION

If no safety veto applies, determine option_readiness:

- "ready": domain constraints are understood, at least one option is feasibly qualifiable given current information, and presenting options to parties is appropriate now.
- "deferred": domain constraints are understood but material gaps prevent responsible qualification. Option work is appropriate in the next turn or session once gaps are addressed.
- "blocked": a fundamental information absence or domain constraint prevents option work (regardless of safety — e.g., key facts about assets, timeline, or legal constraints are completely unknown).

DEFERRED vs BLOCKED — critical distinction when both parties have been heard:
When both parties have been heard but a critical logistics or structural parameter has not yet been surfaced (e.g. current parenting schedule, asset values, income figures, geographic constraints), use "deferred" — NOT "blocked". The issue structure is clear; the gap is factual. "Blocked" is correct only when: (a) only one party has been heard and their interests/position are unknown, OR (b) a genuine safety concern (veto category) prevents option work, OR (c) the issue domain itself is completely unidentified. Applying "blocked" when both parties have contributed but logistical details remain unknown is an over-classification — it signals a harder stop than is warranted and loses the meaningful distinction between a session that cannot proceed and one that needs one more information step.

OPTION QUALIFICATION

When option_readiness is "ready", identify which options from the known option space are feasible. Be concrete: name each option, explain why it's viable given what is actually known (not what you would ideally want to know), and note any conditions that must hold.

CRITICAL DISTINCTION — structural fit vs. parameter calibration:
An option can be qualified when its STRUCTURE is appropriate for the issue type and party interests, even if the specific PARAMETERS (thresholds, timelines, amounts) have not yet been set by the parties. Qualifying a structurally-appropriate option with moderate/low confidence and noting "specific parameters to be set by parties" is correct behavior. It is NOT over-caution to qualify at low or moderate confidence — it is over-caution to refuse all qualification because parameters are unknown.

Examples of this distinction:
- "Tiered notice requirement" — structure is clear from the expense-coordination issue type and Party A's stated concern about late requests. Specific thresholds (24h/48h/72h, dollar amounts) are party decisions. Qualify at moderate confidence with condition "parties to agree on specific tiers."
- "Receipt standard with substitute provision" — structure is clear from Party A's documentation concern. Specific acceptable substitutes (photos, bank statements, verbal confirmation) are party decisions. Qualify at moderate confidence with condition "parties to define acceptable documentation."

When the issue families are expense_coordination or communication_protocol and parties have articulated process-level concerns (timing, fairness, documentation), these structural options are almost always qualifiable at moderate confidence: tiered notice, documentation standards, approval thresholds, shared tracking. Qualify them and let the parties negotiate the parameters.

Do not require perfect information. Options can be qualified with appropriate confidence levels (low/moderate/high) given what's known. Requiring complete information before qualifying any option is over-caution — it perpetuates the bottleneck this tool is designed to resolve.

PROCESS OPTIONS VS. SUBSTANTIVE OPTIONS — a critical distinction

Two types of options have fundamentally different qualification requirements:

SUBSTANTIVE OPTIONS (property division, custody percentages, dollar amounts) require deep interest understanding — the underlying stakes, priorities, and constraints matter because the option content is directly determined by what the parties actually value most. Deep interest exploration is required before qualifying substantive options.

PROCESS OPTIONS (communication protocols, documentation standards, notice windows, approval thresholds, coordination mechanisms) can be qualified based on the surface process concern alone. If Party A has expressed a timing/documentation complaint and Party B has expressed a workability/control concern, that is sufficient basis to qualify structural process options. You do NOT need to know the underlying stakes (financial planning vs. trust repair) to qualify a "tiered notice system" — the structure addresses the predictability concern regardless of its origin. The specific parameters (24h vs. 48h, $50 threshold vs. $100) are negotiated by the parties; the structure is domain-assessable.

For expense-coordination and communication-protocol issue families: when both parties have articulated process-level concerns (timing, documentation, fairness of control), structural process options ARE qualifiable at moderate confidence. Set option_readiness to "ready" and qualify the structural options. Do not defer pending deeper interest exploration for process design work — that is the correct order only for substantive options.

REACTIVE INTEREST STATEMENTS ARE SUFFICIENT FOR PROCESS OPTIONS

A party saying "I don't want one parent to have total control" is a sufficient basis for qualifying process options. You do NOT need a constructive interest statement ("I need shared approval for expenses over $X") to qualify the option — the reactive statement identifies the concern class (unilateral control), and that is enough to select the structural option (approval thresholds, tiered notice). The party will calibrate the parameters when the options are presented.

The distinction you must NOT make: "Their interest is reactive so I cannot qualify." For process options, reactive and constructive interests are equally sufficient. Both tell you what issue structure to address. Managing how parties refine their interests in response to options is the mediator's role — not a domain qualification gate.

YOUR SCOPE ENDS AT STRUCTURAL QUALIFICATION

You are not responsible for ensuring parties are "ready" in a psychological sense before seeing options. You are not responsible for preventing premature convergence on tactical choices. Those are mediator concerns. Your scope is: does the issue type and party input give you enough to identify which structural options are domain-relevant? If yes, qualify them. The risk of premature option presentation is the mediator's to manage, not yours to prevent by deferring.

For expense-coordination disputes where both parties have expressed any process concern (timing, documentation, control, predictability, workability): qualify the structural options at moderate confidence and set option_readiness to "ready". This is the correct behavior.

DOMAIN PRACTITIONER FRAMING

Read the session as a practitioner in this domain would. For divorce mediation: what would an experienced family mediator see as the viable moves right now? For expense coordination disputes: a tiered notice system, receipt standards, and approval thresholds are standard bounded options — they don't require perfect information to qualify, they require that both parties have articulated a process concern (which constitutes sufficient basis for a process-oriented option).

OPTION POOL QUALIFICATION (Stage 4)

When an option pool from the brainstorming pass is provided, you will receive it as a list of candidates under "=== BRAINSTORMER OPTION POOL ===". In this case:

1. Review each brainstormer candidate against domain realities (legal constraints, financial feasibility, domain practice standards for this issue type). Do NOT re-apply psychological or participation readiness filters — that is not your scope.

2. Add your own domain-expert candidates that the brainstormer may not have produced. These are options you know are standard or well-established for this issue type and party situation.

3. Qualify the combined pool (brainstormer candidates + your own additions). For each candidate from either source: assess feasibility, assign confidence, note prerequisite parameters and conditions.

4. Return your qualification results in the "option_pool_qualification" section of your output (in addition to your normal domain analysis output).

When no option pool is provided (Stage 3 path), omit "option_pool_qualification" from your response and qualify only your self-generated candidates as before.

IMPORTANT: Your domain-expert additions go in "domain_expert_candidates" within the qualification block. They will be stamped with source="domain_reasoner" automatically — do not include a source field on them.

OUTPUT FORMAT

Return a JSON object with this structure:
{
  "schema_version": "domain_analysis.v0",
  "source": "domain_reasoner_v0",
  "option_readiness": "ready" | "deferred" | "blocked",
  "readiness_rationale": "...",
  "safety_veto_applied": false,
  "safety_veto_reason": null,
  "qualified_candidates": [
    {
      "option_label": "...",
      "option_description": "...",
      "feasibility_rationale": "...",
      "confidence": "low" | "moderate" | "high",
      "conditions": ["..."]
    }
  ],
  "blocking_constraints": [
    {
      "constraint": "...",
      "severity": "minor" | "moderate" | "critical",
      "what_would_resolve_it": "..."
    }
  ],
  "material_gaps": [
    {
      "gap": "...",
      "importance": "low" | "moderate" | "high",
      "what_it_blocks": "..."
    }
  ],
  "domain_confidence": "low" | "moderate" | "high",
  "domain_notes": "...",
  "option_pool_qualification": {
    "domain_expert_candidates": [
      {
        "candidate_id": "opt-dom-001",
        "label": "...",
        "rationale": "...",
        "party_interest_alignment": {
          "party_a": "...",
          "party_b": "..."
        },
        "related_issues": ["..."]
      }
    ],
    "domain_qualified": [
      {
        "candidate_id": "...",
        "label": "...",
        "feasibility_rationale": "...",
        "confidence": "low" | "moderate" | "high",
        "prerequisite_parameters": ["..."],
        "conditions": ["..."]
      }
    ],
    "domain_blocked": [
      {
        "candidate_id": "...",
        "label": "...",
        "blocking_rationale": "...",
        "what_would_unblock": "..."
      }
    ]
  }
}

qualified_candidates must be empty when option_readiness is not "ready".
safety_veto_reason must be non-null when safety_veto_applied is true.
option_pool_qualification is only included when a brainstormer pool was provided.
When including option_pool_qualification: domain_qualified must include ALL candidates
from both brainstormer_candidates and domain_expert_candidates that pass qualification.
candidate_id values in domain_qualified and domain_blocked must match ids in the input
brainstormer pool or your own domain_expert_candidates."""


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def _build_domain_context(
    state: dict,
    party_state: dict | None,
    plugin_assessment: dict,
    session_history: list[dict],
    turn_index: int,
    option_pool: list[dict] | None = None,
    safety_monitor_signals: list[str] | None = None,
    perception_agent_result: dict | None = None,
) -> str:
    """Build the user message for the domain reasoner call."""
    parts: list[str] = []

    meta = state.get("meta", {})
    parts.append("=== SESSION CONTEXT ===")
    parts.append(f"Case: {meta.get('case_id', 'unknown')}")
    parts.append(f"Turn: {turn_index}")
    parts.append(f"Phase: {state.get('phase', 'unknown')}")
    parts.append(f"Escalation mode: {state.get('escalation', {}).get('mode', 'M0')}")
    parts.append("")

    # Session history (last 6 turns)
    if session_history:
        parts.append("=== RECENT SESSION HISTORY ===")
        for turn in session_history[-6:]:
            role = turn.get("role", "unknown").upper()
            summary = turn.get("message_summary", "")[:200]
            parts.append(f"[{role} T{turn.get('turn_index', '?')}]: {summary}")
        parts.append("")

    # Positions
    positions = state.get("positions", {})
    if positions:
        parts.append("=== CURRENT POSITIONS ===")
        for party_id, pdata in positions.items():
            proposals = pdata.get("proposals", [])
            for p in proposals[:2]:
                if isinstance(p, dict):
                    stmt = p.get("statement") or p.get("summary", "")
                    parts.append(f"{party_id}: {stmt[:120]}")
        parts.append("")

    # Open missing info
    missing = [m for m in state.get("missing_info", [])
               if isinstance(m, dict) and m.get("status") not in ("resolved", "withdrawn")]
    if missing:
        parts.append("=== OPEN INFORMATION GAPS ===")
        for item in missing[:5]:
            topic = item.get("topic") or item.get("item", "")
            parts.append(f"  - {topic}")
        parts.append("")

    # Plugin assessment
    parts.append("=== PLUGIN ASSESSMENT ===")
    parts.append(f"Plugin confidence: {plugin_assessment.get('plugin_confidence', 'unknown')}")
    parts.append(f"Option posture: {plugin_assessment.get('option_posture', 'none')}")
    flags = plugin_assessment.get("active_flag_types", [])
    if flags:
        parts.append(f"Active flag types: {', '.join(flags)}")
    families = plugin_assessment.get("issue_families", [])
    if isinstance(families, dict):
        families = [k for k, v in families.items() if v]
    if families:
        parts.append(f"Issue families: {', '.join(families)}")
    parts.append("")

    # Party state — the key safety veto input
    if party_state is not None:
        parts.append("=== PARTY STATE (accumulated prior turns) ===")
        parts.append("Apply the safety veto rule against the following:")
        parts.append("")
        for pid in ("party_a", "party_b"):
            pb = party_state.get(pid, {})
            if not pb:
                continue
            parts.append(f"{pid.upper()}:")
            parts.append(f"  Emotional state: {pb.get('current_emotional_state', 'unknown')}")
            parts.append(f"  Relational posture: {pb.get('current_relational_posture', 'unknown')}")

            acc = pb.get("accumulated_interests", [])
            observed = [i.get("interest", "") for i in acc
                        if i.get("interest") and not i.get("interest", "").startswith("unknown")]
            if observed:
                parts.append(f"  Accumulated interests ({len(observed)}): {'; '.join(observed[:6])}")
            else:
                parts.append("  Accumulated interests: NONE OBSERVED (party not yet heard or only unknown entries)")

            risks = [r.get("signal", "") for r in pb.get("risk_signal_history", [])
                     if r.get("signal") and not r.get("resolved", False)]
            if risks:
                parts.append(f"  Active risk signals: {'; '.join(risks[:4])}")

            arc = pb.get("relational_posture_progression", [])
            if arc:
                last = arc[-1]
                parts.append(f"  Latest posture: T{last.get('turn_index','?')} — {last.get('posture','?')}")

        cross = party_state.get("cross_party", {})
        dyn = cross.get("current_relational_dynamic", "")
        if dyn:
            parts.append(f"Cross-party dynamic: {dyn}")
        parts.append("")

    # Safety monitor signals (Stage 5) — injected before option pool so the
    # domain reasoner sees them when checking the safety veto rule.
    if safety_monitor_signals:
        parts.append("=== SAFETY MONITOR SIGNALS (Stage 5) ===")
        parts.append(
            "The dedicated safety monitor has observed cross-turn patterns and raised "
            "the following signals. If any signal contains a VETO CATEGORY directive, "
            "apply it — set safety_veto_applied=true and option_readiness='blocked'. "
            "You do NOT need to re-detect the pattern yourself; trust the monitor's finding."
        )
        for signal in safety_monitor_signals:
            parts.append(f"  {signal}")
        parts.append("")

    # Perception agent signals (Stage 6) — richer party interest/concern signals.
    # These are INFORMATIONAL ONLY for domain analysis purposes.
    # CRITICAL: Do NOT self-apply CATEGORY 1/2/3 vetoes based on perception
    # signals. All structural CATEGORY vetoes must come from the
    # SAFETY MONITOR SIGNALS section above. The perception agent's
    # engagement_quality and unsaid_signals enrich the domain analysis and
    # option interest-alignment — they are not veto triggers.
    if (
        perception_agent_result
        and not perception_agent_result.get("_null_result")
    ):
        pa = perception_agent_result.get("party_a") or {}
        pb = perception_agent_result.get("party_b") or {}
        has_pa_signals = (
            pa.get("inferred_concerns")
            or pa.get("unsaid_signals")
        )
        has_pb_signals = (
            pb.get("inferred_concerns")
            or pb.get("unsaid_signals")
        )
        if has_pa_signals or has_pb_signals:
            parts.append("=== PERCEPTION AGENT SIGNALS (Stage 6 — informational) ===")
            parts.append(
                "The following perception signals are context for your domain analysis and "
                "option interest-alignment. They are NOT veto triggers. "
                "Do not apply CATEGORY 1/2/3 vetoes based on these signals alone — "
                "structural vetoes come exclusively from the SAFETY MONITOR SIGNALS section."
            )
            if pa.get("inferred_concerns"):
                parts.append(f"Party A underlying concerns: {'; '.join(pa['inferred_concerns'][:3])}")
            if pa.get("unsaid_signals"):
                parts.append(f"Party A unsaid signals: {'; '.join(pa['unsaid_signals'][:3])}")
            if pb.get("inferred_concerns"):
                parts.append(f"Party B underlying concerns: {'; '.join(pb['inferred_concerns'][:3])}")
            if pb.get("unsaid_signals"):
                parts.append(f"Party B unsaid signals: {'; '.join(pb['unsaid_signals'][:3])}")
            # Perception agent's synthesized notes — what matters most this turn.
            # Complements the raw party signals above; provides the agent's
            # overall synthesis judgment rather than per-party field extracts.
            perception_notes = perception_agent_result.get("perception_notes") or []
            if perception_notes:
                parts.append(f"Perception agent key observations: {'; '.join(perception_notes[:3])}")
            parts.append("")

    # Brainstormer option pool (Stage 4 only)
    if option_pool:
        parts.append("=== BRAINSTORMER OPTION POOL ===")
        parts.append(
            "These candidates were generated by the brainstorming pass. "
            "Qualify each one, add your own domain-expert candidates, "
            "and return the full qualification in option_pool_qualification."
        )
        for candidate in option_pool:
            cid = candidate.get("candidate_id", "?")
            label = candidate.get("label", "?")
            rationale = candidate.get("rationale", "")[:150]
            parts.append(f"  [{cid}] {label}: {rationale}")
        parts.append("")

    # Task
    parts.append("=== YOUR TASK ===")
    if option_pool:
        parts.append(
            f"Assess option readiness for turn {turn_index}. "
            "Apply the safety veto rule first. Then determine option_readiness. "
            "Qualify the brainstormer candidates above, add your own domain-expert candidates, "
            "and return option_pool_qualification along with your normal domain analysis output."
        )
    else:
        parts.append(
            f"Assess option readiness for turn {turn_index}. "
            "Apply the safety veto rule first. Then determine option_readiness. "
            "If ready, qualify candidate options from the domain option space. "
            "Return your assessment as a JSON object matching the specified output format."
        )

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_domain_analysis(
    turn_index: int,
    timestamp: str,
    state: dict,
    party_state: dict | None,
    plugin_assessment: dict,
    session_history: list[dict],
    option_pool: list[dict] | None = None,
    safety_monitor_signals: list[str] | None = None,
    perception_agent_result: dict | None = None,
) -> dict:
    """
    Call the domain reasoner and return a domain_analysis dict.

    Parameters
    ----------
    option_pool:
        Optional list of brainstormer candidate dicts from
        ``option_generator.generate_option_pool()``.  When provided
        (Stage 4 path), the domain reasoner qualifies the incoming pool
        and adds its own domain-expert candidates before returning the
        full ``option_pool_qualification`` block.  When absent (Stage 3
        path), behaviour is unchanged.
    safety_monitor_signals:
        Optional list of veto/caution signal strings from the Stage 5
        safety monitor.  When present, injected into the domain context
        before the safety veto check so the domain reasoner can honour
        CATEGORY 1/2/3 directives without needing to re-detect them.

    On any failure (API error, parse failure), returns a minimal
    fallback dict with option_readiness="deferred" so the main
    lm_engine pass can proceed without crashing.
    """
    try:
        client = _make_client()
        model = _get_model()

        user_content = _build_domain_context(
            state=state,
            party_state=party_state,
            plugin_assessment=plugin_assessment,
            session_history=session_history,
            turn_index=turn_index,
            option_pool=option_pool or [],
            safety_monitor_signals=safety_monitor_signals,
            perception_agent_result=perception_agent_result,
        )

        response = client.messages.create(
            model=model,
            max_tokens=6000,
            system=_DOMAIN_REASONER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )

        raw = response.content[0].text
        parsed = _parse_response(raw)

        meta = state.get("meta", {})
        parsed["schema_version"] = "domain_analysis.v0"
        parsed["case_id"] = meta.get("case_id", "unknown")
        parsed["session_id"] = meta.get("session_id", "unknown")
        parsed["turn_index"] = turn_index
        parsed["generated_at"] = timestamp
        parsed["source"] = "domain_reasoner_v0"

        # Enforce invariants from CONTRACT-016
        _enforce_invariants(parsed)

        # Normalise and stamp source fields on option pool candidates (CONTRACT-017).
        # Always called — normalisation fixes LLM field-name variance in domain_qualified
        # (option_label→label, etc.) regardless of whether a brainstormer pool was supplied.
        _stamp_domain_expert_sources(parsed)

        return parsed

    except Exception as exc:  # noqa: BLE001
        return _fallback(turn_index, timestamp, state, reason=str(exc))


# ---------------------------------------------------------------------------
# Invariant enforcement
# ---------------------------------------------------------------------------

def _normalize_candidate(candidate: dict, fallback_source: str, index: int) -> None:
    """
    Normalise a single candidate dict in-place to match qualifiedCandidate schema.

    The LLM occasionally uses non-standard field names:
    - option_label  → label
    - option_description → label (when label is still absent after above)
    - option_id / id → candidate_id
    Missing required fields (candidate_id, source) are defaulted.
    """
    # Label aliases
    if "label" not in candidate and "option_label" in candidate:
        candidate["label"] = candidate.pop("option_label")
    if "label" not in candidate and "option_description" in candidate:
        candidate["label"] = candidate.pop("option_description")
    # Remove non-schema fields that would cause additionalProperties violations
    for bad_key in ("option_label", "option_description"):
        candidate.pop(bad_key, None)
    # candidate_id aliases
    if "candidate_id" not in candidate:
        for alias in ("option_id", "id"):
            if alias in candidate:
                candidate["candidate_id"] = candidate.pop(alias)
                break
    if "candidate_id" not in candidate:
        candidate["candidate_id"] = f"dr-norm-{index:03d}"
    # source default
    candidate.setdefault("source", fallback_source)


def _stamp_domain_expert_sources(da: dict) -> None:
    """
    Stamp source="domain_reasoner" on all domain_expert_candidates and
    ensure source is preserved on items in domain_qualified/domain_blocked
    that originated from the brainstormer (source="option_generator").

    Also normalises field names via _normalize_candidate so LLM output
    variance (option_label, option_description, etc.) doesn't cause
    option_pool.json schema violations.

    This keeps CONTRACT-017's source provenance invariant without requiring
    the LLM to track source strings.
    """
    opq = da.get("option_pool_qualification")
    if not isinstance(opq, dict):
        return
    for i, candidate in enumerate(opq.get("domain_expert_candidates", [])):
        if isinstance(candidate, dict):
            _normalize_candidate(candidate, "domain_reasoner", i)
    # Qualified and blocked entries may originate from either agent; default
    # source to "domain_reasoner" and normalise field names.
    for i, entry in enumerate(opq.get("domain_qualified", [])):
        if isinstance(entry, dict):
            _normalize_candidate(entry, "domain_reasoner", i)
    for i, entry in enumerate(opq.get("domain_blocked", [])):
        if isinstance(entry, dict):
            _normalize_candidate(entry, "domain_reasoner", i)


def _enforce_invariants(da: dict) -> None:
    """
    Enforce CONTRACT-016 invariants in-place.

    - option_readiness == "blocked" when safety_veto_applied is True
    - qualified_candidates is empty when option_readiness != "ready"
    - safety_veto_reason is non-null when safety_veto_applied is True
    """
    if da.get("safety_veto_applied"):
        da["option_readiness"] = "blocked"
        if not da.get("safety_veto_reason"):
            da["safety_veto_reason"] = "safety_veto_applied_but_reason_not_specified"

    if da.get("option_readiness") != "ready":
        da["qualified_candidates"] = []


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
        "option_readiness": "deferred",
        "readiness_rationale": "Domain reasoner response could not be parsed.",
        "safety_veto_applied": False,
        "safety_veto_reason": None,
        "qualified_candidates": [],
        "blocking_constraints": [],
        "material_gaps": [],
        "domain_confidence": "low",
        "domain_notes": f"Parse failed. Raw text (first 300 chars): {raw[:300]}",
        "_parse_error": True,
    }


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------

def _fallback(turn_index: int, timestamp: str, state: dict, reason: str = "") -> dict:
    """Return a safe fallback domain_analysis when the call fails."""
    meta = state.get("meta", {})
    return {
        "schema_version": "domain_analysis.v0",
        "case_id": meta.get("case_id", "unknown"),
        "session_id": meta.get("session_id", "unknown"),
        "turn_index": turn_index,
        "generated_at": timestamp,
        "source": "domain_reasoner_v0",
        "option_readiness": "deferred",
        "readiness_rationale": "Domain reasoner unavailable — falling back to deferred.",
        "safety_veto_applied": False,
        "safety_veto_reason": None,
        "qualified_candidates": [],
        "blocking_constraints": [],
        "material_gaps": [],
        "domain_confidence": "low",
        "domain_notes": f"Fallback: {reason[:200]}" if reason else "Fallback: domain reasoner call failed.",
        "_fallback": True,
    }


# ---------------------------------------------------------------------------
# Client helpers (shared with lm_engine.py)
# ---------------------------------------------------------------------------

def _load_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        from dotenv import dotenv_values
        key = dotenv_values(env_path).get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not found.")
    return key


def _make_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=_load_api_key())


def _get_model() -> str:
    # Domain reasoner uses the same model as lm_engine by default.
    # Can be independently overridden via SOLOMON_DOMAIN_MODEL env var.
    return os.environ.get("SOLOMON_DOMAIN_MODEL") or os.environ.get("SOLOMON_LM_MODEL", "claude-sonnet-4-5")
