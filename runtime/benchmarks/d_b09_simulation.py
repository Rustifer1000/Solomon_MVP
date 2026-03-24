from __future__ import annotations

from runtime.benchmarks.d_b09_authored import (
    build_mock_model_turns,
    build_reference_turns,
    build_varied_mock_model_turns,
)
from runtime.benchmarks.d_b09_runtime import (
    build_runtime_turn_plan,
    generate_runtime_assistant_turn,
    generate_runtime_client_turn,
)
from runtime.benchmarks.scaffold import (
    BenchmarkRuntimeBuilders,
    BenchmarkSourceBuilders,
    ConfiguredBenchmarkSimulation,
)


DB09Simulation = ConfiguredBenchmarkSimulation


D_B09_SIMULATION = DB09Simulation(
    case_id="D-B09",
    default_session="D-B09-S01-generated",
    reference_session="D-B09-S01",
    benchmark_metadata={
        "descriptor_id": "d_b09_domain_complexity_review_slice",
        "content_model": "patterned_escalation_slice",
        "runtime_shape": "patterned_runtime_synthesis",
        "template_family_ids": ["TF-DIV-08", "TF-DIV-02"],
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
        "descriptor_id": "d_b09_domain_complexity_review",
        "logistics_driven_caution": False,
        "fairness_warning": False,
        "flag_related_issues": [
            "parenting_schedule",
            "school_logistics",
            "child_expense_coordination",
            "communication_protocol",
        ],
    },
    artifact_narrative={
        "descriptor_id": "d_b09_complexity_review_narrative",
        "posture_style": "caution_bounded",
        "missing_info_emphasis": "caution",
    },
    support_artifact={
        "descriptor_id": "d_b09_support_domain_complexity",
        "review_focus": "domain_complexity_review",
    },
)
