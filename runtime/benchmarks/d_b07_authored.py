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
            "message_summary": "Solomon frames the discussion around child-expense reimbursement, timing for notice, and what documentation should be shared before repayment is expected.",
            "state_delta": {
                "issue_updates_structured": [
                    {"issue_id": "child_expense_coordination", "label": "Child expense coordination and reimbursement"},
                    {"issue_id": "communication_protocol", "label": "Communication protocol around future changes"},
                ],
                "facts_structured": [
                    {
                        "statement": "The disagreement centers on how child-related expenses should be noticed, documented, and reimbursed.",
                        "category": "financial_commitment",
                        "status": "accepted",
                        "related_issues": ["child_expense_coordination", "communication_protocol"],
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
            "message_summary": f"{spouse_a} says reimbursement requests should not appear weeks later without receipts or warning.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "position",
                        "issue_id": "child_expense_coordination",
                        "statement": "Reimbursement requests should not arrive weeks later without advance notice and supporting receipts.",
                        "status": "current",
                        "confidence": "high",
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Client opening remained within normal bounds."},
        },
        {
            "turn_index": 3,
            "timestamp": f"{timestamp_prefix}T00:02:20Z",
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon reflects the overlap between predictability, fairness, and avoiding repeated resentment about surprise expenses.",
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Both parents want child-related expenses to feel predictable and fair rather than surprising or one-sided.",
                        "category": "family_structure",
                        "status": "accepted",
                        "related_issues": ["child_expense_coordination", "communication_protocol"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Interest clarification remained constructive."},
        },
        {
            "turn_index": 4,
            "timestamp": f"{timestamp_prefix}T00:03:30Z",
            "role": "client",
            "phase": "interest_exploration",
            "message_summary": f"{spouse_b} says repayment should still stay workable and not depend on one parent having total control over what counts as an approved expense.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_B"],
                        "kind": "position",
                        "issue_id": "communication_protocol",
                        "statement": "Expense coordination should stay fair and workable rather than turning into one-sided approval power.",
                        "status": "current",
                        "confidence": "high",
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Client response remained constructive."},
        },
        {
            "turn_index": 5,
            "timestamp": f"{timestamp_prefix}T00:04:40Z",
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": "Solomon proposes a bounded reimbursement package: minimum notice for non-routine expenses, shared receipts within a set window, and a short response period before repayment is due.",
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Both parents treat shared receipts and clear response windows as workable ways to reduce repeat reimbursement conflict.",
                        "category": "communication_history",
                        "status": "accepted",
                        "related_issues": ["child_expense_coordination", "communication_protocol"],
                    }
                ],
                "option_state_updates": [
                    "Added expense_notice_window_option",
                    "Added shared_receipt_option",
                    "Added reimbursement_response_window_option",
                    "Marked reimbursement_package_as_workable",
                ],
                "packages_structured": [
                    {
                        "package_id": "pkg-d-b07-001",
                        "family": "reimbursement_package",
                        "status": "workable",
                        "summary": "advance notice, shared receipts, and a reimbursement response window",
                        "elements": [
                            "expense_notice_window_option",
                            "shared_receipt_option",
                            "reimbursement_response_window_option",
                        ],
                        "related_issues": ["child_expense_coordination", "communication_protocol"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Option work remained bounded and non-directive."},
        },
        {
            "turn_index": 6,
            "timestamp": f"{timestamp_prefix}T00:05:50Z",
            "role": "client",
            "phase": "agreement_building",
            "message_summary": "Both parents are conditionally open to a reimbursement package with notice windows, shared receipts, and a short response period before repayment is due.",
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A", "spouse_B"],
                        "kind": "proposal",
                        "issue_id": "child_expense_coordination",
                        "statement": "Both parents are open to a child-expense package built around advance notice, shared receipts, and a short reimbursement response window.",
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
            1: "Solomon opens by centering the session on child-expense notice, documentation, and how reimbursement expectations should be communicated.",
            5: "Solomon suggests a narrow reimbursement package built around notice windows, shared receipts, and a short response period.",
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
            3: "Solomon reflects shared interests in predictability, fairness, and reducing repeat friction about child-related expenses.",
        },
    )


def build_varied_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_varied_mock_model_raw_turns(case_bundle, timestamp_prefix))
