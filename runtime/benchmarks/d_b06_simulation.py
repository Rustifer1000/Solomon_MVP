from __future__ import annotations

from runtime.benchmarks.d_b06_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b06_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


DB06Simulation = ConfiguredBenchmarkSimulation


D_B06_SIMULATION = DB06Simulation(
    case_id="D-B06",
    default_session="D-B06-S01-generated",
    reference_session="D-B06-S01",
    benchmark_metadata={
        "descriptor_id": "d_b06_patterned_package_slice",
        "content_model": "patterned_package_slice",
        "runtime_shape": "patterned_runtime_synthesis",
        "template_family_ids": ["TF-DIV-01", "TF-DIV-04"],
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
        "descriptor_id": "d_b06_extracurricular_protocol_balance",
        "logistics_driven_caution": False,
        "fairness_warning": False,
        "flag_related_issues": ["communication_protocol", "fairness_and_parent_role"],
    },
    artifact_narrative={
        "descriptor_id": "d_b06_protocol_balance_narrative",
        "posture_style": "workable_package",
        "missing_info_emphasis": "carry_forward",
    },
    support_artifact={
        "descriptor_id": "d_b06_support_fairness_process",
        "review_focus": "fairness_process_balance",
    },
)
