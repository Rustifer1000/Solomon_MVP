from __future__ import annotations

import hashlib

from runtime.benchmarks.authored_helpers import normalize_raw_turns


def _structured_state_delta_for_turn(turn_index: int) -> dict:
    if turn_index == 1:
        return {
            "issue_updates_structured": [
                {"issue_id": "shared_debt_allocation", "label": "Shared credit-card debt allocation"},
                {"issue_id": "housing_cost_division", "label": "Housing cost division"},
                {"issue_id": "financial_documentation", "label": "Financial documentation and record review"},
            ],
            "escalation_state_updates": [
                "Opened in M1 posture. Financial fact gaps anticipated. Caution available."
            ],
        }
    if turn_index == 2:
        return {
            "facts_structured": [
                {
                    "statement": "The parties dispute how shared credit-card debt and housing costs should be divided.",
                    "category": "financial",
                    "status": "accepted",
                    "related_issues": ["shared_debt_allocation", "housing_cost_division"],
                }
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
            "issue_updates_structured": [
                {"issue_id": "financial_documentation", "label": "Financial documentation and record review"}
            ],
        }
    if turn_index == 3:
        return {
            "facts_structured": [
                {
                    "statement": "Both parties share an interest in ending joint credit liability.",
                    "category": "financial",
                    "status": "accepted",
                    "related_issues": ["shared_debt_allocation"],
                }
            ],
            "issue_updates_structured": [
                {"issue_id": "shared_debt_allocation", "label": "Shared credit-card debt allocation"}
            ],
        }
    if turn_index == 4:
        return {
            "facts_structured": [
                {
                    "statement": "Spouse B acknowledges their recollection of the debt arrangement may not be fully accurate.",
                    "category": "communication_history",
                    "status": "accepted",
                    "related_issues": ["financial_documentation", "shared_debt_allocation"],
                    "note": "Accepted as a stated acknowledgment, not as a factual determination.",
                }
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
        }
    if turn_index == 5:
        return {
            "facts_structured": [
                {
                    "statement": "The missing financial documentation now constitutes a material feasibility gap for responsible option work.",
                    "category": "financial",
                    "status": "accepted",
                    "related_issues": ["financial_documentation", "shared_debt_allocation"],
                }
            ],
            "escalation_state_updates": [
                "Financial fact gaps identified as material. E5 category active. M1 posture maintained. M2 available if gap persists."
            ],
        }
    if turn_index == 6:
        return {
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
            "issue_updates_structured": [
                {"issue_id": "housing_cost_division", "label": "Housing cost division"},
                {"issue_id": "financial_documentation", "label": "Financial documentation and record review"},
            ],
            "escalation_state_updates": [
                "Severity-4 risk check reached. Financial facts still insufficiently established. M2 candidate surfaced."
            ],
        }
    if turn_index == 7:
        return {
            "packages_structured": [
                {
                    "package_id": "pkg-d-b02-001",
                    "family": "documentation_first_allocation_package",
                    "status": "qualified",
                    "summary": "a documentation review step followed by a structured allocation discussion, with neutral referral available if complexity warrants",
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
            "escalation_state_updates": [
                "M1 continue with caution. M2 held available if documentation review reveals complexity beyond parties' capacity to resolve."
            ],
        }
    if turn_index == 8:
        return {
            "facts_structured": [
                {
                    "statement": "Both parties accept the documentation-first approach as the bounded next step.",
                    "category": "timeline",
                    "status": "accepted",
                    "related_issues": ["financial_documentation", "shared_debt_allocation"],
                }
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
            "missing_info_structured": [
                {
                    "action": "resolve",
                    "missing_id": "missing-001",
                    "question": "What do the actual credit-card statements show regarding shared account usage?",
                    "related_issues": ["shared_debt_allocation", "financial_documentation"],
                }
            ],
            "escalation_state_updates": [
                "Closed the slice in M1. Documentation-first next step accepted. M2 remains available if documentation review reveals complexity."
            ],
        }
    return {}


def _enrich_authored_turns(raw_turns: list[dict]) -> list[dict]:
    for raw_turn in raw_turns:
        structured = _structured_state_delta_for_turn(raw_turn["turn_index"])
        if structured:
            raw_turn["state_delta"].update(structured)
    return raw_turns


def get_varied_mock_process_variant(timestamp_prefix: str) -> str:
    digest = hashlib.sha256(timestamp_prefix.encode("utf-8")).hexdigest()
    return "mutual_recollection" if int(digest[:8], 16) % 2 == 0 else "documentation_first"


def build_reference_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    case_id = case_bundle["case_metadata"]["case_id"]
    if case_id != "D-B02":
        raise NotImplementedError(f"Reference scaffold only supports D-B02, not {case_id}.")

    spouse_a = case_bundle["personas"]["spouse_A"]["role_label"]
    spouse_b = case_bundle["personas"]["spouse_B"]["role_label"]
    timestamps = [
        f"{timestamp_prefix}T00:00:10Z",
        f"{timestamp_prefix}T00:01:30Z",
        f"{timestamp_prefix}T00:02:25Z",
        f"{timestamp_prefix}T00:03:40Z",
        f"{timestamp_prefix}T00:04:55Z",
        f"{timestamp_prefix}T00:06:10Z",
        f"{timestamp_prefix}T00:07:35Z",
        f"{timestamp_prefix}T00:08:50Z",
    ]
    raw_turns = [
        {
            "turn_index": 1,
            "timestamp": timestamps[0],
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": "Solomon frames its role as a neutral process support, explicitly notes it is not a financial or legal advisor, and states that both parties remain decision-makers. It opens the issue structure around shared debt, housing costs, and financial documentation.",
            "state_delta": {
                "open_questions_added": [
                    "What shared credit-card accounts and housing costs are at issue?",
                    "Is there any existing written record of the informal debt agreement?",
                ],
                "issue_map_updates": [
                    "Initialized shared_debt_allocation",
                    "Initialized housing_cost_division",
                    "Initialized financial_documentation",
                ],
            },
            "risk_check": {
                "triggered": False,
                "signals": [],
                "severity": 1,
                "notes": "Opening structure is routine. Financial domain acknowledged.",
            },
        },
        {
            "turn_index": 2,
            "timestamp": timestamps[1],
            "role": "client",
            "phase": "info_gathering",
            "message_summary": f"{spouse_a} opens by saying the core problem is that neither party has a shared picture of what was actually spent. States that any split must be based on documented usage rather than memory.",
            "state_delta": {
                "facts_added": [
                    "The parties dispute how shared credit-card debt and housing costs should be divided.",
                ],
                "positions_added_or_updated": [
                    f"{spouse_a} requires documentation before agreeing to any debt split."
                ],
                "open_questions_added": [
                    "Which credit-card accounts and which housing cost period are at issue?"
                ],
                "issue_map_updates": ["Expanded financial_documentation as primary procedural constraint."],
            },
            "risk_check": {
                "triggered": False,
                "signals": ["insufficient_information"],
                "severity": 2,
                "notes": "Documentation-first demand is reasonable. Financial fact baseline not yet established.",
            },
        },
        {
            "turn_index": 3,
            "timestamp": timestamps[2],
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon distinguishes the documentation dispute from the underlying interest in fair allocation, and surfaces the shared interest in ending joint credit liability. Notes that the misunderstanding may be genuine rather than strategic.",
            "state_delta": {
                "open_questions_added": [
                    "What would a fair allocation process look like to each party once the facts are clearer?"
                ],
                "open_questions_resolved": [
                    "What shared credit-card accounts and housing costs are at issue?"
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
        },
        {
            "turn_index": 4,
            "timestamp": timestamps[3],
            "role": "client",
            "phase": "interest_exploration",
            "message_summary": f"{spouse_b} acknowledges their recollection may not be perfect but maintains there was a mutual understanding. Shows openness to a bounded documentation review if it stays practical.",
            "state_delta": {
                "facts_added": [
                    "Spouse B acknowledges their recollection of the debt arrangement may not be fully accurate."
                ],
                "positions_added_or_updated": [
                    f"{spouse_b} prefers practical resolution but accepts documentation review if proportional."
                ],
                "open_questions_added": [
                    "What written records, if any, exist of the informal housing cost or debt agreement?"
                ],
                "issue_map_updates": ["Both parties show conditional openness to documentation-first process."],
            },
            "risk_check": {
                "triggered": False,
                "signals": ["trust_breakdown", "insufficient_information"],
                "severity": 2,
                "notes": "Trust climate strained by different recollections but not collapsed. Still mediable.",
            },
        },
        {
            "turn_index": 5,
            "timestamp": timestamps[4],
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon names the shared interests: both parties want fair allocation and to end joint credit liability. It flags that the missing financial facts now constitute a material feasibility gap and updates the escalation state.",
            "state_delta": {
                "open_questions_resolved": [
                    "What would a fair allocation process look like to each party once the facts are clearer?"
                ],
                "issue_map_updates": [
                    "Financial documentation gap identified as material constraint on option work."
                ],
                "escalation_state_updates": [
                    "E5 category active. Missing financial facts are a material feasibility gap. M1 posture maintained."
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
        },
        {
            "turn_index": 6,
            "timestamp": timestamps[5],
            "role": "client",
            "phase": "info_gathering",
            "message_summary": "The parties clarify what records they actually have: no pulled statements; some housing-cost text messages; rough amount estimates from memory only. The financial picture is partially clarified but still insufficient for responsible packaging.",
            "state_delta": {
                "facts_added": [
                    "Credit-card statement figures are not yet available.",
                    "Some text messages about housing costs exist but do not constitute a clear written agreement.",
                    "Both parties acknowledge that exact amounts are estimates.",
                ],
                "positions_added_or_updated": [
                    "Both parties signal openness to a documentation-then-package approach."
                ],
                "open_questions_resolved": [
                    "What written records, if any, exist of the informal housing cost or debt agreement?"
                ],
                "issue_map_updates": [
                    "Financial documentation gap confirmed as unresolved. Allocation framework remains blocked."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information", "domain_complexity_warning", "decision_quality_risk"],
                "severity": 4,
                "notes": "Financial facts still insufficiently established for confident packaging. M2 should be considered if this gap persists.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M2",
        },
        {
            "turn_index": 7,
            "timestamp": timestamps[6],
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": "Solomon proposes a documentation-first package only. Explicitly declines to recommend a split figure. Notes that if the documentation review reveals complexity beyond what the parties can resolve directly, a qualified financial neutral may be appropriate.",
            "state_delta": {
                "open_questions_resolved": [
                    "Which credit-card accounts and which housing cost period are at issue?"
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information", "domain_complexity_warning"],
                "severity": 3,
                "notes": "Bounded documentation-first path is the correct option posture. M2 held available if documentation reveals complexity.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        },
        {
            "turn_index": 8,
            "timestamp": timestamps[7],
            "role": "client",
            "phase": "agreement_building",
            "message_summary": "Both parties accept the documentation-first approach as the bounded next step. No allocation figures agreed. Both commit to pulling statements and any written records before the next session.",
            "state_delta": {
                "facts_added": [
                    "Both parties accept the documentation-first approach as the bounded next step."
                ],
                "positions_added_or_updated": [
                    "Both parties agree to pull credit-card statements and written records before the next session."
                ],
                "open_questions_resolved": [
                    "Is there any existing written record of the informal debt agreement?"
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information"],
                "severity": 2,
                "notes": "Bounded next step accepted. Financial facts still unresolved but process is progressing appropriately.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        },
    ]
    return _enrich_authored_turns(raw_turns)


def build_reference_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_reference_raw_turns(case_bundle, timestamp_prefix))


def _apply_process_variant_overrides(raw_turns: list[dict], process_variant: str) -> list[dict]:
    if process_variant == "mutual_recollection":
        for turn in raw_turns:
            if turn["turn_index"] == 3:
                turn["message_summary"] = (
                    "Solomon reflects the shared interest in a fair outcome and notes that both parties appear "
                    "to be operating from different but genuinely held recollections of the arrangement."
                )
    return raw_turns


def build_mock_model_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    raw_turns = build_reference_raw_turns(case_bundle, timestamp_prefix)
    for turn in raw_turns:
        if turn["turn_index"] == 1:
            turn["message_summary"] = (
                "Solomon frames its role as a neutral process support, confirms it is not a financial or legal "
                "advisor, and opens the issue structure around shared debt, housing costs, and documentation."
            )
        if turn["turn_index"] == 7:
            turn["message_summary"] = (
                "Solomon proposes only a documentation-first approach as the next step and declines to suggest "
                "any specific allocation figures before the financial baseline is established."
            )
    return raw_turns


def build_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_mock_model_raw_turns(case_bundle, timestamp_prefix))


def build_varied_mock_model_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    process_variant = get_varied_mock_process_variant(timestamp_prefix)
    raw_turns = build_mock_model_raw_turns(case_bundle, timestamp_prefix)
    return _apply_process_variant_overrides(raw_turns, process_variant)


def build_varied_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_varied_mock_model_raw_turns(case_bundle, timestamp_prefix))
