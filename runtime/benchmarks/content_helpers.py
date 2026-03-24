from __future__ import annotations


def raw_turn_from_reference_builder(
    raw_turn_builder,
    case_bundle: dict,
    timestamp_prefix: str,
    turn_index: int,
    expected_role: str,
) -> dict:
    for raw_turn in raw_turn_builder(case_bundle, timestamp_prefix):
        if raw_turn["turn_index"] == turn_index:
            if raw_turn["role"] != expected_role:
                raise ValueError(
                    f"Turn {turn_index} expected role {expected_role}, found {raw_turn['role']}"
                )
            return raw_turn
    raise ValueError(f"Turn {turn_index} was not found in the reference raw turn builder.")
