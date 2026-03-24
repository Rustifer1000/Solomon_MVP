from __future__ import annotations

import json
from pathlib import Path

from runtime.policy_profiles import validate_runtime_artifact_set
from runtime.plugins import get_plugin_runtime
from runtime.session_validation import validate_support_artifact_package
from runtime.support_artifacts import write_support_artifacts


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _source_metadata(source: str, case_id: str, plugin_type: str) -> dict:
    case_slug = case_id.lower().replace("-", "_")
    plugin_slug = plugin_type.lower().replace("-", "_")
    if source == "reference":
        return {
            "model_config": {
                "provider": "authored_reference_turns",
                "model_name": None,
                "temperature": None,
                "other_decoding_settings": {},
            },
            "prompting": {
                "prompt_version": None,
                "prompt_ids": [],
            },
            "randomization": {
                "seed": None,
                "determinism_note": "This run replays authored reference turns for benchmark comparison.",
            },
        }
    if source == "mock_model":
        return {
            "model_config": {
                "provider": "mock_model_scaffold",
                "model_name": f"{case_slug}_mock_model_v0",
                "temperature": 0,
                "other_decoding_settings": {},
            },
            "prompting": {
                "prompt_version": "mock_model_scaffold_v0",
                "prompt_ids": [
                    "solomon_core_mock_v0",
                    f"{plugin_slug}_plugin_mock_v0",
                    f"{case_slug}_case_mock_v0",
                ],
            },
            "randomization": {
                "seed": None,
                "determinism_note": "This run uses a deterministic mock-model scaffold with authored variations.",
            },
        }
    if source == "varied_mock_model":
        return {
            "model_config": {
                "provider": "varied_mock_model_scaffold",
                "model_name": f"{case_slug}_varied_mock_model_v0",
                "temperature": 0,
                "other_decoding_settings": {"variation_mode": "stable_hash_selection"},
            },
            "prompting": {
                "prompt_version": "varied_mock_model_scaffold_v0",
                "prompt_ids": [
                    "solomon_core_mock_v0",
                    f"{plugin_slug}_plugin_mock_v0",
                    f"{case_slug}_case_varied_mock_v0",
                ],
            },
            "randomization": {
                "seed": "stable_hash_from_generated_at",
                "determinism_note": "This run uses stable hash-based variation over mock-model scaffold outputs.",
            },
        }
    return {
        "model_config": {
            "provider": "runtime_generated_scaffold",
            "model_name": f"{case_slug}_runtime_generator_v0",
            "temperature": 0,
            "other_decoding_settings": {"process_variant": "source-aware"},
        },
        "prompting": {
            "prompt_version": "runtime_generator_scaffold_v0",
            "prompt_ids": [
                "solomon_runtime_core_v0",
                f"{plugin_slug}_plugin_runtime_v0",
                f"{case_slug}_runtime_simulation_v0",
            ],
        },
        "randomization": {
            "seed": "stable_hash_from_generated_at",
            "determinism_note": "This run is generated through the runtime turn loop with deterministic source-aware simulation helpers.",
        },
    }


DEFAULT_ARTIFACT_NARRATIVE_POLICY = {
    "descriptor_id": "artifact_narrative_default_v0",
    "posture_style": "state_driven",
    "missing_info_emphasis": "state_driven",
}


def _narrative_policy(state: dict) -> dict:
    policy = state["meta"].get("artifact_narrative_policy")
    if policy is None:
        return dict(DEFAULT_ARTIFACT_NARRATIVE_POLICY)
    return {
        "descriptor_id": policy.get("descriptor_id", DEFAULT_ARTIFACT_NARRATIVE_POLICY["descriptor_id"]),
        "posture_style": policy.get("posture_style", DEFAULT_ARTIFACT_NARRATIVE_POLICY["posture_style"]),
        "missing_info_emphasis": policy.get(
            "missing_info_emphasis",
            DEFAULT_ARTIFACT_NARRATIVE_POLICY["missing_info_emphasis"],
        ),
    }


def _package_element_labels(state: dict) -> dict[str, str]:
    labels = state["meta"].get("package_element_labels") or {}
    if labels:
        return dict(labels)
    try:
        return get_plugin_runtime(state).package_element_labels()
    except (KeyError, NotImplementedError):
        return {}


def _package_element_label(state: dict, element_id: str) -> str:
    return _package_element_labels(state).get(element_id, element_id.replace("_", " "))


def build_run_meta(state: dict, generated_at: str) -> dict:
    case_id = state["meta"]["case_id"]
    plugin_type = state["meta"]["plugin_type"]
    source = state["meta"].get("source", "reference")
    source_metadata = _source_metadata(source, case_id, plugin_type)
    return {
        "schema_version": "run_meta.v0",
        "case_id": case_id,
        "session_id": state["meta"]["session_id"],
        "timestamp": generated_at,
        "session_type": "benchmark_runtime_scaffold",
        "policy_profile": state["meta"]["policy_profile"],
        "runtime": {
            "environment": "local_scaffold",
            "code_version": "runtime-scaffold-v0",
            "git_commit_hash": None,
        },
        "model_config": source_metadata["model_config"],
        "prompting": source_metadata["prompting"],
        "randomization": source_metadata["randomization"],
        "case_context": {
            "plugin_type": state["meta"]["plugin_type"],
            "source": source,
            "process_variant": state["meta"].get("process_variant"),
            "benchmark_descriptor": state["meta"].get("benchmark_descriptor"),
            "artifact_narrative_policy": state["meta"].get("artifact_narrative_policy"),
            "support_artifact_policy": state["meta"].get("support_artifact_policy"),
            "package_element_labels": state["meta"].get("package_element_labels"),
            "evaluator_helper_policy": state["meta"].get("evaluator_helper_policy"),
            "participant_context": state["participants"],
        },
    }


def build_interaction_trace(state: dict, generated_at: str) -> dict:
    return {
        "schema_version": "interaction_trace.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "policy_profile": state["meta"]["policy_profile"],
        "trace_created_at": generated_at,
        "turns": state["trace_buffer"],
    }


def _position_note(state: dict) -> str:
    proposal_count = sum(len(participant["proposals"]) for participant in state["positions"].values())
    if proposal_count:
        return "The session ended with distinct starting positions preserved and at least one bounded proposal or package still open for further discussion."
    return "The session ended with distinct starting positions preserved and no supported option movement yet."


def build_positions(state: dict) -> dict:
    return {
        "schema_version": "positions.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "participants": list(state["positions"].values()),
        "position_notes": _position_note(state),
    }


def _facts_note(state: dict) -> str:
    uncertain_count = sum(1 for fact in state["facts"] if fact["status"] == "uncertain")
    disputed_count = sum(1 for fact in state["facts"] if fact["status"] == "disputed")
    if uncertain_count and disputed_count:
        return "Uncertain feasibility items and disputed constraints remain visible rather than being promoted to settled conclusions."
    if uncertain_count:
        return "Uncertain feasibility items remain explicit rather than being promoted to settled conclusions."
    return "Facts remain separated from unresolved feasibility questions."


def build_facts_snapshot(state: dict) -> dict:
    return {
        "schema_version": "facts_snapshot.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "facts": state["facts"],
        "facts_notes": _facts_note(state),
    }


def _flag_notes(state: dict) -> str:
    active_types = {flag["flag_type"] for flag in state["flags"]}
    narrative_policy = _narrative_policy(state)
    if "plugin_low_confidence" in active_types and "insufficient_information" in active_types:
        return "The session remained workable, but plugin confidence and unresolved information jointly narrowed the run into a caution posture."
    if "insufficient_information" in active_types:
        return "The session remained workable, but unresolved information narrowed the run into a caution posture."
    if narrative_policy["posture_style"] == "workable_package":
        return "No caution-relevant flags remained active at close."
    return "No caution-relevant flags remained active at close."


def build_flags(state: dict) -> dict:
    return {
        "schema_version": "flags.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "active_flags": state["flags"],
        "cleared_flags": [],
        "historical_flags": [],
        "flag_notes": _flag_notes(state),
    }


def _missing_info_note(state: dict) -> str:
    open_count = len([item for item in state["missing_info"] if item["status"] == "open"])
    escalation_mode = state["escalation"]["mode"]
    narrative_policy = _narrative_policy(state)
    if open_count >= 2:
        if narrative_policy["missing_info_emphasis"] == "caution" or escalation_mode == "M1":
            return "The unresolved items remain explicit enough to justify continued caution."
        return "Multiple unresolved items remain visible and should continue to shape the next session's focus."
    if open_count == 1:
        if narrative_policy["missing_info_emphasis"] == "caution" or escalation_mode == "M1":
            return "A remaining unresolved item still justifies a bounded caution posture."
        return "One unresolved item remains visible and should be carried forward explicitly."
    return "No unresolved missing-information items remained at close."


def build_missing_info(state: dict) -> dict:
    return {
        "schema_version": "missing_info.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "missing_items": state["missing_info"],
        "missing_info_notes": _missing_info_note(state),
    }


def _summary_positions(state: dict) -> list[str]:
    lines: list[str] = []
    for participant_id, participant in sorted(state["positions"].items()):
        label = "Parent A" if participant_id == "spouse_A" else "Parent B"
        if participant["current_positions"]:
            lines.append(f"- {label}: {participant['current_positions'][0]['statement']}")
    if any(participant["proposals"] for participant in state["positions"].values()):
        lines.append("- At least one bounded proposal or package remained open for further discussion.")
    package_summary = state.get("plugin_assessment", {}).get("package_summary")
    if package_summary:
        lines.append(f"- The leading bounded package focused on {package_summary}.")
    return lines


def _package_detail_lines(state: dict) -> list[str]:
    packages = state.get("packages", [])
    if not packages:
        return []

    package = packages[-1]
    family_label = package["family"].replace("_", " ")
    lines = [
        f"- Family: {family_label}",
        f"- Status: {package['status']}",
        f"- Summary: {package['summary']}",
    ]
    if package.get("related_issues"):
        related = ", ".join(issue.replace("_", " ") for issue in package["related_issues"])
        lines.append(f"- Related issues: {related}")
    if package.get("elements"):
        element_labels = [_package_element_label(state, element) for element in package["elements"]]
        lines.append(f"- Elements: {', '.join(element_labels)}")
    plugin_assessment = state.get("plugin_assessment", {})
    if plugin_assessment.get("package_quality") and plugin_assessment.get("package_quality") != "none":
        lines.append(f"- Package quality: {plugin_assessment['package_quality']}")
    if plugin_assessment.get("mixed_package_state") and plugin_assessment.get("competing_package_families"):
        competing = ", ".join(
            family.replace("_", " ") for family in plugin_assessment["competing_package_families"]
        )
        lines.append(f"- Competing package families: {competing}")
    if plugin_assessment.get("package_quality") == "partial" and plugin_assessment.get("package_missing_elements"):
        missing_labels = [_package_element_label(state, element) for element in plugin_assessment["package_missing_elements"]]
        lines.append(f"- Still missing: {', '.join(missing_labels)}")
    return lines


def _summary_facts(state: dict) -> list[str]:
    lines: list[str] = []
    accepted = [fact for fact in state["facts"] if fact["status"] == "accepted"]
    uncertain = [fact for fact in state["facts"] if fact["status"] == "uncertain"]
    disputed = [fact for fact in state["facts"] if fact["status"] == "disputed"]
    for fact in accepted[:3]:
        lines.append(f"- Accepted: {fact['statement']}")
    for fact in uncertain[:2]:
        lines.append(f"- Unresolved: {fact['statement']}")
    for fact in disputed[:2]:
        lines.append(f"- Disputed: {fact['statement']}")
    return lines


def _summary_flags(state: dict) -> list[str]:
    lines = []
    for flag in state["flags"][:3]:
        lines.append(f"- {flag['title']}.")
    if not lines:
        lines.append("- No caution-relevant flags remained active at close.")
    return lines


def _summary_missing_items(state: dict) -> list[str]:
    return [f"- {item['question']}" for item in state["missing_info"] if item["status"] == "open"]


def _summary_intro(state: dict) -> str:
    issue_bits = [issue.lower() for issue in state["summary_state"]["issues"][:2]]
    issue_phrase = " and ".join(issue_bits) if issue_bits else "the key dispute"
    plugin_assessment = state.get("plugin_assessment", {})
    narrative_policy = _narrative_policy(state)
    posture_style = narrative_policy["posture_style"]
    if posture_style == "caution_bounded":
        posture = "It kept the process bounded, preserved uncertainty explicitly, and avoided presenting a fixed recommendation."
    elif posture_style == "workable_package":
        posture = "It kept the process bounded, surfaced a workable package for discussion, and avoided overstating agreement."
    elif state["escalation"]["mode"] == "M1" or not plugin_assessment.get("supports_fixed_recommendation", True):
        posture = "It kept the process bounded, preserved uncertainty explicitly, and avoided presenting a fixed recommendation."
    elif state["options"]:
        posture = "It kept the process bounded, surfaced a workable package for discussion, and avoided overstating agreement."
    else:
        posture = "It kept the process bounded, clarified the dispute, and preserved the areas that still required further work."
    return (
        "Solomon framed the matter as a dispute involving "
        f"{issue_phrase}. {posture}"
    )


def _escalation_lines(state: dict) -> list[str]:
    plugin_assessment = state.get("plugin_assessment", {})
    lines = [f"- `{state['escalation']['mode']}` with category `{state['escalation']['category'] or 'none'}`."]
    lines.append(f"- {state['escalation']['rationale']}")
    for warning in plugin_assessment.get("warnings", [])[:3]:
        lines.append(f"- {warning}")
    return lines


def build_summary(state: dict) -> str:
    issues = "\n".join(f"- {issue}" for issue in state["summary_state"]["issues"])
    source = state["meta"].get("source", "reference")
    process_variant = state["meta"].get("process_variant")
    process_line = f"Process Variant: {process_variant}\n" if process_variant else ""
    participant_lines = "\n".join(_summary_positions(state))
    package_lines = "\n".join(_package_detail_lines(state))
    fact_lines = "\n".join(_summary_facts(state))
    flag_lines = "\n".join(_summary_flags(state))
    missing_lines = "\n".join(_summary_missing_items(state))
    escalation_lines = "\n".join(_escalation_lines(state))
    package_section = ""
    if package_lines:
        package_section = "Bounded Package Detail\n" f"{package_lines}\n\n"

    return (
        "Session Summary\n"
        f"Run Source: {source}\n"
        f"{process_line}"
        f"{_summary_intro(state)}\n\n"
        "Issues Identified\n"
        f"{issues}\n\n"
        "Participant Positions\n"
        f"{participant_lines}\n\n"
        f"{package_section}"
        "Facts and Uncertainties\n"
        f"{fact_lines}\n\n"
        "Active Flags / Concerns\n"
        f"{flag_lines}\n\n"
        "Missing Information\n"
        f"{missing_lines}\n\n"
        "Current Escalation Posture\n"
        f"{escalation_lines}\n\n"
        "Recommended Next Step\n"
        f"{state['summary_state']['next_step']}\n"
    )


def write_artifacts(output_dir: Path, state: dict, generated_at: str, case_bundle: dict | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "run_meta.json", build_run_meta(state, generated_at))
    _write_json(output_dir / "interaction_trace.json", build_interaction_trace(state, generated_at))
    _write_json(output_dir / "positions.json", build_positions(state))
    _write_json(output_dir / "facts_snapshot.json", build_facts_snapshot(state))
    _write_json(output_dir / "flags.json", build_flags(state))
    _write_json(output_dir / "missing_info.json", build_missing_info(state))
    (output_dir / "summary.txt").write_text(build_summary(state), encoding="utf-8")
    if case_bundle is not None:
        write_support_artifacts(output_dir, state, case_bundle)
    validation_errors = validate_runtime_artifact_set(output_dir, state)
    if validation_errors:
        raise ValueError("; ".join(validation_errors))
    validate_support_artifact_package(output_dir, state)
