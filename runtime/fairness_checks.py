from __future__ import annotations

import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluator_helper_policy(run_meta: dict) -> dict:
    return dict(run_meta.get("case_context", {}).get("evaluator_helper_policy") or {})


def _fairness_terms(policy: dict) -> tuple[str, ...]:
    return tuple(policy.get("fairness_terms", [])) + tuple(policy.get("fairness_issue_terms", []))


def _fairness_flag_types(policy: dict) -> set[str]:
    return set(policy.get("fairness_flag_types", []))


def _expected_fairness_attention(run_meta: dict, policy: dict) -> bool:
    benchmark_descriptor = run_meta.get("case_context", {}).get("benchmark_descriptor") or {}
    attention_tags = set(benchmark_descriptor.get("evaluator_attention_tags", []))
    policy_tags = set(policy.get("fairness_attention_tags", []))
    return bool(attention_tags & policy_tags)


def run_first_pass_fairness_checks(run_dir: Path) -> dict:
    run_meta = _load_json(run_dir / "run_meta.json")
    positions = _load_json(run_dir / "positions.json")
    facts = _load_json(run_dir / "facts_snapshot.json")
    flags = _load_json(run_dir / "flags.json")
    summary = (run_dir / "summary.txt").read_text(encoding="utf-8")
    policy = _evaluator_helper_policy(run_meta)

    summary_lower = summary.lower()
    active_flags = flags["active_flags"]
    active_flag_types = {flag["flag_type"] for flag in active_flags}
    fairness_flags = sorted(active_flag_types & _fairness_flag_types(policy))

    position_text = json.dumps(positions, sort_keys=True).lower()
    fact_text = json.dumps(facts, sort_keys=True).lower()
    fairness_terms = _fairness_terms(policy)
    summary_mentions_fairness = any(term in summary_lower for term in fairness_terms)
    structured_mentions_fairness = any(term in position_text or term in fact_text for term in fairness_terms)

    case_id = run_meta["case_id"]
    expected_fairness_attention = _expected_fairness_attention(run_meta, policy)

    findings: list[str] = []
    if fairness_flags:
        findings.append("active fairness-specific flags are present")
    if summary_mentions_fairness:
        findings.append("summary preserves fairness-sensitive language")
    if structured_mentions_fairness:
        findings.append("structured artifacts preserve fairness-sensitive language")
    if expected_fairness_attention and not findings:
        findings.append("fairness-sensitive slice lacks explicit fairness cues in the reviewed artifacts")

    return {
        "schema_version": "fairness_check_report.v0",
        "case_id": case_id,
        "session_id": run_meta["session_id"],
        "expected_fairness_attention": expected_fairness_attention,
        "fairness_flag_types": fairness_flags,
        "summary_mentions_fairness": summary_mentions_fairness,
        "structured_mentions_fairness": structured_mentions_fairness,
        "findings": findings,
        "status": "attention_needed" if expected_fairness_attention and not (summary_mentions_fairness or structured_mentions_fairness) else "ok",
    }
