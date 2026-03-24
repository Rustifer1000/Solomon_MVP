from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.evaluator_artifact_validation import (  # noqa: E402
    validate_reference_evaluation_example,
    validate_reference_evaluation_summary_text,
    validate_reference_expert_review_example,
)

REFERENCE_EVALUATIONS = [
    ("D-B04", "D-B04-S01", "M1", "E5"),
    ("D-B05", "D-B05-S01", "M0", "none"),
    ("D-B06", "D-B06-S01", "M0", "none"),
]

REFERENCE_EXPERT_REVIEWS = [
    ("D-B04", "D-B04-S01"),
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    for case_id, session_id, expected_mode, expected_category in REFERENCE_EVALUATIONS:
        case_dir = REPO_ROOT / "annexes" / "benchmark_cases" / case_id
        case_metadata = _load_json(case_dir / "case_metadata.json")
        evaluation = _load_json(case_dir / "sessions" / session_id / "evaluation.json")
        summary_text = (case_dir / "sessions" / session_id / "evaluation_summary.txt").read_text(encoding="utf-8")

        for error in validate_reference_evaluation_example(evaluation, case_metadata, expected_mode, expected_category):
            errors.append(f"{case_id}/{session_id}/evaluation.json: {error}")
        for error in validate_reference_evaluation_summary_text(summary_text, case_metadata, expected_mode):
            errors.append(f"{case_id}/{session_id}/evaluation_summary.txt: {error}")

    for case_id, session_id in REFERENCE_EXPERT_REVIEWS:
        case_dir = REPO_ROOT / "annexes" / "benchmark_cases" / case_id
        case_metadata = _load_json(case_dir / "case_metadata.json")
        evaluation = _load_json(case_dir / "sessions" / session_id / "evaluation.json")
        expert_review = _load_json(case_dir / "sessions" / session_id / "expert_review.json")

        for error in validate_reference_expert_review_example(expert_review, evaluation, case_metadata):
            errors.append(f"{case_id}/{session_id}/expert_review.json: {error}")

    if errors:
        for error in errors:
            print(error)
        return 1

    print("Reference evaluator artifacts are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
