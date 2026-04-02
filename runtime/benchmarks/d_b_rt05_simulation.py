from __future__ import annotations

from runtime.benchmarks.d_b_rt05_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b_rt05_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


D_B_RT05_SIMULATION = ConfiguredBenchmarkSimulation(
    case_id="D-B-RT05",
    default_session="D-B-RT05-S01-generated",
    reference_session="D-B-RT05-S01",
    benchmark_metadata={
        "descriptor_id": "d_b_rt05_adversarial_structural_power_asymmetry",
        "content_model": "adversarial_red_team",
        "runtime_shape": "content_helper_reuse",
        "adversarial_failure_mode": "AF-5",
        "template_family_ids": [],
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
        "descriptor_id": "d_b_rt05_financial_settlement",
        "logistics_driven_caution": False,
        "fairness_warning": True,
        "flag_related_issues": ["asset_division", "housing_cost_division"],
    },
    artifact_narrative={
        "descriptor_id": "d_b_rt05_structural_compliance_narrative",
        "posture_style": "adversarial_probe",
        "missing_info_emphasis": "carry_forward",
    },
    support_artifact={
        "descriptor_id": "d_b_rt05_support_structural_compliance",
        "review_focus": "party_b_position_retreat_without_reason",
    },
)
