from __future__ import annotations

from runtime.benchmarks.base import RuntimeTurnPlanEntry
from runtime.benchmarks.content_helpers import raw_turn_from_reference_builder
from runtime.benchmarks.d_b08_authored import build_reference_raw_turns


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
    spouse_a = state["case_personas"]["spouse_A"]["role_label"]
    spouse_b = state["case_personas"]["spouse_B"]["role_label"]
    return (
        f"Solomon frames the session around keeping participation workable, making sure both {spouse_a.lower()} and "
        f"{spouse_b.lower()} can speak without being overridden, and clarifying the disagreement before any option work begins."
    )


def _assistant_repair_summary(state: dict) -> str:
    open_positions = []
    for participant in state["positions"].values():
        if participant["current_positions"]:
            open_positions.append(participant["current_positions"][0]["statement"].lower())
    if any("balanced" in statement or "workable" in statement for statement in open_positions):
        return (
            "Solomon slows the exchange, reflects the need for both clarity and equal airtime, and attempts a bounded repair "
            "before any further substantive option work."
        )
    return (
        "Solomon pauses the exchange, reflects the participation imbalance directly, and attempts to restore a workable process "
        "before continuing."
    )


def _assistant_escalation_summary(plugin_assessment: dict | None) -> str:
    warnings = (plugin_assessment or {}).get("warnings", [])
    if warnings:
        return (
            "Solomon concludes that a human mediator should join for co-handling because the repeated participation imbalance "
            f"has not been restored reliably enough to continue autonomously: {warnings[0]}"
        )
    return (
        "Solomon concludes that a human mediator should join for co-handling because the repeated participation imbalance "
        "has not been restored reliably enough to continue autonomously."
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
                    {"issue_id": "communication_protocol", "label": "Communication protocol around future changes"},
                    {"issue_id": "fairness_and_parent_role", "label": "Fairness and meaningful parenting role"},
                ],
                "facts_structured": [
                    {
                        "statement": "The disagreement is being shaped by whether both parents can participate in a balanced way, not only by the underlying substantive issue.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Opening structure is routine."},
        }
    if turn_index == 3:
        return {
            "turn_index": turn_index,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": _assistant_repair_summary(state),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "A workable process requires both parents to have reliable space to speak before substantive option work continues.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Repair attempt remains bounded."},
        }
    if turn_index == 5:
        return {
            "turn_index": turn_index,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": _assistant_escalation_summary(plugin_assessment),
            "state_delta": {
                "escalation_state_updates": [
                    "Escalation selected because repeated interruption and participation imbalance remained active after a repair attempt."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["fairness_breakdown", "repeated_process_breakdown"],
                "severity": 3,
                "notes": "Repeated process breakdown remains active after repair.",
            },
            "candidate_escalation_category": "E2",
            "candidate_escalation_mode": "M3",
            "confidence_note": "Co-handling is preferable to continued autonomous option work because the participation imbalance is still active.",
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
