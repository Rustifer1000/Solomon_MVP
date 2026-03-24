from __future__ import annotations

from runtime.benchmarks.base import RuntimeTurnPlanEntry
from runtime.benchmarks.content_helpers import raw_turn_from_reference_builder
from runtime.benchmarks.d_b12_authored import build_reference_raw_turns


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
        f"Solomon frames the session around slowing the pace, protecting workable participation for both {spouse_a.lower()} "
        f"and {spouse_b.lower()}, and keeping the immediate parenting dispute from turning into another emotionally flooded cycle."
    )


def _assistant_repair_summary(state: dict) -> str:
    return (
        "Solomon attempts a bounded repair by slowing the exchange, naming the emotional flooding directly, and narrowing the "
        "conversation to what would make continued participation stable enough to continue."
    )


def _assistant_escalation_summary(plugin_assessment: dict | None) -> str:
    warnings = (plugin_assessment or {}).get("warnings", [])
    if warnings:
        return (
            "Solomon concludes that repeated repair is no longer stabilizing the process and recommends human co-handling so the "
            f"conversation can continue with emotional containment and dignity preserved: {warnings[0]}"
        )
    return (
        "Solomon concludes that repeated repair is no longer stabilizing the process and recommends human co-handling so the "
        "conversation can continue with emotional containment and dignity preserved."
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
                        "statement": "The disagreement is being shaped by emotionally loaded narrative recurrence that destabilizes the process before the parenting issue can be narrowed productively.",
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
            "turn_index": 3,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": _assistant_repair_summary(state),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "A workable next step requires emotional stabilization and a narrower process before substantive option work can continue reliably.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "A bounded repair attempt is still appropriate."},
        }
    if turn_index == 5:
        return {
            "turn_index": 5,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": _assistant_escalation_summary(plugin_assessment),
            "state_delta": {
                "escalation_state_updates": [
                    "Escalation selected because emotional flooding and repeated failed repair attempts made continued autonomous handling unstable."
                ]
            },
            "risk_check": {
                "triggered": True,
                "signals": ["repeated_process_breakdown", "explicit_human_request"],
                "severity": 3,
                "notes": "Emotional flooding remains active after repair and now warrants co-handling."
            },
            "candidate_escalation_category": "E2",
            "candidate_escalation_mode": "M3",
            "confidence_note": "Co-handling is preferable because the process is no longer stabilizing through bounded autonomous repair alone."
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
