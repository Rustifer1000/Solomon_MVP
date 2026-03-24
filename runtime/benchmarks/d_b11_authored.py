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
            "message_summary": "Solomon frames the session around protecting fair participation, clarifying the expense picture carefully, and avoiding pressure on either parent to agree before they understand the obligations clearly.",
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
        },
        {
            "turn_index": 2,
            "timestamp": f"{timestamp_prefix}T00:01:20Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": f"{spouse_a} says they do not have the same access to accounts, statements, or reimbursement history that {spouse_b.lower()} has handled for years, and they are afraid of agreeing blindly just to keep the conflict down.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "position",
                        "issue_id": "child_expense_coordination",
                        "statement": "I cannot agree responsibly until I can see the expense picture clearly enough to know what I am being asked to cover.",
                        "status": "current",
                        "confidence": "high"
                    }
                ],
                "facts_structured": [
                    {
                        "statement": "One parent reports significantly lower confidence and lower information access around the shared expense picture.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["child_expense_coordination", "fairness_and_parent_role"]
                    }
                ],
                "missing_info_structured": [
                    {
                        "missing_id": "d-b11-expense-records",
                        "action": "open",
                        "question": "What shared expense records and account summaries are available for review before reimbursement expectations are set?",
                        "related_issues": ["child_expense_coordination", "fairness_and_parent_role"]
                    }
                ]
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information"],
                "severity": 2,
                "notes": "Information asymmetry is already limiting informed participation."
            }
        },
        {
            "turn_index": 3,
            "timestamp": f"{timestamp_prefix}T00:02:30Z",
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon reflects the confidence asymmetry directly, protects against blind agreement, and narrows the conversation toward what information and documentation would be needed for a fair next step.",
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
        },
        {
            "turn_index": 4,
            "timestamp": f"{timestamp_prefix}T00:03:40Z",
            "role": "client",
            "phase": "interest_exploration",
            "message_summary": f"{spouse_b} says they are not trying to hide anything, but they acknowledge they have handled most of the paperwork and can see why asking for reimbursement decisions now would feel one-sided without clearer shared records.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_B"],
                        "kind": "position",
                        "issue_id": "communication_protocol",
                        "statement": "We need a calmer way to share records and summarize expenses before either of us treats reimbursement expectations as settled.",
                        "status": "current",
                        "confidence": "high"
                    }
                ],
                "facts_structured": [
                    {
                        "statement": "The more informed parent acknowledges that the current reimbursement discussion could feel one-sided without shared documentation.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["child_expense_coordination", "communication_protocol", "fairness_and_parent_role"]
                    }
                ],
                "missing_info_structured": [
                    {
                        "missing_id": "d-b11-document-sharing-protocol",
                        "action": "open",
                        "question": "What document-sharing and written summary process would let both parents review the expense picture before reimbursement expectations are finalized?",
                        "related_issues": ["child_expense_coordination", "communication_protocol", "fairness_and_parent_role"]
                    }
                ]
            },
            "risk_check": {
                "triggered": True,
                "signals": ["decision_quality_risk"],
                "severity": 2,
                "notes": "The session would risk a one-sided commitment if it pushed toward reimbursement conclusions now."
            }
        },
        {
            "turn_index": 5,
            "timestamp": f"{timestamp_prefix}T00:04:50Z",
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": "Solomon keeps the session in bounded caution, recommending document-sharing and written summaries before stronger reimbursement commitments are treated as workable.",
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
        },
        {
            "turn_index": 6,
            "timestamp": f"{timestamp_prefix}T00:06:00Z",
            "role": "client",
            "phase": "option_generation",
            "message_summary": f"{spouse_a} and {spouse_b.lower()} both accept that the next step should be shared document review and written expense summaries before any stronger reimbursement decision is attempted.",
            "state_delta": {},
            "risk_check": {
                "triggered": False,
                "signals": [],
                "severity": 1,
                "notes": "The session remains workable once the next step is narrowed appropriately."
            }
        }
    ]


def build_reference_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_reference_raw_turns(case_bundle, timestamp_prefix))


def build_mock_model_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    return build_message_variant_raw_turns(
        build_reference_raw_turns,
        case_bundle,
        timestamp_prefix,
        {
            1: "Solomon opens by protecting fair participation and making clear that no one should agree from an informational disadvantage.",
            5: "Solomon keeps the run in bounded caution, narrowing the next step to shared records and written summaries before stronger reimbursement commitments are discussed.",
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
            3: "Solomon reflects the confidence asymmetry directly and narrows the discussion toward what shared documentation would protect against blind agreement.",
        },
    )


def build_varied_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_varied_mock_model_raw_turns(case_bundle, timestamp_prefix))
