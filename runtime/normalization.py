from __future__ import annotations

from runtime.contracts import CandidateTurn, RiskCheck, StateDelta, validate_candidate_turn


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
            positions_added_or_updated=_require_list_of_strings(
                state_delta_payload.get("positions_added_or_updated"),
                "state_delta.positions_added_or_updated",
            ),
            open_questions_added=_require_list_of_strings(
                state_delta_payload.get("open_questions_added"),
                "state_delta.open_questions_added",
            ),
            open_questions_resolved=_require_list_of_strings(
                state_delta_payload.get("open_questions_resolved"),
                "state_delta.open_questions_resolved",
            ),
            issue_map_updates=_require_list_of_strings(
                state_delta_payload.get("issue_map_updates"),
                "state_delta.issue_map_updates",
            ),
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
    )
    validate_candidate_turn(turn)
    return turn
