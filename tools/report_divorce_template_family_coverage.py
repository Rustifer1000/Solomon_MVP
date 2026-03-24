from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.benchmarks import get_benchmark_simulation
from runtime.loaders import load_case_bundle


ALL_DIVORCE_TEMPLATE_FAMILIES = [
    "TF-DIV-01",
    "TF-DIV-02",
    "TF-DIV-03",
    "TF-DIV-04",
    "TF-DIV-05",
    "TF-DIV-06",
    "TF-DIV-07",
    "TF-DIV-08",
    "TF-DIV-09",
    "TF-DIV-10",
    "TF-DIV-11",
    "TF-DIV-12",
]


def main() -> None:
    benchmark_root = REPO_ROOT / "annexes" / "benchmark_cases"
    active_cases = ["D-B04", "D-B05", "D-B06", "D-B07", "D-B08", "D-B09", "D-B10", "D-B11", "D-B12", "D-B13", "D-B14"]
    coverage = {}
    covered = set()
    for case_id in active_cases:
        case_bundle = load_case_bundle(benchmark_root / case_id)
        simulation = get_benchmark_simulation(case_bundle)
        descriptor = simulation.benchmark_descriptor(case_bundle) or {}
        families = descriptor.get("template_family_ids", [])
        coverage[case_id] = families
        covered.update(families)

    payload = {
        "covered_families": sorted(covered),
        "missing_families": [family for family in ALL_DIVORCE_TEMPLATE_FAMILIES if family not in covered],
        "slice_coverage": coverage,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
