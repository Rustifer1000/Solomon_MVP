"""Layer B template family loader.

Loads and validates the 12 divorce template family definitions from the
machine-readable JSON source at annexes/divorce_template_families.json.

This module is the Phase 2 contract anchor.  It provides:

  load_all_template_families() -> list[TemplateFamilyRecord]
      Parse and validate every family record.  Raises ValueError if any
      record is missing a required field or if the expected 12 IDs are
      not all present.

  get_template_family(family_id) -> TemplateFamilyRecord
      Return a single record by ID.  Raises KeyError if not found.

Full instantiation (variable sampling, case generation CLI) is out of
scope for Phase 1 and will be implemented in Phase 2.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_FAMILIES_PATH = Path(__file__).resolve().parents[2] / "annexes" / "divorce_template_families.json"

EXPECTED_FAMILY_IDS: tuple[str, ...] = tuple(f"TF-DIV-{i:02d}" for i in range(1, 13))

_REQUIRED_FIELDS: tuple[str, ...] = (
    "family_id",
    "title",
    "base_scenario",
    "typical_issue_clusters",
    "primary_variables",
    "party_private_information_slots",
    "intended_challenge_type",
    "likely_focal_competencies",
    "expected_escalation_posture",
    "main_failure_risks",
)


@dataclass(frozen=True)
class TemplateFamilyRecord:
    """Parsed and validated record for a single template family."""

    family_id: str
    title: str
    base_scenario: str
    typical_issue_clusters: tuple[str, ...]
    primary_variables: tuple[str, ...]
    party_private_information_slots: tuple[str, ...]
    intended_challenge_type: str
    likely_focal_competencies: tuple[str, ...]
    expected_escalation_posture: str
    main_failure_risks: tuple[str, ...]


def _parse_record(raw: dict) -> TemplateFamilyRecord:
    """Parse one raw JSON object into a TemplateFamilyRecord.

    Raises ValueError if any required field is missing or empty.
    """
    for field in _REQUIRED_FIELDS:
        if field not in raw:
            raise ValueError(
                f"Template family record missing required field '{field}': {raw.get('family_id', '<unknown>')}"
            )
        value = raw[field]
        if isinstance(value, str) and not value.strip():
            raise ValueError(
                f"Template family record has empty string for field '{field}': {raw.get('family_id', '<unknown>')}"
            )
        if isinstance(value, list) and len(value) == 0:
            raise ValueError(
                f"Template family record has empty list for field '{field}': {raw.get('family_id', '<unknown>')}"
            )

    return TemplateFamilyRecord(
        family_id=raw["family_id"],
        title=raw["title"],
        base_scenario=raw["base_scenario"],
        typical_issue_clusters=tuple(raw["typical_issue_clusters"]),
        primary_variables=tuple(raw["primary_variables"]),
        party_private_information_slots=tuple(raw["party_private_information_slots"]),
        intended_challenge_type=raw["intended_challenge_type"],
        likely_focal_competencies=tuple(raw["likely_focal_competencies"]),
        expected_escalation_posture=raw["expected_escalation_posture"],
        main_failure_risks=tuple(raw["main_failure_risks"]),
    )


def load_all_template_families() -> list[TemplateFamilyRecord]:
    """Load, parse, and validate all template family definitions.

    Returns a list of :class:`TemplateFamilyRecord` objects in the order
    they appear in the source JSON (TF-DIV-01 through TF-DIV-12).

    Raises:
        FileNotFoundError: if the source JSON file is missing.
        ValueError: if any record fails validation or the full set of
            expected IDs (TF-DIV-01 … TF-DIV-12) is not present.
    """
    raw_list: list[dict] = json.loads(_FAMILIES_PATH.read_text(encoding="utf-8"))
    records = [_parse_record(raw) for raw in raw_list]

    found_ids = {r.family_id for r in records}
    missing_ids = sorted(set(EXPECTED_FAMILY_IDS) - found_ids)
    if missing_ids:
        raise ValueError(
            f"Template family source is missing expected IDs: {missing_ids}"
        )

    return records


def get_template_family(family_id: str) -> TemplateFamilyRecord:
    """Return the :class:`TemplateFamilyRecord` for *family_id*.

    Raises:
        KeyError: if *family_id* is not found in the loaded set.
    """
    families = {r.family_id: r for r in load_all_template_families()}
    if family_id not in families:
        raise KeyError(
            f"Unknown template family ID: {family_id!r}. "
            f"Available: {sorted(families)}"
        )
    return families[family_id]
