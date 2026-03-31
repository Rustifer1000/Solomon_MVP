from __future__ import annotations

import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluator_helper_policy(run_meta: dict) -> dict:
    return dict(run_meta.get("case_context", {}).get("evaluator_helper_policy") or {})


def build_fairness_review_seed(run_dir: Path) -> dict:
    run_meta = _load_json(run_dir / "run_meta.json")
    flags = _load_json(run_dir / "flags.json")
    summary = (run_dir / "summary.txt").read_text(encoding="utf-8")
    policy = _evaluator_helper_policy(run_meta)

    active_flags = flags["active_flags"]
    active_flag_types = {flag["flag_type"] for flag in active_flags}
    fairness_flags = sorted(active_flag_types & set(policy.get("fairness_flag_types", [])))
    fairness_terms = tuple(policy.get("fairness_terms", [])) + tuple(policy.get("fairness_issue_terms", []))
    benchmark_descriptor = run_meta.get("case_context", {}).get("benchmark_descriptor") or {}
    fairness_issue_present = any(term in summary.lower() for term in fairness_terms) or bool(
        set(benchmark_descriptor.get("evaluator_attention_tags", [])) & set(policy.get("fairness_attention_tags", []))
    )

    review_reasons: list[str] = []
    if fairness_flags:
        review_reasons.append("fairness-specific caution flags are active")
    if fairness_issue_present:
        review_reasons.append("the case narrative includes fairness-sensitive issues")

    return {
        "schema_version": "fairness_review_seed.v0",
        "case_id": run_meta["case_id"],
        "session_id": run_meta["session_id"],
        "plugin_type": run_meta["case_context"]["plugin_type"],
        "fairness_flag_types": fairness_flags,
        "fairness_issue_present": fairness_issue_present,
        "recommended_review_level": "heightened" if review_reasons else "standard",
        "review_reasons": review_reasons,
    }


def build_calibration_review_seed(evaluation: dict, expert_review: dict | None = None) -> dict:
    reasons: list[str] = []
    if evaluation["final_judgment"].get("requires_calibration_review"):
        reasons.append("primary evaluation explicitly requested calibration review")
    if expert_review is not None:
        if expert_review["expert_findings"]["agreement_with_primary_evaluation"] != "full_agreement":
            reasons.append("expert review does not show full agreement with the primary evaluation")
        if expert_review["final_review_outcome"]["final_requires_calibration_review"]:
            reasons.append("expert review explicitly requested calibration review")

    return {
        "schema_version": "calibration_review_seed.v0",
        "case_id": evaluation["case_id"],
        "session_id": evaluation["session_id"],
        "requires_calibration_review": bool(reasons),
        "reasons": reasons,
    }


_CONFIRMED_VERDICTS = {"confirmed_correct", "confirmed_correct_with_notes"}


def build_escalation_confirmation_seed(
    evaluation: dict,
    session_dir: Path,
) -> dict:
    """
    Build a pre-filled escalation_confirmation.json seed from a session's
    evaluation.json.  The reviewer fills in escalation_confirmation.verdict
    and rationale; all other fields are pre-populated.
    """
    escalation = evaluation.get("escalation_review", {})
    return {
        "schema_version": "escalation_confirmation.v0",
        "case_id": evaluation.get("case_id", ""),
        "session_id": evaluation.get("session_id", ""),
        "reviewer_id": "",
        "review_date": "",
        "artifacts_reviewed": [
            "review_cover_sheet.txt",
            "review_transcript.txt",
            "review_outcome_sheet.txt",
            "evaluation.json",
        ],
        "session_escalation": {
            "observed_mode": escalation.get("observed_mode", ""),
            "observed_category": escalation.get("primary_escalation_category"),
            "observed_threshold_band": escalation.get("threshold_band", ""),
        },
        "escalation_confirmation": {
            "verdict": "",
            "corrected_mode": None,
            "rationale": "",
            "key_signals_assessed": [],
            "notes": None,
        },
        "training_corpus_eligible": False,
        "corpus_record_id": None,
        "quality_notes": None,
    }


def build_review_corpus_status(sessions_root: Path) -> dict:
    """
    Scan sessions_root recursively for escalation_confirmation.json files and
    return a summary of the confirmed-correct corpus.

    Returns a dict with counts and a list of corpus-eligible session IDs.
    """
    total_reviewed = 0
    confirmed_correct = 0
    corpus_eligible: list[dict] = []
    pending_correction: list[str] = []
    insufficient: list[str] = []

    for conf_path in sorted(sessions_root.rglob("escalation_confirmation.json")):
        total_reviewed += 1
        try:
            record = _load_json(conf_path)
        except Exception:
            continue

        verdict = record.get("escalation_confirmation", {}).get("verdict", "")
        eligible = bool(record.get("training_corpus_eligible"))

        if verdict in _CONFIRMED_VERDICTS:
            confirmed_correct += 1
        elif verdict == "insufficient_information_to_confirm":
            insufficient.append(record.get("session_id", str(conf_path)))
        elif verdict:
            pending_correction.append(record.get("session_id", str(conf_path)))

        if eligible:
            corpus_eligible.append({
                "case_id": record.get("case_id", ""),
                "session_id": record.get("session_id", ""),
                "verdict": verdict,
                "corpus_record_id": record.get("corpus_record_id"),
            })

    return {
        "schema_version": "review_corpus_status.v0",
        "total_reviewed": total_reviewed,
        "confirmed_correct": confirmed_correct,
        "corpus_eligible_count": len(corpus_eligible),
        "pending_correction_count": len(pending_correction),
        "insufficient_information_count": len(insufficient),
        "corpus_eligible_sessions": corpus_eligible,
        "pending_correction_sessions": pending_correction,
        "insufficient_information_sessions": insufficient,
    }


def compare_benchmark_runs(left_dir: Path, right_dir: Path) -> dict:
    left_meta = _load_json(left_dir / "run_meta.json")
    right_meta = _load_json(right_dir / "run_meta.json")
    if left_meta["case_id"] != right_meta["case_id"]:
        raise ValueError("Benchmark comparison requires matching case ids")

    left_flags = _load_json(left_dir / "flags.json")
    right_flags = _load_json(right_dir / "flags.json")
    left_missing = _load_json(left_dir / "missing_info.json")
    right_missing = _load_json(right_dir / "missing_info.json")
    left_summary = (left_dir / "summary.txt").read_text(encoding="utf-8")
    right_summary = (right_dir / "summary.txt").read_text(encoding="utf-8")

    left_open_missing = len([item for item in left_missing["missing_items"] if item["status"] == "open"])
    right_open_missing = len([item for item in right_missing["missing_items"] if item["status"] == "open"])
    left_flag_types = sorted(flag["flag_type"] for flag in left_flags["active_flags"])
    right_flag_types = sorted(flag["flag_type"] for flag in right_flags["active_flags"])

    return {
        "schema_version": "benchmark_run_comparison.v0",
        "case_id": left_meta["case_id"],
        "left_session_id": left_meta["session_id"],
        "right_session_id": right_meta["session_id"],
        "process_variant_changed": left_meta["case_context"].get("process_variant") != right_meta["case_context"].get("process_variant"),
        "summary_changed": left_summary != right_summary,
        "open_missing_info_delta": right_open_missing - left_open_missing,
        "left_flag_types": left_flag_types,
        "right_flag_types": right_flag_types,
        "flag_type_delta": sorted(set(right_flag_types) ^ set(left_flag_types)),
    }
