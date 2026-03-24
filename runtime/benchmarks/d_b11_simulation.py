from __future__ import annotations

from runtime.benchmarks.d_b11_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b11_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


DB11Simulation = ConfiguredBenchmarkSimulation


D_B11_SIMULATION = DB11Simulation(
    case_id="D-B11",
    default_session="D-B11-S01-generated",
    reference_session="D-B11-S01",
    benchmark_metadata={
        "descriptor_id": "d_b11_asymmetry_caution_slice",
        "content_model": "patterned_caution_slice",
        "runtime_shape": "patterned_runtime_synthesis",
        "template_family_ids": ["TF-DIV-05", "TF-DIV-02"],
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
        "descriptor_id": "d_b11_asymmetry_confidence_caution",
        "logistics_driven_caution": False,
        "fairness_warning": False,
        "flag_related_issues": ["child_expense_coordination", "communication_protocol", "fairness_and_parent_role"],
    },
    artifact_narrative={
        "descriptor_id": "d_b11_asymmetry_caution_narrative",
        "posture_style": "caution_bounded",
        "missing_info_emphasis": "caution",
    },
    support_artifact={
        "descriptor_id": "d_b11_support_asymmetry_caution",
        "review_focus": "informational_asymmetry_and_fair_participation",
    },
)
