from __future__ import annotations

import json
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schema"
RECOMMENDED_PERSONA_FIELDS = (
    "emotional_triggers",
    "disclosure_tendencies",
    "compromise_willingness",
    "response_to_perceived_bias_or_pressure",
)


def _load_schema(schema_name: str) -> dict:
    return json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))


def _matches_type(value, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return True


def _validate_schema_subset(instance, schema: dict, path: str = "root") -> list[str]:
    errors: list[str] = []

    if "type" in schema:
        expected_type = schema["type"]
        if isinstance(expected_type, list):
            if not any(_matches_type(instance, candidate) for candidate in expected_type):
                return [f"{path} does not match allowed types {expected_type}"]
        elif not _matches_type(instance, expected_type):
            return [f"{path} does not match type {expected_type}"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path} must equal {schema['const']}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path} must be one of {schema['enum']}")

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}.{key} is required")
        if schema.get("additionalProperties") is False:
            unknown = set(instance.keys()) - set(properties.keys())
            for key in sorted(unknown):
                errors.append(f"{path}.{key} is not allowed by schema")
        for key, value in instance.items():
            if key in properties:
                errors.extend(_validate_schema_subset(value, properties[key], f"{path}.{key}"))
    elif isinstance(instance, list):
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(instance):
                errors.extend(_validate_schema_subset(item, item_schema, f"{path}[{index}]"))
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path} must contain at least {min_items} items")

    return errors


def validate_persona_profile(persona: dict) -> tuple[list[str], list[str]]:
    schema = _load_schema("persona_profile.schema.json")
    errors = _validate_schema_subset(persona, schema)
    warnings = [
        f"recommended field missing: {field}"
        for field in RECOMMENDED_PERSONA_FIELDS
        if field not in persona
    ]
    return errors, warnings
