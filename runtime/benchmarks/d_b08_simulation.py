from __future__ import annotations

from runtime.benchmarks.d_b08_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b08_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


DB08Simulation = ConfiguredBenchmarkSimulation


D_B08_SIMULATION = DB08Simulation(
    case_id="D-B08",
    default_session="D-B08-S01-generated",
    reference_session="D-B08-S01",
    benchmark_metadata={
        "descriptor_id": "d_b08_repeated_process_breakdown_slice",
        "content_model": "patterned_escalation_slice",
        "runtime_shape": "patterned_runtime_synthesis",
        "template_family_ids": ["TF-DIV-06", "TF-DIV-07"],
        "evaluator_attention_tags": ["fairness_sensitive"],
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
        "descriptor_id": "d_b08_process_breakdown_caution",
        "logistics_driven_caution": False,
        "fairness_warning": False,
        "flag_related_issues": ["communication_protocol", "fairness_and_parent_role"],
    },
    artifact_narrative={
        "descriptor_id": "d_b08_process_breakdown_narrative",
        "posture_style": "caution_bounded",
        "missing_info_emphasis": "caution",
    },
    support_artifact={
        "descriptor_id": "d_b08_support_process_breakdown",
        "review_focus": "fairness_process_breakdown",
    },
)
