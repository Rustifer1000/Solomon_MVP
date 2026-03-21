from __future__ import annotations

from copy import deepcopy

from runtime.contracts import CandidateTurn, serialize_candidate_turn


def initialize_session_state(
    case_bundle: dict,
    session_id: str,
    policy_profile: str,
    source: str = "reference",
    process_variant: str | None = None,
) -> dict:
    metadata = case_bundle["case_metadata"]
    participants = list(case_bundle["personas"].keys())
    return {
        "meta": {
            "case_id": metadata["case_id"],
            "benchmark_id": metadata["benchmark_id"],
            "session_id": session_id,
            "policy_profile": policy_profile,
            "source": source,
            "process_variant": process_variant,
            "plugin_type": metadata["plugin_type"],
            "title": metadata["title"],
        },
        "participants": participants,
        "phase": "session_framing",
        "issue_map": [],
        "open_questions": [],
        "positions": {},
        "facts": [],
        "missing_info": [],
        "options": [],
        "flags": [],
        "plugin_assessment": {},
        "escalation": {
            "category": None,
            "threshold_band": None,
            "mode": "M0",
            "rationale": "No caution state has been selected yet.",
        },
        "trace_buffer": [],
        "summary_state": {
            "issues": [],
            "next_step": None,
        },
    }


def snapshot_trace_turn(turn: CandidateTurn | dict) -> dict:
    if isinstance(turn, CandidateTurn):
        return deepcopy(serialize_candidate_turn(turn))
    return deepcopy(turn)


def _append_unique(items: list, value) -> None:
    if value not in items:
        items.append(value)


def _canonical_issue_from_update(update: str) -> str | None:
    mapping = {
        "parenting_schedule": "Parenting schedule",
        "school_logistics": "School logistics",
        "communication_protocol": "Communication protocol around future changes",
        "fairness_and_parent_role": "Fairness and meaningful parenting role",
        "meaningful_parent_role": "Fairness and meaningful parenting role",
        "child_stability": "Parenting schedule",
    }
    for key, label in mapping.items():
        if key in update:
            return label
    return None


def _slug(text: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in text).strip("-")


def _infer_related_issues(text: str) -> list[str]:
    lowered = text.lower()
    issues = []
    keyword_map = {
        "parenting_schedule": ["overnight", "parenting", "weekday", "school-week"],
        "school_logistics": ["transport", "commute", "exchange timing", "homework", "routine", "logistics"],
        "fairness_and_parent_role": ["meaningful relationship", "meaningful parenting-role", "secondary parent", "visitor-level"],
        "communication_protocol": ["notice", "clarified", "reliability markers"],
    }
    for issue_id, keywords in keyword_map.items():
        if any(keyword in lowered for keyword in keywords):
            issues.append(issue_id)
    return issues or ["parenting_schedule"]


def _infer_fact_category(text: str) -> str:
    lowered = text.lower()
    if "dispute" in lowered or "overnight" in lowered:
        return "parenting_schedule"
    if "child" in lowered or "relationship" in lowered:
        return "family_structure"
    if "accept" in lowered or "clarification" in lowered:
        return "timeline"
    if "unresolved" in lowered or "sufficient" in lowered:
        return "timeline"
    return "communication_history"


def _infer_fact_status(text: str) -> str:
    lowered = text.lower()
    if "unresolved" in lowered or "sufficient" in lowered:
        return "uncertain"
    if "justify limiting" in lowered:
        return "disputed"
    return "accepted"


def _canonicalize_fact_statement(text: str) -> str:
    lowered = text.lower()
    logistics_signals = ["commute", "exchange timing", "homework", "evening-routine", "unresolved"]
    if sum(signal in lowered for signal in logistics_signals) >= 2 or (
        "commute" in lowered or "exchange timing" in lowered or "homework" in lowered
    ):
        return "Transport, exchange timing, and homework-routine reliability are already sufficient to support expanded school-week overnights."
    return text


def _infer_fact_note(text: str, status: str) -> str | None:
    lowered = text.lower()
    if "secondary parent" in lowered or "meaningful parenting-role" in lowered:
        return "Accepted as a stated process-relevant concern, not as an adjudicated conclusion about intent."
    if status == "uncertain":
        return "The session surfaced these items as unresolved rather than settled."
    if status == "disputed":
        return "This remains a stated concern rather than a settled conclusion."
    return None


def _add_fact(state: dict, turn_index: int, statement: str) -> None:
    canonical_statement = _canonicalize_fact_statement(statement)
    for existing in state["facts"]:
        if existing["statement"] == canonical_statement:
            _append_unique(existing["source_turns"], turn_index)
            return

    state["facts"].append(
        {
            "fact_id": f"fact-{len(state['facts']) + 1:03d}",
            "category": _infer_fact_category(statement),
            "statement": canonical_statement,
            "status": _infer_fact_status(statement),
            "source_turns": [turn_index],
            "related_issues": _infer_related_issues(statement),
            "note": _infer_fact_note(statement, _infer_fact_status(statement)),
        }
    )


def _ensure_participant(state: dict, participant_id: str) -> dict:
    if participant_id not in state["positions"]:
        state["positions"][participant_id] = {
            "participant_id": participant_id,
            "current_positions": [],
            "proposals": [],
            "red_lines": [],
            "soft_preferences": [],
            "open_to_discussion": [],
            "last_updated_turn": 0,
        }
    return state["positions"][participant_id]


def _infer_participant_ids(statement: str) -> list[str]:
    lowered = statement.lower()
    if "spouse_a" in lowered or "parent a" in lowered:
        return ["spouse_A"]
    if "spouse_b" in lowered or "parent b" in lowered:
        return ["spouse_B"]
    if "both parents" in lowered:
        return ["spouse_A", "spouse_B"]
    return []


def _clean_position_statement(statement: str) -> str:
    cleaned = statement.replace("spouse_A seeks ", "").replace("spouse_B seeks ", "")
    return cleaned[0].upper() + cleaned[1:] if cleaned else statement


def _position_record(participant_id: str, turn_index: int, statement: str) -> dict:
    lowered = statement.lower()
    if "conditional openness" in lowered or "open to phased exploration" in lowered:
        proposal_statement = (
            "A phased trial could be discussed if reliability conditions are explicit and school-week disruption is minimized."
            if participant_id == "spouse_A"
            else "A phased trial is acceptable if it clearly leads to meaningful school-week parenting time rather than indefinite delay."
        )
        return {
            "kind": "proposal",
            "payload": {
                "proposal_id": f"prop-{participant_id.lower()}-001",
                "issue_id": "parenting_schedule",
                "statement": proposal_statement,
                "status": "tentative",
                "source_turns": [turn_index],
            },
        }
    return {
        "kind": "position",
        "payload": {
            "position_id": f"pos-{participant_id.lower()}-001",
            "issue_id": "parenting_schedule",
            "statement": _clean_position_statement(statement),
            "status": "current",
            "confidence": "high",
            "source_turns": [turn_index],
        },
    }


def _update_positions(state: dict, turn_index: int, statement: str) -> None:
    participant_ids = _infer_participant_ids(statement)
    if not participant_ids:
        return

    for participant_id in participant_ids:
        participant = _ensure_participant(state, participant_id)
        record = _position_record(participant_id, turn_index, statement)
        if record["kind"] == "position":
            participant["current_positions"] = [record["payload"]]
            if participant_id == "spouse_A":
                participant["red_lines"] = [
                    "No week-to-week school-night changes without predictable notice.",
                    "No expansion that ignores unresolved commute and homework-routine concerns.",
                ]
                participant["soft_preferences"] = ["A stepwise approach rather than an immediate large change."]
                participant["open_to_discussion"] = ["Conditional trial arrangements tied to reliability markers."]
                _add_fact(
                    state,
                    turn_index,
                    "The child's current dysregulation risk after irregular exchanges is significant enough to justify limiting school-night overnights now.",
                )
            else:
                participant["red_lines"] = [
                    "No arrangement that leaves Parent B in a visitor-level role.",
                    "No unilateral control over future schedule changes by the other parent.",
                ]
                participant["soft_preferences"] = ["A fairness-oriented structure that recognizes meaningful weekday parenting."]
                participant["open_to_discussion"] = [
                    "Contingent or phased options if they are tied to concrete logistics rather than vague reassurance."
                ]
        else:
            existing_ids = {item["proposal_id"] for item in participant["proposals"]}
            payload = record["payload"]
            if payload["proposal_id"] not in existing_ids:
                participant["proposals"].append(payload)
            else:
                for existing in participant["proposals"]:
                    if existing["proposal_id"] == payload["proposal_id"]:
                        _append_unique(existing["source_turns"], turn_index)
        participant["last_updated_turn"] = turn_index


def _update_missing_info(state: dict, turn_index: int, question: str, status: str) -> None:
    lowered = question.lower()
    if "transport plan" in lowered or "school-week exchanges" in lowered:
        template = {
            "missing_id": "missing-001",
            "question": "What specific transport plan would support school-week exchanges without creating school-day instability?",
            "importance": "high",
            "reason_type": "feasibility_gap",
            "related_issues": ["school_logistics", "parenting_schedule"],
            "note": "This is the clearest unresolved constraint on stronger optioning.",
        }
    elif "reliability markers" in lowered or "phased trial" in lowered:
        template = {
            "missing_id": "missing-002",
            "question": "What reliability markers would both parents treat as sufficient for a phased school-week trial?",
            "importance": "high",
            "reason_type": "process_gap",
            "related_issues": ["parenting_schedule", "communication_protocol"],
            "note": "The parents showed openness to a phased arrangement only if the success conditions are explicit.",
        }
    elif "workable" in lowered or "homework" in lowered or "evening-routine" in lowered:
        template = {
            "missing_id": "missing-003",
            "question": "How should homework and evening-routine responsibility be handled on any trial school-night arrangement?",
            "importance": "medium",
            "reason_type": "feasibility_gap",
            "related_issues": ["school_logistics", "parenting_schedule"],
            "note": "The session surfaced this as part of the routine-stability concern but did not resolve it.",
        }
    else:
        return

    for existing in state["missing_info"]:
        if existing["missing_id"] == template["missing_id"]:
            existing["status"] = status
            return

    state["missing_info"].append(
        {
            "missing_id": template["missing_id"],
            "question": template["question"],
            "importance": template["importance"],
            "reason_type": template["reason_type"],
            "related_issues": template["related_issues"],
            "first_identified_turn": turn_index,
            "status": status,
            "note": template["note"],
        }
    )


def _update_flags(state: dict, turn: CandidateTurn) -> None:
    turn_index = turn.turn_index
    signal_set = set(turn.risk_check.signals)
    flag_templates = []
    if "insufficient_information" in signal_set and turn_index >= 6:
        flag_templates.append(
            {
                "flag_id": "flag-db04-001",
                "flag_type": "insufficient_information",
                "severity": 3,
                "source": "platform",
                "first_detected_turn": 6,
                "last_updated_turn": turn_index,
                "related_categories": ["E5"],
                "threshold_band": "T1",
                "title": "Material school-logistics gaps remain unresolved",
                "note": "Transport, exchange timing, and homework-routine questions still materially limit responsible schedule recommendation.",
                "signal_classes": ["insufficient_information", "feasibility_gap"],
                "related_issues": ["school_logistics", "parenting_schedule"],
                "source_turns": [turn_index],
            }
        )
    if "decision_quality_risk" in signal_set:
        flag_templates.append(
            {
                "flag_id": "flag-db04-002",
                "flag_type": "decision_quality_risk",
                "severity": 2,
                "source": "plugin",
                "first_detected_turn": 6,
                "last_updated_turn": turn_index,
                "related_categories": ["E5"],
                "threshold_band": "T1",
                "title": "Option qualification remains incomplete",
                "note": "A fixed overnight recommendation would overstate domain confidence before logistics are clarified.",
                "signal_classes": ["decision_quality_risk", "domain_complexity_warning"],
                "related_issues": ["parenting_schedule", "school_logistics"],
                "source_turns": [turn_index],
            }
        )
    if "plugin_low_confidence" in signal_set:
        flag_templates.append(
            {
                "flag_id": "flag-db04-003",
                "flag_type": "plugin_low_confidence",
                "severity": 2,
                "source": "plugin",
                "first_detected_turn": 7,
                "last_updated_turn": turn_index,
                "related_categories": ["E5"],
                "threshold_band": "T1",
                "title": "Plugin supports caution but not fixed recommendation",
                "note": "The divorce plugin can support phased or contingent exploration, but not a stronger feasibility claim yet.",
                "signal_classes": ["plugin_low_confidence"],
                "related_issues": ["parenting_schedule"],
                "source_turns": [turn_index],
            }
        )

    for template in flag_templates:
        existing = next((flag for flag in state["flags"] if flag["flag_id"] == template["flag_id"]), None)
        if existing is None:
            state["flags"].append(
                {
                    **template,
                    "status": "active",
                    "hard_trigger": False,
                    "cleared_turn": None,
                }
            )
        else:
            existing["last_updated_turn"] = turn_index
            _append_unique(existing["source_turns"], turn_index)


def apply_turn(state: dict, turn: CandidateTurn) -> None:
    state["phase"] = turn.phase
    state["trace_buffer"].append(snapshot_trace_turn(turn))

    delta = turn.state_delta
    for update in delta.issue_map_updates:
        label = _canonical_issue_from_update(update)
        if label is not None:
            _append_unique(state["summary_state"]["issues"], label)
    for question in delta.open_questions_added:
        _append_unique(state["open_questions"], question)
        _update_missing_info(state, turn.turn_index, question, "open")
    for question in delta.open_questions_resolved:
        if question in state["open_questions"]:
            state["open_questions"].remove(question)
    for statement in delta.facts_added:
        _add_fact(state, turn.turn_index, statement)
    for statement in delta.positions_added_or_updated:
        _update_positions(state, turn.turn_index, statement)
    for option in delta.option_state_updates:
        _append_unique(state["options"], option)
    for update in delta.escalation_state_updates:
        state["escalation"]["rationale"] = update

    _update_flags(state, turn)

    if turn.candidate_escalation_mode:
        state["escalation"]["mode"] = turn.candidate_escalation_mode
    if turn.candidate_escalation_category:
        state["escalation"]["category"] = turn.candidate_escalation_category

    if state["escalation"]["mode"] == "M1":
        state["escalation"]["threshold_band"] = "T1"

    if turn.turn_index == 8:
        state["summary_state"]["next_step"] = (
            "Use the next session to clarify transport, exchange timing, and homework-routine expectations, "
            "then revisit whether a phased school-week trial can be explored without overstating feasibility."
        )
