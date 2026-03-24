from __future__ import annotations

"""Thin facade for the D-B04 benchmark slice.

This module preserves the stable import surface while the actual benchmark
implementation lives in smaller sibling modules:

- ``d_b04_authored.py`` for reference/mock authored turn sources
- ``d_b04_runtime.py`` for runtime-generated turn logic
- ``d_b04_simulation.py`` for simulation wiring and registration
"""

from runtime.benchmarks.d_b04_authored import (
    build_mock_model_raw_turns,
    build_mock_model_turns,
    build_reference_raw_turns,
    build_reference_turns,
    build_varied_mock_model_raw_turns,
    build_varied_mock_model_turns,
    get_varied_mock_process_variant,
)
from runtime.benchmarks.d_b04_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.d_b04_simulation import D_B04_SIMULATION, DB04Simulation

__all__ = [
    "D_B04_SIMULATION",
    "DB04Simulation",
    "build_mock_model_raw_turns",
    "build_mock_model_turns",
    "build_reference_raw_turns",
    "build_reference_turns",
    "build_runtime_turn_plan",
    "build_varied_mock_model_raw_turns",
    "build_varied_mock_model_turns",
    "generate_runtime_assistant_turn",
    "generate_runtime_client_turn",
    "get_varied_mock_process_variant",
]
