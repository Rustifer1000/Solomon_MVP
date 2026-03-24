from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.evaluator_operations import build_calibration_review_seed


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    if len(sys.argv) not in {2, 3}:
        raise SystemExit(
            "Usage: python tools\\build_calibration_review_seed.py <evaluation.json> [expert_review.json]"
        )
    evaluation = _load_json(Path(sys.argv[1]).resolve())
    expert_review = _load_json(Path(sys.argv[2]).resolve()) if len(sys.argv) == 3 else None
    print(json.dumps(build_calibration_review_seed(evaluation, expert_review), indent=2))


if __name__ == "__main__":
    main()
