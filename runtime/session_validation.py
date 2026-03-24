from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from runtime.policy_profiles import get_policy_profile

PHASE_ORDER = {
    "info_gathering": 0,
    "interest_exploration": 1,
    "option_generation": 2,
    "agreement_building": 3,
}


def validate_session_trace(turns: list[dict], final_escalation: dict) -> None:
    if not turns:
        raise ValueError("Session trace cannot be empty")

    expected_turns = list(range(1, len(turns) + 1))
    actual_turns = [turn["turn_index"] for turn in turns]
    if actual_turns != expected_turns:
        raise ValueError("Session trace must use sequential turn indexes starting at 1")

    parsed_timestamps = [datetime.fromisoformat(turn["timestamp"].replace("Z", "+00:00")) for turn in turns]
    if parsed_timestamps != sorted(parsed_timestamps):
        raise ValueError("Session trace timestamps must be monotonic")

    phases = [turn["phase"] for turn in turns]
    if phases[0] != "info_gathering":
        raise ValueError("Session trace must begin in info_gathering")
    if "option_generation" in phases and "interest_exploration" not in phases:
        raise ValueError("Session trace cannot enter option_generation before interest_exploration appears")
    if "agreement_building" in phases and "option_generation" not in phases:
        raise ValueError("Session trace cannot enter agreement_building before option_generation appears")

    assistant_phases = [PHASE_ORDER[turn["phase"]] for turn in turns if turn["role"] == "assistant"]
    if assistant_phases != sorted(assistant_phases):
        raise ValueError("Assistant phase progression must be non-decreasing across the session")

    candidate_escalation_turns = [
        turn for turn in turns if turn.get("candidate_escalation_mode") is not None
    ]
    if candidate_escalation_turns:
        last_candidate = candidate_escalation_turns[-1]
        if final_escalation.get("mode") != last_candidate.get("candidate_escalation_mode"):
            raise ValueError("Final escalation mode must match the last explicit candidate escalation mode in the trace")
        if final_escalation.get("category") != last_candidate.get("candidate_escalation_category"):
            raise ValueError("Final escalation category must match the last explicit candidate escalation category in the trace")
        if not last_candidate["risk_check"]["triggered"]:
            raise ValueError("Explicit candidate escalation turns must carry a triggered risk_check")

    if final_escalation.get("mode") in {"M2", "M3", "M4", "M5"}:
        if final_escalation.get("category") is None:
            raise ValueError("Higher-mode sessions must carry a non-null escalation category")
        if final_escalation.get("threshold_band") in {None, "T0"}:
            raise ValueError("Higher-mode sessions must carry a nontrivial threshold band")
        rationale = (final_escalation.get("rationale") or "").strip()
        if not rationale or rationale == "No caution state has been selected yet.":
            raise ValueError("Higher-mode sessions must carry a substantive escalation rationale")


def validate_support_artifact_package(output_dir: Path, state: dict) -> None:
    mode = state["escalation"]["mode"]
    profile = state["meta"]["policy_profile"]
    profile_config = get_policy_profile(profile)

    briefs_dir = output_dir / "briefs"
    continuity_dir = output_dir / "continuity"

    if profile == "eval_support":
        if not (briefs_dir / "case_intake_brief.json").exists():
            raise ValueError("eval_support runs must emit case_intake_brief.json")
        if not (briefs_dir / "early_dynamics_brief.json").exists():
            raise ValueError("eval_support runs must emit early_dynamics_brief.json")

    if mode in {"M1", "M2", "M3", "M4", "M5"} and profile == "eval_support":
        if not (briefs_dir / "risk_alert_brief.json").exists():
            raise ValueError("Escalated eval_support runs must emit risk_alert_brief.json")

    if profile_config.allow_continuity_packet and mode in {"M2", "M3", "M4", "M5"}:
        packet_path = continuity_dir / "continuity_packet.json"
        if not packet_path.exists():
            raise ValueError("Higher-mode runs must emit continuity_packet.json")
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        if packet["escalation"]["mode"] != mode:
            raise ValueError("Continuity packet mode must match the final escalation mode")
        if packet["escalation"]["category"] != state["escalation"]["category"]:
            raise ValueError("Continuity packet category must match the final escalation category")
        if packet["category_family"] == "none":
            raise ValueError("Higher-mode continuity packets must carry a non-empty escalation family")
        if packet["recommended_human_role"] == "none":
            raise ValueError("Higher-mode continuity packets must carry a recommended human role")
