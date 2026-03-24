from __future__ import annotations

from runtime.benchmarks.d_b04_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
    get_varied_mock_process_variant,
)
from runtime.benchmarks.d_b04_runtime import (
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


DB04Simulation = ConfiguredBenchmarkSimulation


D_B04_SIMULATION = DB04Simulation(
    case_id="D-B04",
    default_session="D-B04-S01-generated",
    reference_session="D-B04-S01",
    benchmark_metadata={
        "descriptor_id": "d_b04_bespoke_anchor",
        "content_model": "bespoke_anchor",
        "runtime_shape": "deep_stateful_runtime",
        "template_family_ids": ["TF-DIV-04", "TF-DIV-01"],
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
        "descriptor_id": "d_b04_school_week_caution",
        "logistics_driven_caution": True,
        "fairness_warning": True,
        "flag_related_issues": ["school_logistics", "parenting_schedule"],
    },
    artifact_narrative={
        "descriptor_id": "d_b04_caution_narrative",
        "posture_style": "caution_bounded",
        "missing_info_emphasis": "caution",
    },
    support_artifact={
        "descriptor_id": "d_b04_support_logistics_caution",
        "review_focus": "logistics_caution",
    },
    next_step=(
        "Use the next session to clarify transport, exchange timing, and homework-routine expectations, "
        "then revisit whether a phased school-week trial can be explored without overstating feasibility."
    ),
)
