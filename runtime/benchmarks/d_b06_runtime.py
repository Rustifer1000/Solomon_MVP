from __future__ import annotations

from runtime.benchmarks.base import RuntimeTurnPlanEntry
from runtime.benchmarks.content_helpers import raw_turn_from_reference_builder
from runtime.benchmarks.d_b06_authored import build_reference_raw_turns


def build_runtime_turn_plan(timestamp_prefix: str) -> list[RuntimeTurnPlanEntry]:
    return [
        RuntimeTurnPlanEntry(turn_index=1, role="assistant", timestamp=f"{timestamp_prefix}T00:00:10Z"),
        RuntimeTurnPlanEntry(turn_index=2, role="client", timestamp=f"{timestamp_prefix}T00:01:15Z"),
        RuntimeTurnPlanEntry(turn_index=3, role="assistant", timestamp=f"{timestamp_prefix}T00:02:25Z"),
        RuntimeTurnPlanEntry(turn_index=4, role="client", timestamp=f"{timestamp_prefix}T00:03:35Z"),
        RuntimeTurnPlanEntry(turn_index=5, role="assistant", timestamp=f"{timestamp_prefix}T00:04:45Z"),
        RuntimeTurnPlanEntry(turn_index=6, role="client", timestamp=f"{timestamp_prefix}T00:05:55Z"),
    ]


def _assistant_intro(state: dict) -> str:
    spouse_a = state["case_personas"]["spouse_A"]["role_label"]
    spouse_b = state["case_personas"]["spouse_B"]["role_label"]
    return (
        f"Solomon frames the discussion around extracurricular decisions, enough notice for both {spouse_a.lower()} "
        f"and {spouse_b.lower()} to weigh logistics, and a fair written process for confirming child-activity commitments."
    )


def _assistant_interest_summary(state: dict) -> str:
    participant_statements = []
    for participant in state["positions"].values():
        if participant["current_positions"]:
            participant_statements.append(participant["current_positions"][0]["statement"].lower())
    if any("sidelined" in statement for statement in participant_statements):
        return (
            "Solomon reflects the overlap between predictability, respect, and making sure extracurricular decisions "
            "do not leave either parent feeling sidelined after the fact."
        )
    return (
        "Solomon reflects the overlap between predictability, respect, and preserving meaningful co-parent participation "
        "in child-related decisions."
    )


def _assistant_package_summary(plugin_assessment: dict | None) -> str:
    package_summary = (plugin_assessment or {}).get(
        "package_summary",
        "minimum notice, written summaries, and a pause-before-commitment rule",
    )
    return (
        "Solomon narrows the discussion to a bounded communication package built from "
        f"{package_summary}, while keeping the process mutual rather than one-sided."
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
                        "statement": "The disagreement centers on how extracurricular decisions should be communicated and confirmed.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Opening structure remained routine."},
        }
    if turn_index == 3:
        return {
            "turn_index": turn_index,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": _assistant_interest_summary(state),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Both parents want child-related activity decisions to feel respectful and predictable.",
                        "category": "family_structure",
                        "status": "accepted",
                        "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Interest clarification remained constructive."},
        }
    if turn_index == 5:
        return {
            "turn_index": turn_index,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": _assistant_package_summary(plugin_assessment),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Both parents accept written summaries as a useful way to reduce repeat misunderstandings about child activities.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol"],
                    }
                ],
                "option_state_updates": [
                    "Added minimum_notice_option",
                    "Added written_summary_option",
                    "Added pause_before_commitment_option",
                    "Marked communication_package_as_workable",
                ],
                "packages_structured": [
                    {
                        "package_id": "pkg-d-b06-001",
                        "family": "communication_package",
                        "status": "workable",
                        "summary": "minimum notice, written summaries, and a pause-before-commitment rule",
                        "elements": [
                            "minimum_notice_option",
                            "written_summary_option",
                            "pause_before_commitment_option",
                        ],
                        "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Option work remained bounded and non-directive."},
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
