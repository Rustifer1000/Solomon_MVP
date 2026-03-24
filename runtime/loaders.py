from __future__ import annotations

import json
from pathlib import Path

from runtime.benchmarks import get_benchmark_simulation


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_case_bundle(case_dir: Path) -> dict:
    personas_dir = case_dir / "personas"
    personas = {
        persona_path.stem: load_json(persona_path)
        for persona_path in sorted(personas_dir.glob("*.json"))
    }
    case_metadata = load_json(case_dir / "case_metadata.json")
    case_bundle = {
        "case_dir": case_dir,
        "case_metadata": case_metadata,
        "personas": personas,
    }
    simulation = get_benchmark_simulation(case_bundle)
    return {
        **case_bundle,
        "reference_session_dir": simulation.reference_session_dir(case_dir),
    }
