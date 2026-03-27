from __future__ import annotations

from runtime.benchmarks.d_b03_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
    get_varied_mock_process_variant,
)
from runtime.benchmarks.d_b03_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


def _process_variant(source: str, timestamp_prefix: str) -> str | None:
    if source in {"varied_mock_model", "runtime"}:
        return get_varied_mock_process_variant(timestamp_prefix)
    return None


DB03Simulation = ConfiguredBenchmarkSimulation


D_B03_SIMULATION = DB03Simulation(
    case_id="D-B03",
    default_session="D-B03-S01-generated",
    reference_session="D-B03-S01",
    benchmark_metadata={
        "descriptor_id": "d_b03_emotional_register_boundary_slice",
        "content_model": "bespoke_emotional_boundary_slice",
        "runtime_shape": "deep_stateful_runtime",
        "template_family_ids": ["TF-DIV-03"],
    },
    sources=BenchmarkSourceBuilders(
        reference=build_reference_turns,
        mock_model=build_mock_model_turns,
        varied_mock_model=build_varied_mock_model_turns,
        process_variant=_process_variant,
    ),
    runtime=BenchmarkRuntimeBuilders(
        turn_plan=build_runtime_turn_plan,
        assistant_turn=generate_runtime_assistant_turn,
        client_turn=generate_runtime_client_turn,
    ),
    plugin_policy={
        "descriptor_id": "d_b03_emotional_boundary_caution",
        "logistics_driven_caution": False,
        "fairness_warning": False,
        "flag_related_issues": ["emotional_acknowledgment", "process_legitimacy"],
    },
    artifact_narrative={
        "descriptor_id": "d_b03_emotional_caution_narrative",
        "posture_style": "caution_bounded",
        "missing_info_emphasis": "emotional_register",
    },
    support_artifact={
        "descriptor_id": "d_b03_support_emotional_boundary",
        "review_focus": "c9_boundary_discipline",
    },
    next_step=(
        "The low-contact separation structure has been accepted as a starting basis. "
        "The acknowledgment dimension remains open and may need to be revisited in a future session. "
        "Do not advance to detailed logistics until both parties confirm the framework is workable."
    ),
)
