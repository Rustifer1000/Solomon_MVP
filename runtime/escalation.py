from __future__ import annotations


def determine_escalation(state: dict, plugin_assessment: dict | None = None) -> dict:
    plugin_assessment = plugin_assessment or {}
    unresolved_count = len([item for item in state["missing_info"] if item["status"] == "open"])
    option_count = len(state["options"])
    plugin_confidence = plugin_assessment.get("plugin_confidence", "moderate")

    if unresolved_count >= 2 and option_count >= 1:
        rationale = "Continue with caution because unresolved logistics still constrain responsible option exploration."
        if plugin_confidence == "low":
            rationale = "Continue with caution because plugin confidence remains limited while logistics are unresolved."
        return {
            "category": "E5",
            "threshold_band": "T1",
            "mode": "M1",
            "rationale": rationale,
        }

    return {
        "category": None,
        "threshold_band": "T0",
        "mode": "M0",
        "rationale": "No threshold-relevant caution state has been reached yet.",
    }
