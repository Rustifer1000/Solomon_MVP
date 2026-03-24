from __future__ import annotations

from runtime.benchmarks.base import RuntimeTurnPlanEntry
from runtime.benchmarks.content_helpers import raw_turn_from_reference_builder
from runtime.benchmarks.d_b11_authored import build_reference_raw_turns


def build_runtime_turn_plan(timestamp_prefix: str) -> list[RuntimeTurnPlanEntry]:
    return [
        RuntimeTurnPlanEntry(turn_index=1, role="assistant", timestamp=f"{timestamp_prefix}T00:00:10Z"),
        RuntimeTurnPlanEntry(turn_index=2, role="client", timestamp=f"{timestamp_prefix}T00:01:20Z"),
        RuntimeTurnPlanEntry(turn_index=3, role="assistant", timestamp=f"{timestamp_prefix}T00:02:30Z"),
        RuntimeTurnPlanEntry(turn_index=4, role="client", timestamp=f"{timestamp_prefix}T00:03:40Z"),
        RuntimeTurnPlanEntry(turn_index=5, role="assistant", timestamp=f"{timestamp_prefix}T00:04:50Z"),
        RuntimeTurnPlanEntry(turn_index=6, role="client", timestamp=f"{timestamp_prefix}T00:06:00Z"),
    ]


def _assistant_intro(state: dict) -> str:
    return (
        "Solomon frames the session around protecting fair participation, clarifying the expense picture carefully, "
        "and avoiding pressure on either parent to agree before they understand the obligations clearly."
    )


def _assistant_interest_summary(state: dict) -> str:
    return (
        "Solomon reflects the confidence asymmetry directly, protects against blind agreement, and narrows the conversation "
        "toward what information and documentation would be needed for a fair next step."
    )


def _assistant_caution_summary(plugin_assessment: dict | None) -> str:
    warnings = (plugin_assessment or {}).get("warnings", [])
    if warnings:
        return (
            "Solomon keeps the session in bounded caution, recommending document-sharing and written summaries before stronger "
            f"reimbursement commitments are treated as workable: {warnings[0]}"
        )
    return (
        "Solomon keeps the session in bounded caution, recommending document-sharing and written summaries before stronger "
        "reimbursement commitments are treated as workable."
    )


def generate_runtime_assistant_turn(turn_index: int, timestamp: str, state: dict, plugin_assessment: dict | None = None) -> dict:
    if turn_index == 1:
        return {
            "turn_index": 1,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": _assistant_intro(state),
            "state_delta": {
                "issue_updates_structured": [
                    {"issue_id": "child_expense_coordination", "label": "Child expense coordination and reimbursement"},
                    {"issue_id": "communication_protocol", "label": "Communication protocol around future changes"},
                    {"issue_id": "fairness_and_parent_role", "label": "Fairness and meaningful parenting role"}
                ],
                "facts_structured": [
                    {
                        "statement": "The dispute involves reimbursement expectations, document access, and confidence asymmetry about what the child-related expense picture actually shows.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["child_expense_coordination", "communication_protocol", "fairness_and_parent_role"]
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Opening structure is routine."}
        }
    if turn_index == 3:
        return {
            "turn_index": 3,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": _assistant_interest_summary(state),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "A fair next step requires enough shared documentation that neither parent is pressured into agreeing from an informational disadvantage.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["child_expense_coordination", "fairness_and_parent_role", "communication_protocol"]
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "The process remains workable when the confidence gap is addressed explicitly."}
        }
    if turn_index == 5:
        return {
            "turn_index": 5,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": _assistant_caution_summary(plugin_assessment),
            "state_delta": {
                "option_state_updates": [
                    "Marked fixed_recommendation_out_of_scope_pending_feasibility"
                ],
                "facts_structured": [
                    {
                        "statement": "The responsible next step is shared clarification and written documentation, not a stronger reimbursement recommendation yet.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["child_expense_coordination", "communication_protocol", "fairness_and_parent_role"]
                    }
                ]
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information", "decision_quality_risk", "plugin_low_confidence"],
                "severity": 3,
                "notes": "The confidence asymmetry and missing documentation make stronger autonomous recommendation inappropriate."
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
            "confidence_note": "Bounded caution is preferable because informed participation would otherwise remain too uneven."
        }
    raise ValueError(f"Unsupported assistant turn index: {turn_index}")


def generate_runtime_client_turn(turn_index: int, timestamp: str, state: dict, case_bundle: dict) -> dict:
    return raw_turn_from_reference_builder(
        build_reference_raw_turns,
        case_bundle,
        timestamp[:10],
        turn_index,
        "client",
    )
