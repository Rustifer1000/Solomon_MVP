from __future__ import annotations

import json
from pathlib import Path

import jsonschema

CORE_WEIGHTS = {
    "C1": 9,
    "C2": 7,
    "C3": 12,
    "C4": 9,
    "C5": 13,
    "C6": 16,
    "C7": 7,
    "C8": 6,
    "C9": 16,
    "C10": 5,
}

PLUGIN_WEIGHTS = {
    "P1": 12,
    "P2": 20,
    "P3": 24,
    "P4": 18,
    "P5": 16,
    "P6": 10,
}

INTEGRATION_WEIGHTS = {
    "I1": 18,
    "I2": 20,
    "I3": 22,
    "I4": 16,
    "I5": 10,
    "I6": 14,
}

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schema"


def _load_schema(schema_name: str) -> dict:
    return json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))


def _schema_errors(instance: object, schema_name: str) -> list[str]:
    """Validate *instance* against the named schema file; return a list of error strings."""
    schema = _load_schema(schema_name)
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in validator.iter_errors(instance):
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        errors.append(f"{path}: {error.message}")
    return errors


def _expected_weighted_family_scores(score_block: dict, weights: dict[str, int]) -> dict[str, float]:
    return {
        family_id: round((score_block[family_id]["score"] / 5) * weight, 1)
        for family_id, weight in weights.items()
    }


def _validate_score_family_keys(evaluation: dict, block_name: str, expected_weights: dict[str, int]) -> list[str]:
    block = evaluation[block_name]
    actual_keys = set(block.keys())
    expected_keys = set(expected_weights.keys())
    if actual_keys != expected_keys:
        return [f"{block_name} keys do not match expected family ids"]
    return []


def _validate_weight_block(evaluation: dict, weight_block_name: str, expected_weights: dict[str, int]) -> list[str]:
    actual = evaluation["weighted_scores"][weight_block_name]
    if actual != expected_weights:
        return [f"{weight_block_name} does not match expected weights"]
    return []


def _validate_weighted_family_block(
    evaluation: dict,
    source_block_name: str,
    weighted_block_name: str,
    expected_weights: dict[str, int],
) -> list[str]:
    expected = _expected_weighted_family_scores(evaluation[source_block_name], expected_weights)
    actual = evaluation["weighted_scores"][weighted_block_name]
    errors = []
    for family_id, expected_value in expected.items():
        actual_value = actual.get(family_id)
        if actual_value != expected_value:
            errors.append(
                f"{weighted_block_name}.{family_id} expected {expected_value} but found {actual_value}"
            )
    return errors


def _validate_total_score(
    evaluation: dict,
    weighted_block_name: str,
    total_field_name: str,
) -> list[str]:
    actual_block = evaluation["weighted_scores"][weighted_block_name]
    expected_total = round(sum(actual_block.values()), 1)
    actual_total = evaluation["weighted_scores"][total_field_name]
    if actual_total != expected_total:
        return [f"{total_field_name} expected {expected_total} but found {actual_total}"]
    return []


def validate_reference_evaluation_example(
    evaluation: dict,
    case_metadata: dict,
    expected_mode: str,
    expected_primary_category: str,
) -> list[str]:
    errors: list[str] = []
    errors.extend(_schema_errors(evaluation, "evaluation.schema.json"))

    if evaluation["case_id"] != case_metadata["case_id"]:
        errors.append("evaluation case_id does not match case metadata")
    if evaluation["benchmark_id"] != case_metadata["benchmark_id"]:
        errors.append("evaluation benchmark_id does not match case metadata")
    if evaluation["plugin"] != case_metadata["plugin_type"]:
        errors.append("evaluation plugin does not match case metadata")
    if evaluation["evaluation_meta"]["policy_profile"] != "sim_minimal":
        errors.append("evaluation policy_profile should remain sim_minimal for reference examples")

    for required_artifact in ["benchmark_record", "interaction_trace.json", "summary.txt", "flags.json"]:
        if required_artifact not in evaluation["evaluation_meta"]["artifacts_reviewed"]:
            errors.append(f"evaluation_meta.artifacts_reviewed missing {required_artifact}")

    errors.extend(_validate_score_family_keys(evaluation, "core_family_scores", CORE_WEIGHTS))
    errors.extend(_validate_score_family_keys(evaluation, "plugin_domain_family_scores", PLUGIN_WEIGHTS))
    errors.extend(_validate_score_family_keys(evaluation, "integration_family_scores", INTEGRATION_WEIGHTS))

    errors.extend(_validate_weight_block(evaluation, "core_family_weights", CORE_WEIGHTS))
    errors.extend(_validate_weight_block(evaluation, "plugin_domain_family_weights", PLUGIN_WEIGHTS))
    errors.extend(_validate_weight_block(evaluation, "integration_family_weights", INTEGRATION_WEIGHTS))

    errors.extend(
        _validate_weighted_family_block(
            evaluation,
            "core_family_scores",
            "weighted_core_family_scores",
            CORE_WEIGHTS,
        )
    )
    errors.extend(
        _validate_weighted_family_block(
            evaluation,
            "plugin_domain_family_scores",
            "weighted_plugin_domain_family_scores",
            PLUGIN_WEIGHTS,
        )
    )
    errors.extend(
        _validate_weighted_family_block(
            evaluation,
            "integration_family_scores",
            "weighted_integration_family_scores",
            INTEGRATION_WEIGHTS,
        )
    )

    errors.extend(_validate_total_score(evaluation, "weighted_core_family_scores", "core_general_score"))
    errors.extend(_validate_total_score(evaluation, "weighted_plugin_domain_family_scores", "plugin_domain_score"))
    errors.extend(_validate_total_score(evaluation, "weighted_integration_family_scores", "integration_score"))

    if evaluation["escalation_review"]["observed_mode"] != expected_mode:
        errors.append("observed_mode does not match expected reference posture")
    if evaluation["escalation_review"]["evaluator_preferred_mode"] != expected_mode:
        errors.append("evaluator_preferred_mode does not match expected reference posture")
    if evaluation["escalation_review"]["primary_escalation_category"] != expected_primary_category:
        errors.append("primary_escalation_category does not match expected reference posture")

    return errors


def validate_reference_evaluation_summary_text(
    summary_text: str,
    case_metadata: dict,
    expected_mode: str,
) -> list[str]:
    errors: list[str] = []
    lowered = summary_text.lower()
    if case_metadata["case_id"].lower() not in lowered:
        errors.append("evaluation_summary.txt should name the case id explicitly")
    if expected_mode.lower() not in lowered:
        errors.append("evaluation_summary.txt should name the expected posture explicitly")
    required_fragments = [
        "reference",
        "evaluator",
        "artifact",
    ]
    for fragment in required_fragments:
        if fragment not in lowered:
            errors.append(f"evaluation_summary.txt should mention {fragment}")
    return errors


def validate_escalation_confirmation(confirmation: dict) -> list[str]:
    """Validate an escalation_confirmation record against the schema."""
    return _schema_errors(confirmation, "escalation_confirmation.schema.json")


def validate_reference_expert_review_example(
    expert_review: dict,
    evaluation: dict,
    case_metadata: dict,
) -> list[str]:
    errors: list[str] = []
    errors.extend(_schema_errors(expert_review, "expert_review.schema.json"))

    if expert_review["case_id"] != case_metadata["case_id"]:
        errors.append("expert_review case_id does not match case metadata")
    if expert_review["benchmark_id"] != case_metadata["benchmark_id"]:
        errors.append("expert_review benchmark_id does not match case metadata")
    if expert_review["plugin"] != case_metadata["plugin_type"]:
        errors.append("expert_review plugin does not match case metadata")
    if expert_review["review_meta"]["policy_profile"] != "sim_minimal":
        errors.append("expert_review policy_profile should remain sim_minimal for reference examples")

    for required_artifact in ["evaluation.json", "interaction_trace.json", "summary.txt", "flags.json"]:
        if required_artifact not in expert_review["review_meta"]["artifacts_reviewed"]:
            errors.append(f"review_meta.artifacts_reviewed missing {required_artifact}")

    if not expert_review["source_evaluations"]:
        errors.append("expert_review must reference at least one evaluation")
    else:
        primary = expert_review["source_evaluations"][0]
        if primary.get("evaluation_id") != evaluation["evaluation_meta"]["evaluator_id"]:
            errors.append("expert_review source evaluation id does not match the worked evaluation example")

    if expert_review["final_review_outcome"]["case_status"] == "confirmed_as_scored":
        if expert_review["expert_findings"]["agreement_with_primary_evaluation"] == "substantial_disagreement":
            errors.append("confirmed_as_scored cannot pair with substantial_disagreement")

    if expert_review["final_review_outcome"]["final_requires_separate_review"] and (
        expert_review["review_reason"]["trigger"] not in {"automatic_fail_yes", "safety_concern", "fairness_concern"}
    ):
        errors.append("separate-review flag should be tied to a review reason that justifies it")

    return errors


def validate_flags_artifact(
    flags: dict,
    case_metadata: dict,
) -> list[str]:
    """Validate a flags.json artifact against flags.schema.json and semantic invariants."""
    errors: list[str] = []
    errors.extend(_schema_errors(flags, "flags.schema.json"))

    if flags.get("case_id") != case_metadata["case_id"]:
        errors.append("flags case_id does not match case metadata")

    for flag in flags.get("active_flags", []):
        if flag.get("status") != "active":
            errors.append(f"active flag {flag.get('flag_id')} has non-active status")
        if not 1 <= flag.get("severity", 0) <= 5:
            errors.append(f"active flag {flag.get('flag_id')} has out-of-range severity")
        if flag.get("hard_trigger") and not flag.get("related_categories"):
            errors.append(
                f"active flag {flag.get('flag_id')} has hard_trigger=true but no related_categories"
            )

    for flag in flags.get("cleared_flags", []):
        if flag.get("status") != "cleared":
            errors.append(f"cleared flag {flag.get('flag_id')} has non-cleared status")
        if flag.get("cleared_turn") is None:
            errors.append(f"cleared flag {flag.get('flag_id')} is missing cleared_turn")

    return errors
