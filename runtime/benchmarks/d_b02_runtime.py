from __future__ import annotations

from runtime.benchmarks.base import RuntimeTurnPlanEntry
from runtime.benchmarks.d_b02_authored import get_varied_mock_process_variant


def build_runtime_turn_plan(timestamp_prefix: str) -> list[RuntimeTurnPlanEntry]:
    return [
        RuntimeTurnPlanEntry(turn_index=1, role="assistant", timestamp=f"{timestamp_prefix}T00:00:10Z"),
        RuntimeTurnPlanEntry(turn_index=2, role="client", timestamp=f"{timestamp_prefix}T00:01:30Z"),
        RuntimeTurnPlanEntry(turn_index=3, role="assistant", timestamp=f"{timestamp_prefix}T00:02:25Z"),
        RuntimeTurnPlanEntry(turn_index=4, role="client", timestamp=f"{timestamp_prefix}T00:03:40Z"),
        RuntimeTurnPlanEntry(turn_index=5, role="assistant", timestamp=f"{timestamp_prefix}T00:04:55Z"),
        RuntimeTurnPlanEntry(turn_index=6, role="client", timestamp=f"{timestamp_prefix}T00:06:10Z"),
        RuntimeTurnPlanEntry(turn_index=7, role="assistant", timestamp=f"{timestamp_prefix}T00:07:35Z"),
        RuntimeTurnPlanEntry(turn_index=8, role="client", timestamp=f"{timestamp_prefix}T00:08:50Z"),
    ]


def _persona(case_bundle: dict, participant_id: str) -> dict:
    return case_bundle["personas"][participant_id]


def _client_summary(turn_index: int, state: dict, case_bundle: dict) -> str:
    spouse_a = _persona(case_bundle, "spouse_A")
    spouse_b = _persona(case_bundle, "spouse_B")
    if turn_index == 2:
        opening = spouse_a["likely_openings"][0]
        concern = spouse_a["private_concerns"][0]
        return (
            f"Spouse A says {opening.lower()} and explains that {concern.lower()}, "
            f"insisting that any split must be based on documented usage rather than recollection."
        )
    if turn_index == 4:
        opening = spouse_b["likely_openings"][0]
        concern = spouse_b["private_concerns"][1]
        return (
            f"Spouse B says {opening.lower()} and notes {concern.lower()}, "
            f"but accepts that a bounded documentation review may help clarify the picture."
        )
    if turn_index == 6:
        return (
            "The parties clarify what records they have: no pulled statements, some housing-cost text messages, "
            "and rough estimate amounts from memory. Neither party has a clear written credit agreement."
        )
    if turn_index == 8:
        return (
            "Both parties accept pulling credit-card statements and any written records as the bounded next step "
            "before any allocation discussion can proceed. No figures are agreed."
        )
    raise ValueError(f"Unsupported client turn index for D-B02: {turn_index}")


def _client_state_delta(turn_index: int) -> dict:
    if turn_index == 2:
        return {
            "facts_added": ["The parties dispute how shared credit-card debt and housing costs should be divided."],
            "facts_structured": [
                {
                    "statement": "The parties dispute how shared credit-card debt and housing costs should be divided.",
                    "category": "financial",
                    "status": "accepted",
                    "related_issues": ["shared_debt_allocation", "housing_cost_division"],
                }
            ],
            "positions_added_or_updated": [
                "spouse_A requires documentation before agreeing to any debt split."
            ],
            "positions_structured": [
                {
                    "participant_ids": ["spouse_A"],
                    "kind": "position",
                    "issue_id": "financial_documentation",
                    "statement": "Any debt split must be based on documented usage rather than unverified recollection.",
                    "status": "current",
                    "confidence": "high",
                    "position_id": "pos-spouse_a-001",
                }
            ],
            "open_questions_added": [
                "Which credit-card accounts and which housing cost period are at issue?"
            ],
            "missing_info_structured": [
                {
                    "action": "open",
                    "missing_id": "missing-001",
                    "question": "What do the actual credit-card statements show regarding shared account usage?",
                    "importance": "high",
                    "reason_type": "feasibility_gap",
                    "related_issues": ["shared_debt_allocation", "financial_documentation"],
                    "note": "No responsible allocation framework can be proposed before statements are reviewed.",
                }
            ],
            "issue_map_updates": ["Expanded financial_documentation as primary procedural constraint."],
            "issue_updates_structured": [
                {"issue_id": "financial_documentation", "label": "Financial documentation and record review"}
            ],
        }
    if turn_index == 4:
        return {
            "facts_added": [
                "Spouse B acknowledges their recollection of the debt arrangement may not be fully accurate."
            ],
            "facts_structured": [
                {
                    "statement": "Spouse B acknowledges their recollection of the debt arrangement may not be fully accurate.",
                    "category": "communication_history",
                    "status": "accepted",
                    "related_issues": ["financial_documentation", "shared_debt_allocation"],
                    "note": "Accepted as a stated acknowledgment, not as a factual determination.",
                }
            ],
            "positions_added_or_updated": [
                "spouse_B prefers practical resolution but accepts documentation review if proportional."
            ],
            "positions_structured": [
                {
                    "participant_ids": ["spouse_B"],
                    "kind": "position",
                    "issue_id": "shared_debt_allocation",
                    "statement": "A practical resolution is preferred. Documentation review is acceptable if it stays bounded and proportional.",
                    "status": "current",
                    "confidence": "moderate",
                    "position_id": "pos-spouse_b-001",
                }
            ],
            "open_questions_added": [
                "What written records, if any, exist of the informal housing cost or debt agreement?"
            ],
            "missing_info_structured": [
                {
                    "action": "open",
                    "missing_id": "missing-002",
                    "question": "Is there any written record (email, text message) of the informal debt or housing cost agreement?",
                    "importance": "medium",
                    "reason_type": "feasibility_gap",
                    "related_issues": ["financial_documentation", "housing_cost_division"],
                    "note": "Even partial written records would help establish a shared factual baseline.",
                }
            ],
            "issue_map_updates": ["Both parties show conditional openness to documentation-first process."],
        }
    if turn_index == 6:
        return {
            "facts_added": [
                "Credit-card statement figures are not yet available.",
                "Some text messages about housing costs exist but do not constitute a clear written agreement.",
                "Both parties acknowledge that exact amounts are estimates.",
            ],
            "facts_structured": [
                {
                    "statement": "Credit-card statement figures are not yet available. Parties are working from memory only.",
                    "category": "financial",
                    "status": "uncertain",
                    "related_issues": ["shared_debt_allocation", "financial_documentation"],
                },
                {
                    "statement": "Some text messages about housing costs exist but do not constitute a clear written agreement.",
                    "category": "financial",
                    "status": "uncertain",
                    "related_issues": ["housing_cost_division", "financial_documentation"],
                },
                {
                    "statement": "Both parties acknowledge that exact amounts are estimates rather than verified figures.",
                    "category": "financial",
                    "status": "accepted",
                    "related_issues": ["shared_debt_allocation", "housing_cost_division"],
                },
            ],
            "positions_added_or_updated": [
                "Both parties signal openness to a documentation-then-package approach."
            ],
            "open_questions_resolved": [
                "What written records, if any, exist of the informal housing cost or debt agreement?"
            ],
            "missing_info_structured": [
                {
                    "action": "open",
                    "missing_id": "missing-003",
                    "question": "What exact amounts does each credit-card statement show for the shared period?",
                    "importance": "high",
                    "reason_type": "feasibility_gap",
                    "related_issues": ["shared_debt_allocation", "financial_documentation"],
                    "note": "Statements not yet pulled. Allocation framework cannot be proposed until this is resolved.",
                }
            ],
            "issue_map_updates": [
                "Financial documentation gap confirmed as unresolved. Allocation framework remains blocked."
            ],
            "issue_updates_structured": [
                {"issue_id": "housing_cost_division", "label": "Housing cost division"},
                {"issue_id": "financial_documentation", "label": "Financial documentation and record review"},
            ],
        }
    if turn_index == 8:
        return {
            "facts_added": ["Both parties accept the documentation-first approach as the bounded next step."],
            "facts_structured": [
                {
                    "statement": "Both parties accept the documentation-first approach as the bounded next step.",
                    "category": "timeline",
                    "status": "accepted",
                    "related_issues": ["financial_documentation", "shared_debt_allocation"],
                }
            ],
            "positions_added_or_updated": [
                "Both parties agree to pull statements and written records before the next session."
            ],
            "positions_structured": [
                {
                    "participant_ids": ["spouse_A", "spouse_B"],
                    "kind": "proposal",
                    "issue_id": "financial_documentation",
                    "statement": "Both parties agree to pull credit-card statements and any written records before the next session.",
                    "status": "tentative",
                    "proposal_id": "prop-shared-001",
                }
            ],
            "open_questions_resolved": [
                "Is there any existing written record of the informal debt agreement?"
            ],
            "missing_info_structured": [
                {
                    "action": "resolve",
                    "missing_id": "missing-001",
                    "question": "What do the actual credit-card statements show regarding shared account usage?",
                    "related_issues": ["shared_debt_allocation", "financial_documentation"],
                }
            ],
            "escalation_state_updates": [
                "Closed the slice in M1. Documentation-first next step accepted. M2 available if documentation review reveals complexity."
            ],
        }
    raise ValueError(f"Unsupported client turn index for D-B02: {turn_index}")


def _client_risk_check(turn_index: int) -> dict:
    if turn_index == 2:
        return {
            "triggered": False,
            "signals": ["insufficient_information"],
            "severity": 2,
            "notes": "Documentation-first demand is reasonable. Financial fact baseline not established.",
        }
    if turn_index == 4:
        return {
            "triggered": False,
            "signals": ["trust_breakdown", "insufficient_information"],
            "severity": 2,
            "notes": "Trust strained by differing recollections. Still mediable.",
        }
    if turn_index == 6:
        return {
            "triggered": True,
            "signals": ["insufficient_information", "domain_complexity_warning", "decision_quality_risk"],
            "severity": 4,
            "notes": "Financial facts still insufficiently established for confident packaging. M2 should be considered if this gap persists.",
        }
    if turn_index == 8:
        return {
            "triggered": True,
            "signals": ["insufficient_information"],
            "severity": 2,
            "notes": "Bounded next step accepted. Financial facts still unresolved but process is progressing appropriately.",
        }
    raise ValueError(f"Unsupported client risk check turn index for D-B02: {turn_index}")


def _assistant_option_summary(plugin_assessment: dict) -> str:
    if plugin_assessment.get("plugin_confidence") == "low":
        return (
            "Solomon proposes only a documentation-first approach as the bounded next step. "
            "It explicitly declines to recommend any allocation figures. "
            "It names a qualified financial neutral as an option if the documentation review reveals complexity beyond what the parties can resolve directly."
        )
    return (
        "Solomon proposes a documentation-first package only and declines to suggest any specific allocation "
        "figures before the financial baseline is established. A neutral referral option is noted if needed."
    )


def generate_runtime_client_turn(turn_index: int, timestamp: str, state: dict, case_bundle: dict) -> dict:
    turn = {
        "turn_index": turn_index,
        "timestamp": timestamp,
        "role": "client",
        "phase": (
            "info_gathering" if turn_index in {2, 6}
            else ("interest_exploration" if turn_index == 4 else "agreement_building")
        ),
        "message_summary": _client_summary(turn_index, state, case_bundle),
        "state_delta": _client_state_delta(turn_index),
        "risk_check": _client_risk_check(turn_index),
    }
    if turn_index in {6, 8}:
        turn["candidate_escalation_category"] = "E5"
        turn["candidate_escalation_mode"] = "M2" if turn_index == 6 else "M1"
    return turn


def generate_runtime_assistant_turn(
    turn_index: int,
    timestamp: str,
    state: dict,
    plugin_assessment: dict | None = None,
) -> dict:
    plugin_assessment = plugin_assessment or {}
    process_variant = state["meta"].get("process_variant") or "documentation_first"

    if turn_index == 1:
        return {
            "turn_index": 1,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": (
                "Solomon frames its role as a neutral process support, explicitly notes it is not a financial "
                "or legal advisor, and opens the issue structure around shared debt, housing costs, and documentation."
            ),
            "state_delta": {
                "open_questions_added": [
                    "What shared credit-card accounts and housing costs are at issue?",
                    "Is there any existing written record of the informal debt agreement?",
                ],
                "issue_updates_structured": [
                    {"issue_id": "shared_debt_allocation", "label": "Shared credit-card debt allocation"},
                    {"issue_id": "housing_cost_division", "label": "Housing cost division"},
                    {"issue_id": "financial_documentation", "label": "Financial documentation and record review"},
                ],
                "issue_map_updates": [
                    "Initialized shared_debt_allocation",
                    "Initialized housing_cost_division",
                    "Initialized financial_documentation",
                ],
                "escalation_state_updates": [
                    "Opened in M1 posture. Financial fact gaps anticipated. Caution available."
                ],
            },
            "risk_check": {
                "triggered": False,
                "signals": [],
                "severity": 1,
                "notes": "Opening structure is routine. Financial domain acknowledged.",
            },
        }

    if turn_index == 3:
        return {
            "turn_index": 3,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": (
                "Solomon distinguishes the documentation dispute from the underlying interest in fair allocation "
                "and surfaces the shared interest in ending joint credit liability."
                if process_variant == "documentation_first"
                else "Solomon reflects the shared interest in a fair outcome and notes that both parties appear "
                "to be operating from different but genuinely held recollections of the arrangement."
            ),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Both parties share an interest in ending joint credit liability.",
                        "category": "financial",
                        "status": "accepted",
                        "related_issues": ["shared_debt_allocation"],
                    }
                ],
                "open_questions_added": [
                    "What would a fair allocation process look like to each party once the facts are clearer?"
                ],
                "open_questions_resolved": [
                    "What shared credit-card accounts and housing costs are at issue?"
                ],
                "issue_updates_structured": [
                    {"issue_id": "shared_debt_allocation", "label": "Shared credit-card debt allocation"}
                ],
                "issue_map_updates": [
                    "Linked shared_debt_allocation to joint_credit_liability_interest."
                ],
                "escalation_state_updates": [
                    "Maintained M1 posture. Interest work preceding any option exploration."
                ],
            },
            "risk_check": {
                "triggered": False,
                "signals": [],
                "severity": 1,
                "notes": "Interest-level framing preserved. No overreach toward premature allocation.",
            },
        }

    if turn_index == 5:
        return {
            "turn_index": 5,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": (
                "Solomon names the shared interests — fair allocation and ending joint credit liability — "
                "and flags that the missing financial facts now constitute a material feasibility gap."
            ),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "The missing financial documentation now constitutes a material feasibility gap for responsible option work.",
                        "category": "financial",
                        "status": "accepted",
                        "related_issues": ["financial_documentation", "shared_debt_allocation"],
                    }
                ],
                "open_questions_resolved": [
                    "What would a fair allocation process look like to each party once the facts are clearer?"
                ],
                "issue_map_updates": [
                    "Financial documentation gap identified as material constraint on option work."
                ],
                "escalation_state_updates": [
                    "E5 category active. Missing financial facts are a material feasibility gap. M1 posture maintained. M2 available if gap persists."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information", "decision_quality_risk"],
                "severity": 3,
                "notes": "Missing financial facts materially constrain responsible option work. E5 category confirmed.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        }

    if turn_index == 7:
        low_conf = plugin_assessment.get("plugin_confidence") == "low"
        signals = ["insufficient_information", "domain_complexity_warning"]
        if low_conf:
            signals.append("decision_quality_risk")
        return {
            "turn_index": 7,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": _assistant_option_summary(plugin_assessment),
            "state_delta": {
                "packages_structured": [
                    {
                        "package_id": "pkg-d-b02-001",
                        "family": "documentation_first_allocation_package",
                        "status": "qualified",
                        "summary": "a documentation review step followed by a structured allocation discussion",
                        "elements": [
                            "documentation_review_step",
                            "structured_allocation_discussion",
                            "neutral_referral_option_if_needed",
                        ],
                        "related_issues": [
                            "shared_debt_allocation",
                            "housing_cost_division",
                            "financial_documentation",
                        ],
                    }
                ],
                "option_state_updates": [
                    "Added documentation_review_step",
                    "Added structured_allocation_discussion",
                    "Added neutral_referral_option_if_needed",
                    "Marked allocation_framework_out_of_scope_pending_documentation",
                ],
                "open_questions_resolved": [
                    "Which credit-card accounts and which housing cost period are at issue?"
                ],
                "escalation_state_updates": [
                    "M1 continue with caution. M2 held available if documentation review reveals complexity."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": signals,
                "severity": 3,
                "notes": "Bounded documentation-first path is the correct option posture. M2 held available.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        }

    raise ValueError(f"Unsupported assistant turn index for D-B02: {turn_index}")
