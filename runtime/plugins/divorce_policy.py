from __future__ import annotations

from runtime.plugins.divorce_shared import PACKAGE_ELEMENT_LABELS


DEFAULT_DIVORCE_POLICY = {
    "descriptor_id": "divorce_default_policy_v0",
    "logistics_driven_caution": True,
    "fairness_warning": False,
    "flag_related_issues": ["parenting_schedule"],
}


def normalize_policy_descriptor(policy_descriptor: dict | None) -> dict:
    if policy_descriptor is None:
        return dict(DEFAULT_DIVORCE_POLICY)
    return {
        "descriptor_id": policy_descriptor.get("descriptor_id", DEFAULT_DIVORCE_POLICY["descriptor_id"]),
        "logistics_driven_caution": policy_descriptor.get(
            "logistics_driven_caution",
            DEFAULT_DIVORCE_POLICY["logistics_driven_caution"],
        ),
        "fairness_warning": policy_descriptor.get(
            "fairness_warning",
            DEFAULT_DIVORCE_POLICY["fairness_warning"],
        ),
        "flag_related_issues": list(
            policy_descriptor.get("flag_related_issues", DEFAULT_DIVORCE_POLICY["flag_related_issues"])
        ),
    }


def apply_case_policy(policy_descriptor: dict | None, base_assessment: dict) -> dict:
    policy = normalize_policy_descriptor(policy_descriptor)
    active_flag_types = set(base_assessment["active_flag_types"])
    needs_logistics_clarification = base_assessment["needs_logistics_clarification"]
    option_posture = base_assessment["option_posture"]
    issue_labels = set(base_assessment["issue_labels"])
    issue_families = base_assessment.get("issue_families", {})
    package_family = base_assessment.get("package_family", "none")
    package_summary = base_assessment.get("package_summary")
    package_missing_elements = list(base_assessment.get("package_missing_elements", []))
    package_quality = base_assessment.get("package_quality", "none")
    mixed_package_state = base_assessment.get("mixed_package_state", False)
    competing_package_families = list(base_assessment.get("competing_package_families", []))

    plugin_confidence = "moderate"
    warnings: list[str] = []

    if policy["logistics_driven_caution"]:
        if "plugin_low_confidence" in active_flag_types and needs_logistics_clarification:
            plugin_confidence = "low"
        elif needs_logistics_clarification and option_posture in {"bounded_only", "qualified", "optioning_active"}:
            plugin_confidence = "low"
        elif needs_logistics_clarification:
            plugin_confidence = "moderate"

        if needs_logistics_clarification:
            warnings.append("Plugin confidence remains limited because logistics feasibility is still not fully clarified.")
        if option_posture in {"bounded_only", "qualified"} and needs_logistics_clarification:
            warnings.append("Option work should remain qualified until logistics questions and uncertain feasibility facts are resolved.")
    else:
        if (
            package_family in {"written_notice_package", "communication_package", "reimbursement_package"}
            and option_posture == "optioning_active"
            and package_quality == "complete"
            and not mixed_package_state
        ):
            plugin_confidence = "high"
        elif (
            package_family in {"written_notice_package", "communication_package", "reimbursement_package"}
            and option_posture == "optioning_active"
            and (package_quality == "partial" or mixed_package_state)
        ):
            plugin_confidence = "moderate"
        if "decision_quality_risk" in active_flag_types and option_posture in {"bounded_only", "qualified"}:
            plugin_confidence = "moderate"
        if mixed_package_state and competing_package_families:
            labels = ", ".join(family.replace("_", " ") for family in competing_package_families)
            warnings.append(f"Multiple active package families are present and should be resolved into one coherent bounded direction: {labels}.")
        if package_quality == "partial" and package_missing_elements:
            missing = ", ".join(PACKAGE_ELEMENT_LABELS.get(item, item) for item in package_missing_elements)
            warnings.append(f"The current bounded package is still missing explicit elements: {missing}.")
        if issue_families.get("has_process") and package_family == "communication_package":
            warnings.append("The process package should remain mutual and workable rather than becoming one-sided procedural control.")
        if issue_families.get("has_expense") and package_family == "reimbursement_package":
            warnings.append("Expense coordination should stay fair and documented without turning into retroactive blame or unilateral veto power.")

    if (
        policy["fairness_warning"]
        and "fairness and meaningful parenting role" in issue_labels
        and "parenting schedule" in issue_labels
    ):
        warnings.append("Parent-role fairness concerns should be handled alongside schedule feasibility rather than treated as a substitute for it.")

    supports_fixed_recommendation = not needs_logistics_clarification and plugin_confidence != "low"

    return {
        **base_assessment,
        "plugin_confidence": plugin_confidence,
        "supports_fixed_recommendation": supports_fixed_recommendation,
        "warnings": warnings,
        "package_summary": package_summary,
        "package_quality": package_quality,
        "package_missing_elements": package_missing_elements,
        "mixed_package_state": mixed_package_state,
        "competing_package_families": competing_package_families,
        "policy_descriptor_id": policy["descriptor_id"],
        "policy_flag_related_issues": policy["flag_related_issues"],
    }


def build_case_flag_templates(policy_descriptor: dict | None, state: dict, turn) -> list[dict]:
    policy = normalize_policy_descriptor(policy_descriptor)
    case_id = state["meta"]["case_id"]
    turn_index = turn.turn_index
    signal_set = set(turn.risk_check.signals)
    related_issues = policy["flag_related_issues"]
    flag_templates: list[dict] = []

    if "insufficient_information" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-001",
                "flag_type": "insufficient_information",
                "severity": 3,
                "source": "platform",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E5"],
                "threshold_band": "T1",
                "title": "Material feasibility gaps remain unresolved",
                "note": "Open feasibility questions still materially limit stronger option claims.",
                "signal_classes": ["insufficient_information", "feasibility_gap"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    if "decision_quality_risk" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-002",
                "flag_type": "decision_quality_risk",
                "severity": 2,
                "source": "plugin",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E5"],
                "threshold_band": "T1",
                "title": "Option qualification remains incomplete",
                "note": "The current option posture is ahead of full domain qualification.",
                "signal_classes": ["decision_quality_risk", "domain_complexity_warning"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    if "plugin_low_confidence" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-003",
                "flag_type": "plugin_low_confidence",
                "severity": 2,
                "source": "plugin",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E5"],
                "threshold_band": "T1",
                "title": "Plugin supports caution but not stronger feasibility claims",
                "note": "The domain layer supports bounded exploration, but not a stronger confidence claim yet.",
                "signal_classes": ["plugin_low_confidence"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    if "fairness_breakdown" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-fairness",
                "flag_type": "fairness_breakdown",
                "severity": 3,
                "source": "platform",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E2"],
                "threshold_band": "T2",
                "title": "Participation fairness appears compromised",
                "note": "The current turn suggests one-sidedness, unfair pressure, or meaningful participation imbalance.",
                "signal_classes": ["fairness_breakdown"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    if "repeated_process_breakdown" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-process-breakdown",
                "flag_type": "repeated_process_breakdown",
                "severity": 3,
                "source": "platform",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E2"],
                "threshold_band": "T2",
                "title": "Repeated process breakdown remains active",
                "note": "The turn suggests repair attempts are not restoring workable participation.",
                "signal_classes": ["repeated_process_breakdown"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    if "explicit_human_request" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-human-request",
                "flag_type": "explicit_human_request",
                "severity": 3,
                "source": "participant",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E3"],
                "threshold_band": "T2",
                "title": "A party requested human involvement",
                "note": "The run should preserve a clear human-review path when a party explicitly requests it.",
                "signal_classes": ["explicit_human_request"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    if "domain_complexity_overload" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-domain-complexity",
                "flag_type": "domain_complexity_overload",
                "severity": 2,
                "source": "plugin",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E4"],
                "threshold_band": "T2",
                "title": "Domain complexity is exceeding the bounded autonomous path",
                "note": "Issue coupling or process interdependence may require live human review.",
                "signal_classes": ["domain_complexity_overload"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    if "role_boundary_pressure" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-role-boundary",
                "flag_type": "role_boundary_pressure",
                "severity": 2,
                "source": "platform",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E6"],
                "threshold_band": "T2",
                "title": "Role-boundary pressure is active",
                "note": "The interaction is pressing beyond the mediation role and should not be handled as ordinary clarification.",
                "signal_classes": ["role_boundary_pressure"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    if "coercion_or_intimidation" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-coercion",
                "flag_type": "coercion_or_intimidation",
                "severity": 4,
                "source": "platform",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E1"],
                "threshold_band": "T3",
                "title": "Participation appears constrained by coercive or intimidating pressure",
                "note": "The interaction suggests compromised voluntariness or meaningful fear-based participation limits.",
                "signal_classes": ["coercion_or_intimidation"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    if "acute_safety_concern" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-safety",
                "flag_type": "acute_safety_concern",
                "severity": 5,
                "source": "platform",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E1"],
                "threshold_band": "T3",
                "title": "A serious safety or voluntariness concern is active",
                "note": "The interaction suggests autonomous continuation may be unsafe or illegitimate.",
                "signal_classes": ["acute_safety_concern"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    if "participation_incapacity" in signal_set:
        flag_templates.append(
            {
                "flag_id": f"{case_id.lower()}-flag-capacity",
                "flag_type": "participation_incapacity",
                "severity": 4,
                "source": "platform",
                "first_detected_turn": turn_index,
                "last_updated_turn": turn_index,
                "related_categories": ["E1"],
                "threshold_band": "T3",
                "title": "Meaningful participation appears unstable or impaired",
                "note": "The interaction suggests the session may no longer support informed, stable participation.",
                "signal_classes": ["participation_incapacity"],
                "related_issues": related_issues,
                "source_turns": [turn_index],
            }
        )
    return flag_templates
