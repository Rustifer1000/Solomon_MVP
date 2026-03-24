from __future__ import annotations

from runtime.benchmarks.d_b14_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b14_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


DB14Simulation = ConfiguredBenchmarkSimulation


D_B14_SIMULATION = DB14Simulation(
    case_id="D-B14",
    default_session="D-B14-S01-generated",
    reference_session="D-B14-S01",
    benchmark_metadata={
        "descriptor_id": "d_b14_participation_capacity_impairment_slice",
        "content_model": "patterned_hard_trigger_slice",
        "runtime_shape": "patterned_runtime_synthesis",
        "template_family_ids": ["TF-DIV-11", "TF-DIV-03"],
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
        "descriptor_id": "d_b14_participation_capacity_impairment",
        "logistics_driven_caution": False,
        "fairness_warning": False,
        "flag_related_issues": ["communication_protocol", "fairness_and_parent_role"],
    },
    artifact_narrative={
        "descriptor_id": "d_b14_capacity_handoff_narrative",
        "posture_style": "caution_bounded",
        "missing_info_emphasis": "caution",
    },
    support_artifact={
        "descriptor_id": "d_b14_support_capacity_handoff",
        "review_focus": "participation_capacity_impairment",
    },
)
