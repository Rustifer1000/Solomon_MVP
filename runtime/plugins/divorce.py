from __future__ import annotations


ISSUE_TAXONOMY = [
    "parenting_schedule",
    "school_logistics",
    "fairness_and_parent_role",
    "communication_protocol",
]


def qualify_case(case_bundle: dict) -> dict:
    metadata = case_bundle["case_metadata"]
    return {
        "plugin_type": metadata["plugin_type"],
        "plugin_name": "divorce_v0_runtime",
        "issue_taxonomy": ISSUE_TAXONOMY,
        "feasibility_constraints": [
            "school commute timing",
            "exchange punctuality",
            "homework and evening routine reliability",
        ],
        "caution_note": "Plugin supports phased or contingent exploration, but not a fixed recommendation until logistics are clarified.",
    }


def assess_state(state: dict) -> dict:
    unresolved_questions = {item["question"] for item in state["missing_info"] if item["status"] == "open"}
    logistics_related = [
        question
        for question in unresolved_questions
        if "transport" in question.lower()
        or "school-week" in question.lower()
        or "homework" in question.lower()
        or "trial" in question.lower()
    ]
    option_count = len(state["options"])
    plugin_confidence = "moderate"
    warnings: list[str] = []

    if len(logistics_related) >= 2:
        plugin_confidence = "low"
        warnings.append("Plugin confidence remains limited because material logistics questions are still unresolved.")

    if option_count >= 1 and logistics_related:
        warnings.append("Stronger optioning should remain qualified until logistics questions are clarified.")

    return {
        "plugin_confidence": plugin_confidence,
        "logistics_related_missing_info": logistics_related,
        "warnings": warnings,
        "supports_fixed_recommendation": not logistics_related and plugin_confidence != "low",
    }
