from __future__ import annotations

from runtime.contracts import CandidateTurn, FactDelta, IssueUpdate, MissingInfoDelta, PackageDelta, PositionDelta, RiskCheck, StateDelta, validate_candidate_turn


def _require_mapping(value, field_name: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping")
    return value


def _require_list_of_strings(value, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a list of strings")
    return value


def _require_list_of_mappings(value, field_name: str) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{field_name} must be a list of mappings")
    return value


def _normalize_fact_deltas(value) -> list[FactDelta]:
    facts = []
    for item in _require_list_of_mappings(value, "state_delta.facts_structured"):
        if not isinstance(item.get("statement"), str):
            raise ValueError("state_delta.facts_structured[].statement must be a string")
        related_issues = _require_list_of_strings(item.get("related_issues"), "state_delta.facts_structured[].related_issues")
        facts.append(
            FactDelta(
                statement=item["statement"],
                category=item.get("category"),
                status=item.get("status"),
                related_issues=related_issues,
                note=item.get("note"),
            )
        )
    return facts


def _normalize_position_deltas(value) -> list[PositionDelta]:
    positions = []
    for item in _require_list_of_mappings(value, "state_delta.positions_structured"):
        participant_ids = _require_list_of_strings(item.get("participant_ids"), "state_delta.positions_structured[].participant_ids")
        if not isinstance(item.get("kind"), str):
            raise ValueError("state_delta.positions_structured[].kind must be a string")
        if not isinstance(item.get("issue_id"), str):
            raise ValueError("state_delta.positions_structured[].issue_id must be a string")
        if not isinstance(item.get("statement"), str):
            raise ValueError("state_delta.positions_structured[].statement must be a string")
        if not isinstance(item.get("status"), str):
            raise ValueError("state_delta.positions_structured[].status must be a string")
        positions.append(
            PositionDelta(
                participant_ids=participant_ids,
                kind=item["kind"],
                issue_id=item["issue_id"],
                statement=item["statement"],
                status=item["status"],
                confidence=item.get("confidence"),
                proposal_id=item.get("proposal_id"),
                position_id=item.get("position_id"),
            )
        )
    return positions


def _normalize_missing_info_deltas(value) -> list[MissingInfoDelta]:
    missing_items = []
    for item in _require_list_of_mappings(value, "state_delta.missing_info_structured"):
        if not isinstance(item.get("action"), str):
            raise ValueError("state_delta.missing_info_structured[].action must be a string")
        if not isinstance(item.get("missing_id"), str):
            raise ValueError("state_delta.missing_info_structured[].missing_id must be a string")
        if not isinstance(item.get("question"), str):
            raise ValueError("state_delta.missing_info_structured[].question must be a string")
        related_issues = _require_list_of_strings(item.get("related_issues"), "state_delta.missing_info_structured[].related_issues")
        missing_items.append(
            MissingInfoDelta(
                action=item["action"],
                missing_id=item["missing_id"],
                question=item["question"],
                importance=item.get("importance"),
                reason_type=item.get("reason_type"),
                related_issues=related_issues,
                note=item.get("note"),
            )
        )
    return missing_items


def _normalize_issue_updates(value) -> list[IssueUpdate]:
    updates = []
    for item in _require_list_of_mappings(value, "state_delta.issue_updates_structured"):
        if not isinstance(item.get("issue_id"), str):
            raise ValueError("state_delta.issue_updates_structured[].issue_id must be a string")
        if not isinstance(item.get("label"), str):
            raise ValueError("state_delta.issue_updates_structured[].label must be a string")
        updates.append(IssueUpdate(issue_id=item["issue_id"], label=item["label"]))
    return updates


def _normalize_package_deltas(value) -> list[PackageDelta]:
    packages = []
    for item in _require_list_of_mappings(value, "state_delta.packages_structured"):
        if not isinstance(item.get("package_id"), str):
            raise ValueError("state_delta.packages_structured[].package_id must be a string")
        if not isinstance(item.get("family"), str):
            raise ValueError("state_delta.packages_structured[].family must be a string")
        if not isinstance(item.get("status"), str):
            raise ValueError("state_delta.packages_structured[].status must be a string")
        if not isinstance(item.get("summary"), str):
            raise ValueError("state_delta.packages_structured[].summary must be a string")
        elements = _require_list_of_strings(item.get("elements"), "state_delta.packages_structured[].elements")
        related_issues = _require_list_of_strings(item.get("related_issues"), "state_delta.packages_structured[].related_issues")
        packages.append(
            PackageDelta(
                package_id=item["package_id"],
                family=item["family"],
                status=item["status"],
                summary=item["summary"],
                elements=elements,
                related_issues=related_issues,
            )
        )
    return packages


def normalize_core_output(raw_output: CandidateTurn | dict) -> CandidateTurn:
    if isinstance(raw_output, CandidateTurn):
        validate_candidate_turn(raw_output)
        return raw_output

    payload = _require_mapping(raw_output, "raw_output")
    risk_check_payload = _require_mapping(payload.get("risk_check"), "risk_check")
    state_delta_payload = payload.get("state_delta") or {}
    state_delta_payload = _require_mapping(state_delta_payload, "state_delta")

    if not isinstance(payload.get("turn_index"), int):
        raise ValueError("turn_index must be an integer")
    if not isinstance(payload.get("timestamp"), str):
        raise ValueError("timestamp must be a string")
    if not isinstance(payload.get("role"), str):
        raise ValueError("role must be a string")
    if not isinstance(payload.get("phase"), str):
        raise ValueError("phase must be a string")
    if not isinstance(payload.get("message_summary"), str):
        raise ValueError("message_summary must be a string")
    if not isinstance(risk_check_payload.get("triggered"), bool):
        raise ValueError("risk_check.triggered must be a boolean")
    if not isinstance(risk_check_payload.get("severity"), int):
        raise ValueError("risk_check.severity must be an integer")
    if not isinstance(risk_check_payload.get("notes"), str):
        raise ValueError("risk_check.notes must be a string")

    turn = CandidateTurn(
        turn_index=payload["turn_index"],
        timestamp=payload["timestamp"],
        role=payload["role"],
        phase=payload["phase"],
        message_summary=payload["message_summary"],
        state_delta=StateDelta(
            facts_added=_require_list_of_strings(state_delta_payload.get("facts_added"), "state_delta.facts_added"),
            facts_revised=_require_list_of_strings(state_delta_payload.get("facts_revised"), "state_delta.facts_revised"),
            facts_structured=_normalize_fact_deltas(state_delta_payload.get("facts_structured")),
            positions_added_or_updated=_require_list_of_strings(
                state_delta_payload.get("positions_added_or_updated"),
                "state_delta.positions_added_or_updated",
            ),
            positions_structured=_normalize_position_deltas(state_delta_payload.get("positions_structured")),
            open_questions_added=_require_list_of_strings(
                state_delta_payload.get("open_questions_added"),
                "state_delta.open_questions_added",
            ),
            open_questions_resolved=_require_list_of_strings(
                state_delta_payload.get("open_questions_resolved"),
                "state_delta.open_questions_resolved",
            ),
            missing_info_structured=_normalize_missing_info_deltas(state_delta_payload.get("missing_info_structured")),
            issue_map_updates=_require_list_of_strings(
                state_delta_payload.get("issue_map_updates"),
                "state_delta.issue_map_updates",
            ),
            issue_updates_structured=_normalize_issue_updates(state_delta_payload.get("issue_updates_structured")),
            packages_structured=_normalize_package_deltas(state_delta_payload.get("packages_structured")),
            option_state_updates=_require_list_of_strings(
                state_delta_payload.get("option_state_updates"),
                "state_delta.option_state_updates",
            ),
            escalation_state_updates=_require_list_of_strings(
                state_delta_payload.get("escalation_state_updates"),
                "state_delta.escalation_state_updates",
            ),
        ),
        risk_check=RiskCheck(
            triggered=risk_check_payload["triggered"],
            signals=_require_list_of_strings(risk_check_payload.get("signals"), "risk_check.signals"),
            severity=risk_check_payload["severity"],
            notes=risk_check_payload["notes"],
        ),
        candidate_escalation_category=payload.get("candidate_escalation_category"),
        candidate_escalation_mode=payload.get("candidate_escalation_mode"),
        confidence_note=payload.get("confidence_note"),
        message_text=payload.get("message_text") if isinstance(payload.get("message_text"), str) else None,
        interaction_observations_delta=_require_list_of_strings(
            payload.get("interaction_observations_delta"),
            "interaction_observations_delta",
        ),
        reasoning_trace=payload.get("reasoning_trace") if isinstance(payload.get("reasoning_trace"), dict) else None,
    )
    validate_candidate_turn(turn)
    return turn
