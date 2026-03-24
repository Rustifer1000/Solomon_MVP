from __future__ import annotations

import json
from pathlib import Path

from runtime.policy_profiles import get_policy_profile, should_emit_continuity_packet, should_emit_risk_alert_brief
from runtime.plugins import get_plugin_runtime


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _package_element_label(state: dict, element_id: str) -> str:
    labels = state["meta"].get("package_element_labels") or {}
    if not labels:
        try:
            labels = get_plugin_runtime(state).package_element_labels()
        except (KeyError, NotImplementedError):
            labels = {}
    return labels.get(element_id, element_id.replace("_", " "))


def _participant_snapshots(case_bundle: dict) -> list[dict]:
    snapshots = []
    for participant_id, persona in sorted(case_bundle["personas"].items()):
        snapshots.append(
            {
                "participant_id": participant_id,
                "role_label": persona.get("role_label", participant_id),
                "public_goals": persona.get("public_goals", []),
                "interest_profile": persona.get("interest_profile", []),
                "starting_positions": persona.get("starting_positions", []),
            }
        )
    return snapshots


def build_case_intake_brief(state: dict, case_bundle: dict) -> dict:
    metadata = case_bundle["case_metadata"]
    return {
        "schema_version": "case_intake_brief.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "policy_profile": state["meta"]["policy_profile"],
        "plugin_type": state["meta"]["plugin_type"],
        "title": metadata["title"],
        "scenario_summary": metadata["scenario_summary"],
        "expected_mode_range": metadata.get("expected_mode_range", []),
        "intended_challenge_type": metadata.get("intended_challenge_type"),
        "participant_snapshots": _participant_snapshots(case_bundle),
    }


def render_case_intake_brief_text(brief: dict) -> str:
    lines = [
        "Case Intake Brief",
        f"Case: {brief['case_id']}",
        f"Session: {brief['session_id']}",
        f"Policy Profile: {brief['policy_profile']}",
        f"Plugin: {brief['plugin_type']}",
        "",
        f"Title: {brief['title']}",
        f"Scenario: {brief['scenario_summary']}",
    ]
    if brief["expected_mode_range"]:
        lines.append(f"Expected Mode Range: {', '.join(brief['expected_mode_range'])}")
    if brief.get("intended_challenge_type"):
        lines.append(f"Intended Challenge: {brief['intended_challenge_type']}")
    lines.append("")
    lines.append("Participants")
    for participant in brief["participant_snapshots"]:
        lines.append(f"- {participant['role_label']}:")
        goals = "; ".join(participant["public_goals"][:2])
        interests = "; ".join(participant["interest_profile"][:2])
        position = participant["starting_positions"][0] if participant["starting_positions"] else ""
        if goals:
            lines.append(f"  Goals: {goals}")
        if interests:
            lines.append(f"  Interests: {interests}")
        if position:
            lines.append(f"  Starting position: {position}")
    return "\n".join(lines) + "\n"


def _package_snapshot(state: dict) -> dict | None:
    packages = state.get("packages", [])
    if not packages:
        return None
    package = packages[-1]
    return {
        "family": package["family"],
        "status": package["status"],
        "summary": package["summary"],
        "elements": [_package_element_label(state, element) for element in package.get("elements", [])],
        "related_issues": package.get("related_issues", []),
    }


ESCALATION_FAMILY_MAP = {
    "E1": {
        "family": "safety_or_coercion",
        "recommended_human_role": "full_handoff",
        "handoff_focus": "protect participation safety and determine whether mediation can proceed at all",
    },
    "E2": {
        "family": "fairness_or_process_breakdown",
        "recommended_human_role": "co_handling",
        "handoff_focus": "restore fair participation and workable process control before substantive option work continues",
    },
    "E3": {
        "family": "explicit_human_involvement_request",
        "recommended_human_role": "human_review",
        "handoff_focus": "respond directly to the participant request for human involvement and preserve trust in the process",
    },
    "E4": {
        "family": "domain_complexity_review",
        "recommended_human_role": "human_review",
        "handoff_focus": "review issue coupling and determine whether bounded autonomous handling remains legitimate",
    },
    "E5": {
        "family": "decision_quality_caution",
        "recommended_human_role": "bounded_review_or_caution",
        "handoff_focus": "preserve missing information and feasibility gaps before stronger recommendations are made",
    },
    "E6": {
        "family": "role_boundary_pressure",
        "recommended_human_role": "human_review",
        "handoff_focus": "re-establish mediation role boundaries and prevent role drift",
    },
}


def _escalation_family_metadata(state: dict) -> dict:
    category = state["escalation"].get("category")
    base = ESCALATION_FAMILY_MAP.get(
        category,
        {
            "family": "none",
            "recommended_human_role": "none",
            "handoff_focus": "no special handoff focus is active",
        },
    )
    policy = state["meta"].get("support_artifact_policy") or {
        "descriptor_id": "support_artifact_default_v0",
        "review_focus": "generic",
    }
    return {
        "category_family": base["family"],
        "recommended_human_role": base["recommended_human_role"],
        "handoff_focus": base["handoff_focus"],
        "support_artifact_policy_descriptor": policy.get("descriptor_id", "support_artifact_default_v0"),
        "support_artifact_review_focus": policy.get("review_focus", "generic"),
    }


def build_early_dynamics_brief(state: dict) -> dict:
    positions = []
    for participant_id, participant in sorted(state["positions"].items()):
        if participant["current_positions"]:
            positions.append(
                {
                    "participant_id": participant_id,
                    "statement": participant["current_positions"][0]["statement"],
                }
            )
    return {
        "schema_version": "early_dynamics_brief.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "phase": state["phase"],
        "issues": list(state["summary_state"]["issues"]),
        "opening_positions": positions,
        "open_missing_info": [item["question"] for item in state["missing_info"] if item["status"] == "open"],
        "active_flags": [flag["title"] for flag in state["flags"]],
        "package_snapshot": _package_snapshot(state),
    }


def render_early_dynamics_brief_text(brief: dict) -> str:
    lines = [
        "Early Dynamics Brief",
        f"Case: {brief['case_id']}",
        f"Session: {brief['session_id']}",
        f"Phase Reached: {brief['phase']}",
        "",
        "Issues",
    ]
    for issue in brief["issues"]:
        lines.append(f"- {issue}")
    lines.append("")
    lines.append("Opening Positions")
    for position in brief["opening_positions"]:
        lines.append(f"- {position['participant_id']}: {position['statement']}")
    lines.append("")
    lines.append("Open Missing Information")
    if brief["open_missing_info"]:
        for item in brief["open_missing_info"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    if brief["active_flags"]:
        lines.append("")
        lines.append("Active Flags")
        for flag in brief["active_flags"]:
            lines.append(f"- {flag}")
    if brief["package_snapshot"] is not None:
        lines.append("")
        lines.append("Package Snapshot")
        lines.append(f"- Family: {brief['package_snapshot']['family']}")
        lines.append(f"- Status: {brief['package_snapshot']['status']}")
        lines.append(f"- Summary: {brief['package_snapshot']['summary']}")
    return "\n".join(lines) + "\n"


def build_risk_alert_brief(state: dict) -> dict:
    plugin_assessment = state.get("plugin_assessment", {})
    escalation_meta = _escalation_family_metadata(state)
    return {
        "schema_version": "risk_alert_brief.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "mode": state["escalation"]["mode"],
        "category": state["escalation"]["category"],
        "category_family": escalation_meta["category_family"],
        "recommended_human_role": escalation_meta["recommended_human_role"],
        "handoff_focus": escalation_meta["handoff_focus"],
        "support_artifact_policy_descriptor": escalation_meta["support_artifact_policy_descriptor"],
        "rationale": state["escalation"]["rationale"],
        "active_flags": [
            {
                "flag_type": flag["flag_type"],
                "title": flag["title"],
                "severity": flag["severity"],
            }
            for flag in state["flags"]
        ],
        "plugin_warnings": plugin_assessment.get("warnings", []),
    }


def render_risk_alert_brief_text(brief: dict) -> str:
    lines = [
        "Risk Alert Brief",
        f"Case: {brief['case_id']}",
        f"Session: {brief['session_id']}",
        f"Mode: {brief['mode']}",
        f"Category: {brief['category'] or 'none'}",
        f"Escalation Family: {brief['category_family']}",
        f"Recommended Human Role: {brief['recommended_human_role']}",
        f"Handoff Focus: {brief['handoff_focus']}",
        f"Rationale: {brief['rationale']}",
        "",
        "Active Flags",
    ]
    if brief["active_flags"]:
        for flag in brief["active_flags"]:
            lines.append(f"- {flag['title']} ({flag['flag_type']}, severity {flag['severity']})")
    else:
        lines.append("- None")
    if brief["plugin_warnings"]:
        lines.append("")
        lines.append("Plugin Warnings")
        for warning in brief["plugin_warnings"]:
            lines.append(f"- {warning}")
    return "\n".join(lines) + "\n"


def build_continuity_packet(state: dict, case_bundle: dict) -> dict:
    plugin_assessment = state.get("plugin_assessment", {})
    recent_turns = state["trace_buffer"][-3:]
    escalation_meta = _escalation_family_metadata(state)
    return {
        "schema_version": "continuity_packet.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "plugin_type": state["meta"]["plugin_type"],
        "support_artifact_policy_descriptor": escalation_meta["support_artifact_policy_descriptor"],
        "support_artifact_review_focus": escalation_meta["support_artifact_review_focus"],
        "category_family": escalation_meta["category_family"],
        "recommended_human_role": escalation_meta["recommended_human_role"],
        "handoff_focus": escalation_meta["handoff_focus"],
        "escalation": dict(state["escalation"]),
        "summary_state": dict(state["summary_state"]),
        "issues": list(state["summary_state"]["issues"]),
        "open_missing_info": [item for item in state["missing_info"] if item["status"] == "open"],
        "active_flags": list(state["flags"]),
        "package_snapshot": _package_snapshot(state),
        "plugin_assessment": {
            "plugin_confidence": plugin_assessment.get("plugin_confidence"),
            "supports_fixed_recommendation": plugin_assessment.get("supports_fixed_recommendation"),
            "warnings": plugin_assessment.get("warnings", []),
        },
        "recent_turn_summaries": [
            {
                "turn_index": turn["turn_index"],
                "role": turn["role"],
                "phase": turn["phase"],
                "message_summary": turn["message_summary"],
            }
            for turn in recent_turns
        ],
        "case_title": case_bundle["case_metadata"]["title"],
    }


def render_continuity_packet_text(packet: dict) -> str:
    lines = [
        "Continuity Packet",
        f"Case: {packet['case_id']}",
        f"Session: {packet['session_id']}",
        f"Escalation Mode: {packet['escalation']['mode']}",
        f"Escalation Category: {packet['escalation']['category'] or 'none'}",
        f"Escalation Family: {packet['category_family']}",
        f"Recommended Human Role: {packet['recommended_human_role']}",
        f"Handoff Focus: {packet['handoff_focus']}",
        f"Rationale: {packet['escalation']['rationale']}",
        "",
        "Issues",
    ]
    for issue in packet["issues"]:
        lines.append(f"- {issue}")
    lines.append("")
    lines.append("Open Missing Information")
    if packet["open_missing_info"]:
        for item in packet["open_missing_info"]:
            lines.append(f"- {item['question']}")
    else:
        lines.append("- None")
    if packet["plugin_assessment"]["warnings"]:
        lines.append("")
        lines.append("Plugin Warnings")
        for warning in packet["plugin_assessment"]["warnings"]:
            lines.append(f"- {warning}")
    if packet["recent_turn_summaries"]:
        lines.append("")
        lines.append("Recent Turn Summaries")
        for turn in packet["recent_turn_summaries"]:
            lines.append(f"- T{turn['turn_index']} {turn['role']}: {turn['message_summary']}")
    return "\n".join(lines) + "\n"


def write_support_artifacts(output_dir: Path, state: dict, case_bundle: dict) -> None:
    profile = get_policy_profile(state["meta"]["policy_profile"])
    if not profile.allow_briefs and not should_emit_continuity_packet(state, profile):
        return

    if profile.allow_briefs:
        intake = build_case_intake_brief(state, case_bundle)
        _write_json(output_dir / "briefs" / "case_intake_brief.json", intake)
        (output_dir / "briefs" / "case_intake_brief.txt").write_text(
            render_case_intake_brief_text(intake),
            encoding="utf-8",
        )

        early = build_early_dynamics_brief(state)
        _write_json(output_dir / "briefs" / "early_dynamics_brief.json", early)
        (output_dir / "briefs" / "early_dynamics_brief.txt").write_text(
            render_early_dynamics_brief_text(early),
            encoding="utf-8",
        )

        if should_emit_risk_alert_brief(state):
            risk = build_risk_alert_brief(state)
            _write_json(output_dir / "briefs" / "risk_alert_brief.json", risk)
            (output_dir / "briefs" / "risk_alert_brief.txt").write_text(
                render_risk_alert_brief_text(risk),
                encoding="utf-8",
            )

    if should_emit_continuity_packet(state, profile):
        packet = build_continuity_packet(state, case_bundle)
        _write_json(output_dir / "continuity" / "continuity_packet.json", packet)
        (output_dir / "continuity" / "continuity_packet.txt").write_text(
            render_continuity_packet_text(packet),
            encoding="utf-8",
        )
