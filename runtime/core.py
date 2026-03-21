from __future__ import annotations

"""Compatibility re-exports for benchmark simulation helpers.

The D-B04-specific runtime behavior now lives under ``runtime.benchmarks``.
This module remains as a thin compatibility surface while imports are updated.
"""

from runtime.benchmarks.d_b04 import (
    build_mock_model_raw_turns,
    build_mock_model_turns,
    build_reference_raw_turns,
    build_reference_turns,
    build_varied_mock_model_raw_turns,
    build_varied_mock_model_turns,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
    get_varied_mock_process_variant,
)

__all__ = [
    "build_mock_model_raw_turns",
    "build_mock_model_turns",
    "build_reference_raw_turns",
    "build_reference_turns",
    "build_varied_mock_model_raw_turns",
    "build_varied_mock_model_turns",
    "generate_runtime_assistant_turn",
    "generate_runtime_client_turn",
    "get_varied_mock_process_variant",
]
