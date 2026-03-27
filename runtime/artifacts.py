from __future__ import annotations

import json
import subprocess
from pathlib import Path

from runtime.policy_profiles import get_policy_profile, validate_runtime_artifact_set
from runtime.plugins import get_plugin_runtime
from runtime.redaction import redact_json_values, redact_text
from runtime.reviewer_transcript_rendering import build_rendered_reviewer_transcript
from runtime.session_validation import validate_support_artifact_package
from runtime.support_artifacts import write_support_artifacts


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _resolve_git_commit_hash() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip() or None
    except Exception:
        return None


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


def build_session_meta(state: dict, generated_at: str) -> dict:
    """Build the stable session identity card written once per session folder.

    Contains only fields that are constant across all runs of a given session.
    Per-run details (git hash, model config, policy profile, timestamps) live in
    run_meta.json.
    """
    return {
        "schema_version": "session_meta.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "plugin_type": state["meta"]["plugin_type"],
        "title": state["meta"].get("title"),
        "scenario_summary": state["meta"].get("scenario_summary"),
        "source": state["meta"].get("source", "reference"),
        "created_at": generated_at,
    }


def build_run_meta(state: dict, generated_at: str) -> dict:
    case_id = state["meta"]["case_id"]
    plugin_type = state["meta"]["plugin_type"]
    source = state["meta"].get("source", "reference")
    source_metadata = _source_metadata(source, case_id, plugin_type)
    # If an explicit seed was supplied (e.g. via --seed CLI flag), override the
    # source-metadata default so the run is reproducible from that seed alone.
    explicit_seed = state["meta"].get("seed")
    randomization = dict(source_metadata["randomization"])
    if explicit_seed is not None:
        randomization["seed"] = explicit_seed
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
            "git_commit_hash": _resolve_git_commit_hash(),
        },
        "model_config": source_metadata["model_config"],
        "prompting": source_metadata["prompting"],
        "randomization": randomization,
        "redaction_applied": get_policy_profile(state["meta"]["policy_profile"]).require_redaction,
        "case_context": {
            "plugin_type": state["meta"]["plugin_type"],
            "source": source,
            "process_variant": state["meta"].get("process_variant"),
            "benchmark_descriptor": state["meta"].get("benchmark_descriptor"),
            "artifact_narrative_policy": state["meta"].get("artifact_narrative_policy"),
            "support_artifact_policy": state["meta"].get("support_artifact_policy"),
            "package_element_labels": state["meta"].get("package_element_labels"),
            "evaluator_helper_policy": state["meta"].get("evaluator_helper_policy"),
            "review_transcript_renderer": state["meta"].get("review_transcript_renderer", "none"),
            "participant_context": state["participants"],
        },
    }


def _final_state_summary(state: dict) -> dict:
    esc = state.get("escalation", {})
    open_questions = [
        item["question"]
        for item in state.get("missing_info", [])
        if item.get("status") == "open"
    ]
    active_flags = [
        flag.get("flag_id", "")
        for flag in state.get("flags", [])
        if flag.get("status") != "resolved"
    ]
    return {
        "current_phase": state.get("phase", "unknown"),
        "issues_identified": list(state.get("issues", {}).keys()),
        "open_questions_remaining": open_questions,
        "active_flags": active_flags,
        "current_escalation_state": esc.get("mode"),
        "continuation_recommendation": state.get("summary_state", {}).get("next_step"),
    }


def build_interaction_trace(state: dict, generated_at: str) -> dict:
    return {
        "schema_version": "interaction_trace.v0",
        "case_id": state["meta"]["case_id"],
        "session_id": state["meta"]["session_id"],
        "policy_profile": state["meta"]["policy_profile"],
        "trace_created_at": generated_at,
        "turns": state["trace_buffer"],
        "final_state_summary": _final_state_summary(state),
        "trace_notes": None,
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


def _review_case_cover_sheet(state: dict, case_bundle: dict | None = None) -> str:
    case_metadata = (case_bundle or {}).get("case_metadata", {})
    working_notes = case_metadata.get("working_slice_notes", {})
    challenge_type = case_metadata.get("intended_challenge_type", "Practical review of mediation posture and next-step judgment.")
    posture = state["escalation"]["mode"]
    category = state["escalation"]["category"] or case_metadata.get("likely_escalation_category", "none")
    template_family = working_notes.get("template_family_id", "unspecified")
    review_question = case_metadata.get("hidden_evaluator_notes", {}).get(
        "primary_test",
        "Does the session justify the final posture and next step?",
    )

    return (
        "Reviewer Cover Sheet\n"
        f"Case ID: {state['meta']['case_id']}\n"
        f"Title: {state['meta']['title']}\n"
        f"Plugin: {state['meta']['plugin_type']}\n"
        f"Source: {state['meta'].get('source', 'reference')}\n"
        f"Session ID: {state['meta']['session_id']}\n"
        f"Template Family: {template_family}\n"
        f"Expected Posture At A Glance: {posture} / {category}\n\n"
        "Case Summary\n"
        f"{case_metadata.get('scenario_summary', 'No scenario summary recorded.')}\n\n"
        "Contrast Purpose\n"
        f"{challenge_type}\n\n"
        "Review Question\n"
        f"{review_question}\n"
    )


def _trace_turn_speaker(turn: dict) -> str:
    if turn["role"] == "assistant":
        return "Solomon"

    participant_ids = []
    for position in turn.get("state_delta", {}).get("positions_structured", []):
        participant_ids.extend(position.get("participant_ids", []))
    unique_ids = []
    for participant_id in participant_ids:
        if participant_id not in unique_ids:
            unique_ids.append(participant_id)

    if unique_ids == ["spouse_A"]:
        return "Spouse A"
    if unique_ids == ["spouse_B"]:
        return "Spouse B"
    if set(unique_ids) == {"spouse_A", "spouse_B"}:
        return "Spouses"
    return "Client"


def _sentence(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text if text.endswith((".", "?", "!")) else f"{text}."


def _rewrite_assistant_summary(summary: str) -> str:
    text = summary.strip()
    if text.startswith("Solomon frames the session around "):
        text = "Let's start by " + text.removeprefix("Solomon frames the session around ")
    elif text.startswith("Solomon opens by clarifying that it is facilitating a mediation process, not making decisions for the parents, and proposes focusing first on "):
        text = (
            "I want to start by being clear that I am here to facilitate the conversation, not make decisions for you. "
            "Let's focus first on "
            + text.removeprefix(
                "Solomon opens by clarifying that it is facilitating a mediation process, not making decisions for the parents, and proposes focusing first on "
            )
        )
    elif text.startswith("Solomon pauses the exchange, reflects "):
        text = (
            "I want to pause here. I'm noticing "
            + text.removeprefix("Solomon pauses the exchange, reflects ")
        )
    elif text.startswith("Solomon slows the exchange, reflects "):
        text = (
            "I want to slow this down. I'm hearing "
            + text.removeprefix("Solomon slows the exchange, reflects ")
        )
    elif text.startswith("Solomon slows the pace, "):
        text = "I want to slow this down. " + text.removeprefix("Solomon slows the pace, ")
    elif text.startswith("Solomon reflects the overlap between "):
        text = "What I'm hearing is overlap between " + text.removeprefix("Solomon reflects the overlap between ")
    elif text.startswith("Solomon reflects the emotional strain directly, "):
        text = "I want to acknowledge the emotional strain here. " + text.removeprefix("Solomon reflects the emotional strain directly, ")
    elif text.startswith("Solomon reflects the confidence asymmetry directly, "):
        text = "I want to acknowledge that one of you has much less confidence and information here. " + text.removeprefix("Solomon reflects the confidence asymmetry directly, ")
    elif text.startswith("Solomon reflects the issue-coupling directly, "):
        text = "I want to name that these issues are tightly connected. " + text.removeprefix("Solomon reflects the issue-coupling directly, ")
    elif text.startswith("Solomon summarizes the overlap: "):
        text = "Let me summarize what I'm hearing: " + text.removeprefix("Solomon summarizes the overlap: ")
    elif text.startswith("Solomon summarizes that "):
        text = "Let me summarize what I'm hearing: " + text.removeprefix("Solomon summarizes that ")
    elif text.startswith("Solomon narrows the discussion to "):
        text = "For now, I want to narrow this to " + text.removeprefix("Solomon narrows the discussion to ")
    elif text.startswith("Solomon proposes only bounded exploration: "):
        text = "For now, I want to explore only a limited next step: " + text.removeprefix("Solomon proposes only bounded exploration: ")
    elif text.startswith("Solomon proposes a bounded "):
        text = "For now, I want to suggest a limited " + text.removeprefix("Solomon proposes a bounded ")
    elif text.startswith("Solomon keeps the session in bounded caution, recommending "):
        text = "I don't think we should go further yet. The next step should be " + text.removeprefix("Solomon keeps the session in bounded caution, recommending ")
    elif text.startswith("Solomon concludes that a human mediator should join for co-handling because "):
        text = (
            "At this point, I think a human mediator should join us because "
            + text.removeprefix("Solomon concludes that a human mediator should join for co-handling because ")
        )
    elif text.startswith("Solomon concludes that "):
        text = "At this point, I think " + text.removeprefix("Solomon concludes that ")

    replacements = [
        ("parent a", "Parent A"),
        ("parent b", "Parent B"),
        ("autonomous handling", "continuing this without a human mediator"),
        ("continue autonomously", "continue on our own here"),
        ("option work", "moving into solutions"),
        ("working on options", "moving into solutions"),
        ("co-handling", "a human mediator involved"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return _sentence(text)


def _structured_position_lines(turn: dict) -> list[str]:
    positions = turn.get("state_delta", {}).get("positions_structured", [])
    statements: list[str] = []
    for position in positions:
        statement = position.get("statement")
        if isinstance(statement, str) and statement not in statements:
            statements.append(statement)
    return statements


def _rewrite_client_summary(turn: dict) -> str:
    structured_statements = _structured_position_lines(turn)
    if len(structured_statements) == 1:
        return _sentence(structured_statements[0])
    if len(structured_statements) > 1:
        return " ".join(_sentence(statement) for statement in structured_statements)

    text = turn["message_summary"].strip()
    client_replacements = [
        ("Parent A says ", ""),
        ("Parent B says ", ""),
        ("Both parents are conditionally open to ", "We are both conditionally open to "),
        ("The parents do not reach final agreement, but both accept that ", "We are not at final agreement yet, but we both accept that "),
        ("The parents identify ", "We identify "),
    ]
    for old, new in client_replacements:
        text = text.replace(old, new)
    text = text.replace("parent a", "Parent A").replace("parent b", "Parent B")
    return _sentence(text)


def _format_trace_turn(turn: dict) -> str:
    speaker = _trace_turn_speaker(turn)
    phase = turn.get("phase", "unknown")
    if turn["role"] == "assistant":
        message = _rewrite_assistant_summary(turn["message_summary"])
    else:
        message = _rewrite_client_summary(turn)
    return (
        f"Turn {turn['turn_index']} [{phase}]\n"
        f"{speaker}: {message}\n"
    )


def build_review_transcript(state: dict) -> str:
    turns = "\n".join(_format_trace_turn(turn) for turn in state["trace_buffer"])
    return (
        "Reviewer Transcript\n"
        f"Case ID: {state['meta']['case_id']}\n"
        f"Session ID: {state['meta']['session_id']}\n\n"
        f"{turns}\n"
    )


def build_review_outcome_sheet(state: dict) -> str:
    flags = state.get("flags", [])
    active_flag_types = ", ".join(flag["flag_type"] for flag in flags[:4]) if flags else "none"
    issues = ", ".join(state["summary_state"]["issues"][:2]) or "No issues recorded."
    rationale = state["escalation"]["rationale"]
    next_step = state["summary_state"]["next_step"] or "No next step recorded."
    expert_focus = state.get("plugin_assessment", {}).get("warnings", [])
    focus_line = expert_focus[0] if expert_focus else "No additional warning line recorded."

    return (
        "Reviewer Outcome Sheet\n"
        f"Case ID: {state['meta']['case_id']}\n"
        f"Final Posture: {state['escalation']['mode']} / {state['escalation']['category'] or 'none'}\n"
        f"Main Issues: {issues}\n"
        f"Active Flag Types: {active_flag_types}\n\n"
        "Why This Posture Was Chosen\n"
        f"{rationale}\n"
        f"{focus_line}\n\n"
        "Recommended Next Step\n"
        f"{next_step}\n"
    )


def write_artifacts(output_dir: Path, state: dict, generated_at: str, case_bundle: dict | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    require_redaction = get_policy_profile(state["meta"]["policy_profile"]).require_redaction

    def _rj(payload: dict) -> dict:
        return redact_json_values(payload, state) if require_redaction else payload

    def _rt(text: str) -> str:
        return redact_text(text, state) if require_redaction else text

    _write_json(output_dir / "session_meta.json", _rj(build_session_meta(state, generated_at)))
    _write_json(output_dir / "run_meta.json", _rj(build_run_meta(state, generated_at)))
    _write_json(output_dir / "interaction_trace.json", _rj(build_interaction_trace(state, generated_at)))
    _write_json(output_dir / "positions.json", _rj(build_positions(state)))
    _write_json(output_dir / "facts_snapshot.json", _rj(build_facts_snapshot(state)))
    _write_json(output_dir / "flags.json", _rj(build_flags(state)))
    _write_json(output_dir / "missing_info.json", _rj(build_missing_info(state)))
    (output_dir / "summary.txt").write_text(_rt(build_summary(state)), encoding="utf-8")
    (output_dir / "review_cover_sheet.txt").write_text(_rt(_review_case_cover_sheet(state, case_bundle)), encoding="utf-8")
    (output_dir / "review_transcript.txt").write_text(_rt(build_review_transcript(state)), encoding="utf-8")
    (output_dir / "review_outcome_sheet.txt").write_text(_rt(build_review_outcome_sheet(state)), encoding="utf-8")
    renderer_name = state["meta"].get("review_transcript_renderer", "none")
    if renderer_name != "none":
        (output_dir / "review_transcript_rendered.txt").write_text(
            build_rendered_reviewer_transcript(state, renderer_name),
            encoding="utf-8",
        )
    if case_bundle is not None:
        write_support_artifacts(output_dir, state, case_bundle)
    validation_errors = validate_runtime_artifact_set(output_dir, state)
    if validation_errors:
        raise ValueError("; ".join(validation_errors))
    validate_support_artifact_package(output_dir, state)
