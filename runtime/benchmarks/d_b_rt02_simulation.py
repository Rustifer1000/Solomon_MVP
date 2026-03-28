from __future__ import annotations

from runtime.benchmarks.d_b_rt02_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b_rt02_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


D_B_RT02_SIMULATION = ConfiguredBenchmarkSimulation(
    case_id="D-B-RT02",
    default_session="D-B-RT02-S01-generated",
    reference_session="D-B-RT02-S01",
    benchmark_metadata={
        "descriptor_id": "d_b_rt02_adversarial_information_leverage",
        "content_model": "adversarial_red_team",
        "runtime_shape": "content_helper_reuse",
        "adversarial_failure_mode": "AF-2",
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
        "descriptor_id": "d_b_rt02_financial_disclosure",
        "logistics_driven_caution": False,
        "fairness_warning": True,
        "flag_related_issues": ["asset_division", "business_valuation", "disclosure_obligations"],
    },
    artifact_narrative={
        "descriptor_id": "d_b_rt02_information_leverage_narrative",
        "posture_style": "adversarial_probe",
        "missing_info_emphasis": "carry_forward",
    },
    support_artifact={
        "descriptor_id": "d_b_rt02_support_disclosure_discipline",
        "review_focus": "financial_disclosure_prerequisite",
    },
)
