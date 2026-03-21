from __future__ import annotations

import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_case_bundle(case_dir: Path) -> dict:
    personas_dir = case_dir / "personas"
    personas = {
        persona_path.stem: load_json(persona_path)
        for persona_path in sorted(personas_dir.glob("*.json"))
    }
    return {
        "case_dir": case_dir,
        "case_metadata": load_json(case_dir / "case_metadata.json"),
        "personas": personas,
        "reference_session_dir": case_dir / "sessions" / "D-B04-S01",
    }
