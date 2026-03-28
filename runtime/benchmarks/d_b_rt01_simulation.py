from __future__ import annotations

from runtime.benchmarks.d_b_rt01_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b_rt01_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


D_B_RT01_SIMULATION = ConfiguredBenchmarkSimulation(
    case_id="D-B-RT01",
    default_session="D-B-RT01-S01-generated",
    reference_session="D-B-RT01-S01",
    benchmark_metadata={
        "descriptor_id": "d_b_rt01_adversarial_compliance_trap",
        "content_model": "adversarial_red_team",
        "runtime_shape": "content_helper_reuse",
        "adversarial_failure_mode": "AF-3",
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
        "descriptor_id": "d_b_rt01_parenting_schedule",
        "logistics_driven_caution": False,
        "fairness_warning": True,
        "flag_related_issues": ["parenting_schedule"],
    },
    artifact_narrative={
        "descriptor_id": "d_b_rt01_compliance_trap_narrative",
        "posture_style": "adversarial_probe",
        "missing_info_emphasis": "carry_forward",
    },
    support_artifact={
        "descriptor_id": "d_b_rt01_support_interest_development",
        "review_focus": "party_b_interest_articulation",
    },
)
