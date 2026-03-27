from __future__ import annotations


def determine_escalation(state: dict, plugin_assessment: dict | None = None) -> dict:
    plugin_assessment = plugin_assessment or {}
    active_flag_types = set(plugin_assessment.get("active_flag_types", [])) | {
        flag["flag_type"] for flag in state.get("flags", [])
    }
    plugin_confidence = plugin_assessment.get("plugin_confidence", "moderate")
    option_posture = plugin_assessment.get("option_posture", "none")
    needs_logistics_clarification = plugin_assessment.get("needs_logistics_clarification", False)
    logistics_missing = plugin_assessment.get("logistics_related_missing_info", [])
    uncertain_logistics = plugin_assessment.get("uncertain_logistics_facts", [])

    if "irrecoverable_breakdown" in active_flag_types:
        return {
            "category": "E1",
            "threshold_band": "T4",
            "mode": "M5",
            "rationale": (
                "Mediation must stop immediately and redirect because the process has reached an irrecoverable "
                "breakdown condition. Continued handling — including preparation for handoff — is not appropriate. "
                "The session should be stopped and the parties redirected to appropriate resources."
            ),
        }

    if "acute_safety_concern" in active_flag_types or "coercion_or_intimidation" in active_flag_types:
        return {
            "category": "E1",
            "threshold_band": "T3",
            "mode": "M4",
            "rationale": "Full handoff is required because autonomous continuation is no longer safe and the state includes a serious safety or coercion concern.",
        }

    if "participation_incapacity" in active_flag_types:
        return {
            "category": "E1",
            "threshold_band": "T3",
            "mode": "M4",
            "rationale": "Full handoff is required because autonomous continuation is no longer reliable and participation capacity appears too compromised for continued handling.",
        }

    if "fairness_breakdown" in active_flag_types or "repeated_process_breakdown" in active_flag_types:
        return {
            "category": "E2",
            "threshold_band": "T2",
            "mode": "M3",
            "rationale": "Co-handling is required because the state reflects a fairness or repeated-process breakdown that needs live human mediation support.",
        }

    if "explicit_human_request" in active_flag_types:
        return {
            "category": "E3",
            "threshold_band": "T2",
            "mode": "M2",
            "rationale": "Human review is required because one or more parties explicitly requested human involvement.",
        }

    if "domain_complexity_overload" in active_flag_types:
        return {
            "category": "E4",
            "threshold_band": "T2",
            "mode": "M2",
            "rationale": "Human review is required because the domain layer indicates complexity beyond a clean bounded autonomous path.",
        }

    if "role_boundary_pressure" in active_flag_types:
        return {
            "category": "E6",
            "threshold_band": "T2",
            "mode": "M2",
            "rationale": "Human review is required because the session is pressing against mediation role boundaries.",
        }

    caution_reasons: list[str] = []
    if "insufficient_information" in active_flag_types or logistics_missing:
        caution_reasons.append("material logistics information remains unresolved")
    if "decision_quality_risk" in active_flag_types or option_posture in {"bounded_only", "qualified"}:
        caution_reasons.append("option work is ahead of full feasibility confirmation")
    if "plugin_low_confidence" in active_flag_types or plugin_confidence == "low":
        caution_reasons.append("plugin confidence remains limited")
    if uncertain_logistics:
        caution_reasons.append("uncertain feasibility facts remain active in the state")

    if caution_reasons and (needs_logistics_clarification or option_posture != "none" or plugin_confidence in {"low", "moderate"}):
        rationale = "Continue with caution because " + ", ".join(dict.fromkeys(caution_reasons)) + "."
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
