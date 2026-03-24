from __future__ import annotations

from runtime.benchmarks.base import RuntimeTurnPlanEntry


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
        return f"Parent A emphasizes that {opening.lower()} and says weekday overnights should stay limited until transportation and homework routines are reliable because {concern.lower()}."
    if turn_index == 4:
        opening = spouse_b["likely_openings"][0]
        goal = spouse_b["public_goals"][1]
        return f"Parent B says {opening.lower()} and frames the issue around {goal.lower()}, arguing that logistics should be solved rather than used to block time."
    if turn_index == 6:
        return "Both parents identify commute timing, exchange punctuality, and homework follow-through as the main unresolved constraints, while also signaling some openness to a phased trial if those constraints are made explicit."
    if turn_index == 8:
        return "The parents do not settle the schedule, but both accept that the next bounded step is clarifying logistics and reliability markers before considering any weekday expansion trial."
    raise ValueError(f"Unsupported client turn index: {turn_index}")


def _client_state_delta(turn_index: int) -> dict:
    if turn_index == 2:
        return {
            "facts_added": [
                "There is an active dispute about school-night overnights.",
                "The child has school-related routine needs that both parents recognize as important.",
            ],
            "facts_structured": [
                {
                    "statement": "There is an active dispute about school-night overnights.",
                    "category": "parenting_schedule",
                    "status": "accepted",
                    "related_issues": ["parenting_schedule"],
                },
                {
                    "statement": "The child has school-related routine needs that both parents recognize as important.",
                    "category": "family_structure",
                    "status": "accepted",
                    "related_issues": ["parenting_schedule", "school_logistics"],
                },
            ],
            "positions_added_or_updated": [
                "spouse_A seeks a predictable weekday structure and limited school-night overnights until logistics improve."
            ],
            "positions_structured": [
                {
                    "participant_ids": ["spouse_A"],
                    "kind": "position",
                    "issue_id": "parenting_schedule",
                    "statement": "A predictable weekday structure should remain in place until logistics improve.",
                    "status": "current",
                    "confidence": "high",
                    "position_id": "pos-spouse_a-001",
                }
            ],
            "open_questions_added": [
                "Which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?"
            ],
            "missing_info_structured": [
                {
                    "action": "open",
                    "missing_id": "missing-003",
                    "question": "Which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?",
                    "importance": "high",
                    "reason_type": "feasibility_gap",
                    "related_issues": ["school_logistics", "parenting_schedule"],
                    "note": "The session needs the logistics picture clarified before stronger optioning.",
                }
            ],
            "issue_map_updates": ["Expanded parenting_schedule with stability and routine concerns."],
            "issue_updates_structured": [
                {"issue_id": "parenting_schedule", "label": "Parenting schedule"}
            ],
        }
    if turn_index == 4:
        return {
            "facts_added": ["Parent B links school-week overnights to meaningful parenting-role concerns."],
            "facts_structured": [
                {
                    "statement": "Parent B links school-week overnights to meaningful parenting-role concerns.",
                    "category": "family_structure",
                    "status": "accepted",
                    "related_issues": ["fairness_and_parent_role", "parenting_schedule"],
                    "note": "Accepted as a stated process-relevant concern, not as an adjudicated conclusion about intent.",
                }
            ],
            "positions_added_or_updated": [
                "spouse_B seeks more school-week overnights and rejects being treated as a visitor-level parent."
            ],
            "positions_structured": [
                {
                    "participant_ids": ["spouse_B"],
                    "kind": "position",
                    "issue_id": "parenting_schedule",
                    "statement": "More school-week overnights should be considered and a visitor-level role is not acceptable.",
                    "status": "current",
                    "confidence": "high",
                    "position_id": "pos-spouse_b-001",
                }
            ],
            "open_questions_added": [
                "What concrete logistics would make a phased school-week arrangement workable?"
            ],
            "missing_info_structured": [
                {
                    "action": "open",
                    "missing_id": "missing-003",
                    "question": "What concrete logistics would make a phased school-week arrangement workable?",
                    "importance": "medium",
                    "reason_type": "feasibility_gap",
                    "related_issues": ["school_logistics", "parenting_schedule"],
                    "note": "The session needs concrete logistics before stronger optioning can be justified.",
                }
            ],
            "issue_map_updates": ["Expanded fairness_and_parent_role issue cluster."],
            "issue_updates_structured": [
                {"issue_id": "fairness_and_parent_role", "label": "Fairness and meaningful parenting role"}
            ],
        }
    if turn_index == 6:
        return {
            "facts_added": [
                "School commute feasibility is unresolved.",
                "Exchange timing reliability is unresolved.",
                "Homework and evening-routine reliability is unresolved.",
            ],
            "facts_structured": [
                {
                    "statement": "School commute feasibility is unresolved.",
                    "category": "timeline",
                    "status": "uncertain",
                    "related_issues": ["school_logistics", "parenting_schedule"],
                },
                {
                    "statement": "Exchange timing reliability is unresolved.",
                    "category": "timeline",
                    "status": "uncertain",
                    "related_issues": ["school_logistics", "parenting_schedule"],
                },
                {
                    "statement": "Homework and evening-routine reliability is unresolved.",
                    "category": "timeline",
                    "status": "uncertain",
                    "related_issues": ["school_logistics", "parenting_schedule"],
                },
            ],
            "positions_added_or_updated": [
                "Both parents show conditional openness to phased arrangements if logistics are clarified."
            ],
            "positions_structured": [
                {
                    "participant_ids": ["spouse_A"],
                    "kind": "proposal",
                    "issue_id": "parenting_schedule",
                    "statement": "A phased trial could be discussed if reliability conditions are explicit and school-week disruption is minimized.",
                    "status": "tentative",
                    "proposal_id": "prop-spouse_a-001",
                },
                {
                    "participant_ids": ["spouse_B"],
                    "kind": "proposal",
                    "issue_id": "parenting_schedule",
                    "statement": "A phased trial is acceptable if it clearly leads to meaningful school-week parenting time rather than indefinite delay.",
                    "status": "tentative",
                    "proposal_id": "prop-spouse_b-001",
                },
            ],
            "open_questions_added": [
                "What transport plan would support school-week exchanges?",
                "What reliability markers would both parents treat as sufficient for a phased trial?",
            ],
            "open_questions_resolved": [
                "Which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?"
            ],
            "missing_info_structured": [
                {
                    "action": "open",
                    "missing_id": "missing-001",
                    "question": "What transport plan would support school-week exchanges?",
                    "importance": "high",
                    "reason_type": "feasibility_gap",
                    "related_issues": ["school_logistics", "parenting_schedule"],
                    "note": "Transport planning remains the clearest unresolved feasibility constraint.",
                },
                {
                    "action": "open",
                    "missing_id": "missing-002",
                    "question": "What reliability markers would both parents treat as sufficient for a phased trial?",
                    "importance": "high",
                    "reason_type": "process_gap",
                    "related_issues": ["parenting_schedule", "communication_protocol"],
                    "note": "Phased optioning needs explicit success conditions.",
                },
                {
                    "action": "resolve",
                    "missing_id": "missing-003",
                    "question": "Which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?",
                    "related_issues": ["school_logistics", "parenting_schedule"],
                },
            ],
            "issue_map_updates": [
                "Expanded school_logistics with transport, exchange_timing, and homework_routine subissues."
            ],
            "issue_updates_structured": [
                {"issue_id": "school_logistics", "label": "School logistics"}
            ],
            "option_state_updates": [
                "Option work remains blocked from firm recommendation pending logistics clarification."
            ],
        }
    if turn_index == 8:
        return {
            "facts_added": ["Both parents accept clarification of logistics as the bounded next step."],
            "facts_structured": [
                {
                    "statement": "Both parents accept clarification of logistics as the bounded next step.",
                    "category": "timeline",
                    "status": "accepted",
                    "related_issues": ["school_logistics", "parenting_schedule"],
                }
            ],
            "positions_added_or_updated": [
                "Parent A and Parent B remain open to phased exploration if reliability markers are explicit."
            ],
            "positions_structured": [
                {
                    "participant_ids": ["spouse_A", "spouse_B"],
                    "kind": "proposal",
                    "issue_id": "parenting_schedule",
                    "statement": "Both parents remain open to phased exploration if reliability markers are explicit.",
                    "status": "tentative",
                    "proposal_id": "prop-shared-001",
                }
            ],
            "open_questions_resolved": [
                "What concrete logistics would make a phased school-week arrangement workable?"
            ],
            "missing_info_structured": [
                {
                    "action": "resolve",
                    "missing_id": "missing-003",
                    "question": "What concrete logistics would make a phased school-week arrangement workable?",
                    "related_issues": ["school_logistics", "parenting_schedule"],
                }
            ],
            "escalation_state_updates": [
                "Closed the slice in M1 with unresolved feasibility gaps recorded explicitly."
            ],
        }
    raise ValueError(f"Unsupported client turn index: {turn_index}")


def _client_risk_check(turn_index: int) -> dict:
    if turn_index == 2:
        return {
            "triggered": False,
            "signals": ["insufficient_information"],
            "severity": 2,
            "notes": "Feasibility-relevant details are not yet clear.",
        }
    if turn_index == 4:
        return {
            "triggered": False,
            "signals": ["trust_breakdown"],
            "severity": 2,
            "notes": "The exchange is tense but still mediable.",
        }
    if turn_index == 6:
        return {
            "triggered": True,
            "signals": ["insufficient_information", "decision_quality_risk", "domain_complexity_warning"],
            "severity": 3,
            "notes": "Unresolved logistics now materially constrain responsible optioning.",
        }
    if turn_index == 8:
        return {
            "triggered": True,
            "signals": ["insufficient_information"],
            "severity": 2,
            "notes": "The case remains workable if the next step stays bounded.",
        }
    raise ValueError(f"Unsupported client turn index: {turn_index}")


def generate_runtime_client_turn(turn_index: int, timestamp: str, state: dict, case_bundle: dict) -> dict:
    turn = {
        "turn_index": turn_index,
        "timestamp": timestamp,
        "role": "client",
        "phase": "info_gathering" if turn_index in {2, 6} else ("interest_exploration" if turn_index == 4 else "agreement_building"),
        "message_summary": _client_summary(turn_index, state, case_bundle),
        "state_delta": _client_state_delta(turn_index),
        "risk_check": _client_risk_check(turn_index),
    }
    if turn_index == 8:
        turn["candidate_escalation_category"] = "E5"
        turn["candidate_escalation_mode"] = "M1"
    return turn


def _process_intro(process_variant: str) -> str:
    if process_variant == "logistics_first":
        return "keeps decision authority with the parents and sets a structure that starts with practical logistics before broader option exploration"
    return "states that the parents remain decision-makers and sets a structure focused on schedule concerns, underlying needs, and possible next steps"


def _issue_emphasis(state: dict, process_variant: str) -> str:
    issue_labels = [issue.lower() for issue in state["summary_state"]["issues"]]
    if process_variant == "logistics_first" and "school logistics" in issue_labels:
        return "clarifying what practical constraints have to be understood before broader option exploration"
    if "fairness and meaningful parenting role" in issue_labels:
        return "reframing the dispute around stability needs and meaningful parent-role concerns"
    return "clarifying what each parent needs before stronger option exploration"


def _mid_session_summary(state: dict, process_variant: str) -> str:
    has_logistics = any(issue.lower() == "school logistics" for issue in state["summary_state"]["issues"])
    if process_variant == "logistics_first" and has_logistics:
        return "Solomon summarizes the overlap while emphasizing that logistics clarification is the bridge between both parents' values and any responsible next step."
    return "Solomon summarizes the overlap in the parents' values while keeping the process centered on bounded, non-directive next steps."


def _bounded_option_summary(process_variant: str, plugin_assessment: dict) -> str:
    if process_variant == "logistics_first":
        return "Solomon keeps optioning narrow by anchoring on logistics-conditioned paths first and avoids presenting a fixed recommendation while feasibility remains unresolved."
    if plugin_assessment.get("plugin_confidence") == "low":
        return "Solomon proposes only bounded exploration, keeping any phased school-week option contingent on clarifying transportation and homework routines and avoiding a fixed recommendation."
    return "Solomon proposes only bounded exploration and avoids presenting a single overnight recommendation while unresolved feasibility questions remain."


def _assistant_risk_notes(turn_index: int, plugin_assessment: dict) -> str:
    if turn_index == 7 and plugin_assessment.get("warnings"):
        return plugin_assessment["warnings"][0]
    if turn_index == 7:
        return "Bounded option work remains appropriate under caution."
    if turn_index == 5:
        return "Interest-level synthesis preserved both parties' concerns without overstating feasibility."
    return "Neutral structure preserved progress without overcommitment."


def _candidate_open_questions(turn_index: int, process_variant: str) -> list[str]:
    if turn_index == 1:
        if process_variant == "logistics_first":
            return [
                "What school-week logistics are causing the most strain?",
                "What would each parent need before discussing changes to overnight time?",
            ]
        return [
            "What would each parent need before discussing changes to overnight time?",
            "What school-week logistics are causing the most strain?",
        ]
    if turn_index == 3:
        return ["What would make Parent B feel meaningfully included without destabilizing the school week?"]
    if turn_index == 5:
        if process_variant == "logistics_first":
            return ["Are the disputed logistics temporary coordination problems or persistent reliability problems?"]
        return ["What temporary logistics or sequencing changes could make movement feel safer to both parents?"]
    return []


def _select_new_open_questions(state: dict, turn_index: int, process_variant: str) -> list[str]:
    existing = set(state["open_questions"])
    selected = []
    for question in _candidate_open_questions(turn_index, process_variant):
        if question not in existing:
            selected.append(question)
    return selected


def _resolve_questions(state: dict, turn_index: int, process_variant: str) -> list[str]:
    if turn_index == 3:
        for question in state["open_questions"]:
            if "each parent need" in question.lower():
                return [question]
    if turn_index == 7 and process_variant == "logistics_first":
        for question in state["open_questions"]:
            if "temporary coordination" in question.lower():
                return [question]
    return []


def _issue_updates_for_turn(state: dict, turn_index: int, process_variant: str) -> list[str]:
    if turn_index == 1:
        return [
            "Initialized parenting_schedule",
            "Initialized school_logistics",
            "Initialized communication_protocol",
        ]
    if turn_index == 3:
        return ["Linked parenting_schedule to fairness_and_parent_role concerns."]
    if turn_index == 5:
        if process_variant == "logistics_first":
            return ["Linked school_logistics to meaningful_parent_role as gating constraints."]
        return ["Linked child_stability to meaningful_parent_role as coexisting interests."]
    return []


def _bounded_option_updates(process_variant: str, plugin_assessment: dict) -> list[str]:
    low_conf = plugin_assessment.get("plugin_confidence") == "low"
    if process_variant == "logistics_first":
        ordered = [
            "Added logistics_conditioned_expansion_option",
            "Added phased_trial_option",
        ]
    else:
        ordered = [
            "Added phased_trial_option",
            "Added logistics_conditioned_expansion_option",
        ]
    if low_conf:
        ordered.append("Marked fixed_recommendation_out_of_scope_pending_feasibility")
    else:
        ordered.append("Marked stronger_recommendation_still_qualified")
    return ordered


def _interest_facts(state: dict) -> list[str]:
    facts = []
    fact_statements = {fact["statement"] for fact in state["facts"]}
    if "Both parents identify child stability as important." not in fact_statements:
        facts.append("Both parents identify child stability as important.")
    if "Both parents want the child to maintain a meaningful relationship with each parent." not in fact_statements:
        facts.append("Both parents want the child to maintain a meaningful relationship with each parent.")
    return facts


def generate_runtime_assistant_turn(turn_index: int, timestamp: str, state: dict, plugin_assessment: dict | None = None) -> dict:
    plugin_assessment = plugin_assessment or {}
    process_variant = state["meta"].get("process_variant") or "interest_first"
    if turn_index == 1:
        summary = f"Solomon frames its role as a neutral mediation assistant, {_process_intro(process_variant)}."
        return {
            "turn_index": 1,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": summary,
            "state_delta": {
                "open_questions_added": _select_new_open_questions(state, turn_index, process_variant),
                "issue_updates_structured": [
                    {"issue_id": "parenting_schedule", "label": "Parenting schedule"},
                    {"issue_id": "school_logistics", "label": "School logistics"},
                    {"issue_id": "communication_protocol", "label": "Communication protocol around future changes"},
                ],
                "issue_map_updates": _issue_updates_for_turn(state, turn_index, process_variant),
                "escalation_state_updates": [
                    "Opened in standard posture with caution available if feasibility remains unclear."
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Opening structure is routine."},
        }

    if turn_index == 3:
        summary = f"Solomon shifts from the opening frame into {_issue_emphasis(state, process_variant)}."
        return {
            "turn_index": 3,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": summary,
            "state_delta": {
                "open_questions_added": _select_new_open_questions(state, turn_index, process_variant),
                "open_questions_resolved": _resolve_questions(state, turn_index, process_variant),
                "issue_updates_structured": [
                    {"issue_id": "fairness_and_parent_role", "label": "Fairness and meaningful parenting role"}
                ],
                "issue_map_updates": _issue_updates_for_turn(state, turn_index, process_variant),
                "escalation_state_updates": ["Maintained ordinary handling while shifting toward interest work."],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": _assistant_risk_notes(turn_index, plugin_assessment)},
        }

    if turn_index == 5:
        summary = _mid_session_summary(state, process_variant)
        return {
            "turn_index": 5,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": summary,
            "state_delta": {
                "facts_added": _interest_facts(state),
                "facts_structured": [
                    {
                        "statement": "Both parents identify child stability as important.",
                        "category": "family_structure",
                        "status": "accepted",
                        "related_issues": ["parenting_schedule"],
                    },
                    {
                        "statement": "Both parents want the child to maintain a meaningful relationship with each parent.",
                        "category": "family_structure",
                        "status": "accepted",
                        "related_issues": ["fairness_and_parent_role", "parenting_schedule"],
                    },
                ],
                "issue_updates_structured": [
                    {"issue_id": "parenting_schedule", "label": "Parenting schedule"},
                    {"issue_id": "fairness_and_parent_role", "label": "Fairness and meaningful parenting role"},
                ],
                "open_questions_added": _select_new_open_questions(state, turn_index, process_variant),
                "issue_map_updates": _issue_updates_for_turn(state, turn_index, process_variant),
                "escalation_state_updates": ["Prepared for feasibility qualification before option exploration."],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": _assistant_risk_notes(turn_index, plugin_assessment)},
        }

    if turn_index == 7:
        low_conf = plugin_assessment.get("plugin_confidence") == "low"
        warnings = plugin_assessment.get("warnings", [])
        summary = _bounded_option_summary(process_variant, plugin_assessment)
        signals = ["insufficient_information"]
        if low_conf:
            signals.append("plugin_low_confidence")
        if warnings:
            signals.append("decision_quality_risk")
        return {
            "turn_index": 7,
            "timestamp": timestamp,
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": summary,
            "state_delta": {
                "packages_structured": [
                    {
                        "package_id": "pkg-d-b04-001",
                        "family": "logistics_package",
                        "status": "bounded_only",
                        "summary": "a phased trial and logistics-conditioned expansion path",
                        "elements": [
                            "phased_trial_option",
                            "logistics_conditioned_expansion_option",
                        ],
                        "related_issues": ["school_logistics", "parenting_schedule"],
                    }
                ],
                "option_state_updates": _bounded_option_updates(process_variant, plugin_assessment),
                "open_questions_resolved": _resolve_questions(state, turn_index, process_variant),
                "escalation_state_updates": [
                    "Selected M1 continue_with_caution due to unresolved feasibility questions."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": signals,
                "severity": 3,
                "notes": _assistant_risk_notes(turn_index, plugin_assessment),
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        }

    raise ValueError(f"Unsupported assistant turn index: {turn_index}")
