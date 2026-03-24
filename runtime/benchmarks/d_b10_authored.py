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
            "message_summary": "Solomon frames the session around slowing the emotional temperature, clarifying the immediate parenting dispute, and keeping the discussion workable without pretending the strain is not real.",
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
        },
        {
            "turn_index": 2,
            "timestamp": f"{timestamp_prefix}T00:01:20Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": f"{spouse_a} speaks with visible frustration, saying the last-minute schedule changes keep reopening old wounds and make every school-week transition feel unstable.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "position",
                        "issue_id": "parenting_schedule",
                        "statement": "The handoff plan keeps changing at the last minute, and that makes each school-week transition feel chaotic.",
                        "status": "current",
                        "confidence": "high",
                    }
                ],
                "facts_structured": [
                    {
                        "statement": "One parent describes repeated last-minute schedule changes as emotionally exhausting and destabilizing.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule", "communication_protocol"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Strong emotion is present but the process remains workable."},
        },
        {
            "turn_index": 3,
            "timestamp": f"{timestamp_prefix}T00:02:30Z",
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon reflects the emotional strain directly, distinguishes the intensity from any immediate escalation trigger, and narrows the discussion to predictability and enough notice before schedule changes.",
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
        },
        {
            "turn_index": 4,
            "timestamp": f"{timestamp_prefix}T00:03:40Z",
            "role": "client",
            "phase": "interest_exploration",
            "message_summary": f"{spouse_b} responds emotionally too, saying they feel blamed whenever plans change, but they agree the immediate problem is finding a calmer way to give notice before schedule adjustments.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_B"],
                        "kind": "position",
                        "issue_id": "communication_protocol",
                        "statement": "If schedule changes need to happen, they need a calmer notice process so every adjustment does not become another fight.",
                        "status": "current",
                        "confidence": "high",
                    }
                ],
                "facts_structured": [
                    {
                        "statement": "Both parents accept that emotional strain is high, but they still orient toward a workable notice process rather than asking to stop the session.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule", "communication_protocol"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "The exchange remains intense but still workable."},
        },
        {
            "turn_index": 5,
            "timestamp": f"{timestamp_prefix}T00:04:50Z",
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": "Solomon narrows the discussion to a bounded notice-and-confirmation package that reduces emotional reactivity without pretending the underlying strain is already resolved.",
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
        },
        {
            "turn_index": 6,
            "timestamp": f"{timestamp_prefix}T00:06:00Z",
            "role": "client",
            "phase": "option_generation",
            "message_summary": f"{spouse_a} and {spouse_b.lower()} both agree that an advance-notice window and written confirmation rule would be a better immediate next step than continuing to argue the whole emotional history.",
            "state_delta": {},
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "The parties accept a bounded workable package."},
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
            1: "Solomon opens by acknowledging the emotional intensity directly while keeping the conversation bounded around the immediate schedule problem.",
            5: "Solomon narrows the next step to an advance-notice and written-confirmation package instead of escalating just because the exchange is emotionally hot.",
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
            3: "Solomon reflects the emotional strain without treating it as an escalation trigger and narrows the conversation to predictability and notice before schedule changes.",
        },
    )


def build_varied_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_varied_mock_model_raw_turns(case_bundle, timestamp_prefix))
