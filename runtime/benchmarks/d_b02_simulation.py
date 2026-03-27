from __future__ import annotations

from runtime.benchmarks.d_b02_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
    get_varied_mock_process_variant,
)
from runtime.benchmarks.d_b02_runtime import (
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


DB02Simulation = ConfiguredBenchmarkSimulation


D_B02_SIMULATION = DB02Simulation(
    case_id="D-B02",
    default_session="D-B02-S01-generated",
    reference_session="D-B02-S01",
    benchmark_metadata={
        "descriptor_id": "d_b02_financial_domain_baseline",
        "content_model": "bespoke_financial_slice",
        "runtime_shape": "deep_stateful_runtime",
        "template_family_ids": ["TF-DIV-02"],
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
        "descriptor_id": "d_b02_financial_documentation_caution",
        "logistics_driven_caution": False,
        "fairness_warning": True,
        "flag_related_issues": ["shared_debt_allocation", "financial_documentation"],
    },
    artifact_narrative={
        "descriptor_id": "d_b02_documentation_first_narrative",
        "posture_style": "caution_bounded",
        "missing_info_emphasis": "caution",
    },
    support_artifact={
        "descriptor_id": "d_b02_support_financial_documentation",
        "review_focus": "financial_fact_gap",
    },
    next_step=(
        "Both parties should pull credit-card statements and any written records of the housing cost arrangement "
        "before the next session. Option packaging should wait until the documentation baseline is established."
    ),
)
