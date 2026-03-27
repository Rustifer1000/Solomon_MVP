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
            "message_summary": "Solomon frames its role as a neutral process support, explains that both parents remain decision-makers, and names three areas to work through: logistics scheduling, activity coordination, and holiday sequencing.",
            "state_delta": {
                "issue_updates_structured": [
                    {"issue_id": "parenting_schedule", "label": "Parenting schedule"},
                    {"issue_id": "communication_protocol", "label": "Communication protocol for logistics coordination"},
                    {"issue_id": "activity_coordination", "label": "Activity hand-off and coordination"},
                ],
                "facts_structured": [
                    {
                        "statement": "Both parents are in a cooperative separation and are working toward a logistics coordination framework.",
                        "category": "timeline",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule", "communication_protocol"],
                    }
                ],
                "escalation_state_updates": [
                    "Opened in M0 posture. Cooperative state confirmed. No caution threshold present."
                ],
            },
            "risk_check": {
                "triggered": False,
                "signals": [],
                "severity": 1,
                "notes": "Opening structure is routine. Cooperative context confirmed.",
            },
        },
        {
            "turn_index": 2,
            "timestamp": f"{timestamp_prefix}T00:01:20Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": f"{spouse_a} opens by naming the desire for a clear pickup schedule and notes that vague arrangements are already causing confusion. Sets the frame around predictability and written defaults.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "position",
                        "issue_id": "communication_protocol",
                        "statement": "Pickup and dropoff logistics should use a written schedule with defined windows rather than informal last-minute calls.",
                        "status": "current",
                        "confidence": "high",
                        "position_id": "pos-spouse_a-001",
                    }
                ],
                "facts_structured": [
                    {
                        "statement": "The current absence of a logistics framework is creating friction and confusion for both parents and the child.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol", "parenting_schedule"],
                    }
                ],
            },
            "risk_check": {
                "triggered": False,
                "signals": [],
                "severity": 1,
                "notes": "Client opening remained within cooperative bounds.",
            },
        },
        {
            "turn_index": 3,
            "timestamp": f"{timestamp_prefix}T00:02:30Z",
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon reflects that both parents share an interest in the child's comfort and a workable co-parenting process, and surfaces the underlying tension between clarity and flexibility as a values difference rather than a conflict.",
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Both parents share an interest in the child's comfort and a workable co-parenting logistics process.",
                        "category": "family_structure",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule", "communication_protocol"],
                    },
                    {
                        "statement": "The parents differ in whether written structure or mutual flexibility should be the primary framing.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol"],
                    },
                ],
            },
            "risk_check": {
                "triggered": False,
                "signals": [],
                "severity": 1,
                "notes": "Interest clarification remained orderly and non-adversarial.",
            },
        },
        {
            "turn_index": 4,
            "timestamp": f"{timestamp_prefix}T00:03:40Z",
            "role": "client",
            "phase": "interest_exploration",
            "message_summary": f"{spouse_b} affirms cooperative intent and raises the concern about over-formalization, reframing the ask as wanting defaults rather than hard rules. Both parents identify child comfort as the common anchor.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_B"],
                        "kind": "position",
                        "issue_id": "communication_protocol",
                        "statement": "Logistics should use a default guide rather than a binding protocol so that normal life variation does not create automatic conflict.",
                        "status": "current",
                        "confidence": "high",
                        "position_id": "pos-spouse_b-001",
                    }
                ],
                "facts_structured": [
                    {
                        "statement": "Both parents identify child comfort as the common anchor for any logistics framework.",
                        "category": "family_structure",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule", "activity_coordination"],
                    }
                ],
            },
            "risk_check": {
                "triggered": False,
                "signals": [],
                "severity": 1,
                "notes": "Client response remained constructive. Reframe toward defaults is workable.",
            },
        },
        {
            "turn_index": 5,
            "timestamp": f"{timestamp_prefix}T00:04:50Z",
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": "Solomon proposes a bounded logistics coordination package: a default pickup window guideline, a simple activity hand-off default assignment, and a written-but-flexible holiday sequence. Marks the package as workable given the cooperative state.",
            "state_delta": {
                "packages_structured": [
                    {
                        "package_id": "pkg-d-b01-001",
                        "family": "logistics_coordination_package",
                        "status": "workable",
                        "summary": "a default pickup window guideline, activity hand-off default assignment, and flexible holiday sequence",
                        "elements": [
                            "pickup_window_guideline",
                            "activity_default_assignment",
                            "holiday_sequence_framework",
                        ],
                        "related_issues": ["parenting_schedule", "communication_protocol", "activity_coordination"],
                    }
                ],
                "option_state_updates": [
                    "Added pickup_window_guideline",
                    "Added activity_default_assignment",
                    "Added holiday_sequence_framework",
                    "Marked logistics_coordination_package_as_workable",
                ],
                "facts_structured": [
                    {
                        "statement": "Both parents accept that a default-guide framing can satisfy both the clarity need and the flexibility need.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["communication_protocol"],
                    }
                ],
            },
            "risk_check": {
                "triggered": False,
                "signals": [],
                "severity": 1,
                "notes": "Option work remained bounded and non-directive. Package is correctly party-owned.",
            },
        },
        {
            "turn_index": 6,
            "timestamp": f"{timestamp_prefix}T00:06:00Z",
            "role": "client",
            "phase": "agreement_building",
            "message_summary": "Both parents are conditionally open to the logistics coordination package. Parent A confirms the written-guideline framing satisfies the clarity need. Parent B confirms the default-guide framing preserves the flexibility need.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A", "spouse_B"],
                        "kind": "proposal",
                        "issue_id": "communication_protocol",
                        "statement": "Both parents are conditionally open to a default-guideline logistics coordination package covering pickup windows, activity hand-off, and holiday sequencing.",
                        "status": "tentative",
                        "proposal_id": "prop-shared-001",
                    }
                ],
                "escalation_state_updates": [
                    "Closed the slice in M0. No threshold-relevant concern arose. Package accepted as workable starting basis."
                ],
            },
            "risk_check": {
                "triggered": False,
                "signals": [],
                "severity": 1,
                "notes": "Agreement-building remained bounded and voluntary. M0 maintained throughout.",
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
            1: "Solomon opens by framing the session around logistics coordination, names the three areas to work through, and confirms that both parents remain decision-makers.",
            5: "Solomon suggests a logistics coordination package: a default pickup window, an activity hand-off default, and a flexible holiday sequence.",
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
            3: "Solomon reflects that both parents share an interest in child comfort and a workable co-parenting process, and surfaces the clarity/flexibility tension as a values difference rather than a conflict.",
        },
    )


def build_varied_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_varied_mock_model_raw_turns(case_bundle, timestamp_prefix))
