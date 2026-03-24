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
            "message_summary": "Solomon frames the discussion around extracurricular decision-making, notice expectations, and a fair co-parenting communication protocol.",
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
        },
        {
            "turn_index": 2,
            "timestamp": f"{timestamp_prefix}T00:01:15Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": f"{spouse_a} says new extracurricular commitments should not be made without enough notice to discuss logistics and fairness first.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "position",
                        "issue_id": "communication_protocol",
                        "statement": "New extracurricular commitments should not be made without enough notice to discuss them first.",
                        "status": "current",
                        "confidence": "high",
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Client opening remained within normal bounds."},
        },
        {
            "turn_index": 3,
            "timestamp": f"{timestamp_prefix}T00:02:25Z",
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon reflects the overlap between predictability, respect, and preserving meaningful co-parent participation in child-related decisions.",
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
        },
        {
            "turn_index": 4,
            "timestamp": f"{timestamp_prefix}T00:03:35Z",
            "role": "client",
            "phase": "interest_exploration",
            "message_summary": f"{spouse_b} says fairness matters too, because activity decisions should not make one parent feel sidelined after the fact.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_B"],
                        "kind": "position",
                        "issue_id": "fairness_and_parent_role",
                        "statement": "Child-activity decisions should not leave one parent feeling sidelined or treated as an afterthought.",
                        "status": "current",
                        "confidence": "high",
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Client response remained constructive."},
        },
        {
            "turn_index": 5,
            "timestamp": f"{timestamp_prefix}T00:04:45Z",
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": "Solomon proposes a bounded communication package: minimum notice, written summaries of decisions, and a pause-before-commitment rule for new activities.",
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
        },
        {
            "turn_index": 6,
            "timestamp": f"{timestamp_prefix}T00:05:55Z",
            "role": "client",
            "phase": "agreement_building",
            "message_summary": "Both parents are conditionally open to a communication package with minimum notice, written summaries, and a pause-before-commitment rule.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A", "spouse_B"],
                        "kind": "proposal",
                        "issue_id": "communication_protocol",
                        "statement": "Both parents are open to a minimum-notice, written-summary, and pause-before-commitment package for extracurricular decisions.",
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
            1: "Solomon opens by centering the session on extracurricular decisions, advance notice, and a fair communication process.",
            5: "Solomon suggests a narrow communication package built around minimum notice, written summaries, and a pause-before-commitment rule.",
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
            3: "Solomon reflects shared interests in predictability, respect, and not sidelining either parent in child-activity decisions.",
        },
    )


def build_varied_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_varied_mock_model_raw_turns(case_bundle, timestamp_prefix))
