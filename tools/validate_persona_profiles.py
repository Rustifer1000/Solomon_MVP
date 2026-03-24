from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.persona_validation import validate_persona_profile


def main() -> None:
    benchmark_root = REPO_ROOT / "annexes" / "benchmark_cases"
    persona_paths = sorted(benchmark_root.glob("D-B*/personas/*.json"))
    errors: list[str] = []
    warnings: list[str] = []
    for path in persona_paths:
        persona = json.loads(path.read_text(encoding="utf-8"))
        persona_errors, persona_warnings = validate_persona_profile(persona)
        errors.extend(f"{path.relative_to(REPO_ROOT)}: {item}" for item in persona_errors)
        warnings.extend(f"{path.relative_to(REPO_ROOT)}: {item}" for item in persona_warnings)

    if errors:
        for item in errors:
            print(item)
        raise SystemExit(1)

    if warnings:
        print("Persona profiles are schema-valid. Recommended-field warnings:")
        for item in warnings:
            print(f"- {item}")
    else:
        print("Persona profiles are schema-valid and include all recommended fields.")


if __name__ == "__main__":
    main()
