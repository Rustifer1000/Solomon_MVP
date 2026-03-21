from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib

from runtime.contracts import CandidateTurn
from runtime.normalization import normalize_core_output


def build_reference_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    case_id = case_bundle["case_metadata"]["case_id"]
    if case_id != "D-B04":
        raise NotImplementedError(f"Reference scaffold only supports D-B04 right now, not {case_id}.")

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
    return [
        {
            "turn_index": 1,
            "timestamp": timestamps[0],
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": "Solomon frames its role as a neutral mediation assistant, states that the parents remain decision-makers, and sets a structure focused on schedule concerns, underlying needs, and possible next steps.",
            "state_delta": {
                "open_questions_added": [
                    "What school-week logistics are causing the most strain?",
                    "What would each parent need before discussing changes to overnight time?",
                ],
                "issue_map_updates": [
                    "Initialized parenting_schedule",
                    "Initialized school_logistics",
                    "Initialized communication_protocol",
                ],
                "escalation_state_updates": [
                    "Opened in standard posture with caution available if feasibility remains unclear."
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Opening structure is routine."},
        },
        {
            "turn_index": 2,
            "timestamp": timestamps[1],
            "role": "client",
            "phase": "info_gathering",
            "message_summary": "Parent A says school-night overnights should remain limited until transport and homework routines are reliable, emphasizing the child's need for stability.",
            "state_delta": {
                "facts_added": [
                    "There is an active dispute about school-night overnights.",
                    "The child has school-related routine needs that both parents recognize as important.",
                ],
                "positions_added_or_updated": [
                    "spouse_A seeks a predictable weekday structure and limited school-night overnights until logistics improve."
                ],
                "open_questions_added": [
                    "Which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?"
                ],
                "issue_map_updates": ["Expanded parenting_schedule with stability and routine concerns."],
            },
            "risk_check": {
                "triggered": False,
                "signals": ["insufficient_information"],
                "severity": 2,
                "notes": "Feasibility-relevant details are not yet clear.",
            },
        },
        {
            "turn_index": 3,
            "timestamp": timestamps[2],
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon distinguishes Parent A's position from underlying interests, reframing the dispute as stability versus marginalization rather than a simple overnight fight.",
            "state_delta": {
                "open_questions_added": [
                    "What would make Parent B feel meaningfully included without destabilizing the school week?"
                ],
                "open_questions_resolved": [
                    "What would each parent need before discussing changes to overnight time?"
                ],
                "issue_map_updates": ["Linked parenting_schedule to fairness_and_parent_role concerns."],
                "escalation_state_updates": ["Maintained ordinary handling while shifting toward interest work."],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Neutral reframing reduced rigidity."},
        },
        {
            "turn_index": 4,
            "timestamp": timestamps[3],
            "role": "client",
            "phase": "interest_exploration",
            "message_summary": "Parent B says the issue is about having a meaningful parenting role during the school week and asks that logistics be solved rather than used as a blocker.",
            "state_delta": {
                "facts_added": ["Parent B links school-week overnights to meaningful parenting-role concerns."],
                "positions_added_or_updated": [
                    "spouse_B seeks more school-week overnights and rejects being treated as a visitor-level parent."
                ],
                "open_questions_added": [
                    "What concrete logistics would make a phased school-week arrangement workable?"
                ],
                "issue_map_updates": ["Expanded fairness_and_parent_role issue cluster."],
            },
            "risk_check": {
                "triggered": False,
                "signals": ["trust_breakdown"],
                "severity": 2,
                "notes": "The exchange is tense but still mediable.",
            },
        },
        {
            "turn_index": 5,
            "timestamp": timestamps[4],
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon summarizes the overlap: both parents care about stability and a meaningful role, but differ on what must happen before more overnights are tried.",
            "state_delta": {
                "facts_added": [
                    "Both parents identify child stability as important.",
                    "Both parents want the child to maintain a meaningful relationship with each parent.",
                ],
                "open_questions_added": [
                    "Are the disputed logistics temporary coordination problems or persistent reliability problems?"
                ],
                "issue_map_updates": ["Linked child_stability to meaningful_parent_role as coexisting interests."],
                "escalation_state_updates": ["Prepared for feasibility qualification before option exploration."],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Interest synthesis preserved both concerns."},
        },
        {
            "turn_index": 6,
            "timestamp": timestamps[5],
            "role": "client",
            "phase": "info_gathering",
            "message_summary": "The parents identify unresolved school commute timing, exchange punctuality, and homework-routine reliability as the main practical barriers, while showing some openness to a phased arrangement if clarified.",
            "state_delta": {
                "facts_added": [
                    "School commute feasibility is unresolved.",
                    "Exchange timing reliability is unresolved.",
                    "Homework and evening-routine reliability is unresolved.",
                ],
                "positions_added_or_updated": [
                    "Both parents show conditional openness to phased arrangements if logistics are clarified."
                ],
                "open_questions_added": [
                    "What transport plan would support school-week exchanges?",
                    "What reliability markers would both parents treat as sufficient for a phased trial?",
                ],
                "open_questions_resolved": [
                    "Which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?"
                ],
                "issue_map_updates": [
                    "Expanded school_logistics with transport, exchange_timing, and homework_routine subissues."
                ],
                "option_state_updates": [
                    "Option work remains blocked from firm recommendation pending logistics clarification."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information", "decision_quality_risk", "domain_complexity_warning"],
                "severity": 3,
                "notes": "Unresolved logistics now materially constrain responsible optioning.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        },
        {
            "turn_index": 7,
            "timestamp": timestamps[6],
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": "Solomon proposes only bounded exploration: a phased trial or contingent school-week expansion tied to clarified transportation and homework routines, and avoids a final schedule recommendation.",
            "state_delta": {
                "option_state_updates": [
                    "Added phased_trial_option",
                    "Added logistics_conditioned_expansion_option",
                    "Marked fixed_recommendation_out_of_scope_pending_feasibility",
                ],
                "escalation_state_updates": [
                    "Selected M1 continue_with_caution due to unresolved feasibility questions."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information", "plugin_low_confidence"],
                "severity": 3,
                "notes": "Bounded option work is appropriate, but stronger commitment would overstate domain confidence.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        },
        {
            "turn_index": 8,
            "timestamp": timestamps[7],
            "role": "client",
            "phase": "agreement_building",
            "message_summary": "The parents do not reach final agreement, but both accept that clarifying transport and routine details should come before any phased school-week change.",
            "state_delta": {
                "facts_added": ["Both parents accept clarification of logistics as the bounded next step."],
                "positions_added_or_updated": [
                    "Parent A and Parent B remain open to phased exploration if reliability markers are explicit."
                ],
                "open_questions_resolved": [
                    "What concrete logistics would make a phased school-week arrangement workable?"
                ],
                "escalation_state_updates": [
                    "Closed the slice in M1 with unresolved feasibility gaps recorded explicitly."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information"],
                "severity": 2,
                "notes": "The case remains workable if the next step stays bounded.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        },
    ]


def build_reference_turns(case_bundle: dict, timestamp_prefix: str) -> list[CandidateTurn]:
    return [normalize_core_output(raw_turn) for raw_turn in build_reference_raw_turns(case_bundle, timestamp_prefix)]


def build_mock_model_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    case_id = case_bundle["case_metadata"]["case_id"]
    if case_id != "D-B04":
        raise NotImplementedError(f"Mock model scaffold only supports D-B04 right now, not {case_id}.")

    timestamps = [
        f"{timestamp_prefix}T00:00:12Z",
        f"{timestamp_prefix}T00:01:34Z",
        f"{timestamp_prefix}T00:02:28Z",
        f"{timestamp_prefix}T00:03:43Z",
        f"{timestamp_prefix}T00:04:58Z",
        f"{timestamp_prefix}T00:06:14Z",
        f"{timestamp_prefix}T00:07:38Z",
        f"{timestamp_prefix}T00:08:55Z",
    ]
    return [
        {
            "turn_index": 1,
            "timestamp": timestamps[0],
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": "Solomon opens by clarifying that it is facilitating a mediation process, not making decisions for the parents, and proposes focusing first on the school-week schedule problem and the reasons behind each position.",
            "state_delta": {
                "open_questions_added": [
                    "What school-week logistics are causing the most strain?",
                    "What would each parent need before discussing changes to overnight time?",
                ],
                "issue_map_updates": [
                    "Initialized parenting_schedule",
                    "Initialized school_logistics",
                    "Initialized communication_protocol",
                ],
                "escalation_state_updates": [
                    "Opened in standard posture with caution available if feasibility remains unclear."
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Opening structure is routine."},
        },
        {
            "turn_index": 2,
            "timestamp": timestamps[1],
            "role": "client",
            "phase": "info_gathering",
            "message_summary": "Parent A says weekday overnights should stay limited for now because transportation and homework consistency are not reliable enough yet.",
            "state_delta": {
                "facts_added": [
                    "There is an active dispute about school-night overnights.",
                    "The child has school-related routine needs that both parents recognize as important.",
                ],
                "positions_added_or_updated": [
                    "spouse_A seeks a predictable weekday structure and limited school-night overnights until logistics improve."
                ],
                "open_questions_added": [
                    "Which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?"
                ],
                "issue_map_updates": ["Expanded parenting_schedule with stability and routine concerns."],
            },
            "risk_check": {
                "triggered": False,
                "signals": ["insufficient_information"],
                "severity": 2,
                "notes": "Feasibility-relevant details are not yet clear.",
            },
        },
        {
            "turn_index": 3,
            "timestamp": timestamps[2],
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon reframes the disagreement as a tension between preserving stability and avoiding a marginal parenting role, rather than treating it as a simple yes-or-no overnight question.",
            "state_delta": {
                "open_questions_added": [
                    "What would make Parent B feel meaningfully included without destabilizing the school week?"
                ],
                "open_questions_resolved": [
                    "What would each parent need before discussing changes to overnight time?"
                ],
                "issue_map_updates": ["Linked parenting_schedule to fairness_and_parent_role concerns."],
                "escalation_state_updates": ["Maintained ordinary handling while shifting toward interest work."],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Neutral reframing reduced rigidity."},
        },
        {
            "turn_index": 4,
            "timestamp": timestamps[3],
            "role": "client",
            "phase": "interest_exploration",
            "message_summary": "Parent B says the real concern is having meaningful school-week parenting time and not letting logistics become a permanent excuse for staying in a weekend-only role.",
            "state_delta": {
                "facts_added": ["Parent B links school-week overnights to meaningful parenting-role concerns."],
                "positions_added_or_updated": [
                    "spouse_B seeks more school-week overnights and rejects being treated as a visitor-level parent."
                ],
                "open_questions_added": [
                    "What concrete logistics would make a phased school-week arrangement workable?"
                ],
                "issue_map_updates": ["Expanded fairness_and_parent_role issue cluster."],
            },
            "risk_check": {
                "triggered": False,
                "signals": ["trust_breakdown"],
                "severity": 2,
                "notes": "The exchange is tense but still mediable.",
            },
        },
        {
            "turn_index": 5,
            "timestamp": timestamps[4],
            "role": "assistant",
            "phase": "interest_exploration",
            "message_summary": "Solomon summarizes that both parents value stability and meaningful involvement, but they disagree on what conditions have to be met before trying more weekday overnights.",
            "state_delta": {
                "facts_added": [
                    "Both parents identify child stability as important.",
                    "Both parents want the child to maintain a meaningful relationship with each parent.",
                ],
                "open_questions_added": [
                    "Are the disputed logistics temporary coordination problems or persistent reliability problems?"
                ],
                "issue_map_updates": ["Linked child_stability to meaningful_parent_role as coexisting interests."],
                "escalation_state_updates": ["Prepared for feasibility qualification before option exploration."],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Interest synthesis preserved both concerns."},
        },
        {
            "turn_index": 6,
            "timestamp": timestamps[5],
            "role": "client",
            "phase": "info_gathering",
            "message_summary": "The parents identify the commute, exchange punctuality, and homework follow-through as the main unresolved constraints, while also signaling some openness to a phased trial if those constraints are made explicit.",
            "state_delta": {
                "facts_added": [
                    "School commute feasibility is unresolved.",
                    "Exchange timing reliability is unresolved.",
                    "Homework and evening-routine reliability is unresolved.",
                ],
                "positions_added_or_updated": [
                    "Both parents show conditional openness to phased arrangements if logistics are clarified."
                ],
                "open_questions_added": [
                    "What transport plan would support school-week exchanges?",
                    "What reliability markers would both parents treat as sufficient for a phased trial?",
                ],
                "open_questions_resolved": [
                    "Which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?"
                ],
                "issue_map_updates": [
                    "Expanded school_logistics with transport, exchange_timing, and homework_routine subissues."
                ],
                "option_state_updates": [
                    "Option work remains blocked from firm recommendation pending logistics clarification."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information", "decision_quality_risk", "domain_complexity_warning"],
                "severity": 3,
                "notes": "Unresolved logistics now materially constrain responsible optioning.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        },
        {
            "turn_index": 7,
            "timestamp": timestamps[6],
            "role": "assistant",
            "phase": "option_generation",
            "message_summary": "Solomon limits the discussion to contingent or phased possibilities and explicitly avoids presenting a single overnight recommendation while logistics remain unresolved.",
            "state_delta": {
                "option_state_updates": [
                    "Added phased_trial_option",
                    "Added logistics_conditioned_expansion_option",
                    "Marked fixed_recommendation_out_of_scope_pending_feasibility",
                ],
                "escalation_state_updates": [
                    "Selected M1 continue_with_caution due to unresolved feasibility questions."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information", "plugin_low_confidence"],
                "severity": 3,
                "notes": "Bounded option work is appropriate, but stronger commitment would overstate domain confidence.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        },
        {
            "turn_index": 8,
            "timestamp": timestamps[7],
            "role": "client",
            "phase": "agreement_building",
            "message_summary": "The parents do not settle the schedule, but both accept that the next bounded step is clarifying logistics before considering any weekday expansion trial.",
            "state_delta": {
                "facts_added": ["Both parents accept clarification of logistics as the bounded next step."],
                "positions_added_or_updated": [
                    "Parent A and Parent B remain open to phased exploration if reliability markers are explicit."
                ],
                "open_questions_resolved": [
                    "What concrete logistics would make a phased school-week arrangement workable?"
                ],
                "escalation_state_updates": [
                    "Closed the slice in M1 with unresolved feasibility gaps recorded explicitly."
                ],
            },
            "risk_check": {
                "triggered": True,
                "signals": ["insufficient_information"],
                "severity": 2,
                "notes": "The case remains workable if the next step stays bounded.",
            },
            "candidate_escalation_category": "E5",
            "candidate_escalation_mode": "M1",
        },
    ]


def build_mock_model_turns(case_bundle: dict, timestamp_prefix: str) -> list[CandidateTurn]:
    return [normalize_core_output(raw_turn) for raw_turn in build_mock_model_raw_turns(case_bundle, timestamp_prefix)]


def _variant_index(seed_material: str, modulo: int) -> int:
    digest = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulo


def get_varied_mock_process_variant(timestamp_prefix: str) -> str:
    variants = ["interest_first", "logistics_first"]
    choice = _variant_index(f"{timestamp_prefix}:process_variant", len(variants))
    return variants[choice]


def build_varied_mock_model_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    raw_turns = deepcopy(build_mock_model_raw_turns(case_bundle, timestamp_prefix))
    process_variant = get_varied_mock_process_variant(timestamp_prefix)
    summary_variants = {
        1: [
            "Solomon opens by clarifying that it is facilitating a mediation process, not making decisions for the parents, and proposes focusing first on the school-week schedule problem and the reasons behind each position.",
            "Solomon starts by naming its role as a neutral mediation aid, keeping decision authority with the parents, and setting a structure around schedule concerns and the reasons underneath them.",
            "Solomon begins with a bounded mediation frame: it is there to support process, not decide outcomes, and it suggests starting with the school-week conflict and its underlying constraints.",
        ],
        3: [
            "Solomon reframes the disagreement as a tension between preserving stability and avoiding a marginal parenting role, rather than treating it as a simple yes-or-no overnight question.",
            "Solomon recasts the conflict as one between stability needs and meaningful parenting-role concerns instead of a binary fight about overnights.",
            "Solomon shifts the conversation away from a raw overnight dispute and toward the deeper tension between school-week stability and parent-role legitimacy.",
        ],
        5: [
            "Solomon summarizes that both parents value stability and meaningful involvement, but they disagree on what conditions have to be met before trying more weekday overnights.",
            "Solomon highlights the overlap: both parents care about stability and meaningful participation, even though they disagree about the conditions for more weekday time.",
            "Solomon notes that both parents are protecting something important, but they diverge on what needs to be true before a weekday expansion can be tried.",
        ],
        7: [
            "Solomon limits the discussion to contingent or phased possibilities and explicitly avoids presenting a single overnight recommendation while logistics remain unresolved.",
            "Solomon keeps optioning narrow by exploring only phased or contingent paths and by avoiding any fixed recommendation while logistics are still open.",
            "Solomon explores only bounded possibilities, making clear that unresolved logistics prevent it from responsibly endorsing a single schedule outcome.",
        ],
        8: [
            "The parents do not settle the schedule, but both accept that the next bounded step is clarifying logistics before considering any weekday expansion trial.",
            "No final schedule is reached, but both parents agree that the immediate next step is to clarify logistics before testing any weekday expansion.",
            "The discussion stops short of agreement, but both parents accept that logistics must be clarified before any weekday trial should be considered.",
        ],
    }

    risk_note_variants = {
        6: [
            "Unresolved logistics now materially constrain responsible optioning.",
            "The unresolved logistics now meaningfully limit what can be recommended responsibly.",
            "The session remains workable, but the logistics gaps now sharply limit responsible option development.",
        ],
        7: [
            "Bounded option work is appropriate, but stronger commitment would overstate domain confidence.",
            "Cautious option exploration is still justified, but firmer commitment would outrun domain support.",
            "The system can explore bounded paths here, but a stronger recommendation would overclaim feasibility.",
        ],
    }

    structural_variants = {
        1: {
            "open_questions_added": [
                [
                    "What school-week logistics are causing the most strain?",
                    "What would each parent need before discussing changes to overnight time?",
                ],
                [
                    "What would each parent need before discussing changes to overnight time?",
                    "What school-week logistics are causing the most strain?",
                ],
            ]
        },
        6: {
            "open_questions_added": [
                [
                    "What transport plan would support school-week exchanges?",
                    "What reliability markers would both parents treat as sufficient for a phased trial?",
                ],
                [
                    "What reliability markers would both parents treat as sufficient for a phased trial?",
                    "What transport plan would support school-week exchanges?",
                ],
            ]
        },
        7: {
            "option_state_updates": [
                [
                    "Added phased_trial_option",
                    "Added logistics_conditioned_expansion_option",
                    "Marked fixed_recommendation_out_of_scope_pending_feasibility",
                ],
                [
                    "Added logistics_conditioned_expansion_option",
                    "Added phased_trial_option",
                    "Marked fixed_recommendation_out_of_scope_pending_feasibility",
                ],
            ]
        },
    }

    for raw_turn in raw_turns:
        turn_index = raw_turn["turn_index"]
        if turn_index in summary_variants:
            variants = summary_variants[turn_index]
            choice = _variant_index(f"{timestamp_prefix}:{turn_index}:summary", len(variants))
            raw_turn["message_summary"] = variants[choice]
        if turn_index in risk_note_variants:
            variants = risk_note_variants[turn_index]
            choice = _variant_index(f"{timestamp_prefix}:{turn_index}:risk", len(variants))
            raw_turn["risk_check"]["notes"] = variants[choice]
        if turn_index in structural_variants:
            for field_name, variants in structural_variants[turn_index].items():
                choice = _variant_index(f"{timestamp_prefix}:{turn_index}:{field_name}", len(variants))
                raw_turn["state_delta"][field_name] = variants[choice]

    if process_variant == "interest_first":
        raw_turns[2]["message_summary"] = (
            "Solomon first leans into interest elicitation, framing the conflict around stability needs and meaningful parent-role concerns before moving back toward practical sequencing."
        )
        raw_turns[4]["message_summary"] = (
            "Solomon reinforces the overlap in values before naming logistics as the next gating constraint, keeping the process centered on interests first and feasibility second."
        )
        raw_turns[5]["message_summary"] = (
            "Once shared interests are clearer, the parents identify commute, exchange timing, and homework follow-through as the practical constraints that must be clarified before stronger optioning."
        )
    else:
        raw_turns[2]["message_summary"] = (
            "Solomon keeps the process anchored in logistics earlier, using the stability-versus-role tension to clarify why practical constraints need to be surfaced before broader option exploration."
        )
        raw_turns[4]["message_summary"] = (
            "Solomon summarizes the overlap, but emphasizes that logistics clarification is the main bridge between the parents' values and any responsible next step."
        )
        raw_turns[5]["message_summary"] = (
            "The parents identify commute, exchange timing, and homework follow-through as the first practical constraints to resolve, with broader interest framing staying present but secondary."
        )
    return raw_turns


def build_varied_mock_model_turns(case_bundle: dict, timestamp_prefix: str) -> list[CandidateTurn]:
    return [normalize_core_output(raw_turn) for raw_turn in build_varied_mock_model_raw_turns(case_bundle, timestamp_prefix)]


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
            "positions_added_or_updated": [
                "spouse_A seeks a predictable weekday structure and limited school-night overnights until logistics improve."
            ],
            "open_questions_added": [
                "Which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?"
            ],
            "issue_map_updates": ["Expanded parenting_schedule with stability and routine concerns."],
        }
    if turn_index == 4:
        return {
            "facts_added": ["Parent B links school-week overnights to meaningful parenting-role concerns."],
            "positions_added_or_updated": [
                "spouse_B seeks more school-week overnights and rejects being treated as a visitor-level parent."
            ],
            "open_questions_added": [
                "What concrete logistics would make a phased school-week arrangement workable?"
            ],
            "issue_map_updates": ["Expanded fairness_and_parent_role issue cluster."],
        }
    if turn_index == 6:
        return {
            "facts_added": [
                "School commute feasibility is unresolved.",
                "Exchange timing reliability is unresolved.",
                "Homework and evening-routine reliability is unresolved.",
            ],
            "positions_added_or_updated": [
                "Both parents show conditional openness to phased arrangements if logistics are clarified."
            ],
            "open_questions_added": [
                "What transport plan would support school-week exchanges?",
                "What reliability markers would both parents treat as sufficient for a phased trial?",
            ],
            "open_questions_resolved": [
                "Which logistics are currently unreliable: transport, exchange timing, homework routine, or all three?"
            ],
            "issue_map_updates": [
                "Expanded school_logistics with transport, exchange_timing, and homework_routine subissues."
            ],
            "option_state_updates": [
                "Option work remains blocked from firm recommendation pending logistics clarification."
            ],
        }
    if turn_index == 8:
        return {
            "facts_added": ["Both parents accept clarification of logistics as the bounded next step."],
            "positions_added_or_updated": [
                "Parent A and Parent B remain open to phased exploration if reliability markers are explicit."
            ],
            "open_questions_resolved": [
                "What concrete logistics would make a phased school-week arrangement workable?"
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


@dataclass(frozen=True)
class DB04Simulation:
    case_id: str = "D-B04"

    def build_turns(self, source: str, case_bundle: dict, timestamp_prefix: str) -> list[CandidateTurn]:
        builders = {
            "reference": build_reference_turns,
            "mock_model": build_mock_model_turns,
            "varied_mock_model": build_varied_mock_model_turns,
        }
        try:
            return builders[source](case_bundle, timestamp_prefix)
        except KeyError as exc:
            raise ValueError(f"Unsupported source for {self.case_id}: {source}") from exc

    def get_process_variant(self, source: str, timestamp_prefix: str) -> str | None:
        if source in {"varied_mock_model", "runtime"}:
            return get_varied_mock_process_variant(timestamp_prefix)
        return None

    def generate_runtime_assistant_turn(
        self,
        turn_index: int,
        timestamp: str,
        state: dict,
        plugin_assessment: dict | None = None,
    ) -> dict:
        return generate_runtime_assistant_turn(turn_index, timestamp, state, plugin_assessment)

    def generate_runtime_client_turn(
        self,
        turn_index: int,
        timestamp: str,
        state: dict,
        case_bundle: dict,
    ) -> dict:
        return generate_runtime_client_turn(turn_index, timestamp, state, case_bundle)


D_B04_SIMULATION = DB04Simulation()
