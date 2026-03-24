from __future__ import annotations

from runtime.benchmarks.d_b10_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b10_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


DB10Simulation = ConfiguredBenchmarkSimulation


D_B10_SIMULATION = DB10Simulation(
    case_id="D-B10",
    default_session="D-B10-S01-generated",
    reference_session="D-B10-S01",
    benchmark_metadata={
        "descriptor_id": "d_b10_emotional_heat_workable_slice",
        "content_model": "patterned_package_slice",
        "runtime_shape": "patterned_runtime_synthesis",
        "template_family_ids": ["TF-DIV-03", "TF-DIV-04"],
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
        "descriptor_id": "d_b10_emotional_heat_workable",
        "logistics_driven_caution": False,
        "fairness_warning": False,
        "flag_related_issues": ["parenting_schedule", "communication_protocol"],
    },
    artifact_narrative={
        "descriptor_id": "d_b10_emotional_heat_narrative",
        "posture_style": "workable_package",
        "missing_info_emphasis": "carry_forward",
    },
    support_artifact={
        "descriptor_id": "d_b10_support_emotional_heat",
        "review_focus": "emotional_intensity_without_escalation",
    },
)
