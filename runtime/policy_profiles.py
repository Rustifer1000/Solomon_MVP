from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import jsonschema


_SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schema"

# Maps each core JSON artifact filename to its schema file.  Only JSON
# artifacts that have a schema are listed here; text artifacts are skipped.
_ARTIFACT_SCHEMAS: dict[str, str] = {
    "session_meta.json": "session_meta.schema.json",
    "run_meta.json": "run_meta.schema.json",
    "interaction_trace.json": "interaction_trace.schema.json",
    "positions.json": "positions.schema.json",
    "facts_snapshot.json": "facts_snapshot.schema.json",
    "flags.json": "flags.schema.json",
    "missing_info.json": "missing_info.schema.json",
    "briefs/case_intake_brief.json": "case_intake_brief.schema.json",
    "briefs/early_dynamics_brief.json": "early_dynamics_brief.schema.json",
    "briefs/risk_alert_brief.json": "risk_alert_brief.schema.json",
    "continuity/continuity_packet.json": "continuity_packet.schema.json",
}


CORE_RUNTIME_ARTIFACTS = (
    "session_meta.json",
    "run_meta.json",
    "interaction_trace.json",
    "positions.json",
    "facts_snapshot.json",
    "flags.json",
    "missing_info.json",
    "summary.txt",
    "review_cover_sheet.txt",
    "review_transcript.txt",
    "review_outcome_sheet.txt",
)


@dataclass(frozen=True)
class PolicyProfile:
    name: str
    required_core_artifacts: tuple[str, ...]
    allow_briefs: bool = False
    allow_continuity_packet: bool = False
    continuity_required_modes: tuple[str, ...] = ()
    # dev_verbose: reserved for future raw-transcript and debug-trace writing
    allow_raw_transcripts: bool = False
    allow_debug_traces: bool = False
    # redacted: reserved for future write-time redaction hook enforcement
    require_redaction: bool = False


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
    "dev_verbose": PolicyProfile(
        name="dev_verbose",
        required_core_artifacts=CORE_RUNTIME_ARTIFACTS,
        allow_briefs=True,
        allow_continuity_packet=True,
        continuity_required_modes=("M2", "M3", "M4", "M5"),
        allow_raw_transcripts=True,
        allow_debug_traces=True,
    ),
    "redacted": PolicyProfile(
        name="redacted",
        required_core_artifacts=CORE_RUNTIME_ARTIFACTS,
        allow_briefs=True,
        allow_continuity_packet=True,
        continuity_required_modes=("M2", "M3", "M4", "M5"),
        require_redaction=True,
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
    if state["meta"].get("review_transcript_renderer", "none") != "none":
        expected.add("review_transcript_rendered.txt")

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

    # Schema conformance check for every core JSON artifact that has a schema.
    for artifact_name, schema_file in _ARTIFACT_SCHEMAS.items():
        artifact_path = output_dir / artifact_name
        if not artifact_path.exists():
            continue  # presence errors already reported above
        schema = json.loads((_SCHEMA_DIR / schema_file).read_text(encoding="utf-8"))
        instance = json.loads(artifact_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        for error in validator.iter_errors(instance):
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
            errors.append(f"{artifact_name} schema violation ({path}): {error.message}")

    return errors
