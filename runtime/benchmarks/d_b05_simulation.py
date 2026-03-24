from __future__ import annotations

from runtime.benchmarks.d_b05_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b05_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


DB05Simulation = ConfiguredBenchmarkSimulation


D_B05_SIMULATION = DB05Simulation(
    case_id="D-B05",
    default_session="D-B05-S01-generated",
    reference_session="D-B05-S01",
    benchmark_metadata={
        "descriptor_id": "d_b05_patterned_package_slice",
        "content_model": "patterned_package_slice",
        "runtime_shape": "content_helper_reuse",
        "template_family_ids": ["TF-DIV-01", "TF-DIV-04"],
    },
    sources=BenchmarkSourceBuilders(
        reference=build_reference_turns,
        mock_model=build_mock_model_turns,
        varied_mock_model=build_varied_mock_model_turns,
    ),
    runtime=BenchmarkRuntimeBuilders(
        turn_plan=build_runtime_turn_plan,
        assistant_turn=generate_runtime_assistant_turn,
        client_turn=generate_runtime_client_turn,
    ),
    plugin_policy={
        "descriptor_id": "d_b05_break_schedule_packaging",
        "logistics_driven_caution": False,
        "fairness_warning": False,
        "flag_related_issues": ["communication_protocol", "parenting_schedule"],
    },
    artifact_narrative={
        "descriptor_id": "d_b05_workable_package_narrative",
        "posture_style": "workable_package",
        "missing_info_emphasis": "carry_forward",
    },
    support_artifact={
        "descriptor_id": "d_b05_support_workable_package",
        "review_focus": "package_confirmation",
    },
)
