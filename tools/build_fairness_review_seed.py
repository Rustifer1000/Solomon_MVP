from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.evaluator_operations import build_fairness_review_seed


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools\\build_fairness_review_seed.py <run-dir>")
    run_dir = Path(sys.argv[1]).resolve()
    print(json.dumps(build_fairness_review_seed(run_dir), indent=2))


if __name__ == "__main__":
    main()
