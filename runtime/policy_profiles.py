from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


CORE_RUNTIME_ARTIFACTS = (
    "run_meta.json",
    "interaction_trace.json",
    "positions.json",
    "facts_snapshot.json",
    "flags.json",
    "missing_info.json",
    "summary.txt",
)


@dataclass(frozen=True)
class PolicyProfile:
    name: str
    required_core_artifacts: tuple[str, ...]
    allow_briefs: bool = False
    allow_continuity_packet: bool = False
    continuity_required_modes: tuple[str, ...] = ()


POLICY_PROFILES = {
    "sim_minimal": PolicyProfile(
        name="sim_minimal",
        required_core_artifacts=CORE_RUNTIME_ARTIFACTS,
        allow_briefs=False,
        allow_continuity_packet=False,
    ),
    "eval_support": PolicyProfile(
        name="eval_support",
        required_core_artifacts=CORE_RUNTIME_ARTIFACTS,
        allow_briefs=True,
        allow_continuity_packet=True,
        continuity_required_modes=("M2", "M3", "M4", "M5"),
    ),
}


def get_policy_profile(profile_name: str) -> PolicyProfile:
    try:
        return POLICY_PROFILES[profile_name]
    except KeyError as exc:
        supported = ", ".join(sorted(POLICY_PROFILES))
        raise ValueError(f"Unsupported policy profile: {profile_name}. Supported profiles: {supported}") from exc


def should_emit_risk_alert_brief(state: dict) -> bool:
    return bool(state.get("flags")) or state["escalation"]["mode"] != "M0"


def should_emit_continuity_packet(state: dict, profile: PolicyProfile) -> bool:
    return profile.allow_continuity_packet and state["escalation"]["mode"] in profile.continuity_required_modes


def expected_runtime_artifact_paths(state: dict) -> set[str]:
    profile = get_policy_profile(state["meta"]["policy_profile"])
    expected = set(profile.required_core_artifacts)

    if profile.allow_briefs:
        expected.update(
            {
                "briefs/case_intake_brief.json",
                "briefs/case_intake_brief.txt",
                "briefs/early_dynamics_brief.json",
                "briefs/early_dynamics_brief.txt",
            }
        )
        if should_emit_risk_alert_brief(state):
            expected.update(
                {
                    "briefs/risk_alert_brief.json",
                    "briefs/risk_alert_brief.txt",
                }
            )

    if should_emit_continuity_packet(state, profile):
        expected.update(
            {
                "continuity/continuity_packet.json",
                "continuity/continuity_packet.txt",
            }
        )

    return expected


def validate_runtime_artifact_set(output_dir: Path, state: dict) -> list[str]:
    expected = expected_runtime_artifact_paths(state)
    actual = {
        str(path.relative_to(output_dir)).replace("\\", "/")
        for path in output_dir.rglob("*")
        if path.is_file()
    }
    errors: list[str] = []
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    for item in missing:
        errors.append(f"missing artifact for policy profile {state['meta']['policy_profile']}: {item}")
    for item in unexpected:
        errors.append(f"unexpected artifact for policy profile {state['meta']['policy_profile']}: {item}")
    return errors
