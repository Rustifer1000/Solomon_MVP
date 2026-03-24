from __future__ import annotations

from runtime.benchmarks.d_b07_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b07_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


DB07Simulation = ConfiguredBenchmarkSimulation


D_B07_SIMULATION = DB07Simulation(
    case_id="D-B07",
    default_session="D-B07-S01-generated",
    reference_session="D-B07-S01",
    benchmark_metadata={
        "descriptor_id": "d_b07_patterned_package_slice",
        "content_model": "patterned_package_slice",
        "runtime_shape": "content_helper_reuse",
        "template_family_ids": ["TF-DIV-02", "TF-DIV-12"],
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
        "descriptor_id": "d_b07_expense_reimbursement_protocol",
        "logistics_driven_caution": False,
        "fairness_warning": False,
        "flag_related_issues": ["child_expense_coordination", "communication_protocol"],
    },
    artifact_narrative={
        "descriptor_id": "d_b07_expense_package_narrative",
        "posture_style": "workable_package",
        "missing_info_emphasis": "carry_forward",
    },
    support_artifact={
        "descriptor_id": "d_b07_support_expense_protocol",
        "review_focus": "expense_protocol",
    },
)
