from __future__ import annotations

from copy import deepcopy

from runtime.normalization import normalize_core_output


def normalize_raw_turns(raw_turns: list[dict]):
    return [normalize_core_output(raw_turn) for raw_turn in raw_turns]


def build_message_variant_raw_turns(
    reference_raw_turn_builder,
    case_bundle: dict,
    timestamp_prefix: str,
    message_overrides: dict[int, str],
) -> list[dict]:
    turns = deepcopy(reference_raw_turn_builder(case_bundle, timestamp_prefix))
    for turn_index, message_summary in message_overrides.items():
        turns[turn_index - 1]["message_summary"] = message_summary
    return turns
