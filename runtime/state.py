from __future__ import annotations

from copy import deepcopy

from runtime.contracts import CandidateTurn, FactDelta, IssueUpdate, MissingInfoDelta, PackageDelta, PositionDelta, serialize_candidate_turn
from runtime.policy_profiles import get_policy_profile


def initialize_session_state(
    case_bundle: dict,
    session_id: str,
    policy_profile: str,
    source: str = "reference",
    process_variant: str | None = None,
    review_transcript_renderer: str = "none",
) -> dict:
    get_policy_profile(policy_profile)
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
            "review_transcript_renderer": review_transcript_renderer,
            "plugin_type": metadata["plugin_type"],
            "benchmark_descriptor": None,
            "plugin_policy_descriptor": None,
            "artifact_narrative_policy": None,
            "support_artifact_policy": None,
            "package_element_labels": {},
            "evaluator_helper_policy": None,
            "title": metadata["title"],
        },
        "participants": participants,
        "case_personas": deepcopy(case_bundle["personas"]),
        "phase": "session_framing",
        "issue_map": [],
        "open_questions": [],
        "positions": {},
        "facts": [],
        "missing_info": [],
        "packages": [],
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


ISSUE_LABELS = {
    "parenting_schedule": "Parenting schedule",
    "school_logistics": "School logistics",
    "communication_protocol": "Communication protocol around future changes",
    "fairness_and_parent_role": "Fairness and meaningful parenting role",
    "child_expense_coordination": "Child expense coordination and reimbursement",
    "meaningful_parent_role": "Fairness and meaningful parenting role",
    "child_stability": "Parenting schedule",
}


def _canonical_issue_from_update(update: str) -> str | None:
    for key, label in ISSUE_LABELS.items():
        if key in update:
            return label
    return None


def _slug(text: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in text).strip("-")


FALLBACK_FACT_TEMPLATES = {
    "there is an active dispute about school-night overnights.": {
        "category": "parenting_schedule",
        "status": "accepted",
        "related_issues": ["parenting_schedule"],
    },
    "the child has school-related routine needs that both parents recognize as important.": {
        "category": "family_structure",
        "status": "accepted",
        "related_issues": ["parenting_schedule", "school_logistics"],
    },
    "parent b links school-week overnights to meaningful parenting-role concerns.": {
        "category": "family_structure",
        "status": "accepted",
        "related_issues": ["fairness_and_parent_role", "parenting_schedule"],
    },
    "both parents identify child stability as important.": {
        "category": "family_structure",
        "status": "accepted",
        "related_issues": ["parenting_schedule"],
    },
    "both parents want the child to maintain a meaningful relationship with each parent.": {
        "category": "family_structure",
        "status": "accepted",
        "related_issues": ["fairness_and_parent_role", "parenting_schedule"],
    },
    "both parents accept clarification of logistics as the bounded next step.": {
        "category": "timeline",
        "status": "accepted",
        "related_issues": ["school_logistics", "parenting_schedule"],
    },
    "school commute feasibility is unresolved.": {
        "category": "timeline",
        "status": "uncertain",
        "related_issues": ["school_logistics", "parenting_schedule"],
    },
    "exchange timing reliability is unresolved.": {
        "category": "timeline",
        "status": "uncertain",
        "related_issues": ["school_logistics", "parenting_schedule"],
    },
    "homework and evening-routine reliability is unresolved.": {
        "category": "timeline",
        "status": "uncertain",
        "related_issues": ["school_logistics", "parenting_schedule"],
    },
    "transport, exchange timing, and homework-routine reliability remain unresolved for school-week overnights.": {
        "category": "timeline",
        "status": "uncertain",
        "related_issues": ["school_logistics", "parenting_schedule"],
    },
}


def _fallback_fact_template(statement: str) -> dict | None:
    return FALLBACK_FACT_TEMPLATES.get(statement.lower())


def _infer_fact_category(text: str) -> str:
    template = _fallback_fact_template(_canonicalize_fact_statement(text))
    if template is not None:
        return template["category"]
    return "communication_history"


def _infer_fact_status(text: str) -> str:
    template = _fallback_fact_template(_canonicalize_fact_statement(text))
    if template is not None:
        return template["status"]
    return "accepted"


def _canonicalize_fact_statement(text: str) -> str:
    lowered = text.lower()
    if "unresolved" in lowered and (
        "commute" in lowered
        or "transport" in lowered
        or "exchange timing" in lowered
        or "homework" in lowered
        or "evening-routine" in lowered
    ):
        return "Transport, exchange timing, and homework-routine reliability remain unresolved for school-week overnights."
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


def _infer_related_issues(text: str) -> list[str]:
    template = _fallback_fact_template(_canonicalize_fact_statement(text))
    if template is not None:
        return template["related_issues"]
    return ["parenting_schedule"]


def _write_fact(
    state: dict,
    turn_index: int,
    statement: str,
    category: str,
    status: str,
    related_issues: list[str],
    note: str | None,
) -> None:
    canonical_statement = _canonicalize_fact_statement(statement)
    for existing in state["facts"]:
        if existing["statement"] == canonical_statement:
            _append_unique(existing["source_turns"], turn_index)
            return

    state["facts"].append(
        {
            "fact_id": f"fact-{len(state['facts']) + 1:03d}",
            "category": category,
            "statement": canonical_statement,
            "status": status,
            "source_turns": [turn_index],
            "related_issues": related_issues,
            "note": note,
        }
    )


def _add_fact(state: dict, turn_index: int, statement: str) -> None:
    status = _infer_fact_status(statement)
    _write_fact(
        state,
        turn_index,
        statement,
        _infer_fact_category(statement),
        status,
        _infer_related_issues(statement),
        _infer_fact_note(statement, status),
    )


def _add_structured_fact(state: dict, turn_index: int, fact: FactDelta) -> None:
    status = fact.status or _infer_fact_status(fact.statement)
    _write_fact(
        state,
        turn_index,
        fact.statement,
        fact.category or _infer_fact_category(fact.statement),
        status,
        fact.related_issues or _infer_related_issues(fact.statement),
        fact.note if fact.note is not None else _infer_fact_note(fact.statement, status),
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
    cleaned = statement
    for prefix in [
        "spouse_A seeks ",
        "spouse_B seeks ",
        "Parent A and Parent B remain ",
        "Both parents show ",
    ]:
        cleaned = cleaned.replace(prefix, "")
    return cleaned[0].upper() + cleaned[1:] if cleaned else statement


def _position_record(participant_id: str, turn_index: int, statement: str) -> dict:
    lowered = statement.lower()
    cleaned_statement = _clean_position_statement(statement)
    if "conditional openness" in lowered or "open to" in lowered:
        return {
            "kind": "proposal",
            "payload": {
                "proposal_id": f"prop-{participant_id.lower()}-001",
                "issue_id": "parenting_schedule",
                "statement": cleaned_statement,
                "status": "tentative",
                "source_turns": [turn_index],
            },
        }
    return {
        "kind": "position",
        "payload": {
            "position_id": f"pos-{participant_id.lower()}-001",
            "issue_id": "parenting_schedule",
            "statement": cleaned_statement,
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


def _update_positions_structured(state: dict, turn_index: int, position: PositionDelta) -> None:
    for participant_id in position.participant_ids:
        participant = _ensure_participant(state, participant_id)
        if position.kind == "position":
            participant["current_positions"] = [
                {
                    "position_id": position.position_id or f"pos-{participant_id.lower()}-001",
                    "issue_id": position.issue_id,
                    "statement": position.statement,
                    "status": position.status,
                    "confidence": position.confidence or "high",
                    "source_turns": [turn_index],
                }
            ]
        else:
            proposal_id = position.proposal_id or f"prop-{participant_id.lower()}-001"
            existing = next((item for item in participant["proposals"] if item["proposal_id"] == proposal_id), None)
            if existing is None:
                participant["proposals"].append(
                    {
                        "proposal_id": proposal_id,
                        "issue_id": position.issue_id,
                        "statement": position.statement,
                        "status": position.status,
                        "source_turns": [turn_index],
                    }
                )
            else:
                _append_unique(existing["source_turns"], turn_index)
        participant["last_updated_turn"] = turn_index


FALLBACK_MISSING_INFO_TEMPLATES = {
    "what transport plan would support school-week exchanges?": {
        "missing_id": "missing-001",
        "question": "What specific transport plan would support school-week exchanges without creating school-day instability?",
        "importance": "high",
        "reason_type": "feasibility_gap",
        "related_issues": ["school_logistics", "parenting_schedule"],
        "note": "This is the clearest unresolved constraint on stronger optioning.",
    },
    "what reliability markers would both parents treat as sufficient for a phased trial?": {
        "missing_id": "missing-002",
        "question": "What reliability markers would both parents treat as sufficient for a phased school-week trial?",
        "importance": "high",
        "reason_type": "process_gap",
        "related_issues": ["parenting_schedule", "communication_protocol"],
        "note": "The parents showed openness to a phased arrangement only if the success conditions are explicit.",
    },
    "what concrete logistics would make a phased school-week arrangement workable?": {
        "missing_id": "missing-003",
        "question": "How should homework and evening-routine responsibility be handled on any trial school-night arrangement?",
        "importance": "medium",
        "reason_type": "feasibility_gap",
        "related_issues": ["school_logistics", "parenting_schedule"],
        "note": "The session surfaced this as part of the routine-stability concern but did not resolve it.",
    },
    "which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?": {
        "missing_id": "missing-003",
        "question": "How should homework and evening-routine responsibility be handled on any trial school-night arrangement?",
        "importance": "medium",
        "reason_type": "feasibility_gap",
        "related_issues": ["school_logistics", "parenting_schedule"],
        "note": "The session surfaced this as part of the routine-stability concern but did not resolve it.",
    },
}


def _missing_info_template(question: str) -> dict | None:
    return FALLBACK_MISSING_INFO_TEMPLATES.get(question.lower())


def _set_missing_info_status(state: dict, question: str, status: str) -> None:
    template = _missing_info_template(question)
    if template is not None:
        for existing in state["missing_info"]:
            if existing["missing_id"] == template["missing_id"]:
                existing["status"] = status
                return
    for existing in state["missing_info"]:
        if existing["question"] == question:
            existing["status"] = status
            return


def _update_missing_info(state: dict, turn_index: int, question: str, status: str) -> None:
    template = _missing_info_template(question)
    if template is None:
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


def _update_missing_info_structured(state: dict, turn_index: int, item: MissingInfoDelta) -> None:
    existing = next((entry for entry in state["missing_info"] if entry["missing_id"] == item.missing_id), None)
    if item.action == "resolve":
        if existing is None:
            raise ValueError(f"Cannot resolve missing info before it is opened: {item.missing_id}")
        existing["status"] = "resolved"
        return

    if existing is not None:
        existing["status"] = "open"
        return

    state["missing_info"].append(
        {
            "missing_id": item.missing_id,
            "question": item.question,
            "importance": item.importance or "medium",
            "reason_type": item.reason_type or "process_gap",
            "related_issues": item.related_issues,
            "first_identified_turn": turn_index,
            "status": "open",
            "note": item.note,
        }
    )


def _apply_issue_update(state: dict, update: IssueUpdate) -> None:
    _append_unique(state["summary_state"]["issues"], update.label)


def _update_package_structured(state: dict, turn_index: int, package: PackageDelta) -> None:
    existing = next((item for item in state["packages"] if item["package_id"] == package.package_id), None)
    payload = {
        "package_id": package.package_id,
        "family": package.family,
        "status": package.status,
        "summary": package.summary,
        "elements": list(package.elements),
        "related_issues": list(package.related_issues),
        "last_updated_turn": turn_index,
    }
    if existing is None:
        state["packages"].append(payload)
        return
    existing.update(payload)


def merge_flag_templates(state: dict, flag_templates: list[dict]) -> None:
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
            existing["last_updated_turn"] = template["last_updated_turn"]
            for source_turn in template.get("source_turns", []):
                _append_unique(existing["source_turns"], source_turn)


def apply_turn(state: dict, turn: CandidateTurn) -> None:
    state["phase"] = turn.phase
    state["trace_buffer"].append(snapshot_trace_turn(turn))

    delta = turn.state_delta
    has_structured_issues = bool(delta.issue_updates_structured)
    has_structured_missing_info = bool(delta.missing_info_structured)
    has_structured_facts = bool(delta.facts_structured)
    has_structured_positions = bool(delta.positions_structured)

    for update in delta.issue_updates_structured:
        _apply_issue_update(state, update)
    if not has_structured_issues:
        for update in delta.issue_map_updates:
            label = _canonical_issue_from_update(update)
            if label is not None:
                _append_unique(state["summary_state"]["issues"], label)
    for item in delta.missing_info_structured:
        _update_missing_info_structured(state, turn.turn_index, item)
        if item.action == "open":
            _append_unique(state["open_questions"], item.question)
        else:
            if item.question in state["open_questions"]:
                state["open_questions"].remove(item.question)
    if not has_structured_missing_info:
        for question in delta.open_questions_added:
            _append_unique(state["open_questions"], question)
            _update_missing_info(state, turn.turn_index, question, "open")
        for question in delta.open_questions_resolved:
            if question in state["open_questions"]:
                state["open_questions"].remove(question)
            _set_missing_info_status(state, question, "resolved")
    for fact in delta.facts_structured:
        _add_structured_fact(state, turn.turn_index, fact)
    if not has_structured_facts:
        for statement in delta.facts_added:
            _add_fact(state, turn.turn_index, statement)
    for position in delta.positions_structured:
        _update_positions_structured(state, turn.turn_index, position)
    if not has_structured_positions:
        for statement in delta.positions_added_or_updated:
            _update_positions(state, turn.turn_index, statement)
    for package in delta.packages_structured:
        _update_package_structured(state, turn.turn_index, package)
    for option in delta.option_state_updates:
        _append_unique(state["options"], option)
    for update in delta.escalation_state_updates:
        state["escalation"]["rationale"] = update

    if turn.candidate_escalation_mode:
        state["escalation"]["mode"] = turn.candidate_escalation_mode
    if turn.candidate_escalation_category:
        state["escalation"]["category"] = turn.candidate_escalation_category

    if state["escalation"]["mode"] == "M1":
        state["escalation"]["threshold_band"] = "T1"

    if turn.phase == "agreement_building" and state["summary_state"]["next_step"] is None:
        if any(item["status"] == "open" for item in state["missing_info"]):
            state["summary_state"]["next_step"] = (
                "Use the next session to resolve the remaining open questions before treating any tentative option as settled."
            )
        elif state["options"]:
            state["summary_state"]["next_step"] = (
                "Use the next session to confirm the bounded options that appear workable and record any agreed process terms clearly."
            )
        else:
            state["summary_state"]["next_step"] = (
                "Use the next session to continue clarifying positions, interests, and process expectations without overstating agreement."
            )
