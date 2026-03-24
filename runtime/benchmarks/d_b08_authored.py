from __future__ import annotations

from runtime.benchmarks.authored_helpers import build_message_variant_raw_turns, normalize_raw_turns


def build_reference_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    spouse_a = case_bundle["personas"]["spouse_A"]["role_label"]
    spouse_b = case_bundle["personas"]["spouse_B"]["role_label"]
    return [
        {
            "turn_index": 1,
            "timestamp": f"{timestamp_prefix}T00:00:10Z",
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": "Solomon frames the session around keeping participation workable, hearing each parent clearly, and clarifying the disagreement before pushing toward options.",
            "state_delta": {
                "issue_updates_structured": [
                    {"issue_id": "communication_protocol", "label": "Communication protocol around future changes"},
                    {"issue_id": "fairness_and_parent_role", "label": "Fairness and meaningful parenting role"},
                ],
                "facts_structured": [
                    {
                        "statement": "The disagreement is currently being shaped by how each parent is able to participate in the conversation, not only by the underlying parenting issue itself.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Opening structure is routine."},
        },
        {
            "turn_index": 2,
            "timestamp": f"{timestamp_prefix}T00:01:20Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": f"{spouse_a} starts outlining concerns rapidly, interrupting to correct {spouse_b.lower()} before they can finish and insisting the real problem is that decisions keep getting derailed by confusion.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "position",
                        "issue_id": "communication_protocol",
                        "statement": "The discussion needs to stay focused and stop circling because the same concerns keep getting repeated.",
                        "status": "current",
                        "confidence": "high",
                    }
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["fairness_breakdown"],
                "severity": 2,
                "notes": "Early participation imbalance is visible.",
            },
        },
        {
            "turn_index": 3,
            "timestamp": f"{timestamp_prefix}T00:02:30Z",
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon slows the exchange, reflects the need for both clarity and equal space to speak, and tries to re-establish a mutual process before option work begins.",
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Both parents need the process to feel workable before substantive decision-making can continue productively.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Repair attempt is appropriate but still early."},
        },
        {
            "turn_index": 4,
            "timestamp": f"{timestamp_prefix}T00:03:40Z",
            "role": "client",
            "phase": "interest_exploration",
            "message_summary": f"{spouse_b} says they keep getting cut off, no longer believe the discussion is balanced, and are starting to doubt whether continuing without a human mediator is workable.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_B"],
                        "kind": "position",
                        "issue_id": "fairness_and_parent_role",
                        "statement": "The process no longer feels balanced enough to keep going productively without stronger intervention.",
                        "status": "current",
                        "confidence": "high",
                    }
                ],
                "facts_structured": [
                    {
                        "statement": "One parent explicitly reports feeling cut off and doubts that the current process is staying balanced.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                        "note": "This is preserved as a process-relevant report, not an adjudicated conclusion about intent.",
                    }
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["fairness_breakdown", "repeated_process_breakdown", "explicit_human_request"],
                "severity": 3,
                "notes": "Repair effort did not restore workable participation.",
            },
        },
        {
            "turn_index": 5,
            "timestamp": f"{timestamp_prefix}T00:04:50Z",
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": "Solomon concludes that equal participation has not been restored reliably enough for continued autonomous handling and recommends bringing in a human mediator for co-handling rather than forcing further option work.",
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
        },
        {
            "turn_index": 6,
            "timestamp": f"{timestamp_prefix}T00:06:00Z",
            "role": "client",
            "phase": "option_generation",
            "message_summary": f"{spouse_b} agrees a human mediator should join before the discussion continues, and {spouse_a.lower()} says they are frustrated but willing to continue with clearer live process control.",
            "state_delta": {},
            "risk_check": {
                "triggered": True,
                "signals": ["explicit_human_request"],
                "severity": 2,
                "notes": "The parties are now oriented toward human co-handling.",
            },
        },
    ]


def build_reference_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_reference_raw_turns(case_bundle, timestamp_prefix))


def build_mock_model_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    return build_message_variant_raw_turns(
        build_reference_raw_turns,
        case_bundle,
        timestamp_prefix,
        {
            1: "Solomon opens by focusing on workable participation, clear airtime, and clarifying the disagreement before any solution pressure appears.",
            5: "Solomon concludes the repeated interruption pattern now calls for human co-handling rather than more autonomous option work.",
        },
    )


def build_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_mock_model_raw_turns(case_bundle, timestamp_prefix))


def build_varied_mock_model_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    return build_message_variant_raw_turns(
        build_mock_model_raw_turns,
        case_bundle,
        timestamp_prefix,
        {
            3: "Solomon pauses the exchange, reflects the need for equal participation and clarity, and attempts a bounded repair before any option work continues.",
        },
    )


def build_varied_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_varied_mock_model_raw_turns(case_bundle, timestamp_prefix))
