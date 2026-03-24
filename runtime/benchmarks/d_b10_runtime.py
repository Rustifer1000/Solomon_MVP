from __future__ import annotations

from runtime.benchmarks.base import RuntimeTurnPlanEntry
from runtime.benchmarks.content_helpers import raw_turn_from_reference_builder
from runtime.benchmarks.d_b10_authored import build_reference_raw_turns


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
        "Solomon frames the session around slowing the emotional temperature, clarifying the immediate parenting dispute, "
        "and keeping the discussion workable without pretending the strain is not real."
    )


def _assistant_interest_summary(state: dict) -> str:
    return (
        "Solomon reflects the emotional strain directly, distinguishes the intensity from any immediate escalation trigger, "
        "and narrows the discussion to predictability and enough notice before schedule changes."
    )


def _assistant_package_summary(plugin_assessment: dict | None) -> str:
    package_summary = (plugin_assessment or {}).get(
        "package_summary",
        "an advance-notice window and written confirmation process",
    )
    return (
        "Solomon narrows the discussion to a bounded notice package built from "
        f"{package_summary}, reducing reactivity without overstating that the underlying emotional strain is resolved."
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
                    {"issue_id": "parenting_schedule", "label": "Parenting schedule"},
                    {"issue_id": "communication_protocol", "label": "Communication protocol around future changes"},
                ],
                "facts_structured": [
                    {
                        "statement": "The dispute is emotionally charged, but both parents are still participating and asking for a workable next step.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule", "communication_protocol"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Opening structure is routine despite elevated emotion."},
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
                        "statement": "Both parents need the schedule conversation to feel more predictable so emotional strain does not keep driving the next exchange.",
                        "category": "family_structure",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule", "communication_protocol"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Emotional heat is acknowledged without becoming an escalation trigger."},
        }
    if turn_index == 5:
        return {
            "turn_index": 5,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": _assistant_package_summary(plugin_assessment),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "A bounded notice and written confirmation process can help keep future schedule changes from reopening the same conflict immediately.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule", "communication_protocol"],
                    }
                ],
                "option_state_updates": [
                    "Added advance_notice_window_option",
                    "Added written_confirmation_option",
                    "Marked written_notice_package_as_workable"
                ],
                "packages_structured": [
                    {
                        "package_id": "pkg-d-b10-001",
                        "family": "written_notice_package",
                        "status": "workable",
                        "summary": "an advance-notice window and written confirmation process",
                        "elements": [
                            "advance_notice_window_option",
                            "written_confirmation_option"
                        ],
                        "related_issues": ["parenting_schedule", "communication_protocol"]
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Option work remains bounded and emotionally workable."},
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
