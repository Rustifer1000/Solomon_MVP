from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.fairness_checks import run_first_pass_fairness_checks


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools\\run_fairness_checks.py <run-dir>")

    run_dir = Path(sys.argv[1])
    result = run_first_pass_fairness_checks(run_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
