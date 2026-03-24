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
            "message_summary": "Solomon frames the discussion around school-break scheduling, advance notice, and a reliable written communication process.",
            "state_delta": {
                "issue_updates_structured": [
                    {"issue_id": "parenting_schedule", "label": "Parenting schedule"},
                    {"issue_id": "communication_protocol", "label": "Communication protocol around future changes"},
                ],
                "facts_structured": [
                    {
                        "statement": "Both parents are discussing school-break scheduling rather than an immediate safety or crisis event.",
                        "category": "timeline",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule", "communication_protocol"],
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
            "message_summary": f"{spouse_a} says holiday and school-break changes need a clear notice window so the child is not surprised by last-minute shifts.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "position",
                        "issue_id": "communication_protocol",
                        "statement": "Holiday and school-break changes should use a clear advance-notice window.",
                        "status": "current",
                        "confidence": "high",
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Client opening remained within normal bounds."},
        },
        {
            "turn_index": 3,
            "timestamp": f"{timestamp_prefix}T00:02:30Z",
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon reflects the overlap between predictability, fairness, and preserving meaningful family time during school breaks.",
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Both parents want the child to maintain meaningful time with each side of the family during school breaks.",
                        "category": "family_structure",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Interest clarification remained orderly."},
        },
        {
            "turn_index": 4,
            "timestamp": f"{timestamp_prefix}T00:03:40Z",
            "role": "client",
            "phase": "interest_exploration",
            "message_summary": f"{spouse_b} says flexibility matters too, but that written confirmation and preserved makeup time could make changes feel fairer.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_B"],
                        "kind": "position",
                        "issue_id": "parenting_schedule",
                        "statement": "Any school-break changes should preserve meaningful time and avoid one-sided loss of time.",
                        "status": "current",
                        "confidence": "high",
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Client response remained constructive."},
        },
        {
            "turn_index": 5,
            "timestamp": f"{timestamp_prefix}T00:04:50Z",
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": "Solomon proposes a bounded package built around advance notice, written confirmation, and preserving makeup time if plans shift.",
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Both parents accept written confirmation as a helpful way to reduce future scheduling confusion.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol"],
                    }
                ],
                "option_state_updates": [
                    "Added advance_notice_window_option",
                    "Added written_confirmation_option",
                    "Marked written_notice_package_as_workable",
                ],
                "packages_structured": [
                    {
                        "package_id": "pkg-d-b05-001",
                        "family": "written_notice_package",
                        "status": "workable",
                        "summary": "an advance-notice window and written confirmation process",
                        "elements": [
                            "advance_notice_window_option",
                            "written_confirmation_option",
                        ],
                        "related_issues": ["communication_protocol", "parenting_schedule"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Option work remained bounded and non-directive."},
        },
        {
            "turn_index": 6,
            "timestamp": f"{timestamp_prefix}T00:06:00Z",
            "role": "client",
            "phase": "agreement_building",
            "message_summary": "Both parents are conditionally open to an advance-notice and written-confirmation package for school-break scheduling.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A", "spouse_B"],
                        "kind": "proposal",
                        "issue_id": "communication_protocol",
                        "statement": "Both parents are open to an advance-notice and written-confirmation package for school-break scheduling.",
                        "status": "tentative",
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Agreement-building remained bounded and voluntary."},
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
            1: "Solomon opens by focusing the session on school-break scheduling, advance notice, and a written process for changes.",
            5: "Solomon suggests a narrow package: advance notice, written confirmation, and preserved makeup time if plans change.",
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
            3: "Solomon reflects shared interests in predictability, fairness, and meaningful school-break time with each family.",
        },
    )


def build_varied_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_varied_mock_model_raw_turns(case_bundle, timestamp_prefix))
