from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.evaluator_operations import compare_benchmark_runs


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python tools\\compare_benchmark_runs.py <left-run-dir> <right-run-dir>")
    left_dir = Path(sys.argv[1]).resolve()
    right_dir = Path(sys.argv[2]).resolve()
    print(json.dumps(compare_benchmark_runs(left_dir, right_dir), indent=2))


if __name__ == "__main__":
    main()
