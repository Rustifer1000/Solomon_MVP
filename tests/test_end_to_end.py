from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from runtime.benchmarks import get_benchmark_simulation
from runtime.benchmarks.base import RuntimeTurnPlanEntry
from runtime.benchmarks.d_b04 import (
    build_mock_model_raw_turns,
    build_mock_model_turns,
    build_reference_raw_turns,
    build_reference_turns,
    build_runtime_turn_plan,
    build_varied_mock_model_raw_turns,
    build_varied_mock_model_turns,
    generate_runtime_client_turn,
    get_varied_mock_process_variant,
)
from runtime.benchmarks.d_b01_simulation import D_B01_SIMULATION
from runtime.benchmarks.d_b02_simulation import D_B02_SIMULATION
from runtime.benchmarks.d_b03_simulation import D_B03_SIMULATION
from runtime.benchmarks.d_b04_simulation import D_B04_SIMULATION
from runtime.benchmarks.d_b05_simulation import D_B05_SIMULATION
from runtime.benchmarks.d_b06_simulation import D_B06_SIMULATION
from runtime.benchmarks.d_b07_simulation import D_B07_SIMULATION
from runtime.benchmarks.d_b08_simulation import D_B08_SIMULATION
from runtime.benchmarks.d_b09_simulation import D_B09_SIMULATION
from runtime.benchmarks.d_b10_simulation import D_B10_SIMULATION
from runtime.benchmarks.d_b11_simulation import D_B11_SIMULATION
from runtime.benchmarks.d_b12_simulation import D_B12_SIMULATION
from runtime.benchmarks.d_b13_simulation import D_B13_SIMULATION
from runtime.benchmarks.d_b14_simulation import D_B14_SIMULATION
from runtime.contracts import CandidateTurn, RiskCheck, StateDelta, validate_candidate_turn
from runtime.artifacts import write_artifacts
from runtime.escalation import determine_escalation
from runtime.evaluator_artifact_validation import (
    validate_flags_artifact,
    validate_reference_evaluation_example,
    validate_reference_evaluation_summary_text,
    validate_reference_expert_review_example,
)
from runtime.evaluator_operations import (
    build_calibration_review_seed,
    build_fairness_review_seed,
    compare_benchmark_runs,
)
from runtime.fairness_checks import run_first_pass_fairness_checks
from runtime.loaders import load_case_bundle
from runtime.normalization import normalize_core_output
from runtime.orchestrator import _run_runtime_generated_session
from runtime.persona_validation import validate_persona_profile
from runtime.plugins.divorce_shared import qualify_case_shared
from runtime.plugins import get_plugin_runtime
from runtime.policy_profiles import get_policy_profile
from runtime.session_validation import validate_session_trace, validate_support_artifact_package
from runtime.state import initialize_session_state


REPO_ROOT = Path(__file__).resolve().parents[1]
D_B01_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B01"
D_B02_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B02"
D_B03_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B03"
CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B04"
D_B05_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B05"
D_B06_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B06"
D_B07_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B07"
D_B08_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B08"
D_B09_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B09"
D_B10_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B10"
D_B11_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B11"
D_B12_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B12"
D_B13_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B13"
D_B14_CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B14"


class EndToEndScaffoldTest(unittest.TestCase):
    def _run_benchmark(
        self,
        source: str = "runtime",
        case_dir: Path = CASE_DIR,
        policy_profile: str = "sim_minimal",
        review_transcript_renderer: str = "none",
    ) -> dict:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        output_dir = Path(temp_dir.name) / f"{case_dir.name}-S01-{source}"
        command = [
            sys.executable,
            "-m",
            "runtime.cli.run_benchmark",
            "--case-dir",
            str(case_dir),
            "--output-dir",
            str(output_dir),
            "--source",
            source,
            "--policy-profile",
            policy_profile,
            "--review-transcript-renderer",
            review_transcript_renderer,
            "--generated-at",
            "2026-03-19T12:00:00Z",
        ]
        subprocess.run(command, cwd=REPO_ROOT, check=True)
        return {
            "output_dir": output_dir,
            "session_meta": json.loads((output_dir / "session_meta.json").read_text(encoding="utf-8")),
            "run_meta": json.loads((output_dir / "run_meta.json").read_text(encoding="utf-8")),
            "trace": json.loads((output_dir / "interaction_trace.json").read_text(encoding="utf-8")),
            "positions": json.loads((output_dir / "positions.json").read_text(encoding="utf-8")),
            "facts": json.loads((output_dir / "facts_snapshot.json").read_text(encoding="utf-8")),
            "flags": json.loads((output_dir / "flags.json").read_text(encoding="utf-8")),
            "missing_info": json.loads((output_dir / "missing_info.json").read_text(encoding="utf-8")),
            "summary": (output_dir / "summary.txt").read_text(encoding="utf-8"),
        }

    def test_benchmark_registry_returns_d_b01_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B01_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B01")

    def test_benchmark_registry_returns_d_b02_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B02_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B02")

    def test_benchmark_registry_returns_d_b03_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B03_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B03")

    def test_benchmark_registry_returns_d_b04_simulation(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B04")

    def test_benchmark_registry_returns_d_b05_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B05_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B05")

    def test_benchmark_registry_returns_d_b06_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B06")

    def test_benchmark_registry_returns_d_b07_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B07_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B07")

    def test_benchmark_registry_returns_d_b08_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B08_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B08")

    def test_benchmark_registry_returns_d_b09_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B09_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B09")

    def test_benchmark_registry_returns_d_b10_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B10_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B10")

    def test_benchmark_registry_returns_d_b11_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B11_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B11")

    def test_benchmark_registry_returns_d_b12_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B12_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B12")

    def test_benchmark_registry_returns_d_b13_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B13_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B13")

    def test_benchmark_registry_returns_d_b14_simulation(self) -> None:
        case_bundle = load_case_bundle(D_B14_CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B14")

    def test_active_divorce_slices_have_evaluator_review_paths(self) -> None:
        for case_dir in [D_B01_CASE_DIR, D_B02_CASE_DIR, D_B03_CASE_DIR, CASE_DIR, D_B05_CASE_DIR, D_B06_CASE_DIR, D_B07_CASE_DIR, D_B08_CASE_DIR, D_B09_CASE_DIR, D_B10_CASE_DIR, D_B11_CASE_DIR, D_B12_CASE_DIR, D_B13_CASE_DIR, D_B14_CASE_DIR]:
            self.assertTrue((case_dir / "evaluator_review_path.md").exists(), f"Missing evaluator path for {case_dir.name}")

    def test_active_divorce_slice_metadata_keeps_evaluator_artifact_expectations_consistent(self) -> None:
        for case_dir in [D_B01_CASE_DIR, D_B02_CASE_DIR, D_B03_CASE_DIR, CASE_DIR, D_B05_CASE_DIR, D_B06_CASE_DIR, D_B07_CASE_DIR, D_B08_CASE_DIR, D_B09_CASE_DIR, D_B10_CASE_DIR, D_B11_CASE_DIR, D_B12_CASE_DIR, D_B13_CASE_DIR, D_B14_CASE_DIR]:
            metadata = json.loads((case_dir / "case_metadata.json").read_text(encoding="utf-8"))
            required = metadata["artifact_expectations"]["required"]
            recommended = metadata["artifact_expectations"]["recommended"]

            self.assertEqual(
                required,
                [
                    "session_meta.json",
                    "run_meta.json",
                    "interaction_trace.json",
                    "positions.json",
                    "facts_snapshot.json",
                    "flags.json",
                    "missing_info.json",
                    "summary.txt",
                    "review_cover_sheet.txt",
                    "review_transcript.txt",
                    "review_outcome_sheet.txt",
                ],
            )
            self.assertEqual(recommended, ["evaluation.json", "evaluation_summary.txt"])
            self.assertTrue(metadata["expected_focal_scoring_areas"])

    def test_plugin_registry_returns_divorce_plugin_runtime(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        plugin_runtime = get_plugin_runtime(case_bundle)

        self.assertEqual(plugin_runtime.plugin_type, "divorce")

    def test_shared_artifact_layers_do_not_import_divorce_package_vocabulary_directly(self) -> None:
        artifacts_source = (REPO_ROOT / "runtime" / "artifacts.py").read_text(encoding="utf-8")
        support_source = (REPO_ROOT / "runtime" / "support_artifacts.py").read_text(encoding="utf-8")

        self.assertNotIn("from runtime.plugins.divorce_shared import PACKAGE_ELEMENT_LABELS", artifacts_source)
        self.assertNotIn("from runtime.plugins.divorce_shared import PACKAGE_ELEMENT_LABELS", support_source)

    def test_shared_divorce_qualification_reflects_broader_divorce_issue_families(self) -> None:
        qualification = qualify_case_shared(load_case_bundle(D_B07_CASE_DIR))

        self.assertIn("communication_protocol", qualification["issue_taxonomy"])
        self.assertIn("fairness_and_parent_role", qualification["issue_taxonomy"])
        self.assertIn("child_expense_coordination", qualification["issue_taxonomy"])
        self.assertIn("fair co-parent communication process", qualification["feasibility_constraints"])
        self.assertIn("child-expense documentation and reimbursement workflow", qualification["feasibility_constraints"])
        self.assertIn("bounded process packages", qualification["caution_note"])

    def test_plugin_registry_rejects_unknown_plugin_type(self) -> None:
        with self.assertRaises(NotImplementedError):
            get_plugin_runtime({"case_metadata": {"plugin_type": "workplace"}})

    def test_plugin_registry_rejects_missing_plugin_type_context(self) -> None:
        with self.assertRaises(KeyError):
            get_plugin_runtime({})

    def test_d_b04_simulation_owns_custom_next_step_policy(self) -> None:
        next_step = D_B04_SIMULATION.finalize_next_step({"summary_state": {}, "missing_info": [], "options": []})
        self.assertIn("transport, exchange timing, and homework-routine expectations", next_step)

    def test_d_b05_simulation_uses_generic_next_step_policy(self) -> None:
        self.assertIsNone(D_B05_SIMULATION.finalize_next_step({"summary_state": {}, "missing_info": [], "options": []}))

    def test_divorce_slices_expose_benchmark_owned_policy_descriptors(self) -> None:
        d_b01_policy = D_B01_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B01_CASE_DIR))
        d_b02_policy = D_B02_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B02_CASE_DIR))
        d_b03_policy = D_B03_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B03_CASE_DIR))
        d_b04_policy = D_B04_SIMULATION.plugin_policy_descriptor(load_case_bundle(CASE_DIR))
        d_b05_policy = D_B05_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B05_CASE_DIR))
        d_b06_policy = D_B06_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B06_CASE_DIR))
        d_b07_policy = D_B07_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B07_CASE_DIR))
        d_b08_policy = D_B08_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B08_CASE_DIR))
        d_b09_policy = D_B09_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B09_CASE_DIR))
        d_b10_policy = D_B10_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B10_CASE_DIR))
        d_b11_policy = D_B11_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B11_CASE_DIR))
        d_b12_policy = D_B12_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B12_CASE_DIR))
        d_b13_policy = D_B13_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B13_CASE_DIR))
        d_b14_policy = D_B14_SIMULATION.plugin_policy_descriptor(load_case_bundle(D_B14_CASE_DIR))

        self.assertEqual(d_b01_policy["descriptor_id"], "d_b01_cooperative_logistics_packaging")
        self.assertEqual(d_b02_policy["descriptor_id"], "d_b02_financial_documentation_caution")
        self.assertEqual(d_b03_policy["descriptor_id"], "d_b03_emotional_boundary_caution")
        self.assertEqual(d_b04_policy["descriptor_id"], "d_b04_school_week_caution")
        self.assertEqual(d_b05_policy["descriptor_id"], "d_b05_break_schedule_packaging")
        self.assertEqual(d_b06_policy["descriptor_id"], "d_b06_extracurricular_protocol_balance")
        self.assertEqual(d_b07_policy["descriptor_id"], "d_b07_expense_reimbursement_protocol")
        self.assertEqual(d_b08_policy["descriptor_id"], "d_b08_process_breakdown_caution")
        self.assertEqual(d_b09_policy["descriptor_id"], "d_b09_domain_complexity_review")
        self.assertEqual(d_b10_policy["descriptor_id"], "d_b10_emotional_heat_workable")
        self.assertEqual(d_b11_policy["descriptor_id"], "d_b11_asymmetry_confidence_caution")
        self.assertEqual(d_b12_policy["descriptor_id"], "d_b12_emotional_flooding_caution")
        self.assertEqual(d_b13_policy["descriptor_id"], "d_b13_safety_compromised_participation")
        self.assertEqual(d_b14_policy["descriptor_id"], "d_b14_participation_capacity_impairment")
        self.assertNotEqual(d_b04_policy["flag_related_issues"], d_b06_policy["flag_related_issues"])

    def test_divorce_slices_expose_benchmark_owned_artifact_narrative_policy(self) -> None:
        d_b01_policy = D_B01_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B01_CASE_DIR))
        d_b02_policy = D_B02_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B02_CASE_DIR))
        d_b03_policy = D_B03_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B03_CASE_DIR))
        d_b04_policy = D_B04_SIMULATION.artifact_narrative_policy(load_case_bundle(CASE_DIR))
        d_b05_policy = D_B05_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B05_CASE_DIR))
        d_b06_policy = D_B06_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B06_CASE_DIR))
        d_b07_policy = D_B07_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B07_CASE_DIR))
        d_b08_policy = D_B08_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B08_CASE_DIR))
        d_b09_policy = D_B09_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B09_CASE_DIR))
        d_b10_policy = D_B10_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B10_CASE_DIR))
        d_b11_policy = D_B11_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B11_CASE_DIR))
        d_b12_policy = D_B12_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B12_CASE_DIR))
        d_b13_policy = D_B13_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B13_CASE_DIR))
        d_b14_policy = D_B14_SIMULATION.artifact_narrative_policy(load_case_bundle(D_B14_CASE_DIR))

        self.assertEqual(d_b01_policy["descriptor_id"], "d_b01_cooperative_package_narrative")
        self.assertEqual(d_b02_policy["descriptor_id"], "d_b02_documentation_first_narrative")
        self.assertEqual(d_b03_policy["descriptor_id"], "d_b03_emotional_caution_narrative")
        self.assertEqual(d_b04_policy["descriptor_id"], "d_b04_caution_narrative")
        self.assertEqual(d_b05_policy["descriptor_id"], "d_b05_workable_package_narrative")
        self.assertEqual(d_b06_policy["descriptor_id"], "d_b06_protocol_balance_narrative")
        self.assertEqual(d_b07_policy["descriptor_id"], "d_b07_expense_package_narrative")
        self.assertEqual(d_b08_policy["descriptor_id"], "d_b08_process_breakdown_narrative")
        self.assertEqual(d_b09_policy["descriptor_id"], "d_b09_complexity_review_narrative")
        self.assertEqual(d_b10_policy["descriptor_id"], "d_b10_emotional_heat_narrative")
        self.assertEqual(d_b11_policy["descriptor_id"], "d_b11_asymmetry_caution_narrative")
        self.assertEqual(d_b12_policy["descriptor_id"], "d_b12_emotional_flooding_narrative")
        self.assertEqual(d_b13_policy["descriptor_id"], "d_b13_safety_handoff_narrative")
        self.assertEqual(d_b14_policy["descriptor_id"], "d_b14_capacity_handoff_narrative")

    def test_divorce_slices_expose_support_artifact_policy_descriptors(self) -> None:
        d_b01_policy = D_B01_SIMULATION.support_artifact_policy(load_case_bundle(D_B01_CASE_DIR))
        d_b02_policy = D_B02_SIMULATION.support_artifact_policy(load_case_bundle(D_B02_CASE_DIR))
        d_b03_policy = D_B03_SIMULATION.support_artifact_policy(load_case_bundle(D_B03_CASE_DIR))
        d_b04_policy = D_B04_SIMULATION.support_artifact_policy(load_case_bundle(CASE_DIR))
        d_b06_policy = D_B06_SIMULATION.support_artifact_policy(load_case_bundle(D_B06_CASE_DIR))
        d_b08_policy = D_B08_SIMULATION.support_artifact_policy(load_case_bundle(D_B08_CASE_DIR))
        d_b09_policy = D_B09_SIMULATION.support_artifact_policy(load_case_bundle(D_B09_CASE_DIR))
        d_b10_policy = D_B10_SIMULATION.support_artifact_policy(load_case_bundle(D_B10_CASE_DIR))
        d_b11_policy = D_B11_SIMULATION.support_artifact_policy(load_case_bundle(D_B11_CASE_DIR))
        d_b12_policy = D_B12_SIMULATION.support_artifact_policy(load_case_bundle(D_B12_CASE_DIR))
        d_b13_policy = D_B13_SIMULATION.support_artifact_policy(load_case_bundle(D_B13_CASE_DIR))
        d_b14_policy = D_B14_SIMULATION.support_artifact_policy(load_case_bundle(D_B14_CASE_DIR))

        self.assertEqual(d_b01_policy["descriptor_id"], "d_b01_support_workable_logistics")
        self.assertEqual(d_b02_policy["descriptor_id"], "d_b02_support_financial_documentation")
        self.assertEqual(d_b03_policy["descriptor_id"], "d_b03_support_emotional_boundary")
        self.assertEqual(d_b04_policy["descriptor_id"], "d_b04_support_logistics_caution")
        self.assertEqual(d_b06_policy["descriptor_id"], "d_b06_support_fairness_process")
        self.assertEqual(d_b08_policy["descriptor_id"], "d_b08_support_process_breakdown")
        self.assertEqual(d_b09_policy["descriptor_id"], "d_b09_support_domain_complexity")
        self.assertEqual(d_b10_policy["descriptor_id"], "d_b10_support_emotional_heat")
        self.assertEqual(d_b11_policy["descriptor_id"], "d_b11_support_asymmetry_caution")
        self.assertEqual(d_b12_policy["descriptor_id"], "d_b12_support_emotional_flooding")
        self.assertEqual(d_b13_policy["descriptor_id"], "d_b13_support_protected_handoff")
        self.assertEqual(d_b14_policy["descriptor_id"], "d_b14_support_capacity_handoff")

    def test_divorce_slices_expose_template_family_coverage_in_benchmark_descriptors(self) -> None:
        d_b04_descriptor = D_B04_SIMULATION.benchmark_descriptor(load_case_bundle(CASE_DIR))
        d_b06_descriptor = D_B06_SIMULATION.benchmark_descriptor(load_case_bundle(D_B06_CASE_DIR))
        d_b07_descriptor = D_B07_SIMULATION.benchmark_descriptor(load_case_bundle(D_B07_CASE_DIR))
        d_b08_descriptor = D_B08_SIMULATION.benchmark_descriptor(load_case_bundle(D_B08_CASE_DIR))
        d_b09_descriptor = D_B09_SIMULATION.benchmark_descriptor(load_case_bundle(D_B09_CASE_DIR))
        d_b10_descriptor = D_B10_SIMULATION.benchmark_descriptor(load_case_bundle(D_B10_CASE_DIR))
        d_b11_descriptor = D_B11_SIMULATION.benchmark_descriptor(load_case_bundle(D_B11_CASE_DIR))
        d_b12_descriptor = D_B12_SIMULATION.benchmark_descriptor(load_case_bundle(D_B12_CASE_DIR))
        d_b13_descriptor = D_B13_SIMULATION.benchmark_descriptor(load_case_bundle(D_B13_CASE_DIR))
        d_b14_descriptor = D_B14_SIMULATION.benchmark_descriptor(load_case_bundle(D_B14_CASE_DIR))

        self.assertIn("TF-DIV-04", d_b04_descriptor["template_family_ids"])
        self.assertIn("TF-DIV-02", d_b07_descriptor["template_family_ids"])
        self.assertIn("TF-DIV-06", d_b08_descriptor["template_family_ids"])
        self.assertIn("TF-DIV-08", d_b09_descriptor["template_family_ids"])
        self.assertIn("TF-DIV-03", d_b10_descriptor["template_family_ids"])
        self.assertIn("TF-DIV-05", d_b11_descriptor["template_family_ids"])
        self.assertIn("TF-DIV-09", d_b12_descriptor["template_family_ids"])
        self.assertIn("TF-DIV-10", d_b13_descriptor["template_family_ids"])
        self.assertIn("TF-DIV-11", d_b14_descriptor["template_family_ids"])
        self.assertIn("fairness_sensitive", d_b06_descriptor["evaluator_attention_tags"])
        self.assertIn("fairness_sensitive", d_b08_descriptor["evaluator_attention_tags"])
        self.assertIn("fairness_sensitive", d_b10_descriptor["evaluator_attention_tags"])

    def test_runtime_run_meta_records_plugin_owned_package_labels_and_evaluator_helper_policy(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B06_CASE_DIR)
        case_context = run["run_meta"]["case_context"]

        self.assertEqual(case_context["package_element_labels"]["written_summary_option"], "written summaries")
        self.assertEqual(case_context["evaluator_helper_policy"]["descriptor_id"], "divorce_evaluator_helpers_v0")

    def test_divorce_persona_profiles_validate_against_schema(self) -> None:
        for case_dir in [D_B01_CASE_DIR, D_B02_CASE_DIR, D_B03_CASE_DIR, CASE_DIR, D_B05_CASE_DIR, D_B06_CASE_DIR, D_B07_CASE_DIR, D_B08_CASE_DIR, D_B09_CASE_DIR, D_B10_CASE_DIR, D_B11_CASE_DIR, D_B12_CASE_DIR, D_B13_CASE_DIR, D_B14_CASE_DIR]:
            for persona_path in sorted((case_dir / "personas").glob("*.json")):
                persona = json.loads(persona_path.read_text(encoding="utf-8"))
                errors, _warnings = validate_persona_profile(persona)
                self.assertEqual(errors, [], f"{persona_path.name} failed persona schema validation")

    def test_d_b10_persona_profiles_include_all_recommended_role_profile_fields(self) -> None:
        for persona_path in sorted((D_B10_CASE_DIR / "personas").glob("*.json")):
            persona = json.loads(persona_path.read_text(encoding="utf-8"))
            _errors, warnings = validate_persona_profile(persona)
            self.assertEqual(warnings, [], f"{persona_path.name} is missing recommended persona fields")

    def test_first_pass_fairness_checks_surface_expected_attention_by_slice(self) -> None:
        d_b06 = run_first_pass_fairness_checks(self._run_benchmark("runtime", case_dir=D_B06_CASE_DIR)["output_dir"])
        d_b08 = run_first_pass_fairness_checks(self._run_benchmark("runtime", case_dir=D_B08_CASE_DIR)["output_dir"])
        d_b10 = run_first_pass_fairness_checks(self._run_benchmark("runtime", case_dir=D_B10_CASE_DIR)["output_dir"])

        self.assertTrue(d_b06["expected_fairness_attention"])
        self.assertEqual(d_b06["status"], "ok")
        self.assertTrue(d_b08["expected_fairness_attention"])
        self.assertIn("fairness_breakdown", d_b08["fairness_flag_types"])
        self.assertEqual(d_b08["status"], "ok")
        self.assertTrue(d_b10["expected_fairness_attention"])
        self.assertTrue(d_b10["summary_mentions_fairness"] or d_b10["structured_mentions_fairness"])

    def test_benchmark_descriptors_make_d_b04_anchor_status_explicit(self) -> None:
        d_b04_descriptor = D_B04_SIMULATION.benchmark_descriptor(load_case_bundle(CASE_DIR))
        d_b05_descriptor = D_B05_SIMULATION.benchmark_descriptor(load_case_bundle(D_B05_CASE_DIR))

        self.assertEqual(d_b04_descriptor["descriptor_id"], "d_b04_bespoke_anchor")
        self.assertEqual(d_b04_descriptor["content_model"], "bespoke_anchor")
        self.assertEqual(d_b05_descriptor["content_model"], "patterned_package_slice")

    def test_initialize_session_state_records_source(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="mock_model")

        self.assertEqual(state["meta"]["source"], "mock_model")

    def test_loader_and_cli_use_simulation_defaults_not_hardcoded_d_b04_values(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(case_bundle["reference_session_dir"], simulation.reference_session_dir(CASE_DIR))

        from runtime.cli import run_benchmark

        fake_args = type(
            "Args",
            (),
            {
                "case_dir": CASE_DIR,
                "output_dir": CASE_DIR / "tmp-output",
                "session_id": None,
                "policy_profile": "sim_minimal",
                "source": "runtime",
                "generated_at": "2026-03-19T12:00:00Z",
            },
        )()

        with mock.patch("runtime.cli.run_benchmark.parse_args", return_value=fake_args), \
            mock.patch("runtime.cli.run_benchmark.initialize_session_state") as init_state, \
            mock.patch("runtime.cli.run_benchmark.run_session") as run_session:
            init_state.return_value = {"meta": {}}
            run_benchmark.main()

        init_state.assert_called_once()
        called_session_id = init_state.call_args.args[1]
        self.assertEqual(called_session_id, simulation.default_session_id())
        run_session.assert_called_once()

    def test_normalize_core_output_builds_candidate_turn(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        raw_turn = build_reference_raw_turns(case_bundle, "2026-03-19")[0]

        normalized = normalize_core_output(raw_turn)

        self.assertIsInstance(normalized, CandidateTurn)
        self.assertEqual(normalized.turn_index, 1)
        self.assertEqual(normalized.role, "assistant")

    def test_normalize_core_output_builds_structured_state_delta_fields(self) -> None:
        normalized = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Structured delta example.",
                "state_delta": {
                    "facts_structured": [
                        {
                            "statement": "A structured fact.",
                            "category": "timeline",
                            "status": "accepted",
                            "related_issues": ["school_logistics"],
                        }
                    ],
                    "positions_structured": [
                        {
                            "participant_ids": ["spouse_A"],
                            "kind": "position",
                            "issue_id": "parenting_schedule",
                            "statement": "A structured position.",
                            "status": "current",
                        }
                    ],
                    "missing_info_structured": [
                        {
                            "action": "open",
                            "missing_id": "missing-900",
                            "question": "A structured missing-info question?",
                        }
                    ],
                    "issue_updates_structured": [
                        {
                            "issue_id": "school_logistics",
                            "label": "School logistics",
                        }
                    ],
                    "packages_structured": [
                        {
                            "package_id": "pkg-900",
                            "family": "communication_package",
                            "status": "workable",
                            "summary": "minimum notice, written summaries, and a pause-before-commitment rule",
                            "elements": ["minimum_notice_option", "written_summary_option"],
                            "related_issues": ["communication_protocol"],
                        }
                    ],
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        self.assertEqual(normalized.state_delta.facts_structured[0].statement, "A structured fact.")
        self.assertEqual(normalized.state_delta.positions_structured[0].participant_ids, ["spouse_A"])
        self.assertEqual(normalized.state_delta.missing_info_structured[0].missing_id, "missing-900")
        self.assertEqual(normalized.state_delta.issue_updates_structured[0].issue_id, "school_logistics")
        self.assertEqual(normalized.state_delta.packages_structured[0].family, "communication_package")

    def test_normalize_core_output_rejects_unknown_structured_issue_id(self) -> None:
        with self.assertRaises(ValueError):
            normalize_core_output(
                {
                    "turn_index": 1,
                    "timestamp": "2026-03-19T00:00:10Z",
                    "role": "assistant",
                    "phase": "info_gathering",
                    "message_summary": "Unknown issue id.",
                    "state_delta": {
                        "issue_updates_structured": [
                            {
                                "issue_id": "school_logisitcs",
                                "label": "School logistics",
                            }
                        ]
                    },
                    "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
                }
            )

    def test_runtime_client_turn_uses_case_and_persona_context(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        raw_turn = generate_runtime_client_turn(2, "2026-03-19T00:01:30Z", state, case_bundle)

        self.assertEqual(raw_turn["role"], "client")
        self.assertIn("Parent A", raw_turn["message_summary"])
        self.assertIn("child", raw_turn["message_summary"].lower())
        self.assertIn("positions_added_or_updated", raw_turn["state_delta"])

    def test_package_slice_runtime_turns_reuse_reference_content_helper(self) -> None:
        case_bundle = load_case_bundle(D_B07_CASE_DIR)
        from runtime.state import initialize_session_state
        from runtime.benchmarks.d_b07_authored import build_reference_raw_turns
        from runtime.benchmarks.d_b07_runtime import generate_runtime_assistant_turn, generate_runtime_client_turn

        state = initialize_session_state(case_bundle, "D-B07-S01-generated", "sim_minimal", source="runtime")
        authored_turns = build_reference_raw_turns(case_bundle, "2026-03-19")

        runtime_assistant = generate_runtime_assistant_turn(5, "2026-03-19T00:04:40Z", state, None)
        runtime_client = generate_runtime_client_turn(6, "2026-03-19T00:05:50Z", state, case_bundle)

        self.assertEqual(runtime_assistant, authored_turns[4])
        self.assertEqual(runtime_client, authored_turns[5])

    def test_d_b06_runtime_assistant_turns_use_live_generation_not_reference_replay(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        from runtime.state import initialize_session_state
        from runtime.benchmarks.d_b06_authored import build_reference_raw_turns
        from runtime.benchmarks.d_b06_runtime import generate_runtime_assistant_turn

        state = initialize_session_state(case_bundle, "D-B06-S01-generated", "sim_minimal", source="runtime")
        state["positions"]["spouse_A"] = {
            "participant_id": "spouse_A",
            "current_positions": [
                {
                    "position_id": "pos-spouse_a-001",
                    "issue_id": "communication_protocol",
                    "statement": "New extracurricular commitments should not be made without enough notice to discuss them first.",
                    "status": "current",
                    "confidence": "high",
                    "source_turns": [2],
                }
            ],
            "proposals": [],
            "red_lines": [],
            "soft_preferences": [],
            "open_to_discussion": [],
            "last_updated_turn": 2,
        }
        state["positions"]["spouse_B"] = {
            "participant_id": "spouse_B",
            "current_positions": [
                {
                    "position_id": "pos-spouse_b-001",
                    "issue_id": "fairness_and_parent_role",
                    "statement": "Child-activity decisions should not leave one parent feeling sidelined or treated as an afterthought.",
                    "status": "current",
                    "confidence": "high",
                    "source_turns": [4],
                }
            ],
            "proposals": [],
            "red_lines": [],
            "soft_preferences": [],
            "open_to_discussion": [],
            "last_updated_turn": 4,
        }
        authored_turn = build_reference_raw_turns(case_bundle, "2026-03-19")[4]
        runtime_turn = generate_runtime_assistant_turn(
            5,
            "2026-03-19T00:04:45Z",
            state,
            {"package_summary": "minimum notice, written summaries, and a pause-before-commitment rule"},
        )

        self.assertNotEqual(runtime_turn["message_summary"], authored_turn["message_summary"])
        self.assertEqual(runtime_turn["state_delta"]["packages_structured"][0]["family"], "communication_package")
        self.assertIn("mutual rather than one-sided", runtime_turn["message_summary"])

    def test_package_oriented_slices_emit_structured_package_deltas(self) -> None:
        for case_dir, expected_family in [
            (D_B05_CASE_DIR, "written_notice_package"),
            (D_B06_CASE_DIR, "communication_package"),
            (D_B07_CASE_DIR, "reimbursement_package"),
        ]:
            case_bundle = load_case_bundle(case_dir)
            simulation = get_benchmark_simulation(case_bundle)
            turns = simulation.build_turns("reference", case_bundle, "2026-03-19")
            package_turn = next(turn for turn in turns if turn.state_delta.packages_structured)

            self.assertEqual(package_turn.state_delta.packages_structured[0].family, expected_family)

    def test_patterned_authored_slices_share_message_variant_helper_behavior(self) -> None:
        from runtime.benchmarks.d_b05_authored import build_mock_model_raw_turns as build_d_b05_mock_turns
        from runtime.benchmarks.d_b06_authored import build_varied_mock_model_raw_turns as build_d_b06_varied_turns

        d_b05_turns = build_d_b05_mock_turns(load_case_bundle(D_B05_CASE_DIR), "2026-03-19")
        d_b06_turns = build_d_b06_varied_turns(load_case_bundle(D_B06_CASE_DIR), "2026-03-19")

        self.assertIn("written process for changes", d_b05_turns[0]["message_summary"])
        self.assertIn("narrow package", d_b05_turns[4]["message_summary"])
        self.assertIn("not sidelining either parent", d_b06_turns[2]["message_summary"])

    def test_d_b04_simulation_provides_runtime_turn_plan(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        plan = simulation.build_runtime_turn_plan(case_bundle, "2026-03-19")

        self.assertEqual(len(plan), 8)
        self.assertEqual([entry.turn_index for entry in plan], list(range(1, 9)))
        self.assertEqual(plan[0].role, "assistant")
        self.assertEqual(plan[-1].role, "client")
        self.assertEqual(plan[0].timestamp, "2026-03-19T00:00:10Z")
        self.assertEqual(plan[-1].timestamp, "2026-03-19T00:08:50Z")

    def test_runtime_session_uses_simulation_owned_turn_plan(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        custom_plan = [
            RuntimeTurnPlanEntry(turn_index=1, role="client", timestamp="2026-03-19T00:00:10Z"),
            RuntimeTurnPlanEntry(turn_index=2, role="assistant", timestamp="2026-03-19T00:01:10Z"),
        ]

        simulation = get_benchmark_simulation(case_bundle)
        with mock.patch("runtime.orchestrator.get_benchmark_simulation", return_value=simulation), \
            mock.patch.object(type(simulation), "build_runtime_turn_plan", return_value=custom_plan), \
            mock.patch.object(type(simulation), "generate_runtime_client_turn") as generate_client, \
            mock.patch.object(type(simulation), "generate_runtime_assistant_turn") as generate_assistant:
            generate_client.return_value = {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "message_summary": "Client starts this benchmark plan.",
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
            generate_assistant.return_value = {
                "turn_index": 2,
                "timestamp": "2026-03-19T00:01:10Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Assistant follows the benchmark plan.",
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }

            _run_runtime_generated_session(case_bundle, state, "2026-03-19T12:00:00Z")

        generate_client.assert_called_once()
        generate_assistant.assert_called_once()
        self.assertEqual(generate_client.call_args.kwargs["turn_index"], 1)
        self.assertEqual(generate_assistant.call_args.kwargs["turn_index"], 2)
        self.assertEqual(generate_client.call_args.kwargs["timestamp"], "2026-03-19T00:00:10Z")
        self.assertEqual(generate_assistant.call_args.kwargs["timestamp"], "2026-03-19T00:01:10Z")

    def test_build_runtime_turn_plan_returns_expected_d_b04_order(self) -> None:
        plan = build_runtime_turn_plan("2026-03-19")

        self.assertEqual(
            [(entry.turn_index, entry.role) for entry in plan],
            [
                (1, "assistant"),
                (2, "client"),
                (3, "assistant"),
                (4, "client"),
                (5, "assistant"),
                (6, "client"),
                (7, "assistant"),
                (8, "client"),
            ],
        )

    def test_normalize_core_output_rejects_invalid_payload(self) -> None:
        with self.assertRaises(ValueError):
            normalize_core_output(
                {
                    "turn_index": 0,
                    "timestamp": "2026-03-19T00:00:10Z",
                    "role": "assistant",
                    "phase": "info_gathering",
                    "message_summary": "bad turn",
                    "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
                }
            )

    def test_normalize_core_output_rejects_invalid_timestamp_format(self) -> None:
        with self.assertRaises(ValueError):
            normalize_core_output(
                {
                    "turn_index": 1,
                    "timestamp": "03/19/2026 00:00:10",
                    "role": "assistant",
                    "phase": "info_gathering",
                    "message_summary": "bad timestamp",
                    "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
                }
            )

    def test_normalize_core_output_rejects_triggered_risk_without_signals(self) -> None:
        with self.assertRaises(ValueError):
            normalize_core_output(
                {
                    "turn_index": 1,
                    "timestamp": "2026-03-19T00:00:10Z",
                    "role": "assistant",
                    "phase": "info_gathering",
                    "message_summary": "bad risk coherence",
                    "risk_check": {"triggered": True, "signals": [], "severity": 3, "notes": "x"},
                }
            )

    def test_normalize_core_output_rejects_invalid_escalation_category(self) -> None:
        with self.assertRaises(ValueError):
            normalize_core_output(
                {
                    "turn_index": 1,
                    "timestamp": "2026-03-19T00:00:10Z",
                    "role": "assistant",
                    "phase": "option_generation",
                    "message_summary": "bad escalation category",
                    "risk_check": {
                        "triggered": True,
                        "signals": ["insufficient_information"],
                        "severity": 3,
                        "notes": "x",
                    },
                    "candidate_escalation_category": "E9",
                    "candidate_escalation_mode": "M1",
                }
            )

    def test_normalize_core_output_rejects_partially_specified_escalation(self) -> None:
        with self.assertRaises(ValueError):
            normalize_core_output(
                {
                    "turn_index": 1,
                    "timestamp": "2026-03-19T00:00:10Z",
                    "role": "assistant",
                    "phase": "option_generation",
                    "message_summary": "bad escalation pairing",
                    "risk_check": {
                        "triggered": True,
                        "signals": ["insufficient_information"],
                        "severity": 3,
                        "notes": "x",
                    },
                    "candidate_escalation_mode": "M1",
                }
            )

    def test_normalize_core_output_rejects_add_and_resolve_same_question(self) -> None:
        with self.assertRaises(ValueError):
            normalize_core_output(
                {
                    "turn_index": 1,
                    "timestamp": "2026-03-19T00:00:10Z",
                    "role": "assistant",
                    "phase": "info_gathering",
                    "message_summary": "contradictory question delta",
                    "state_delta": {
                        "open_questions_added": ["What transport plan would support school-week exchanges?"],
                        "open_questions_resolved": ["What transport plan would support school-week exchanges?"],
                    },
                    "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
                }
            )

    def test_normalize_core_output_rejects_add_and_revise_same_fact(self) -> None:
        with self.assertRaises(ValueError):
            normalize_core_output(
                {
                    "turn_index": 1,
                    "timestamp": "2026-03-19T00:00:10Z",
                    "role": "assistant",
                    "phase": "info_gathering",
                    "message_summary": "contradictory fact delta",
                    "state_delta": {
                        "facts_added": ["School commute feasibility is unresolved."],
                        "facts_revised": ["School commute feasibility is unresolved."],
                    },
                    "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
                }
            )

    def test_mock_model_raw_turns_normalize_successfully(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        raw_turns = build_mock_model_raw_turns(case_bundle, "2026-03-19")
        normalized_turns = build_mock_model_turns(case_bundle, "2026-03-19")

        self.assertEqual(len(raw_turns), 8)
        self.assertEqual(len(normalized_turns), 8)
        self.assertIn("facts_structured", raw_turns[1]["state_delta"])
        self.assertIn("positions_structured", raw_turns[1]["state_delta"])
        self.assertGreaterEqual(len(normalized_turns[1].state_delta.facts_structured), 1)
        self.assertEqual(normalized_turns[0].phase, "info_gathering")
        self.assertEqual(normalized_turns[-1].candidate_escalation_mode, "M1")
        for turn in normalized_turns:
            self.assertIsInstance(turn, CandidateTurn)
            validate_candidate_turn(turn)

    def test_varied_mock_model_turns_normalize_successfully(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        baseline_raw_turns = build_mock_model_raw_turns(case_bundle, "2026-03-19")
        raw_turns = build_varied_mock_model_raw_turns(case_bundle, "2026-03-19")
        normalized_turns = build_varied_mock_model_turns(case_bundle, "2026-03-19")
        process_variant = get_varied_mock_process_variant("2026-03-19")

        self.assertEqual(len(raw_turns), 8)
        self.assertEqual(len(normalized_turns), 8)
        self.assertEqual(normalized_turns[-1].candidate_escalation_mode, "M1")
        self.assertIn(process_variant, {"interest_first", "logistics_first"})
        self.assertTrue(
            any(
                varied["message_summary"] != baseline["message_summary"]
                or varied["risk_check"]["notes"] != baseline["risk_check"]["notes"]
                or varied["state_delta"].get("open_questions_added") != baseline["state_delta"].get("open_questions_added")
                or varied["state_delta"].get("option_state_updates") != baseline["state_delta"].get("option_state_updates")
                for varied, baseline in zip(raw_turns, baseline_raw_turns, strict=True)
            )
        )
        for turn in normalized_turns:
            self.assertIsInstance(turn, CandidateTurn)
            validate_candidate_turn(turn)

    def test_reference_turns_conform_to_candidate_turn_contract(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        raw_turns = build_reference_raw_turns(case_bundle, "2026-03-19")
        turns = build_reference_turns(case_bundle, "2026-03-19")

        self.assertEqual(len(turns), 8)
        self.assertIn("issue_updates_structured", raw_turns[0]["state_delta"])
        self.assertIn("missing_info_structured", raw_turns[5]["state_delta"])
        self.assertGreaterEqual(len(turns[5].state_delta.missing_info_structured), 1)
        for turn in turns:
            self.assertIsInstance(turn, CandidateTurn)
            validate_candidate_turn(turn)

    def test_resolved_question_closes_missing_info_entry(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        opening_turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Open a transport feasibility question.",
                "state_delta": {
                    "open_questions_added": [
                        "What transport plan would support school-week exchanges?"
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Opening question."},
            }
        )
        resolution_turn = normalize_core_output(
            {
                "turn_index": 2,
                "timestamp": "2026-03-19T00:01:10Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Resolve the transport feasibility question.",
                "state_delta": {
                    "open_questions_resolved": [
                        "What transport plan would support school-week exchanges?"
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Question resolved."},
            }
        )

        apply_turn(state, opening_turn)
        self.assertEqual(state["missing_info"][0]["status"], "open")

        apply_turn(state, resolution_turn)

        self.assertNotIn("What transport plan would support school-week exchanges?", state["open_questions"])
        self.assertEqual(state["missing_info"][0]["status"], "resolved")

    def test_plugin_and_escalation_clear_after_missing_info_resolution(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        opening_turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "assistant",
                "phase": "option_generation",
                "message_summary": "Open logistics constraints and bounded option work.",
                "state_delta": {
                    "open_questions_added": [
                        "What transport plan would support school-week exchanges?",
                        "What reliability markers would both parents treat as sufficient for a phased trial?",
                    ],
                    "option_state_updates": [
                        "Added phased_trial_option"
                    ],
                },
                "risk_check": {
                    "triggered": True,
                    "signals": ["insufficient_information", "plugin_low_confidence"],
                    "severity": 3,
                    "notes": "Constraints remain unresolved.",
                },
                "candidate_escalation_category": "E5",
                "candidate_escalation_mode": "M1",
            }
        )
        resolution_turn = normalize_core_output(
            {
                "turn_index": 2,
                "timestamp": "2026-03-19T00:01:10Z",
                "role": "assistant",
                "phase": "agreement_building",
                "message_summary": "Resolve the gating logistics questions.",
                "state_delta": {
                    "open_questions_resolved": [
                        "What transport plan would support school-week exchanges?",
                        "What reliability markers would both parents treat as sufficient for a phased trial?",
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Questions resolved."},
            }
        )

        apply_turn(state, opening_turn)
        plugin_assessment = get_plugin_runtime(state).assess_state(state)
        escalation = determine_escalation(state, plugin_assessment)

        self.assertEqual(plugin_assessment["plugin_confidence"], "low")
        self.assertEqual(escalation["mode"], "M1")

        apply_turn(state, resolution_turn)
        plugin_assessment = get_plugin_runtime(state).assess_state(state)
        escalation = determine_escalation(state, plugin_assessment)

        self.assertEqual(plugin_assessment["plugin_confidence"], "moderate")
        self.assertEqual(plugin_assessment["logistics_related_missing_info"], [])
        self.assertEqual(escalation["mode"], "M0")

    def test_plugin_assessment_uses_state_shape_not_just_open_question_counts(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        state["meta"]["plugin_policy_descriptor"] = D_B04_SIMULATION.plugin_policy_descriptor(case_bundle)
        state["summary_state"]["issues"] = ["Parenting schedule", "School logistics"]
        state["missing_info"].append(
            {
                "missing_id": "missing-001",
                "question": "What specific transport plan would support school-week exchanges without creating school-day instability?",
                "importance": "high",
                "reason_type": "feasibility_gap",
                "related_issues": ["school_logistics", "parenting_schedule"],
                "first_identified_turn": 1,
                "status": "open",
                "note": "x",
            }
        )
        state["facts"].append(
            {
                "fact_id": "fact-001",
                "category": "timeline",
                "statement": "Transport, exchange timing, and homework-routine reliability remain unresolved for school-week overnights.",
                "status": "uncertain",
                "source_turns": [1],
                "related_issues": ["school_logistics", "parenting_schedule"],
                "note": "x",
            }
        )
        state["options"].append("Marked fixed_recommendation_out_of_scope_pending_feasibility")
        state["flags"].append({"flag_id": "flag-db04-003", "flag_type": "plugin_low_confidence"})

        plugin_assessment = get_plugin_runtime(state).assess_state(state)

        self.assertEqual(plugin_assessment["policy_descriptor_id"], "d_b04_school_week_caution")
        self.assertEqual(plugin_assessment["plugin_confidence"], "low")
        self.assertEqual(plugin_assessment["option_posture"], "bounded_only")
        self.assertTrue(plugin_assessment["needs_logistics_clarification"])
        self.assertIn(
            "Transport, exchange timing, and homework-routine reliability remain unresolved for school-week overnights.",
            plugin_assessment["uncertain_logistics_facts"],
        )

    def test_run_session_records_benchmark_owned_plugin_policy_descriptor(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B06-S01-generated", "sim_minimal", source="runtime")
        simulation = get_benchmark_simulation(case_bundle)
        state["meta"]["plugin_policy_descriptor"] = simulation.plugin_policy_descriptor(case_bundle)

        self.assertEqual(
            state["meta"]["plugin_policy_descriptor"]["descriptor_id"],
            "d_b06_extracurricular_protocol_balance",
        )

    def test_run_session_records_benchmark_descriptor(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        simulation = get_benchmark_simulation(case_bundle)
        state["meta"]["benchmark_descriptor"] = simulation.benchmark_descriptor(case_bundle)

        self.assertEqual(state["meta"]["benchmark_descriptor"]["descriptor_id"], "d_b04_bespoke_anchor")

    def test_escalation_can_enter_m1_from_state_evidence_not_just_counts(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        state["summary_state"]["issues"] = ["Parenting schedule", "School logistics"]
        state["missing_info"].append(
            {
                "missing_id": "missing-001",
                "question": "What specific transport plan would support school-week exchanges without creating school-day instability?",
                "importance": "high",
                "reason_type": "feasibility_gap",
                "related_issues": ["school_logistics", "parenting_schedule"],
                "first_identified_turn": 1,
                "status": "open",
                "note": "x",
            }
        )
        state["facts"].append(
            {
                "fact_id": "fact-001",
                "category": "timeline",
                "statement": "Transport, exchange timing, and homework-routine reliability remain unresolved for school-week overnights.",
                "status": "uncertain",
                "source_turns": [1],
                "related_issues": ["school_logistics", "parenting_schedule"],
                "note": "x",
            }
        )
        state["options"].append("Marked stronger_recommendation_still_qualified")
        state["flags"].append({"flag_id": "flag-db04-002", "flag_type": "decision_quality_risk"})

        plugin_assessment = get_plugin_runtime(state).assess_state(state)
        escalation = determine_escalation(state, plugin_assessment)

        self.assertEqual(escalation["mode"], "M1")
        self.assertEqual(escalation["category"], "E5")
        self.assertIn("option work is ahead of full feasibility confirmation", escalation["rationale"])

    def test_shared_divorce_plugin_assesses_communication_package_beyond_logistics(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B06-S01-generated", "sim_minimal", source="runtime")
        state["meta"]["plugin_policy_descriptor"] = D_B06_SIMULATION.plugin_policy_descriptor(case_bundle)
        state["summary_state"]["issues"] = [
            "Communication protocol around future changes",
            "Fairness and meaningful parenting role",
        ]
        state["options"].extend(
            [
                "Added minimum_notice_option",
                "Added written_summary_option",
                "Added pause_before_commitment_option",
                "Marked communication_package_as_workable",
            ]
        )

        plugin_assessment = get_plugin_runtime(state).assess_state(state)

        self.assertEqual(plugin_assessment["package_family"], "communication_package")
        self.assertEqual(
            plugin_assessment["package_summary"],
            "minimum notice, written summaries, and a pause-before-commitment rule",
        )
        self.assertEqual(plugin_assessment["plugin_confidence"], "high")
        self.assertTrue(plugin_assessment["supports_fixed_recommendation"])

    def test_shared_divorce_plugin_prefers_structured_package_meaning_over_option_markers(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B06-S01-generated", "sim_minimal", source="runtime")
        state["meta"]["plugin_policy_descriptor"] = D_B06_SIMULATION.plugin_policy_descriptor(case_bundle)
        state["summary_state"]["issues"] = [
            "Communication protocol around future changes",
            "Fairness and meaningful parenting role",
        ]
        state["packages"].append(
            {
                "package_id": "pkg-d-b06-001",
                "family": "communication_package",
                "status": "workable",
                "summary": "minimum notice, written summaries, and a pause-before-commitment rule",
                "elements": [
                    "minimum_notice_option",
                    "written_summary_option",
                    "pause_before_commitment_option",
                ],
                "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                "last_updated_turn": 5,
            }
        )

        plugin_assessment = get_plugin_runtime(case_bundle).assess_state(state)

        self.assertEqual(plugin_assessment["package_family"], "communication_package")
        self.assertEqual(
            plugin_assessment["package_summary"],
            "minimum notice, written summaries, and a pause-before-commitment rule",
        )
        self.assertEqual(plugin_assessment["plugin_confidence"], "high")

    def test_shared_divorce_plugin_detects_partial_structured_package_elements(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B06-S01-generated", "sim_minimal", source="runtime")
        state["meta"]["plugin_policy_descriptor"] = D_B06_SIMULATION.plugin_policy_descriptor(case_bundle)
        state["summary_state"]["issues"] = [
            "Communication protocol around future changes",
            "Fairness and meaningful parenting role",
        ]
        state["packages"].append(
            {
                "package_id": "pkg-d-b06-001",
                "family": "communication_package",
                "status": "workable",
                "summary": "minimum notice, written summaries, and a pause-before-commitment rule",
                "elements": [
                    "minimum_notice_option",
                    "written_summary_option",
                ],
                "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                "last_updated_turn": 5,
            }
        )

        plugin_assessment = get_plugin_runtime(state).assess_state(state)

        self.assertEqual(plugin_assessment["package_quality"], "partial")
        self.assertEqual(plugin_assessment["plugin_confidence"], "moderate")
        self.assertIn("pause_before_commitment_option", plugin_assessment["package_missing_elements"])
        self.assertTrue(any("pause-before-commitment rule" in warning for warning in plugin_assessment["warnings"]))

    def test_partial_package_summary_does_not_overstate_completeness(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        from runtime.artifacts import build_summary
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B06-S01-generated", "sim_minimal", source="runtime")
        state["meta"]["plugin_policy_descriptor"] = D_B06_SIMULATION.plugin_policy_descriptor(case_bundle)
        state["summary_state"]["issues"] = [
            "Communication protocol around future changes",
            "Fairness and meaningful parenting role",
        ]
        state["summary_state"]["next_step"] = "Confirm whether the missing communication safeguard should be added before treating the package as settled."
        state["positions"]["spouse_A"] = {
            "participant_id": "spouse_A",
            "current_positions": [{"statement": "New extracurricular commitments should not be made without enough notice to discuss them first."}],
            "proposals": [],
            "red_lines": [],
            "soft_preferences": [],
            "open_to_discussion": [],
            "last_updated_turn": 2,
        }
        state["packages"].append(
            {
                "package_id": "pkg-d-b06-001",
                "family": "communication_package",
                "status": "workable",
                "summary": "minimum notice, written summaries, and a pause-before-commitment rule",
                "elements": [
                    "minimum_notice_option",
                    "written_summary_option",
                ],
                "related_issues": ["communication_protocol", "fairness_and_parent_role"],
                "last_updated_turn": 5,
            }
        )
        state["plugin_assessment"] = get_plugin_runtime(state).assess_state(state)

        summary = build_summary(state)

        self.assertIn("Package quality: partial", summary)
        self.assertIn("Still missing: a pause-before-commitment rule", summary)
        self.assertNotIn("Package quality: complete", summary)

    def test_shared_divorce_plugin_detects_competing_package_families(self) -> None:
        case_bundle = load_case_bundle(D_B07_CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B07-S01-generated", "sim_minimal", source="runtime")
        state["meta"]["plugin_policy_descriptor"] = D_B07_SIMULATION.plugin_policy_descriptor(case_bundle)
        state["summary_state"]["issues"] = [
            "Communication protocol around future changes",
            "Child expense coordination and reimbursement",
        ]
        state["packages"].extend(
            [
                {
                    "package_id": "pkg-d-b06-001",
                    "family": "communication_package",
                    "status": "workable",
                    "summary": "minimum notice, written summaries, and a pause-before-commitment rule",
                    "elements": [
                        "minimum_notice_option",
                        "written_summary_option",
                        "pause_before_commitment_option",
                    ],
                    "related_issues": ["communication_protocol"],
                    "last_updated_turn": 5,
                },
                {
                    "package_id": "pkg-d-b07-001",
                    "family": "reimbursement_package",
                    "status": "workable",
                    "summary": "advance notice, shared receipts, and a reimbursement response window",
                    "elements": [
                        "expense_notice_window_option",
                        "shared_receipt_option",
                        "reimbursement_response_window_option",
                    ],
                    "related_issues": ["child_expense_coordination", "communication_protocol"],
                    "last_updated_turn": 6,
                },
            ]
        )

        plugin_assessment = get_plugin_runtime(state).assess_state(state)

        self.assertTrue(plugin_assessment["mixed_package_state"])
        self.assertEqual(plugin_assessment["plugin_confidence"], "moderate")
        self.assertEqual(
            set(plugin_assessment["competing_package_families"]),
            {"communication_package", "reimbursement_package"},
        )
        self.assertTrue(any("Multiple active package families are present" in warning for warning in plugin_assessment["warnings"]))

    def test_mixed_package_summary_surfaces_competing_package_families(self) -> None:
        case_bundle = load_case_bundle(D_B07_CASE_DIR)
        from runtime.artifacts import build_summary
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B07-S01-generated", "sim_minimal", source="runtime")
        state["meta"]["plugin_policy_descriptor"] = D_B07_SIMULATION.plugin_policy_descriptor(case_bundle)
        state["summary_state"]["issues"] = [
            "Communication protocol around future changes",
            "Child expense coordination and reimbursement",
        ]
        state["summary_state"]["next_step"] = "Narrow the discussion to one coherent package direction before treating the package work as settled."
        state["positions"]["spouse_A"] = {
            "participant_id": "spouse_A",
            "current_positions": [{"statement": "Reimbursement requests should not arrive weeks later without advance notice and supporting receipts."}],
            "proposals": [],
            "red_lines": [],
            "soft_preferences": [],
            "open_to_discussion": [],
            "last_updated_turn": 2,
        }
        state["packages"].extend(
            [
                {
                    "package_id": "pkg-d-b06-001",
                    "family": "communication_package",
                    "status": "workable",
                    "summary": "minimum notice, written summaries, and a pause-before-commitment rule",
                    "elements": [
                        "minimum_notice_option",
                        "written_summary_option",
                        "pause_before_commitment_option",
                    ],
                    "related_issues": ["communication_protocol"],
                    "last_updated_turn": 5,
                },
                {
                    "package_id": "pkg-d-b07-001",
                    "family": "reimbursement_package",
                    "status": "workable",
                    "summary": "advance notice, shared receipts, and a reimbursement response window",
                    "elements": [
                        "expense_notice_window_option",
                        "shared_receipt_option",
                        "reimbursement_response_window_option",
                    ],
                    "related_issues": ["child_expense_coordination", "communication_protocol"],
                    "last_updated_turn": 6,
                },
            ]
        )
        state["plugin_assessment"] = get_plugin_runtime(state).assess_state(state)

        summary = build_summary(state)

        self.assertIn("Competing package families: communication package, reimbursement package", summary)
        self.assertIn("Multiple active package families are present", summary)

    def test_shared_divorce_plugin_assesses_reimbursement_package_beyond_logistics(self) -> None:
        case_bundle = load_case_bundle(D_B07_CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B07-S01-generated", "sim_minimal", source="runtime")
        state["meta"]["plugin_policy_descriptor"] = D_B07_SIMULATION.plugin_policy_descriptor(case_bundle)
        state["summary_state"]["issues"] = [
            "Child expense coordination and reimbursement",
            "Communication protocol around future changes",
        ]
        state["options"].extend(
            [
                "Added expense_notice_window_option",
                "Added shared_receipt_option",
                "Added reimbursement_response_window_option",
                "Marked reimbursement_package_as_workable",
            ]
        )

        plugin_assessment = get_plugin_runtime(state).assess_state(state)

        self.assertEqual(plugin_assessment["package_family"], "reimbursement_package")
        self.assertEqual(
            plugin_assessment["package_summary"],
            "advance notice, shared receipts, and a reimbursement response window",
        )
        self.assertEqual(plugin_assessment["plugin_confidence"], "high")
        self.assertTrue(plugin_assessment["supports_fixed_recommendation"])

    def test_logistics_fact_canonicalization_preserves_unresolved_meaning(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "message_summary": "Report unresolved logistics barriers.",
                "state_delta": {
                    "facts_added": [
                        "School commute feasibility is unresolved.",
                        "Exchange timing reliability is unresolved.",
                        "Homework and evening-routine reliability is unresolved.",
                    ]
                },
                "risk_check": {
                    "triggered": True,
                    "signals": ["insufficient_information"],
                    "severity": 2,
                    "notes": "Logistics remain unresolved.",
                },
            }
        )

        apply_turn(state, turn)

        fact_statements = [fact["statement"] for fact in state["facts"]]
        self.assertIn(
            "Transport, exchange timing, and homework-routine reliability remain unresolved for school-week overnights.",
            fact_statements,
        )
        self.assertNotIn(
            "Transport, exchange timing, and homework-routine reliability are already sufficient to support expanded school-week overnights.",
            fact_statements,
        )

    def test_uncertain_logistics_fact_remains_uncertain_not_sufficient(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "message_summary": "Report unresolved commute, exchange timing, and homework barriers.",
                "state_delta": {
                    "facts_added": [
                        "School commute feasibility is unresolved and exchange timing reliability is unresolved while homework and evening-routine reliability is unresolved."
                    ]
                },
                "risk_check": {
                    "triggered": True,
                    "signals": ["insufficient_information"],
                    "severity": 2,
                    "notes": "Feasibility remains uncertain.",
                },
            }
        )

        apply_turn(state, turn)

        logistics_fact = state["facts"][0]
        self.assertEqual(logistics_fact["status"], "uncertain")
        self.assertIn("remain unresolved", logistics_fact["statement"])

    def test_position_updates_do_not_inject_unattributed_participant_state(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "message_summary": "Parent A states a current position.",
                "state_delta": {
                    "positions_added_or_updated": [
                        "spouse_A seeks a predictable weekday structure and limited school-night overnights until logistics improve."
                    ]
                },
                "risk_check": {
                    "triggered": False,
                    "signals": [],
                    "severity": 1,
                    "notes": "Current position recorded.",
                },
            }
        )

        apply_turn(state, turn)

        spouse_a = state["positions"]["spouse_A"]
        self.assertEqual(spouse_a["red_lines"], [])
        self.assertEqual(spouse_a["soft_preferences"], [])
        self.assertEqual(spouse_a["open_to_discussion"], [])
        self.assertFalse(
            any("dysregulation risk" in fact["statement"].lower() for fact in state["facts"]),
            "Position updates should not inject extra facts outside the normalized turn content.",
        )

    def test_unstructured_position_fallback_preserves_stated_proposal_without_synthesizing_new_text(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "message_summary": "Proposal fallback should preserve source phrasing.",
                "state_delta": {
                    "positions_added_or_updated": [
                        "Both parents show conditional openness to phased arrangements if logistics are clarified."
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        apply_turn(state, turn)

        spouse_a_proposal = state["positions"]["spouse_A"]["proposals"][0]["statement"]
        self.assertEqual(spouse_a_proposal, "Conditional openness to phased arrangements if logistics are clarified.")

    def test_unstructured_missing_info_fallback_uses_explicit_template_lookup(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Fallback missing info lookup.",
                "state_delta": {
                    "open_questions_added": [
                        "What transport plan would support school-week exchanges?"
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        apply_turn(state, turn)

        self.assertEqual(state["missing_info"][0]["missing_id"], "missing-001")

    def test_unstructured_fact_fallback_uses_explicit_template_lookup(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "message_summary": "Fallback fact lookup.",
                "state_delta": {
                    "facts_added": [
                        "There is an active dispute about school-night overnights."
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        apply_turn(state, turn)

        fact = state["facts"][0]
        self.assertEqual(fact["category"], "parenting_schedule")
        self.assertEqual(fact["status"], "accepted")
        self.assertEqual(fact["related_issues"], ["parenting_schedule"])

    def test_unknown_unstructured_fact_fallback_stays_minimal(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "message_summary": "Unknown fallback fact.",
                "state_delta": {
                    "facts_added": [
                        "A novel unstructured fact with no template match."
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        apply_turn(state, turn)

        fact = state["facts"][0]
        self.assertEqual(fact["category"], "communication_history")
        self.assertEqual(fact["status"], "accepted")
        self.assertEqual(fact["related_issues"], ["parenting_schedule"])

    def test_structured_position_delta_can_set_participant_without_name_heuristic(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "message_summary": "Structured participant routing.",
                "state_delta": {
                    "positions_structured": [
                        {
                            "participant_ids": ["spouse_B"],
                            "kind": "position",
                            "issue_id": "parenting_schedule",
                            "statement": "Weekday time should expand.",
                            "status": "current",
                            "confidence": "high",
                        }
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        apply_turn(state, turn)

        self.assertEqual(state["positions"]["spouse_B"]["current_positions"][0]["statement"], "Weekday time should expand.")

    def test_structured_missing_info_delta_can_open_and_resolve_without_template_heuristic(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        opening_turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Open structured missing info.",
                "state_delta": {
                    "missing_info_structured": [
                        {
                            "action": "open",
                            "missing_id": "missing-custom-001",
                            "question": "What calendar constraints affect summer exchanges?",
                            "importance": "medium",
                            "reason_type": "process_gap",
                            "related_issues": ["communication_protocol"],
                        }
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )
        resolution_turn = normalize_core_output(
            {
                "turn_index": 2,
                "timestamp": "2026-03-19T00:01:10Z",
                "role": "assistant",
                "phase": "agreement_building",
                "message_summary": "Resolve structured missing info.",
                "state_delta": {
                    "missing_info_structured": [
                        {
                            "action": "resolve",
                            "missing_id": "missing-custom-001",
                            "question": "What calendar constraints affect summer exchanges?",
                            "related_issues": ["communication_protocol"],
                        }
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        apply_turn(state, opening_turn)
        self.assertEqual(state["missing_info"][0]["missing_id"], "missing-custom-001")
        self.assertEqual(state["missing_info"][0]["status"], "open")

        apply_turn(state, resolution_turn)
        self.assertEqual(state["missing_info"][0]["status"], "resolved")

    def test_structured_missing_info_resolve_requires_prior_open_state(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        resolution_turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:01:10Z",
                "role": "assistant",
                "phase": "agreement_building",
                "message_summary": "Resolve structured missing info without opening it first.",
                "state_delta": {
                    "missing_info_structured": [
                        {
                            "action": "resolve",
                            "missing_id": "missing-custom-404",
                            "question": "What calendar constraints affect summer exchanges?",
                            "related_issues": ["communication_protocol"],
                        }
                    ]
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        with self.assertRaises(ValueError):
            apply_turn(state, resolution_turn)

    def test_structured_fact_delta_overrides_conflicting_string_fallback(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "message_summary": "Structured fact should win.",
                "state_delta": {
                    "facts_added": ["A vague fallback fact that should not be used."],
                    "facts_structured": [
                        {
                            "statement": "A structured accepted fact.",
                            "category": "timeline",
                            "status": "accepted",
                            "related_issues": ["school_logistics"],
                        }
                    ],
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        apply_turn(state, turn)

        self.assertEqual(len(state["facts"]), 1)
        self.assertEqual(state["facts"][0]["statement"], "A structured accepted fact.")

    def test_structured_position_delta_overrides_conflicting_string_fallback(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "message_summary": "Structured position should win.",
                "state_delta": {
                    "positions_added_or_updated": [
                        "spouse_A seeks a predictable weekday structure and limited school-night overnights until logistics improve."
                    ],
                    "positions_structured": [
                        {
                            "participant_ids": ["spouse_B"],
                            "kind": "position",
                            "issue_id": "parenting_schedule",
                            "statement": "Structured position for Parent B.",
                            "status": "current",
                            "confidence": "high",
                        }
                    ],
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        apply_turn(state, turn)

        self.assertIn("spouse_B", state["positions"])
        self.assertNotIn("spouse_A", state["positions"])
        self.assertEqual(state["positions"]["spouse_B"]["current_positions"][0]["statement"], "Structured position for Parent B.")

    def test_structured_issue_update_overrides_string_issue_fallback(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import apply_turn, initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        turn = normalize_core_output(
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Structured issue should win.",
                "state_delta": {
                    "issue_map_updates": ["Expanded parenting_schedule with stability and routine concerns."],
                    "issue_updates_structured": [
                        {"issue_id": "school_logistics", "label": "School logistics"}
                    ],
                },
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "x"},
            }
        )

        apply_turn(state, turn)

        self.assertEqual(state["summary_state"]["issues"], ["School logistics"])

    def test_d_b04_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime")
        output_dir = run["output_dir"]
        required_files = [
            "session_meta.json",
            "run_meta.json",
            "interaction_trace.json",
            "positions.json",
            "facts_snapshot.json",
            "flags.json",
            "missing_info.json",
            "summary.txt",
            "review_cover_sheet.txt",
            "review_transcript.txt",
            "review_outcome_sheet.txt",
        ]
        for file_name in required_files:
            self.assertTrue((output_dir / file_name).exists(), f"Missing {file_name}")

        run_meta = run["run_meta"]
        flags = run["flags"]
        trace = run["trace"]
        summary = run["summary"]
        review_cover = (output_dir / "review_cover_sheet.txt").read_text(encoding="utf-8")
        review_transcript = (output_dir / "review_transcript.txt").read_text(encoding="utf-8")
        review_outcome = (output_dir / "review_outcome_sheet.txt").read_text(encoding="utf-8")

        self.assertEqual(run_meta["case_id"], "D-B04")
        self.assertEqual(run_meta["policy_profile"], "sim_minimal")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(run_meta["model_config"]["provider"], "runtime_generated_scaffold")
        self.assertEqual(run_meta["model_config"]["model_name"], "d_b04_runtime_generator_v0")
        self.assertIn("divorce_plugin_runtime_v0", run_meta["prompting"]["prompt_ids"])
        self.assertIn("runtime turn loop", run_meta["randomization"]["determinism_note"])
        self.assertEqual(len(flags["active_flags"]), 3)
        self.assertEqual(len(trace["turns"]), 8)
        self.assertIn("Run Source: runtime", summary)
        self.assertIn("Process Variant:", summary)
        self.assertIn("Current Escalation Posture", summary)
        self.assertIn("Unresolved:", summary)
        self.assertIn("Missing Information", summary)
        self.assertIn("Plugin confidence remains limited", summary)
        self.assertIn("Reviewer Cover Sheet", review_cover)
        self.assertIn("Case ID: D-B04", review_cover)
        self.assertIn("Reviewer Transcript", review_transcript)
        self.assertIn("Solomon:", review_transcript)
        self.assertIn("Turn 1", review_transcript)
        self.assertNotIn("Solomon: Solomon frames the session around", review_transcript)
        self.assertNotIn("Solomon: Solomon pauses the exchange", review_transcript)
        self.assertIn("Reviewer Outcome Sheet", review_outcome)
        self.assertIn("Recommended Next Step", review_outcome)
        self.assertTrue(all(flag["flag_id"].startswith("d-b04-flag-") for flag in flags["active_flags"]))
        self.assertTrue(
            any(flag["flag_type"] == "plugin_low_confidence" for flag in flags["active_flags"]),
            "Expected plugin_low_confidence to remain visible as an anti-overreach guardrail.",
        )

    def test_write_artifacts_produces_valid_session_meta(self) -> None:
        run = self._run_benchmark("runtime")
        session_meta = run["session_meta"]
        run_meta = run["run_meta"]

        # Identity fields match run_meta
        self.assertEqual(session_meta["schema_version"], "session_meta.v0")
        self.assertEqual(session_meta["case_id"], "D-B04")
        self.assertEqual(session_meta["session_id"], run_meta["session_id"])
        self.assertEqual(session_meta["plugin_type"], "divorce")
        self.assertEqual(session_meta["source"], "runtime")
        # created_at is a non-empty ISO timestamp string
        self.assertIsInstance(session_meta["created_at"], str)
        self.assertTrue(session_meta["created_at"])
        # Per-run fields must NOT bleed into session_meta
        self.assertNotIn("policy_profile", session_meta)
        self.assertNotIn("git_commit_hash", session_meta)
        self.assertNotIn("model_config", session_meta)

    def test_optional_review_transcript_renderer_writes_side_by_side_artifact(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B08_CASE_DIR, review_transcript_renderer="prototype_local_v0")
        output_dir = run["output_dir"]

        deterministic = (output_dir / "review_transcript.txt").read_text(encoding="utf-8")
        rendered = (output_dir / "review_transcript_rendered.txt").read_text(encoding="utf-8")
        run_meta = run["run_meta"]

        self.assertTrue((output_dir / "review_transcript_rendered.txt").exists())
        self.assertIn("Source Note: reviewer-facing rendered transcript derived from the structured interaction trace", rendered)
        self.assertIn("Renderer: prototype_local_v0", rendered)
        self.assertIn("Spouse B:", rendered)
        self.assertIn("Spouse A:", rendered)
        self.assertNotEqual(deterministic, rendered)
        self.assertEqual(run_meta["case_context"]["review_transcript_renderer"], "prototype_local_v0")

    def test_runtime_artifacts_preserve_trace_to_flag_and_escalation_consistency(self) -> None:
        run = self._run_benchmark("runtime")
        trace = run["trace"]["turns"]
        flags = run["flags"]["active_flags"]
        summary = run["summary"]

        all_signals = {signal for turn in trace for signal in turn["risk_check"]["signals"]}
        flag_types = {flag["flag_type"] for flag in flags}

        self.assertIn("insufficient_information", all_signals)
        self.assertIn("plugin_low_confidence", all_signals)
        self.assertTrue(flag_types.issubset(all_signals | {"decision_quality_risk"}))
        self.assertIn("`M1`", summary)
        self.assertIn("category `E5`", summary)

    def test_runtime_trace_turns_are_sequential_and_match_summary_mentions(self) -> None:
        run = self._run_benchmark("runtime")
        trace = run["trace"]["turns"]
        summary = run["summary"]
        facts = run["facts"]["facts"]

        turn_indexes = [turn["turn_index"] for turn in trace]
        self.assertEqual(turn_indexes, list(range(1, len(trace) + 1)))
        unresolved_from_trace = {
            fact
            for turn in trace
            for fact in turn["state_delta"].get("facts_added", [])
            if "unresolved" in fact.lower()
        }
        self.assertTrue(unresolved_from_trace)
        authoritative_unresolved = [fact["statement"] for fact in facts if fact["status"] == "uncertain"]
        self.assertTrue(authoritative_unresolved)
        self.assertTrue(any(statement in summary for statement in authoritative_unresolved))

    def test_session_validation_accepts_runtime_trace(self) -> None:
        run = self._run_benchmark("runtime")
        validate_session_trace(
            run["trace"]["turns"],
            {
                "mode": "M1",
                "category": "E5",
            },
        )

    def test_session_validation_rejects_non_monotonic_timestamps(self) -> None:
        turns = [
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:01:10Z",
                "role": "assistant",
                "phase": "info_gathering",
                "risk_check": {"triggered": False},
                "candidate_escalation_mode": None,
                "candidate_escalation_category": None,
            },
            {
                "turn_index": 2,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "client",
                "phase": "info_gathering",
                "risk_check": {"triggered": False},
                "candidate_escalation_mode": None,
                "candidate_escalation_category": None,
            },
        ]

        with self.assertRaises(ValueError):
            validate_session_trace(turns, {"mode": "M0", "category": None})

    def test_session_validation_rejects_invalid_phase_progression(self) -> None:
        turns = [
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "assistant",
                "phase": "info_gathering",
                "risk_check": {"triggered": False},
                "candidate_escalation_mode": None,
                "candidate_escalation_category": None,
            },
            {
                "turn_index": 2,
                "timestamp": "2026-03-19T00:01:10Z",
                "role": "assistant",
                "phase": "agreement_building",
                "risk_check": {"triggered": False},
                "candidate_escalation_mode": None,
                "candidate_escalation_category": None,
            },
        ]

        with self.assertRaises(ValueError):
            validate_session_trace(turns, {"mode": "M0", "category": None})

    def test_session_validation_rejects_final_escalation_mismatch(self) -> None:
        turns = [
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T00:00:10Z",
                "role": "assistant",
                "phase": "info_gathering",
                "risk_check": {"triggered": False},
                "candidate_escalation_mode": None,
                "candidate_escalation_category": None,
            },
            {
                "turn_index": 2,
                "timestamp": "2026-03-19T00:01:10Z",
                "role": "assistant",
                "phase": "interest_exploration",
                "risk_check": {"triggered": True},
                "candidate_escalation_mode": "M1",
                "candidate_escalation_category": "E5",
            },
            {
                "turn_index": 3,
                "timestamp": "2026-03-19T00:02:10Z",
                "role": "client",
                "phase": "agreement_building",
                "risk_check": {"triggered": False},
                "candidate_escalation_mode": None,
                "candidate_escalation_category": None,
            },
        ]

        with self.assertRaises(ValueError):
            validate_session_trace(turns, {"mode": "M0", "category": None})

    def test_runtime_missing_info_artifact_matches_open_entries_and_summary(self) -> None:
        run = self._run_benchmark("runtime")
        missing_items = run["missing_info"]["missing_items"]
        summary = run["summary"]

        open_items = [item for item in missing_items if item["status"] == "open"]
        resolved_items = [item for item in missing_items if item["status"] == "resolved"]

        self.assertGreaterEqual(len(open_items), 1)
        self.assertEqual(len(resolved_items), 1)
        for item in open_items:
            self.assertIn(item["question"], summary)
        for item in resolved_items:
            self.assertNotIn(item["question"], summary)
        self.assertIn("Missing Information", summary)
        self.assertIn("Current Escalation Posture", summary)

    def test_runtime_summary_claims_are_supported_by_authoritative_artifacts(self) -> None:
        run = self._run_benchmark("runtime")
        summary = run["summary"]
        facts = run["facts"]["facts"]
        positions = run["positions"]["participants"]
        flags = run["flags"]["active_flags"]

        self.assertTrue(any(fact["status"] == "uncertain" for fact in facts))
        self.assertTrue(any(participant["current_positions"] for participant in positions))
        self.assertTrue(any(flag["flag_type"] == "plugin_low_confidence" for flag in flags))
        self.assertIn("avoided presenting a fixed recommendation", summary)
        self.assertIn("Plugin supports caution but not stronger feasibility claims.", summary)
        self.assertIn("Option work should remain qualified until logistics questions and uncertain feasibility facts are resolved.", summary)
        self.assertIn("Transport, exchange timing, and homework-routine reliability remain unresolved", summary)

    def test_runtime_runner_records_runtime_source(self) -> None:
        run_meta = self._run_benchmark("runtime")["run_meta"]
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(run_meta["model_config"]["provider"], "runtime_generated_scaffold")
        self.assertIn(run_meta["case_context"]["process_variant"], {"interest_first", "logistics_first"})
        self.assertEqual(
            run_meta["case_context"]["benchmark_descriptor"]["descriptor_id"],
            "d_b04_bespoke_anchor",
        )
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b04_caution_narrative",
        )

    def test_sim_minimal_profile_writes_only_core_runtime_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR, policy_profile="sim_minimal")

        self.assertFalse((run["output_dir"] / "briefs").exists())
        self.assertFalse((run["output_dir"] / "continuity").exists())

    def test_eval_support_profile_writes_briefs(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR, policy_profile="eval_support")

        self.assertEqual(run["run_meta"]["policy_profile"], "eval_support")
        self.assertTrue((run["output_dir"] / "briefs" / "case_intake_brief.json").exists())
        self.assertTrue((run["output_dir"] / "briefs" / "early_dynamics_brief.json").exists())
        self.assertFalse((run["output_dir"] / "continuity").exists())

    def test_eval_support_profile_writes_risk_alert_brief_for_caution_run(self) -> None:
        run = self._run_benchmark("runtime", case_dir=CASE_DIR, policy_profile="eval_support")

        self.assertTrue((run["output_dir"] / "briefs" / "risk_alert_brief.json").exists())
        self.assertFalse((run["output_dir"] / "continuity").exists())

    def test_dev_verbose_profile_writes_briefs(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR, policy_profile="dev_verbose")

        self.assertEqual(run["run_meta"]["policy_profile"], "dev_verbose")
        self.assertTrue((run["output_dir"] / "briefs" / "case_intake_brief.json").exists())
        self.assertTrue((run["output_dir"] / "briefs" / "early_dynamics_brief.json").exists())
        self.assertFalse((run["output_dir"] / "continuity").exists())

    def test_dev_verbose_profile_exposes_raw_transcript_and_debug_trace_flags(self) -> None:
        profile = get_policy_profile("dev_verbose")

        self.assertTrue(profile.allow_raw_transcripts)
        self.assertTrue(profile.allow_debug_traces)
        self.assertFalse(profile.require_redaction)

    def test_dev_verbose_profile_writes_continuity_for_m2_state(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        state = initialize_session_state(case_bundle, "D-B06-S01-dev-verbose", "dev_verbose", source="runtime")
        state["meta"]["support_artifact_policy"] = D_B06_SIMULATION.support_artifact_policy(case_bundle)
        state["summary_state"]["issues"] = ["Communication protocol around future changes"]
        state["summary_state"]["next_step"] = "Escalate to a human reviewer."
        state["escalation"] = {
            "category": "E3",
            "threshold_band": "T2",
            "mode": "M2",
            "rationale": "Human review is required because a party explicitly requested human involvement.",
        }
        state["flags"] = [
            {
                "flag_id": "d-b06-flag-human-request",
                "flag_type": "explicit_human_request",
                "status": "active",
                "severity": 3,
                "source": "participant",
                "first_detected_turn": 1,
                "last_updated_turn": 1,
                "hard_trigger": False,
                "title": "A party requested human involvement",
            }
        ]
        state["trace_buffer"] = [
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T12:00:00Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Solomon explains the bounded process.",
                "state_delta": {},
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": ""},
            }
        ]

        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        output_dir = Path(temp_dir.name) / "dev-verbose-continuity"
        write_artifacts(output_dir, state, "2026-03-19T12:00:00Z", case_bundle)

        self.assertTrue((output_dir / "briefs" / "case_intake_brief.json").exists())
        self.assertTrue((output_dir / "briefs" / "risk_alert_brief.json").exists())
        self.assertTrue((output_dir / "continuity" / "continuity_packet.json").exists())

    def test_redacted_profile_writes_briefs(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR, policy_profile="redacted")

        self.assertEqual(run["run_meta"]["policy_profile"], "redacted")
        self.assertTrue((run["output_dir"] / "briefs" / "case_intake_brief.json").exists())
        self.assertTrue((run["output_dir"] / "briefs" / "early_dynamics_brief.json").exists())
        self.assertFalse((run["output_dir"] / "continuity").exists())

    def test_redacted_profile_exposes_require_redaction_flag(self) -> None:
        profile = get_policy_profile("redacted")

        self.assertTrue(profile.require_redaction)
        self.assertFalse(profile.allow_raw_transcripts)
        self.assertFalse(profile.allow_debug_traces)

    def test_redacted_profile_sets_redaction_applied_true_in_run_meta(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR, policy_profile="redacted")

        self.assertTrue(run["run_meta"]["redaction_applied"])

    def test_non_redacted_profiles_set_redaction_applied_false_in_run_meta(self) -> None:
        for profile in ("sim_minimal", "eval_support", "dev_verbose"):
            with self.subTest(profile=profile):
                run = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR, policy_profile=profile)
                self.assertFalse(run["run_meta"]["redaction_applied"])

    def test_redacted_profile_scrubs_pii_patterns_from_text_artifacts(self) -> None:
        # Inject a fake email and phone number into the session state, then
        # verify the redacted profile removes them from written artifacts.
        case_bundle = load_case_bundle(D_B05_CASE_DIR)
        state = initialize_session_state(case_bundle, "D-B05-S01-redact-pii", "redacted", source="runtime")
        state["meta"]["support_artifact_policy"] = D_B05_SIMULATION.support_artifact_policy(case_bundle)
        # Plant PII in the summary state so it will appear in summary.txt.
        state["summary_state"]["issues"] = ["Contact alice@example.com or call 555-867-5309 to proceed."]
        state["summary_state"]["next_step"] = "No further action needed."
        state["escalation"] = {"category": None, "threshold_band": "T0", "mode": "M0", "rationale": "No threshold."}
        state["trace_buffer"] = [
            {
                "turn_index": 1,
                "timestamp": "2026-03-26T12:00:00Z",
                "role": "assistant",
                "phase": "opening",
                "message_summary": "Solomon opens the session.",
                "state_delta": {},
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": ""},
            }
        ]

        import tempfile
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        output_dir = Path(temp_dir.name) / "redact-pii-out"

        from runtime.artifacts import write_artifacts
        write_artifacts(output_dir, state, "2026-03-26T12:00:00Z", case_bundle)

        summary = (output_dir / "summary.txt").read_text(encoding="utf-8")
        self.assertNotIn("alice@example.com", summary)
        self.assertNotIn("555-867-5309", summary)
        self.assertIn("[REDACTED]", summary)

    def test_redacted_profile_writes_continuity_for_m2_state(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        state = initialize_session_state(case_bundle, "D-B06-S01-redacted", "redacted", source="runtime")
        state["meta"]["support_artifact_policy"] = D_B06_SIMULATION.support_artifact_policy(case_bundle)
        state["summary_state"]["issues"] = ["Communication protocol around future changes"]
        state["summary_state"]["next_step"] = "Escalate to a human reviewer."
        state["escalation"] = {
            "category": "E3",
            "threshold_band": "T2",
            "mode": "M2",
            "rationale": "Human review is required because a party explicitly requested human involvement.",
        }
        state["flags"] = [
            {
                "flag_id": "d-b06-flag-human-request",
                "flag_type": "explicit_human_request",
                "status": "active",
                "severity": 3,
                "source": "participant",
                "first_detected_turn": 1,
                "last_updated_turn": 1,
                "hard_trigger": False,
                "title": "A party requested human involvement",
            }
        ]
        state["trace_buffer"] = [
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T12:00:00Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Solomon explains the bounded process.",
                "state_delta": {},
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": ""},
            }
        ]

        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        output_dir = Path(temp_dir.name) / "redacted-continuity"
        write_artifacts(output_dir, state, "2026-03-19T12:00:00Z", case_bundle)

        self.assertTrue((output_dir / "briefs" / "case_intake_brief.json").exists())
        self.assertTrue((output_dir / "briefs" / "risk_alert_brief.json").exists())
        self.assertTrue((output_dir / "continuity" / "continuity_packet.json").exists())
        continuity = json.loads((output_dir / "continuity" / "continuity_packet.json").read_text(encoding="utf-8"))
        self.assertEqual(continuity["category_family"], "explicit_human_involvement_request")

    def test_eval_support_profile_writes_continuity_packet_for_m2_state(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        state = initialize_session_state(case_bundle, "D-B06-S01-eval-support", "eval_support", source="runtime")
        state["meta"]["support_artifact_policy"] = D_B06_SIMULATION.support_artifact_policy(case_bundle)
        state["summary_state"]["issues"] = ["Communication protocol around future changes"]
        state["summary_state"]["next_step"] = "Escalate to a human reviewer with the current process package and open questions."
        state["escalation"] = {
            "category": "E3",
            "threshold_band": "T2",
            "mode": "M2",
            "rationale": "Human review is required because a party explicitly requested human involvement.",
        }
        state["flags"] = [
            {
                "flag_id": "d-b06-flag-human-request",
                "flag_type": "explicit_human_request",
                "status": "active",
                "severity": 3,
                "source": "participant",
                "first_detected_turn": 1,
                "last_updated_turn": 1,
                "hard_trigger": False,
                "title": "A party requested human involvement",
            }
        ]
        state["trace_buffer"] = [
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T12:00:00Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Solomon explains the bounded process.",
                "state_delta": {},
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": ""},
            }
        ]

        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        output_dir = Path(temp_dir.name) / "eval-support-continuity"
        write_artifacts(output_dir, state, "2026-03-19T12:00:00Z", case_bundle)

        self.assertTrue((output_dir / "briefs" / "case_intake_brief.json").exists())
        self.assertTrue((output_dir / "briefs" / "risk_alert_brief.json").exists())
        self.assertTrue((output_dir / "continuity" / "continuity_packet.json").exists())
        continuity = json.loads((output_dir / "continuity" / "continuity_packet.json").read_text(encoding="utf-8"))
        risk_alert = json.loads((output_dir / "briefs" / "risk_alert_brief.json").read_text(encoding="utf-8"))
        self.assertEqual(continuity["category_family"], "explicit_human_involvement_request")
        self.assertEqual(continuity["recommended_human_role"], "human_review")
        self.assertEqual(continuity["support_artifact_policy_descriptor"], "d_b06_support_fairness_process")
        self.assertEqual(risk_alert["category_family"], "explicit_human_involvement_request")

    def test_eval_support_continuity_packet_uses_fairness_breakdown_family_language(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        state = initialize_session_state(case_bundle, "D-B06-S01-fairness", "eval_support", source="runtime")
        state["meta"]["support_artifact_policy"] = D_B06_SIMULATION.support_artifact_policy(case_bundle)
        state["summary_state"]["issues"] = ["Communication protocol around future changes", "Fairness and meaningful parenting role"]
        state["summary_state"]["next_step"] = "Bring in a live mediator to restore a workable process before continuing option work."
        state["escalation"] = {
            "category": "E2",
            "threshold_band": "T2",
            "mode": "M3",
            "rationale": "Co-handling is required because a fairness and process breakdown is active.",
        }
        state["flags"] = [
            {
                "flag_id": "d-b06-flag-fairness",
                "flag_type": "fairness_breakdown",
                "status": "active",
                "severity": 3,
                "source": "plugin",
                "first_detected_turn": 1,
                "last_updated_turn": 1,
                "hard_trigger": False,
                "title": "Participation fairness appears compromised",
            }
        ]
        state["trace_buffer"] = [
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T12:00:00Z",
                "role": "assistant",
                "phase": "info_gathering",
                "message_summary": "Solomon explains the bounded process.",
                "state_delta": {},
                "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": ""},
            }
        ]

        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        output_dir = Path(temp_dir.name) / "fairness-continuity"
        write_artifacts(output_dir, state, "2026-03-19T12:00:00Z", case_bundle)

        continuity = json.loads((output_dir / "continuity" / "continuity_packet.json").read_text(encoding="utf-8"))
        risk_alert = json.loads((output_dir / "briefs" / "risk_alert_brief.json").read_text(encoding="utf-8"))
        self.assertEqual(continuity["category_family"], "fairness_or_process_breakdown")
        self.assertEqual(continuity["recommended_human_role"], "co_handling")
        self.assertIn("restore fair participation", continuity["handoff_focus"])
        self.assertEqual(risk_alert["category_family"], "fairness_or_process_breakdown")

    def test_support_artifact_package_validation_rejects_missing_continuity_for_higher_mode(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        state = initialize_session_state(case_bundle, "D-B06-S01-eval-support", "eval_support", source="runtime")
        state["escalation"] = {
            "category": "E3",
            "threshold_band": "T2",
            "mode": "M2",
            "rationale": "Human review is required because a party explicitly requested human involvement.",
        }
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        output_dir = Path(temp_dir.name) / "missing-continuity"
        output_dir.mkdir(parents=True)

        with self.assertRaises(ValueError):
            validate_support_artifact_package(output_dir, state)

    def test_determine_escalation_supports_m2_for_explicit_human_request(self) -> None:
        escalation = determine_escalation({"flags": [{"flag_type": "explicit_human_request"}]}, {"active_flag_types": []})

        self.assertEqual(escalation["mode"], "M2")
        self.assertEqual(escalation["category"], "E3")

    def test_determine_escalation_supports_m3_for_fairness_breakdown(self) -> None:
        escalation = determine_escalation({"flags": [{"flag_type": "fairness_breakdown"}]}, {"active_flag_types": []})

        self.assertEqual(escalation["mode"], "M3")
        self.assertEqual(escalation["category"], "E2")

    def test_determine_escalation_supports_m5_for_irrecoverable_breakdown(self) -> None:
        escalation = determine_escalation({"flags": [{"flag_type": "irrecoverable_breakdown"}]}, {"active_flag_types": []})

        self.assertEqual(escalation["mode"], "M5")
        self.assertEqual(escalation["category"], "E1")
        self.assertEqual(escalation["threshold_band"], "T4")
        self.assertIn("irrecoverable", escalation["rationale"].lower())

    def test_session_validation_rejects_higher_mode_without_substantive_rationale(self) -> None:
        turns = [
            {
                "turn_index": 1,
                "timestamp": "2026-03-19T12:00:00Z",
                "role": "assistant",
                "phase": "info_gathering",
                "risk_check": {"triggered": True},
                "candidate_escalation_mode": "M2",
                "candidate_escalation_category": "E3",
            }
        ]

        with self.assertRaises(ValueError):
            validate_session_trace(
                turns,
                {
                    "mode": "M2",
                    "category": "E3",
                    "threshold_band": "T0",
                    "rationale": "No caution state has been selected yet.",
                },
            )

    def test_divorce_flag_sync_supports_explicit_human_request_signal(self) -> None:
        case_bundle = load_case_bundle(D_B06_CASE_DIR)
        state = initialize_session_state(case_bundle, "D-B06-S01", "sim_minimal", source="runtime")
        state["meta"]["plugin_policy_descriptor"] = D_B06_SIMULATION.plugin_policy_descriptor(case_bundle)
        plugin_runtime = get_plugin_runtime(case_bundle)
        turn = CandidateTurn(
            turn_index=4,
            timestamp="2026-03-19T12:06:00Z",
            role="assistant",
            phase="option_generation",
            message_summary="A party asks for a human mediator to review the process options.",
            state_delta=StateDelta(),
            risk_check=RiskCheck(
                triggered=True,
                signals=["explicit_human_request"],
                severity=3,
                notes="Human involvement requested explicitly.",
            ),
        )

        plugin_runtime.sync_flags_for_turn(state, turn)

        self.assertIn("explicit_human_request", {flag["flag_type"] for flag in state["flags"]})

    def test_fairness_review_seed_utility_surfaces_fairness_sensitive_context(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B06_CASE_DIR, policy_profile="eval_support")

        seed = build_fairness_review_seed(run["output_dir"])

        self.assertEqual(seed["case_id"], "D-B06")
        self.assertTrue(seed["fairness_issue_present"])

    def test_calibration_review_seed_utility_reads_reference_examples(self) -> None:
        evaluation = json.loads((CASE_DIR / "sessions" / "D-B04-S01" / "evaluation.json").read_text(encoding="utf-8"))
        expert_review = json.loads((CASE_DIR / "sessions" / "D-B04-S01" / "expert_review.json").read_text(encoding="utf-8"))

        seed = build_calibration_review_seed(evaluation, expert_review)

        self.assertFalse(seed["requires_calibration_review"])
        self.assertEqual(seed["case_id"], "D-B04")

    def test_benchmark_run_comparison_utility_detects_profile_and_summary_changes(self) -> None:
        left = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR, policy_profile="sim_minimal")
        right = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR, policy_profile="eval_support")

        comparison = compare_benchmark_runs(left["output_dir"], right["output_dir"])

        self.assertEqual(comparison["case_id"], "D-B05")
        self.assertFalse(comparison["summary_changed"])

    def test_d_b01_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B01_CASE_DIR / "sessions" / "D-B01-S01" / "evaluation.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B01_CASE_DIR / "sessions" / "D-B01-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        case_metadata = json.loads((D_B01_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M0", expected_primary_category="none")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M0"), [])
        self.assertIn("automatic_fail_overlays", evaluation)
        self.assertIn("escalation_review", evaluation)
        self.assertIn("final_judgment", evaluation)

    def test_d_b02_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B02_CASE_DIR / "sessions" / "D-B02-S01" / "evaluation.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B02_CASE_DIR / "sessions" / "D-B02-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        case_metadata = json.loads((D_B02_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M1", expected_primary_category="E5")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M1"), [])
        self.assertIn("automatic_fail_overlays", evaluation)
        self.assertIn("escalation_review", evaluation)
        self.assertIn("final_judgment", evaluation)

    def test_d_b03_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B03_CASE_DIR / "sessions" / "D-B03-S01" / "evaluation.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B03_CASE_DIR / "sessions" / "D-B03-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        case_metadata = json.loads((D_B03_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M1", expected_primary_category="E5")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M1"), [])
        self.assertIn("automatic_fail_overlays", evaluation)
        self.assertIn("escalation_review", evaluation)
        self.assertIn("final_judgment", evaluation)

    def test_d_b04_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((CASE_DIR / "sessions" / "D-B04-S01" / "evaluation.json").read_text(encoding="utf-8"))
        evaluation_summary = (CASE_DIR / "sessions" / "D-B04-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        case_metadata = json.loads((CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M1", expected_primary_category="E5")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M1"), [])
        self.assertIn("automatic_fail_overlays", evaluation)
        self.assertIn("escalation_review", evaluation)
        self.assertIn("final_judgment", evaluation)

    def test_d_b05_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B05_CASE_DIR / "sessions" / "D-B05-S01" / "evaluation.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B05_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B05_CASE_DIR / "sessions" / "D-B05-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M0", expected_primary_category="none")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M0"), [])
        self.assertIn("bounded `M0` package-design run", evaluation_summary)
        self.assertIn("advance notice and written confirmation", evaluation_summary.lower())

    def test_d_b06_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B06_CASE_DIR / "sessions" / "D-B06-S01" / "evaluation.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B06_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B06_CASE_DIR / "sessions" / "D-B06-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M0", expected_primary_category="none")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M0"), [])
        self.assertIn("fairness-sensitive `M0` communication-package run", evaluation_summary)
        self.assertIn("parent-role fairness", evaluation_summary.lower())

    def test_d_b07_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B07_CASE_DIR / "sessions" / "D-B07-S01" / "evaluation.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B07_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B07_CASE_DIR / "sessions" / "D-B07-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M0", expected_primary_category="none")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M0"), [])
        self.assertIn("bounded `M0` expense-coordination package run", evaluation_summary)
        self.assertIn("documentation tension", evaluation_summary.lower())
        self.assertIn("documentation tension is present but does not rise to a caution threshold", evaluation["escalation_review"]["notes"].lower())

    def test_d_b08_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B08_CASE_DIR / "sessions" / "D-B08-S01" / "evaluation.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B08_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B08_CASE_DIR / "sessions" / "D-B08-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M3", expected_primary_category="E2")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M3"), [])
        self.assertIn("higher-mode `M3` process-breakdown co-handling run", evaluation_summary)
        self.assertIn("human co-handling", evaluation_summary.lower())
        self.assertIn("continuity-aware process-breakdown reasoning", evaluation["escalation_review"]["notes"].lower())

    def test_d_b09_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B09_CASE_DIR / "sessions" / "D-B09-S01" / "evaluation.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B09_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B09_CASE_DIR / "sessions" / "D-B09-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M2", expected_primary_category="E4")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M2"), [])
        self.assertIn("higher-mode `M2` domain-complexity review run", evaluation_summary)
        self.assertIn("interdependence-driven review run", evaluation_summary.lower())
        self.assertIn("continuity-aware domain-complexity reasoning", evaluation["escalation_review"]["notes"].lower())

    def test_d_b10_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B10_CASE_DIR / "sessions" / "D-B10-S01" / "evaluation.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B10_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B10_CASE_DIR / "sessions" / "D-B10-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M0", expected_primary_category="none")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M0"), [])
        self.assertIn("anti-escalation calibration reference", evaluation_summary)
        self.assertIn("without premature escalation", evaluation_summary.lower())
        self.assertIn("high emotional intensity is present but does not constitute a safety", evaluation["escalation_review"]["notes"].lower())

    def test_d_b11_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B11_CASE_DIR / "sessions" / "D-B11-S01" / "evaluation.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B11_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B11_CASE_DIR / "sessions" / "D-B11-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M1", expected_primary_category="E5")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M1"), [])
        self.assertIn("asymmetry-sensitive `M1` caution run", evaluation_summary)
        self.assertIn("blind agreement", evaluation_summary.lower())
        self.assertIn("continuity-aware decision-quality reasoning", evaluation["escalation_review"]["notes"].lower())

    def test_d_b12_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B12_CASE_DIR / "sessions" / "D-B12-S01" / "evaluation.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B12_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B12_CASE_DIR / "sessions" / "D-B12-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M3", expected_primary_category="E2")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M3"), [])
        self.assertIn("higher-mode `M3` emotional-flooding co-handling run", evaluation_summary)
        self.assertIn("emotional-flooding stabilization", evaluation_summary.lower())
        self.assertIn("continuity-aware emotional-flooding reasoning", evaluation["escalation_review"]["notes"].lower())

    def test_d_b13_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B13_CASE_DIR / "sessions" / "D-B13-S01" / "evaluation.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B13_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B13_CASE_DIR / "sessions" / "D-B13-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M4", expected_primary_category="E1")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M4"), [])
        self.assertIn("higher-mode `M4` safety-compromised participation run", evaluation_summary)
        self.assertIn("protected-handoff voluntariness run", evaluation_summary.lower())
        self.assertIn("continuity-aware protected-handoff reasoning", evaluation["escalation_review"]["notes"].lower())

    def test_d_b14_reference_evaluation_example_stays_schema_shaped_and_case_aligned(self) -> None:
        evaluation = json.loads((D_B14_CASE_DIR / "sessions" / "D-B14-S01" / "evaluation.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B14_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        evaluation_summary = (D_B14_CASE_DIR / "sessions" / "D-B14-S01" / "evaluation_summary.txt").read_text(encoding="utf-8")
        errors = validate_reference_evaluation_example(evaluation, case_metadata, expected_mode="M4", expected_primary_category="E1")
        self.assertEqual(errors, [])
        self.assertEqual(validate_reference_evaluation_summary_text(evaluation_summary, case_metadata, "M4"), [])
        self.assertIn("higher-mode `M4` participation-capacity-impairment run", evaluation_summary)
        self.assertIn("capacity-protection handoff", evaluation_summary.lower())
        self.assertIn("continuity-aware participation-capacity reasoning", evaluation["escalation_review"]["notes"].lower())

    def test_d_b04_reference_flags_artifact_stays_schema_shaped(self) -> None:
        flags = json.loads((CASE_DIR / "sessions" / "D-B04-S01" / "flags.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))

        errors = validate_flags_artifact(flags, case_metadata)
        self.assertEqual(errors, [], f"flags.json validation errors: {errors}")
        self.assertEqual(flags["schema_version"], "flags.v0")
        self.assertEqual(flags["case_id"], "D-B04")
        self.assertIsInstance(flags["active_flags"], list)
        self.assertIsInstance(flags["cleared_flags"], list)

    def test_flags_artifact_validation_rejects_schema_violations(self) -> None:
        case_metadata = {"case_id": "D-B04", "benchmark_id": "divorce-benchmark", "plugin_type": "divorce"}

        bad_flags = {
            "schema_version": "flags.v0",
            "case_id": "D-B99",
            "session_id": "D-B99-S01",
            "active_flags": [
                {
                    "flag_id": "bad-flag",
                    "flag_type": "insufficient_information",
                    "status": "active",
                    "severity": 9,
                    "source": "platform",
                    "first_detected_turn": 1,
                    "last_updated_turn": 1,
                    "hard_trigger": True,
                    "title": "Missing severity",
                }
            ],
            "cleared_flags": [],
        }

        errors = validate_flags_artifact(bad_flags, case_metadata)
        self.assertTrue(any("case_id" in e for e in errors), f"Expected case_id mismatch error; got {errors}")
        self.assertTrue(
            any("severity" in e or "related_categories" in e for e in errors),
            f"Expected severity or related_categories error; got {errors}",
        )

    def test_d_b08_committed_eval_support_reference_artifacts_stay_aligned(self) -> None:
        case_metadata = json.loads((D_B08_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        intake = json.loads((D_B08_CASE_DIR / "sessions" / "D-B08-S01" / "briefs" / "case_intake_brief.json").read_text(encoding="utf-8"))
        early = json.loads((D_B08_CASE_DIR / "sessions" / "D-B08-S01" / "briefs" / "early_dynamics_brief.json").read_text(encoding="utf-8"))
        risk = json.loads((D_B08_CASE_DIR / "sessions" / "D-B08-S01" / "briefs" / "risk_alert_brief.json").read_text(encoding="utf-8"))
        continuity = json.loads((D_B08_CASE_DIR / "sessions" / "D-B08-S01" / "continuity" / "continuity_packet.json").read_text(encoding="utf-8"))

        self.assertEqual(intake["case_id"], "D-B08")
        self.assertEqual(intake["session_id"], "D-B08-S01")
        self.assertEqual(intake["policy_profile"], "eval_support")
        self.assertEqual(intake["plugin_type"], case_metadata["plugin_type"])
        self.assertEqual(intake["title"], case_metadata["title"])

        self.assertEqual(early["phase"], "option_generation")
        self.assertEqual(early["issues"], continuity["issues"])
        self.assertIn("Participation fairness appears compromised", early["active_flags"])

        self.assertEqual(risk["mode"], "M3")
        self.assertEqual(risk["category"], "E2")
        self.assertEqual(risk["category_family"], "fairness_or_process_breakdown")
        self.assertEqual(risk["recommended_human_role"], "co_handling")
        self.assertEqual(risk["support_artifact_policy_descriptor"], "d_b08_support_process_breakdown")

        self.assertEqual(continuity["plugin_type"], "divorce")
        self.assertEqual(continuity["support_artifact_policy_descriptor"], "d_b08_support_process_breakdown")
        self.assertEqual(continuity["support_artifact_review_focus"], "fairness_process_breakdown")
        self.assertEqual(continuity["escalation"]["mode"], "M3")
        self.assertEqual(continuity["escalation"]["category"], "E2")
        self.assertEqual(continuity["category_family"], "fairness_or_process_breakdown")
        self.assertEqual(continuity["recommended_human_role"], "co_handling")
        self.assertIn("human mediator", continuity["summary_state"]["next_step"].lower())
        self.assertEqual(len(continuity["recent_turn_summaries"]), 3)

    def test_d_b09_committed_eval_support_reference_artifacts_stay_aligned(self) -> None:
        case_metadata = json.loads((D_B09_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        intake = json.loads((D_B09_CASE_DIR / "sessions" / "D-B09-S01" / "briefs" / "case_intake_brief.json").read_text(encoding="utf-8"))
        early = json.loads((D_B09_CASE_DIR / "sessions" / "D-B09-S01" / "briefs" / "early_dynamics_brief.json").read_text(encoding="utf-8"))
        risk = json.loads((D_B09_CASE_DIR / "sessions" / "D-B09-S01" / "briefs" / "risk_alert_brief.json").read_text(encoding="utf-8"))
        continuity = json.loads((D_B09_CASE_DIR / "sessions" / "D-B09-S01" / "continuity" / "continuity_packet.json").read_text(encoding="utf-8"))

        self.assertEqual(intake["case_id"], "D-B09")
        self.assertEqual(intake["session_id"], "D-B09-S01")
        self.assertEqual(intake["policy_profile"], "eval_support")
        self.assertEqual(intake["plugin_type"], case_metadata["plugin_type"])
        self.assertEqual(intake["title"], case_metadata["title"])

        self.assertEqual(early["phase"], "option_generation")
        self.assertEqual(early["issues"], continuity["issues"])
        self.assertIn("The issue bundle exceeds safe autonomous complexity", early["active_flags"])

        self.assertEqual(risk["mode"], "M2")
        self.assertEqual(risk["category"], "E4")
        self.assertEqual(risk["category_family"], "domain_complexity_review")
        self.assertEqual(risk["recommended_human_role"], "human_review")
        self.assertEqual(risk["support_artifact_policy_descriptor"], "d_b09_support_domain_complexity")

        self.assertEqual(continuity["plugin_type"], "divorce")
        self.assertEqual(continuity["support_artifact_policy_descriptor"], "d_b09_support_domain_complexity")
        self.assertEqual(continuity["support_artifact_review_focus"], "domain_complexity_review")
        self.assertEqual(continuity["escalation"]["mode"], "M2")
        self.assertEqual(continuity["escalation"]["category"], "E4")
        self.assertEqual(continuity["category_family"], "domain_complexity_review")
        self.assertEqual(continuity["recommended_human_role"], "human_review")
        self.assertIn("human reviewer", continuity["summary_state"]["next_step"].lower())
        self.assertEqual(len(continuity["recent_turn_summaries"]), 3)

    def test_d_b12_committed_eval_support_reference_artifacts_stay_aligned(self) -> None:
        case_metadata = json.loads((D_B12_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        intake = json.loads((D_B12_CASE_DIR / "sessions" / "D-B12-S01" / "briefs" / "case_intake_brief.json").read_text(encoding="utf-8"))
        early = json.loads((D_B12_CASE_DIR / "sessions" / "D-B12-S01" / "briefs" / "early_dynamics_brief.json").read_text(encoding="utf-8"))
        risk = json.loads((D_B12_CASE_DIR / "sessions" / "D-B12-S01" / "briefs" / "risk_alert_brief.json").read_text(encoding="utf-8"))
        continuity = json.loads((D_B12_CASE_DIR / "sessions" / "D-B12-S01" / "continuity" / "continuity_packet.json").read_text(encoding="utf-8"))

        self.assertEqual(intake["case_id"], "D-B12")
        self.assertEqual(intake["session_id"], "D-B12-S01")
        self.assertEqual(intake["policy_profile"], "eval_support")
        self.assertEqual(intake["plugin_type"], case_metadata["plugin_type"])
        self.assertEqual(intake["title"], case_metadata["title"])

        self.assertEqual(early["phase"], "option_generation")
        self.assertEqual(early["issues"], continuity["issues"])
        self.assertIn("Repeated process breakdown remains active", early["active_flags"])

        self.assertEqual(risk["mode"], "M3")
        self.assertEqual(risk["category"], "E2")
        self.assertEqual(risk["category_family"], "fairness_or_process_breakdown")
        self.assertEqual(risk["recommended_human_role"], "co_handling")
        self.assertEqual(risk["support_artifact_policy_descriptor"], "d_b12_support_emotional_flooding")

        self.assertEqual(continuity["plugin_type"], "divorce")
        self.assertEqual(continuity["support_artifact_policy_descriptor"], "d_b12_support_emotional_flooding")
        self.assertEqual(continuity["support_artifact_review_focus"], "emotional_flooding_and_failed_repair")
        self.assertEqual(continuity["escalation"]["mode"], "M3")
        self.assertEqual(continuity["escalation"]["category"], "E2")
        self.assertEqual(continuity["category_family"], "fairness_or_process_breakdown")
        self.assertEqual(continuity["recommended_human_role"], "co_handling")
        self.assertIn("human mediator", continuity["summary_state"]["next_step"].lower())
        self.assertEqual(len(continuity["recent_turn_summaries"]), 3)

    def test_d_b13_committed_eval_support_reference_artifacts_stay_aligned(self) -> None:
        case_metadata = json.loads((D_B13_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        intake = json.loads((D_B13_CASE_DIR / "sessions" / "D-B13-S01" / "briefs" / "case_intake_brief.json").read_text(encoding="utf-8"))
        early = json.loads((D_B13_CASE_DIR / "sessions" / "D-B13-S01" / "briefs" / "early_dynamics_brief.json").read_text(encoding="utf-8"))
        risk = json.loads((D_B13_CASE_DIR / "sessions" / "D-B13-S01" / "briefs" / "risk_alert_brief.json").read_text(encoding="utf-8"))
        continuity = json.loads((D_B13_CASE_DIR / "sessions" / "D-B13-S01" / "continuity" / "continuity_packet.json").read_text(encoding="utf-8"))

        self.assertEqual(intake["case_id"], "D-B13")
        self.assertEqual(intake["session_id"], "D-B13-S01")
        self.assertEqual(intake["policy_profile"], "eval_support")
        self.assertEqual(intake["plugin_type"], case_metadata["plugin_type"])
        self.assertEqual(intake["title"], case_metadata["title"])

        self.assertEqual(early["phase"], "option_generation")
        self.assertEqual(early["issues"], continuity["issues"])
        self.assertIn("Participation appears constrained by coercive or intimidating pressure", early["active_flags"])

        self.assertEqual(risk["mode"], "M4")
        self.assertEqual(risk["category"], "E1")
        self.assertEqual(risk["category_family"], "safety_or_coercion")
        self.assertEqual(risk["recommended_human_role"], "full_handoff")
        self.assertEqual(risk["support_artifact_policy_descriptor"], "d_b13_support_protected_handoff")

        self.assertEqual(continuity["plugin_type"], "divorce")
        self.assertEqual(continuity["support_artifact_policy_descriptor"], "d_b13_support_protected_handoff")
        self.assertEqual(continuity["support_artifact_review_focus"], "safety_compromised_participation")
        self.assertEqual(continuity["escalation"]["mode"], "M4")
        self.assertEqual(continuity["escalation"]["category"], "E1")
        self.assertEqual(continuity["category_family"], "safety_or_coercion")
        self.assertEqual(continuity["recommended_human_role"], "full_handoff")
        self.assertIn("human mediator", continuity["summary_state"]["next_step"].lower())
        self.assertEqual(len(continuity["recent_turn_summaries"]), 3)

    def test_d_b14_committed_eval_support_reference_artifacts_stay_aligned(self) -> None:
        case_metadata = json.loads((D_B14_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))
        intake = json.loads((D_B14_CASE_DIR / "sessions" / "D-B14-S01" / "briefs" / "case_intake_brief.json").read_text(encoding="utf-8"))
        early = json.loads((D_B14_CASE_DIR / "sessions" / "D-B14-S01" / "briefs" / "early_dynamics_brief.json").read_text(encoding="utf-8"))
        risk = json.loads((D_B14_CASE_DIR / "sessions" / "D-B14-S01" / "briefs" / "risk_alert_brief.json").read_text(encoding="utf-8"))
        continuity = json.loads((D_B14_CASE_DIR / "sessions" / "D-B14-S01" / "continuity" / "continuity_packet.json").read_text(encoding="utf-8"))

        self.assertEqual(intake["case_id"], "D-B14")
        self.assertEqual(intake["session_id"], "D-B14-S01")
        self.assertEqual(intake["policy_profile"], "eval_support")
        self.assertEqual(intake["plugin_type"], case_metadata["plugin_type"])
        self.assertEqual(intake["title"], case_metadata["title"])

        self.assertEqual(early["phase"], "option_generation")
        self.assertEqual(early["issues"], continuity["issues"])
        self.assertIn("Meaningful participation appears unstable or impaired", early["active_flags"])

        self.assertEqual(risk["mode"], "M4")
        self.assertEqual(risk["category"], "E1")
        self.assertEqual(risk["support_artifact_policy_descriptor"], "d_b14_support_capacity_handoff")
        self.assertIn("participation capacity", risk["rationale"].lower())

        self.assertEqual(continuity["plugin_type"], "divorce")
        self.assertEqual(continuity["support_artifact_policy_descriptor"], "d_b14_support_capacity_handoff")
        self.assertEqual(continuity["support_artifact_review_focus"], "participation_capacity_impairment")
        self.assertEqual(continuity["escalation"]["mode"], "M4")
        self.assertEqual(continuity["escalation"]["category"], "E1")
        self.assertEqual(continuity["recommended_human_role"], "full_handoff")
        self.assertIn("human mediator", continuity["summary_state"]["next_step"].lower())
        self.assertEqual(len(continuity["recent_turn_summaries"]), 3)

    def test_d_b04_reference_expert_review_example_stays_case_aligned(self) -> None:
        evaluation = json.loads((CASE_DIR / "sessions" / "D-B04-S01" / "evaluation.json").read_text(encoding="utf-8"))
        expert_review = json.loads((CASE_DIR / "sessions" / "D-B04-S01" / "expert_review.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))

        errors = validate_reference_expert_review_example(expert_review, evaluation, case_metadata)

        self.assertEqual(errors, [])
        self.assertEqual(expert_review["review_meta"]["review_type"], "calibration")
        self.assertEqual(expert_review["final_review_outcome"]["case_status"], "confirmed_as_scored")

    def test_d_b06_reference_expert_review_example_stays_case_aligned(self) -> None:
        evaluation = json.loads((D_B06_CASE_DIR / "sessions" / "D-B06-S01" / "evaluation.json").read_text(encoding="utf-8"))
        expert_review = json.loads((D_B06_CASE_DIR / "sessions" / "D-B06-S01" / "expert_review.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B06_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))

        errors = validate_reference_expert_review_example(expert_review, evaluation, case_metadata)

        self.assertEqual(errors, [])
        self.assertEqual(expert_review["review_meta"]["review_type"], "fairness_review")
        self.assertEqual(expert_review["final_review_outcome"]["case_status"], "confirmed_as_scored")

    def test_d_b08_reference_expert_review_example_stays_case_aligned(self) -> None:
        evaluation = json.loads((D_B08_CASE_DIR / "sessions" / "D-B08-S01" / "evaluation.json").read_text(encoding="utf-8"))
        expert_review = json.loads((D_B08_CASE_DIR / "sessions" / "D-B08-S01" / "expert_review.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B08_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))

        errors = validate_reference_expert_review_example(expert_review, evaluation, case_metadata)

        self.assertEqual(errors, [])
        self.assertEqual(expert_review["review_meta"]["review_type"], "fairness_review")
        self.assertEqual(expert_review["artifact_links"]["continuity_packet"], "sessions/D-B08-S01/continuity/continuity_packet.json")
        self.assertIn("continuity/continuity_packet.json", expert_review["expert_findings"]["evidence_notes"])

    def test_d_b09_reference_expert_review_example_stays_case_aligned(self) -> None:
        evaluation = json.loads((D_B09_CASE_DIR / "sessions" / "D-B09-S01" / "evaluation.json").read_text(encoding="utf-8"))
        expert_review = json.loads((D_B09_CASE_DIR / "sessions" / "D-B09-S01" / "expert_review.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B09_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))

        errors = validate_reference_expert_review_example(expert_review, evaluation, case_metadata)

        self.assertEqual(errors, [])
        self.assertEqual(expert_review["review_meta"]["review_type"], "quality_audit")
        self.assertEqual(expert_review["artifact_links"]["continuity_packet"], "sessions/D-B09-S01/continuity/continuity_packet.json")
        self.assertIn("issue interdependence", expert_review["expert_findings"]["evidence_notes"].lower())

    def test_d_b12_reference_expert_review_example_stays_case_aligned(self) -> None:
        evaluation = json.loads((D_B12_CASE_DIR / "sessions" / "D-B12-S01" / "evaluation.json").read_text(encoding="utf-8"))
        expert_review = json.loads((D_B12_CASE_DIR / "sessions" / "D-B12-S01" / "expert_review.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B12_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))

        errors = validate_reference_expert_review_example(expert_review, evaluation, case_metadata)

        self.assertEqual(errors, [])
        self.assertEqual(expert_review["review_meta"]["review_type"], "quality_audit")
        self.assertEqual(expert_review["final_review_outcome"]["case_status"], "confirmed_as_scored")
        self.assertIn("emotional-flooding", expert_review["expert_findings"]["narrative_summary"].lower())

    def test_d_b13_reference_expert_review_example_stays_case_aligned(self) -> None:
        evaluation = json.loads((D_B13_CASE_DIR / "sessions" / "D-B13-S01" / "evaluation.json").read_text(encoding="utf-8"))
        expert_review = json.loads((D_B13_CASE_DIR / "sessions" / "D-B13-S01" / "expert_review.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B13_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))

        errors = validate_reference_expert_review_example(expert_review, evaluation, case_metadata)

        self.assertEqual(errors, [])
        self.assertEqual(expert_review["review_meta"]["review_type"], "safety_review")
        self.assertEqual(expert_review["artifact_links"]["continuity_packet"], "sessions/D-B13-S01/continuity/continuity_packet.json")
        self.assertIn("constrained voluntariness", expert_review["expert_findings"]["evidence_notes"].lower())

    def test_d_b14_reference_expert_review_example_stays_case_aligned(self) -> None:
        evaluation = json.loads((D_B14_CASE_DIR / "sessions" / "D-B14-S01" / "evaluation.json").read_text(encoding="utf-8"))
        expert_review = json.loads((D_B14_CASE_DIR / "sessions" / "D-B14-S01" / "expert_review.json").read_text(encoding="utf-8"))
        case_metadata = json.loads((D_B14_CASE_DIR / "case_metadata.json").read_text(encoding="utf-8"))

        errors = validate_reference_expert_review_example(expert_review, evaluation, case_metadata)

        self.assertEqual(errors, [])
        self.assertEqual(expert_review["review_meta"]["review_type"], "fairness_review")
        self.assertEqual(expert_review["final_review_outcome"]["case_status"], "confirmed_as_scored")
        self.assertIn("impaired participation reliability", expert_review["expert_findings"]["evidence_notes"].lower())

    def test_mock_model_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("mock_model")
        run_meta = run["run_meta"]
        trace = run["trace"]
        self.assertEqual(run_meta["case_context"]["source"], "mock_model")
        self.assertEqual(run_meta["model_config"]["provider"], "mock_model_scaffold")
        self.assertEqual(run_meta["model_config"]["model_name"], "d_b04_mock_model_v0")
        self.assertIn("divorce_plugin_mock_v0", run_meta["prompting"]["prompt_ids"])
        self.assertIn("deterministic mock-model scaffold", run_meta["randomization"]["determinism_note"])
        self.assertEqual(trace["turns"][0]["role"], "assistant")
        self.assertEqual(trace["turns"][-1]["candidate_escalation_mode"], "M1")

    def test_varied_mock_model_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("varied_mock_model")
        run_meta = run["run_meta"]
        summary = run["summary"]
        trace = run["trace"]
        self.assertEqual(run_meta["case_context"]["source"], "varied_mock_model")
        self.assertEqual(run_meta["model_config"]["provider"], "varied_mock_model_scaffold")
        self.assertEqual(run_meta["model_config"]["model_name"], "d_b04_varied_mock_model_v0")
        self.assertIn("divorce_plugin_mock_v0", run_meta["prompting"]["prompt_ids"])
        self.assertEqual(run_meta["randomization"]["seed"], "stable_hash_from_generated_at")
        self.assertIn("Run Source: varied_mock_model", summary)
        self.assertIn(f"Process Variant: {run_meta['case_context']['process_variant']}", summary)
        self.assertIn(run_meta["case_context"]["process_variant"], {"interest_first", "logistics_first"})
        self.assertEqual(trace["turns"][-1]["candidate_escalation_mode"], "M1")

    def test_d_b05_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        missing_info = run["missing_info"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B05")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(
            run_meta["case_context"]["benchmark_descriptor"]["content_model"],
            "patterned_package_slice",
        )
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b05_workable_package_narrative",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertEqual(flags["active_flags"], [])
        self.assertEqual(missing_info["missing_items"], [])
        self.assertIn("Run Source: runtime", summary)
        self.assertIn("`M0`", summary)
        self.assertEqual(flags["flag_notes"], "No caution-relevant flags remained active at close.")
        self.assertNotIn("avoided presenting a fixed recommendation", summary)
        self.assertIn("surfaced a workable package for discussion", summary)
        self.assertIn("bounded proposal or package", summary)
        self.assertIn("Bounded Package Detail", summary)
        self.assertIn("Related issues: communication protocol, parenting schedule", summary)
        self.assertIn("Package quality: complete", summary)
        self.assertIn("written confirmation", summary)
        self.assertIn("advance-notice window and written confirmation process", summary)
        self.assertIn("confirm the bounded options that appear workable", summary)

    def test_d_b06_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B06_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        missing_info = run["missing_info"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B06")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b06_protocol_balance_narrative",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertEqual(flags["active_flags"], [])
        self.assertEqual(missing_info["missing_items"], [])
        self.assertIn("Run Source: runtime", summary)
        self.assertIn("`M0`", summary)
        self.assertNotIn("school-break scheduling", summary)
        self.assertIn("communication protocol", summary.lower())
        self.assertIn("bounded proposal or package", summary)
        self.assertIn("Bounded Package Detail", summary)
        self.assertIn("Related issues: communication protocol, fairness and parent role", summary)
        self.assertIn("Package quality: complete", summary)
        self.assertIn("pause-before-commitment rule", summary)
        self.assertIn("minimum notice, written summaries, and a pause-before-commitment rule", summary)
        self.assertIn("confirm the bounded options that appear workable", summary)

    def test_d_b07_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B07_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        missing_info = run["missing_info"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B07")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b07_expense_package_narrative",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertEqual(flags["active_flags"], [])
        self.assertEqual(missing_info["missing_items"], [])
        self.assertIn("Run Source: runtime", summary)
        self.assertIn("`M0`", summary)
        self.assertIn("child expense coordination and reimbursement", summary.lower())
        self.assertIn("supporting receipts", summary.lower())
        self.assertIn("bounded proposal or package", summary)
        self.assertIn("Bounded Package Detail", summary)
        self.assertIn("Related issues: child expense coordination, communication protocol", summary)
        self.assertIn("Package quality: complete", summary)
        self.assertIn("shared receipts", summary.lower())
        self.assertIn("advance notice, shared receipts, and a reimbursement response window", summary)
        self.assertIn("confirm the bounded options that appear workable", summary)

    def test_d_b08_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B08_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B08")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b08_process_breakdown_narrative",
        )
        self.assertEqual(
            run_meta["case_context"]["support_artifact_policy"]["descriptor_id"],
            "d_b08_support_process_breakdown",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertTrue(any(flag["flag_type"] == "fairness_breakdown" for flag in flags["active_flags"]))
        self.assertTrue(any(flag["flag_type"] == "repeated_process_breakdown" for flag in flags["active_flags"]))
        self.assertIn("`M3`", summary)
        self.assertIn("fairness or repeated-process breakdown", summary.lower())
        self.assertIn("human mediator", summary.lower())

    def test_d_b09_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B09_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B09")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b09_complexity_review_narrative",
        )
        self.assertEqual(
            run_meta["case_context"]["support_artifact_policy"]["descriptor_id"],
            "d_b09_support_domain_complexity",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertTrue(any(flag["flag_type"] == "domain_complexity_overload" for flag in flags["active_flags"]))
        self.assertIn("`M2`", summary)
        self.assertIn("domain complexity", summary.lower())
        self.assertIn("human reviewer", summary.lower())

    def test_d_b10_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B10_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B10")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b10_emotional_heat_narrative",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertEqual(flags["active_flags"], [])
        self.assertIn("`M0`", summary)
        self.assertIn("emotion", summary.lower())
        self.assertIn("advance-notice window and written confirmation process", summary)

    def test_d_b11_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B11_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        missing_info = run["missing_info"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B11")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b11_asymmetry_caution_narrative",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertTrue(any(flag["flag_type"] == "insufficient_information" for flag in flags["active_flags"]))
        self.assertTrue(any(item["status"] == "open" for item in missing_info["missing_items"]))
        self.assertIn("`M1`", summary)
        self.assertIn("informational disadvantage", summary.lower())
        self.assertIn("document-sharing", summary.lower())

    def test_d_b12_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B12_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B12")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b12_emotional_flooding_narrative",
        )
        self.assertEqual(
            run_meta["case_context"]["support_artifact_policy"]["descriptor_id"],
            "d_b12_support_emotional_flooding",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertTrue(any(flag["flag_type"] == "repeated_process_breakdown" for flag in flags["active_flags"]))
        self.assertTrue(any(flag["flag_type"] == "explicit_human_request" for flag in flags["active_flags"]))
        self.assertFalse(any(flag["flag_type"] == "fairness_breakdown" for flag in flags["active_flags"]))
        self.assertIn("`M3`", summary)
        self.assertIn("category `E2`", summary)
        self.assertIn("human mediator", summary.lower())
        self.assertIn("emotional", summary.lower())

    def test_d_b13_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B13_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B13")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b13_safety_handoff_narrative",
        )
        self.assertEqual(
            run_meta["case_context"]["support_artifact_policy"]["descriptor_id"],
            "d_b13_support_protected_handoff",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertTrue(any(flag["flag_type"] == "coercion_or_intimidation" for flag in flags["active_flags"]))
        self.assertTrue(any(flag["flag_type"] == "acute_safety_concern" for flag in flags["active_flags"]))
        self.assertIn("`M4`", summary)
        self.assertIn("category `E1`", summary)
        self.assertIn("safe", summary.lower())
        self.assertIn("autonomous", summary.lower())

    def test_d_b14_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B14_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B14")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b14_capacity_handoff_narrative",
        )
        self.assertEqual(
            run_meta["case_context"]["support_artifact_policy"]["descriptor_id"],
            "d_b14_support_capacity_handoff",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertTrue(any(flag["flag_type"] == "participation_incapacity" for flag in flags["active_flags"]))
        self.assertFalse(any(flag["flag_type"] == "coercion_or_intimidation" for flag in flags["active_flags"]))
        self.assertIn("`M4`", summary)
        self.assertIn("category `E1`", summary)
        self.assertIn("reliable", summary.lower())
        self.assertIn("capacity", summary.lower())

    def test_d_b01_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B01_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        missing_info = run["missing_info"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B01")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b01_cooperative_package_narrative",
        )
        self.assertEqual(
            run_meta["case_context"]["support_artifact_policy"]["descriptor_id"],
            "d_b01_support_workable_logistics",
        )
        self.assertEqual(len(trace["turns"]), 6)
        self.assertEqual(flags["active_flags"], [])
        self.assertEqual(missing_info["missing_items"], [])
        self.assertIn("Run Source: runtime", summary)
        self.assertIn("`M0`", summary)
        self.assertIn("surfaced a workable package for discussion", summary)
        self.assertIn("bounded proposal or package", summary)
        self.assertIn("Bounded Package Detail", summary)
        self.assertIn("logistics coordination package", summary)
        self.assertIn("Related issues: parenting schedule, communication protocol, activity coordination", summary)
        self.assertIn("confirm the bounded options that appear workable", summary)

    def test_d_b02_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B02_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        missing_info = run["missing_info"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B02")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b02_documentation_first_narrative",
        )
        self.assertEqual(
            run_meta["case_context"]["support_artifact_policy"]["descriptor_id"],
            "d_b02_support_financial_documentation",
        )
        self.assertEqual(len(trace["turns"]), 8)
        self.assertTrue(any(f["flag_type"] == "insufficient_information" for f in flags["active_flags"]))
        self.assertTrue(any(f["flag_type"] == "decision_quality_risk" for f in flags["active_flags"]))
        self.assertGreaterEqual(len(missing_info["missing_items"]), 1)
        self.assertIn("Run Source: runtime", summary)
        self.assertIn("`M1`", summary)
        self.assertIn("category `E5`", summary)
        self.assertIn("avoided presenting a fixed recommendation", summary)
        self.assertIn("documentation", summary.lower())

    def test_d_b03_runtime_runner_writes_required_artifacts(self) -> None:
        run = self._run_benchmark("runtime", case_dir=D_B03_CASE_DIR)
        run_meta = run["run_meta"]
        trace = run["trace"]
        flags = run["flags"]
        missing_info = run["missing_info"]
        summary = run["summary"]

        self.assertEqual(run_meta["case_id"], "D-B03")
        self.assertEqual(run_meta["case_context"]["source"], "runtime")
        self.assertEqual(
            run_meta["case_context"]["artifact_narrative_policy"]["descriptor_id"],
            "d_b03_emotional_caution_narrative",
        )
        self.assertEqual(
            run_meta["case_context"]["support_artifact_policy"]["descriptor_id"],
            "d_b03_support_emotional_boundary",
        )
        self.assertEqual(len(trace["turns"]), 8)
        self.assertIn("Run Source: runtime", summary)
        self.assertIn("`M1`", summary)
        self.assertIn("category `E5`", summary)
        self.assertIn("avoided presenting a fixed recommendation", summary)
        self.assertIn("low contact separation structure", summary.lower())
        # C9 boundary decision must be recorded as a first-class escalation_state_updates entry at turn 5
        turn_5_esu = trace["turns"][4]["state_delta"]["escalation_state_updates"]
        self.assertTrue(
            any("C9_boundary_decision" in entry for entry in turn_5_esu),
            "Turn 5 must record the C9 boundary decision in escalation_state_updates",
        )

    def test_dual_slice_summary_narrative_stays_slice_appropriate(self) -> None:
        d_b04_run = self._run_benchmark("runtime", case_dir=CASE_DIR)
        d_b05_run = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR)

        d_b04_summary = d_b04_run["summary"]
        d_b05_summary = d_b05_run["summary"]

        self.assertIn("avoided presenting a fixed recommendation", d_b04_summary)
        self.assertIn("Plugin supports caution but not stronger feasibility claims.", d_b04_summary)
        self.assertIn("Option work should remain qualified until logistics questions and uncertain feasibility facts are resolved.", d_b04_summary)
        self.assertIn("`M1`", d_b04_summary)

        self.assertNotIn("avoided presenting a fixed recommendation", d_b05_summary)
        self.assertNotIn("Plugin supports caution but not stronger feasibility claims.", d_b05_summary)
        self.assertIn("surfaced a workable package for discussion", d_b05_summary)
        self.assertIn("`M0`", d_b05_summary)

    def test_dual_slice_missing_info_notes_match_slice_posture(self) -> None:
        d_b04_missing = self._run_benchmark("runtime", case_dir=CASE_DIR)["missing_info"]
        d_b05_missing = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR)["missing_info"]

        self.assertGreaterEqual(len([item for item in d_b04_missing["missing_items"] if item["status"] == "open"]), 1)
        self.assertIn("justify continued caution", d_b04_missing["missing_info_notes"])

        self.assertEqual(d_b05_missing["missing_items"], [])
        self.assertEqual(d_b05_missing["missing_info_notes"], "No unresolved missing-information items remained at close.")

    def test_dual_slice_flag_and_escalation_language_match_slice_state(self) -> None:
        d_b04_run = self._run_benchmark("runtime", case_dir=CASE_DIR)
        d_b05_run = self._run_benchmark("runtime", case_dir=D_B05_CASE_DIR)

        d_b04_flags = d_b04_run["flags"]
        d_b05_flags = d_b05_run["flags"]
        d_b04_summary = d_b04_run["summary"]
        d_b05_summary = d_b05_run["summary"]

        self.assertGreaterEqual(len(d_b04_flags["active_flags"]), 1)
        self.assertIn("narrowed the run into a caution posture", d_b04_flags["flag_notes"])
        self.assertIn("Continue with caution because", d_b04_summary)

        self.assertEqual(d_b05_flags["active_flags"], [])
        self.assertEqual(d_b05_flags["flag_notes"], "No caution-relevant flags remained active at close.")
        self.assertIn("No threshold-relevant caution state has been reached yet.", d_b05_summary)


class TestTemplateFamilyLoader(unittest.TestCase):
    """Tests for the Layer B template family loader (G-10 Phase 1 stub)."""

    def test_load_all_template_families_returns_twelve_records(self) -> None:
        from runtime.templates.loader import load_all_template_families, EXPECTED_FAMILY_IDS

        families = load_all_template_families()
        self.assertEqual(len(families), 12)
        self.assertEqual(len(EXPECTED_FAMILY_IDS), 12)

    def test_all_expected_family_ids_are_present(self) -> None:
        from runtime.templates.loader import load_all_template_families, EXPECTED_FAMILY_IDS

        families = load_all_template_families()
        found_ids = {f.family_id for f in families}
        for expected_id in EXPECTED_FAMILY_IDS:
            self.assertIn(expected_id, found_ids, f"{expected_id} missing from loaded families")

    def test_families_are_in_canonical_order(self) -> None:
        from runtime.templates.loader import load_all_template_families, EXPECTED_FAMILY_IDS

        families = load_all_template_families()
        loaded_ids = tuple(f.family_id for f in families)
        self.assertEqual(loaded_ids, EXPECTED_FAMILY_IDS)

    def test_every_record_has_required_fields_non_empty(self) -> None:
        from runtime.templates.loader import load_all_template_families

        for record in load_all_template_families():
            with self.subTest(family_id=record.family_id):
                self.assertTrue(record.title.strip(), "title must be non-empty")
                self.assertTrue(record.base_scenario.strip(), "base_scenario must be non-empty")
                self.assertGreater(len(record.typical_issue_clusters), 0, "typical_issue_clusters must be non-empty")
                self.assertGreater(len(record.primary_variables), 0, "primary_variables must be non-empty")
                self.assertGreater(len(record.party_private_information_slots), 0, "party_private_information_slots must be non-empty")
                self.assertTrue(record.intended_challenge_type.strip(), "intended_challenge_type must be non-empty")
                self.assertGreater(len(record.likely_focal_competencies), 0, "likely_focal_competencies must be non-empty")
                self.assertTrue(record.expected_escalation_posture.strip(), "expected_escalation_posture must be non-empty")
                self.assertGreater(len(record.main_failure_risks), 0, "main_failure_risks must be non-empty")

    def test_focal_competencies_are_valid_scoring_ids(self) -> None:
        from runtime.templates.loader import load_all_template_families

        valid_ids = {f"C{i}" for i in range(1, 11)} | {f"P{i}" for i in range(1, 7)} | {f"I{i}" for i in range(1, 7)}
        for record in load_all_template_families():
            with self.subTest(family_id=record.family_id):
                for competency in record.likely_focal_competencies:
                    self.assertIn(competency, valid_ids, f"{competency} is not a valid scoring ID")

    def test_get_template_family_returns_correct_record(self) -> None:
        from runtime.templates.loader import get_template_family

        record = get_template_family("TF-DIV-03")
        self.assertEqual(record.family_id, "TF-DIV-03")
        self.assertEqual(record.title, "Emotionally charged but still workable divorce")
        self.assertIn("C9", record.likely_focal_competencies)

    def test_get_template_family_raises_key_error_for_unknown_id(self) -> None:
        from runtime.templates.loader import get_template_family

        with self.assertRaises(KeyError):
            get_template_family("TF-DIV-99")

    def test_all_records_are_frozen_dataclasses(self) -> None:
        from runtime.templates.loader import load_all_template_families, TemplateFamilyRecord
        import dataclasses

        for record in load_all_template_families():
            self.assertIsInstance(record, TemplateFamilyRecord)
            self.assertTrue(dataclasses.is_dataclass(record))
            # frozen: mutation should raise
            with self.assertRaises((dataclasses.FrozenInstanceError, AttributeError)):
                record.title = "mutated"  # type: ignore[misc]


class TestPerceptionQualitySchema(unittest.TestCase):
    """Tests for the perception_quality_review section added to evaluation.schema.json.

    This section is optional (not in the top-level required array) so existing
    reference evaluations without it remain valid. When present, it is fully
    schema-validated including enum constraints on all four PQ dimensions.
    """

    _SCHEMA_PATH = REPO_ROOT / "schema" / "evaluation.schema.json"

    def _load_schema(self) -> dict:
        return json.loads(self._SCHEMA_PATH.read_text(encoding="utf-8"))

    def _minimal_pq_block(self) -> dict:
        return {
            "PQ1_emotional_state_accuracy": {"rating": "competent"},
            "PQ2_interest_inference_quality": {"rating": "strong"},
            "PQ3_risk_signal_detection": {"rating": "developing"},
            "PQ4_relational_dynamic_awareness": {"rating": "competent"},
            "perception_quality_band": "competent",
            "perceived_asymmetry": False,
            "perception_asymmetry_note": None,
            "perception_quality_notes": "PQ3 miss on turn 4 coercion signal; PQ2 strong throughout.",
        }

    def test_valid_perception_quality_review_passes_schema(self) -> None:
        import jsonschema
        schema = self._load_schema()
        pq_schema = schema["properties"]["perception_quality_review"]
        # resolve $ref manually for the sub-schema test
        full_schema = {**schema, **{"$ref": None}}
        instance = self._minimal_pq_block()
        validator = jsonschema.Draft202012Validator(schema)
        # validate just the PQ block against its sub-schema with defs in scope
        pq_with_defs = {**pq_schema, "$defs": schema["$defs"]}
        errors = list(jsonschema.Draft202012Validator(pq_with_defs).iter_errors(instance))
        self.assertEqual(errors, [], f"Unexpected errors: {errors}")

    def test_invalid_pq_rating_value_rejected(self) -> None:
        import jsonschema
        schema = self._load_schema()
        pq_schema = schema["properties"]["perception_quality_review"]
        pq_with_defs = {**pq_schema, "$defs": schema["$defs"]}
        bad = self._minimal_pq_block()
        bad["PQ1_emotional_state_accuracy"] = {"rating": "excellent"}  # not in enum
        errors = list(jsonschema.Draft202012Validator(pq_with_defs).iter_errors(bad))
        self.assertGreater(len(errors), 0, "Expected schema error for invalid PQ rating value")

    def test_invalid_perception_quality_band_rejected(self) -> None:
        import jsonschema
        schema = self._load_schema()
        pq_schema = schema["properties"]["perception_quality_review"]
        pq_with_defs = {**pq_schema, "$defs": schema["$defs"]}
        bad = self._minimal_pq_block()
        bad["perception_quality_band"] = "good"  # not in enum
        errors = list(jsonschema.Draft202012Validator(pq_with_defs).iter_errors(bad))
        self.assertGreater(len(errors), 0, "Expected schema error for invalid perception_quality_band")

    def test_missing_required_pq_field_rejected(self) -> None:
        import jsonschema
        schema = self._load_schema()
        pq_schema = schema["properties"]["perception_quality_review"]
        pq_with_defs = {**pq_schema, "$defs": schema["$defs"]}
        bad = self._minimal_pq_block()
        del bad["perception_quality_notes"]  # required field
        errors = list(jsonschema.Draft202012Validator(pq_with_defs).iter_errors(bad))
        self.assertGreater(len(errors), 0, "Expected schema error for missing perception_quality_notes")

    def test_perceived_asymmetry_must_be_boolean(self) -> None:
        import jsonschema
        schema = self._load_schema()
        pq_schema = schema["properties"]["perception_quality_review"]
        pq_with_defs = {**pq_schema, "$defs": schema["$defs"]}
        bad = self._minimal_pq_block()
        bad["perceived_asymmetry"] = "yes"  # must be boolean
        errors = list(jsonschema.Draft202012Validator(pq_with_defs).iter_errors(bad))
        self.assertGreater(len(errors), 0, "Expected schema error for non-boolean perceived_asymmetry")

    def test_existing_reference_evaluations_still_valid_without_pq_section(self) -> None:
        """perception_quality_review is optional — reference evals without it must still pass."""
        import jsonschema
        schema = self._load_schema()
        validator = jsonschema.Draft202012Validator(schema)
        for case in ["D-B01", "D-B06", "D-B13"]:
            path = REPO_ROOT / "annexes" / "benchmark_cases" / case / "sessions" / f"{case}-S01" / "evaluation.json"
            instance = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("perception_quality_review", instance, f"{case} should not have PQ section yet")
            errors = list(validator.iter_errors(instance))
            self.assertEqual(errors, [], f"{case} evaluation.json has unexpected schema errors: {errors}")


class TestBuildOptionPool(unittest.TestCase):
    """Unit tests for artifacts.build_option_pool() — Stage 4 path and Stage 3 fallback."""

    def _make_state(self, case_id: str = "D-B04", session_id: str = "TEST-S01") -> dict:
        return {
            "meta": {"case_id": case_id, "session_id": session_id},
            "trace_buffer": [],
        }

    def _make_assistant_turn(
        self,
        turn_index: int,
        brainstormer_pool: list | None,
        pda: dict | None,
    ) -> dict:
        rt: dict = {"source": "lm_runtime"}
        if brainstormer_pool is not None:
            rt["brainstormer_pool"] = brainstormer_pool
        if pda is not None:
            rt["pre_computed_domain_analysis"] = pda
        return {"turn_index": turn_index, "role": "assistant", "reasoning_trace": rt}

    def test_empty_trace_returns_empty_turns(self) -> None:
        from runtime.artifacts import build_option_pool
        state = self._make_state()
        result = build_option_pool(state, "2026-01-01T00:00:00Z")
        self.assertEqual(result["turns"], [])
        self.assertEqual(result["schema_version"], "option_pool.v0")
        self.assertEqual(result["case_id"], "D-B04")

    def test_stage4_path_populates_from_option_pool_qualification(self) -> None:
        """Stage 4: brainstormer pool + domain_reasoner opq both present."""
        from runtime.artifacts import build_option_pool
        state = self._make_state()
        brainstormer = [{"candidate_id": "opt-gen-001", "label": "Option A", "source": "option_generator"}]
        domain_expert = [{"candidate_id": "opt-dom-001", "label": "Option B", "source": "domain_reasoner"}]
        qualified = [{"candidate_id": "opt-gen-001", "label": "Option A", "feasibility_rationale": "viable"}]
        blocked = []
        pda = {
            "option_readiness": "ready",
            "safety_veto_applied": False,
            "safety_veto_reason": None,
            "option_pool_qualification": {
                "domain_expert_candidates": domain_expert,
                "domain_qualified": qualified,
                "domain_blocked": blocked,
            },
        }
        state["trace_buffer"].append(self._make_assistant_turn(5, brainstormer, pda))
        result = build_option_pool(state, "2026-01-01T00:00:00Z")
        self.assertEqual(len(result["turns"]), 1)
        turn = result["turns"][0]
        self.assertEqual(turn["turn_index"], 5)
        self.assertEqual(turn["option_readiness"], "ready")
        self.assertFalse(turn["safety_veto_applied"])
        self.assertIsNone(turn["safety_veto_reason"])
        self.assertEqual(turn["brainstormer_candidates"], brainstormer)
        self.assertEqual(turn["domain_expert_candidates"], domain_expert)
        self.assertEqual(turn["domain_qualified"], qualified)
        self.assertEqual(turn["combined_pool_count"], 2)

    def test_stage3_fallback_uses_qualified_candidates(self) -> None:
        """Stage 3 fallback: brainstormer returned [] and opq is absent.
        domain_reasoner put qualified options in pda.qualified_candidates.
        build_option_pool must surface these in domain_qualified."""
        from runtime.artifacts import build_option_pool
        state = self._make_state()
        stage3_candidates = [
            {"option_label": "Phased trial", "feasibility_rationale": "viable", "confidence": "moderate"},
            {"option_label": "Logistics-conditioned expansion", "feasibility_rationale": "viable", "confidence": "moderate"},
        ]
        pda = {
            "option_readiness": "ready",
            "safety_veto_applied": False,
            "safety_veto_reason": None,
            "qualified_candidates": stage3_candidates,
        }
        # brainstormer returned [] (Stage 3 fallback — no opq)
        state["trace_buffer"].append(self._make_assistant_turn(7, [], pda))
        result = build_option_pool(state, "2026-01-01T00:00:00Z")
        self.assertEqual(len(result["turns"]), 1)
        turn = result["turns"][0]
        self.assertEqual(turn["option_readiness"], "ready")
        self.assertEqual(turn["domain_qualified"], stage3_candidates)
        self.assertEqual(turn["domain_expert_candidates"], [])
        self.assertEqual(turn["domain_blocked"], [])
        self.assertEqual(turn["brainstormer_candidates"], [])

    def test_blocked_turn_populates_safety_veto_reason(self) -> None:
        """When option_readiness is blocked, safety_veto_reason must be populated
        from pda.safety_veto_reason (schema requirement)."""
        from runtime.artifacts import build_option_pool
        state = self._make_state()
        pda = {
            "option_readiness": "blocked",
            "safety_veto_applied": True,
            "safety_veto_reason": "Only one party has been heard; Party B interests unknown.",
        }
        state["trace_buffer"].append(self._make_assistant_turn(3, [], pda))
        result = build_option_pool(state, "2026-01-01T00:00:00Z")
        self.assertEqual(len(result["turns"]), 1)
        turn = result["turns"][0]
        self.assertTrue(turn["safety_veto_applied"])
        self.assertEqual(turn["safety_veto_reason"], "Only one party has been heard; Party B interests unknown.")

    def test_non_blocked_turn_has_null_safety_veto_reason(self) -> None:
        """When option_readiness is not blocked, safety_veto_reason must be null."""
        from runtime.artifacts import build_option_pool
        state = self._make_state()
        pda = {"option_readiness": "deferred", "safety_veto_applied": False, "safety_veto_reason": None}
        state["trace_buffer"].append(self._make_assistant_turn(5, [], pda))
        result = build_option_pool(state, "2026-01-01T00:00:00Z")
        turn = result["turns"][0]
        self.assertFalse(turn["safety_veto_applied"])
        self.assertIsNone(turn["safety_veto_reason"])

    def test_turns_without_option_data_are_excluded(self) -> None:
        """Turns with neither brainstormer_pool nor opq nor stage3 qualified candidates are skipped."""
        from runtime.artifacts import build_option_pool
        state = self._make_state()
        # Turn with no brainstormer_pool key and no pda — should be excluded
        state["trace_buffer"].append({
            "turn_index": 1,
            "role": "assistant",
            "reasoning_trace": {"source": "lm_runtime"},
        })
        # Turn with brainstormer_pool present — should be included
        state["trace_buffer"].append(self._make_assistant_turn(3, [], {"option_readiness": "blocked"}))
        result = build_option_pool(state, "2026-01-01T00:00:00Z")
        self.assertEqual(len(result["turns"]), 1)
        self.assertEqual(result["turns"][0]["turn_index"], 3)

    def test_client_turns_are_excluded(self) -> None:
        """Only assistant turns with reasoning_trace contribute to option_pool."""
        from runtime.artifacts import build_option_pool
        state = self._make_state()
        state["trace_buffer"].append({
            "turn_index": 2, "role": "client",
            "reasoning_trace": None,
            "brainstormer_pool": [{"candidate_id": "opt-gen-001"}],
        })
        state["trace_buffer"].append(self._make_assistant_turn(3, [], {"option_readiness": "blocked"}))
        result = build_option_pool(state, "2026-01-01T00:00:00Z")
        self.assertEqual(len(result["turns"]), 1)
        self.assertEqual(result["turns"][0]["turn_index"], 3)

    def test_turns_sorted_by_turn_index(self) -> None:
        """Pool turns are emitted in turn_index order regardless of trace_buffer order."""
        from runtime.artifacts import build_option_pool
        state = self._make_state()
        state["trace_buffer"].append(self._make_assistant_turn(7, [], {"option_readiness": "ready"}))
        state["trace_buffer"].append(self._make_assistant_turn(3, [], {"option_readiness": "blocked"}))
        result = build_option_pool(state, "2026-01-01T00:00:00Z")
        self.assertEqual([t["turn_index"] for t in result["turns"]], [3, 7])


class TestSafetyMonitor(unittest.TestCase):
    """Unit tests for runtime.engine.safety_monitor — Stage 5."""

    def _make_state(self, case_id: str = "TEST-CASE") -> dict:
        return {
            "meta": {"case_id": case_id, "session_id": "TEST-S01"},
            "flags": [],
            "summary_state": {"issues": []},
            "missing_info": [],
            "facts": [],
            "trace_buffer": [],
        }

    def _make_client_turn(self, turn_index: int, text: str) -> dict:
        return {"role": "client", "turn_index": turn_index, "message_text": text, "message_summary": text}

    def _make_assistant_turn(self, turn_index: int, summary: str) -> dict:
        return {"role": "assistant", "turn_index": turn_index, "message_summary": summary, "reasoning_trace": None}

    # ------------------------------------------------------------------
    # Null result paths
    # ------------------------------------------------------------------

    def test_turn_1_returns_null_result(self) -> None:
        """Safety monitor returns null/low-confidence result on turn 1 without API call."""
        from runtime.engine.safety_monitor import generate_safety_monitor_result
        state = self._make_state()
        result = generate_safety_monitor_result(
            turn_index=1,
            timestamp="2026-01-01T00:00:00Z",
            state=state,
            interaction_history=[],
        )
        self.assertEqual(result["schema_version"], "safety_monitor.v0")
        self.assertEqual(result["monitor_confidence"], "low")
        self.assertIsNone(result["veto_recommendation"])
        self.assertEqual(result["flags_raised"], [])
        self.assertEqual(result["party_state_signals"], [])
        self.assertTrue(result.get("_null_result"))

    def test_turn_2_returns_null_result(self) -> None:
        """Safety monitor returns null result on turn 2 without API call."""
        from runtime.engine.safety_monitor import generate_safety_monitor_result
        state = self._make_state()
        result = generate_safety_monitor_result(
            turn_index=2,
            timestamp="2026-01-01T00:00:00Z",
            state=state,
            interaction_history=[self._make_client_turn(1, "Hello")],
        )
        self.assertTrue(result.get("_null_result"))
        self.assertEqual(result["monitor_confidence"], "low")

    def test_null_result_shape_matches_schema(self) -> None:
        """Null result has all required schema fields."""
        from runtime.engine.safety_monitor import generate_safety_monitor_result
        required = [
            "schema_version", "case_id", "session_id", "turn_index",
            "generated_at", "source", "compliance_pattern", "deflection_pattern",
            "discordant_signals", "flags_raised", "party_state_signals",
            "veto_recommendation", "veto_reason", "monitor_confidence", "monitor_notes",
        ]
        state = self._make_state()
        result = generate_safety_monitor_result(
            turn_index=1,
            timestamp="2026-01-01T00:00:00Z",
            state=state,
            interaction_history=[],
        )
        for field in required:
            self.assertIn(field, result, f"Missing required field: {field}")

    # ------------------------------------------------------------------
    # Flag template builder
    # ------------------------------------------------------------------

    def test_build_flag_templates_empty_when_no_flags(self) -> None:
        """build_safety_monitor_flag_templates returns [] when flags_raised is empty."""
        from runtime.engine.safety_monitor import build_safety_monitor_flag_templates
        smr = {"turn_index": 5, "flags_raised": []}
        result = build_safety_monitor_flag_templates(smr, "TEST-CASE")
        self.assertEqual(result, [])

    def test_build_flag_templates_compliance_only(self) -> None:
        """compliance_only_pattern flag template has correct metadata."""
        from runtime.engine.safety_monitor import build_safety_monitor_flag_templates
        smr = {"turn_index": 5, "flags_raised": ["compliance_only_pattern"]}
        templates = build_safety_monitor_flag_templates(smr, "TEST-CASE")
        self.assertEqual(len(templates), 1)
        t = templates[0]
        self.assertEqual(t["flag_type"], "compliance_only_pattern")
        self.assertEqual(t["source"], "safety_monitor")
        self.assertEqual(t["first_detected_turn"], 5)
        self.assertIn("related_categories", t)
        self.assertIn("flag_id", t)

    def test_build_flag_templates_multiple_flags(self) -> None:
        """Multiple flags_raised produce multiple distinct templates."""
        from runtime.engine.safety_monitor import build_safety_monitor_flag_templates
        smr = {"turn_index": 7, "flags_raised": ["compliance_only_pattern", "decision_quality_risk"]}
        templates = build_safety_monitor_flag_templates(smr, "D-B-RT01")
        self.assertEqual(len(templates), 2)
        flag_types = {t["flag_type"] for t in templates}
        self.assertEqual(flag_types, {"compliance_only_pattern", "decision_quality_risk"})

    # ------------------------------------------------------------------
    # _derive_actions (tested via parse output injection)
    # ------------------------------------------------------------------

    def test_derive_actions_category1_raises_flags(self) -> None:
        """CATEGORY 1 veto recommendation populates flags_raised and party_state_signals."""
        from runtime.engine.safety_monitor import _derive_actions
        result = {
            "veto_recommendation": "CATEGORY 1",
            "veto_reason": "Party B acceptance-only across T2, T4, T6.",
            "compliance_pattern": {"detected": True, "party": "B", "pattern_type": "acceptance_only", "severity": "high", "evidence_turns": [2, 4, 6]},
            "deflection_pattern": None,
            "discordant_signals": [],
            "flags_raised": [],
            "party_state_signals": [],
        }
        _derive_actions(result)
        self.assertIn("compliance_only_pattern", result["flags_raised"])
        self.assertTrue(len(result["party_state_signals"]) > 0)
        self.assertIn("CATEGORY 1", result["party_state_signals"][0])

    def test_derive_actions_category2_raises_flags(self) -> None:
        """CATEGORY 2 veto recommendation populates flags_raised and party_state_signals."""
        from runtime.engine.safety_monitor import _derive_actions
        result = {
            "veto_recommendation": "CATEGORY 2",
            "veto_reason": "Party A deflected twice: complexity_reframe (T5), timing_deflection (T7).",
            "compliance_pattern": None,
            "deflection_pattern": {"detected": True, "deflecting_party": "A", "target_request_turn": 4, "deflection_turns": [5, 7], "deflection_tactics": ["complexity_reframe", "timing_deflection"], "pattern_confirmed": True},
            "discordant_signals": [],
            "flags_raised": [],
            "party_state_signals": [],
        }
        _derive_actions(result)
        self.assertIn("decision_quality_risk", result["flags_raised"])
        self.assertIn("CATEGORY 2", result["party_state_signals"][0])

    def test_derive_actions_category3_raises_flags(self) -> None:
        """CATEGORY 3 veto recommendation populates flags_raised and party_state_signals."""
        from runtime.engine.safety_monitor import _derive_actions
        result = {
            "veto_recommendation": "CATEGORY 3",
            "veto_reason": "Party B T6 discordant signal suppressed by Party A reframe at T7.",
            "compliance_pattern": None,
            "deflection_pattern": None,
            "discordant_signals": [{"party": "B", "signal_turn": 6, "signal_summary": "Worried about time", "was_reframed": True, "reframe_turn": 7, "reframe_party": "A", "return_to_compliance": True, "compliance_turn": 8}],
            "flags_raised": [],
            "party_state_signals": [],
        }
        _derive_actions(result)
        self.assertIn("compliance_only_pattern", result["flags_raised"])
        self.assertIn("CATEGORY 3", result["party_state_signals"][0])

    def test_derive_actions_no_veto_no_flags(self) -> None:
        """No veto and no moderate compliance signal produces no flags or signals."""
        from runtime.engine.safety_monitor import _derive_actions
        result = {
            "veto_recommendation": None,
            "veto_reason": None,
            "compliance_pattern": {"detected": False, "party": "B", "pattern_type": "reactive_with_independent", "severity": "low", "evidence_turns": []},
            "deflection_pattern": None,
            "discordant_signals": [],
            "flags_raised": [],
            "party_state_signals": [],
        }
        _derive_actions(result)
        self.assertEqual(result["flags_raised"], [])
        self.assertEqual(result["party_state_signals"], [])


class TestPerceptionAgent(unittest.TestCase):
    """
    Unit tests for runtime.engine.perception_agent (Stage 6).

    Tests cover:
    - Null result on turns 1 and 2 (no API call)
    - Null result schema shape (required fields present)
    - Full result schema shape (15 required fields when non-null)
    - _build_result produces correct structure from parsed LM output
    - _build_party normalises party perception dict correctly
    - _enforce_confidence_floor: turns 3–5 cannot be 'high'
    - extract_perception_notes: returns empty list on null result
    - extract_perception_notes: returns notes from non-null result
    - extract_party_perception: returns None on null result
    - extract_party_perception: returns party dict from non-null result
    """

    def test_null_result_on_turn_1(self):
        """Turns 1–2 return null result without API call."""
        from runtime.engine.perception_agent import generate_perception_agent_result
        from runtime.engine.perception import PerceptionContext, PartyPerception

        def _dummy_perception():
            pa = PartyPerception(
                party_id="party_a",
                emotional_state="apparently_stable",
                inferred_interests=["(insufficient signal)"],
                risk_signals=["no_active_risk_signals"],
                relational_posture="engaged_and_cooperative",
            )
            pb = PartyPerception(
                party_id="party_b",
                emotional_state="apparently_stable",
                inferred_interests=["(insufficient signal)"],
                risk_signals=["no_active_risk_signals"],
                relational_posture="engaged_and_cooperative",
            )
            return PerceptionContext(
                turn_index=1,
                party_a=pa,
                party_b=pb,
                relational_dynamic="cooperative_and_stable",
                perception_confidence="low",
            )

        for t in (1, 2):
            result = generate_perception_agent_result(
                turn_index=t,
                timestamp="2026-03-29T00:00:00Z",
                state={"meta": {}, "flags": {}, "trace_buffer": []},
                scaffold_perception=_dummy_perception(),
                interaction_history=[],
            )
            self.assertTrue(result.get("_null_result"), f"Expected null result at T{t}")
            self.assertEqual(result["schema_version"], "perception_agent.v0")
            self.assertIsNone(result["confidence"])

    def test_null_result_schema_shape(self):
        """Null result contains all required top-level fields."""
        from runtime.engine.perception_agent import _null_result

        result = _null_result(turn_index=1, timestamp="2026-03-29T00:00:00Z")
        required_fields = [
            "schema_version", "turn_index", "timestamp", "confidence", "_null_result",
            "party_a", "party_b", "relational_dynamic", "dynamic_trajectory",
            "perception_signals", "scaffold_divergence", "perception_notes", "veto_signals",
        ]
        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")
        self.assertTrue(result["_null_result"])
        self.assertIsNone(result["party_a"])
        self.assertIsNone(result["party_b"])

    def test_build_result_schema_shape(self):
        """_build_result produces correct full result structure."""
        from runtime.engine.perception_agent import _build_result

        parsed = {
            "party_a": {
                "emotional_state": "anxious but cooperative",
                "emotional_trajectory": "stable",
                "engagement_quality": "genuine",
                "communication_style": "direct",
                "inferred_interests": ["stability for the children", "financial clarity"],
                "inferred_concerns": ["loss of daily contact"],
                "unsaid_signals": ["Has not mentioned own emotional experience"],
                "relational_posture": "engaged and assertive",
            },
            "party_b": {
                "emotional_state": "quietly resigned",
                "emotional_trajectory": "de-escalating",
                "engagement_quality": "compliant_only",
                "communication_style": "indirect",
                "inferred_interests": ["lower stress"],
                "inferred_concerns": [],
                "unsaid_signals": [],
                "relational_posture": "deferential",
            },
            "relational_dynamic": "one party setting pace, other adjusting",
            "dynamic_trajectory": "stable",
            "perception_signals": ["Party B has not independently stated interests across 3 turns"],
            "scaffold_divergence": "Scaffold assessed cooperative_and_stable; LM assessed asymmetric",
            "perception_notes": [
                "Party B engagement_quality=compliant_only — create space for independent articulation before options"
            ],
            "veto_signals": ["Party B may not have independently engaged with interests"],
            "confidence": "moderate",
        }

        result = _build_result(parsed=parsed, turn_index=5, timestamp="2026-03-29T00:00:00Z")

        self.assertEqual(result["schema_version"], "perception_agent.v0")
        self.assertEqual(result["turn_index"], 5)
        self.assertFalse(result["_null_result"])
        self.assertEqual(result["confidence"], "moderate")
        self.assertIsNotNone(result["party_a"])
        self.assertIsNotNone(result["party_b"])
        self.assertEqual(result["party_a"]["engagement_quality"], "genuine")
        self.assertEqual(result["party_b"]["engagement_quality"], "compliant_only")
        self.assertEqual(result["relational_dynamic"], "one party setting pace, other adjusting")
        self.assertEqual(result["dynamic_trajectory"], "stable")
        self.assertEqual(len(result["perception_notes"]), 1)
        self.assertEqual(len(result["veto_signals"]), 1)
        self.assertEqual(result["scaffold_divergence"], "Scaffold assessed cooperative_and_stable; LM assessed asymmetric")

    def test_build_party_normalises_empty(self):
        """_build_party handles empty dict gracefully."""
        from runtime.engine.perception_agent import _build_party

        result = _build_party({})
        self.assertIsNone(result["emotional_state"])
        self.assertIsNone(result["engagement_quality"])
        self.assertEqual(result["inferred_interests"], [])
        self.assertEqual(result["unsaid_signals"], [])

    def test_build_party_normalises_full(self):
        """_build_party extracts all fields from a full dict."""
        from runtime.engine.perception_agent import _build_party

        party = {
            "emotional_state": "anxious",
            "emotional_trajectory": "escalating",
            "engagement_quality": "genuine",
            "communication_style": "direct",
            "inferred_interests": ["interest_a"],
            "inferred_concerns": ["concern_a"],
            "unsaid_signals": ["unsaid_a"],
            "relational_posture": "assertive",
        }
        result = _build_party(party)
        self.assertEqual(result["emotional_state"], "anxious")
        self.assertEqual(result["emotional_trajectory"], "escalating")
        self.assertEqual(result["inferred_interests"], ["interest_a"])
        self.assertEqual(result["unsaid_signals"], ["unsaid_a"])

    def test_confidence_floor_high_on_turn_3_becomes_moderate(self):
        """Turns 3–5 cannot have confidence='high'."""
        from runtime.engine.perception_agent import _enforce_confidence_floor

        for t in (3, 4, 5):
            result = {"confidence": "high"}
            _enforce_confidence_floor(result, t)
            self.assertEqual(result["confidence"], "moderate", f"Expected moderate at T{t}")

    def test_confidence_floor_high_on_turn_6_unchanged(self):
        """Turn 6+ may have confidence='high'."""
        from runtime.engine.perception_agent import _enforce_confidence_floor

        result = {"confidence": "high"}
        _enforce_confidence_floor(result, 6)
        self.assertEqual(result["confidence"], "high")

    def test_extract_perception_notes_null_result(self):
        """extract_perception_notes returns [] for null result."""
        from runtime.engine.perception_agent import extract_perception_notes

        self.assertEqual(extract_perception_notes(None), [])
        self.assertEqual(extract_perception_notes({"_null_result": True, "perception_notes": ["x"]}), [])

    def test_extract_perception_notes_non_null(self):
        """extract_perception_notes returns notes from non-null result."""
        from runtime.engine.perception_agent import extract_perception_notes

        result = {"_null_result": False, "perception_notes": ["note_a", "note_b"]}
        self.assertEqual(extract_perception_notes(result), ["note_a", "note_b"])

    def test_extract_party_perception_null_result(self):
        """extract_party_perception returns None for null result."""
        from runtime.engine.perception_agent import extract_party_perception

        self.assertIsNone(extract_party_perception(None, "party_a"))
        self.assertIsNone(extract_party_perception({"_null_result": True}, "party_a"))

    def test_extract_party_perception_non_null(self):
        """extract_party_perception returns party dict from non-null result."""
        from runtime.engine.perception_agent import extract_party_perception

        party_data = {"emotional_state": "stable", "engagement_quality": "genuine"}
        result = {"_null_result": False, "party_b": party_data}
        self.assertEqual(extract_party_perception(result, "party_b"), party_data)
        self.assertIsNone(extract_party_perception(result, "party_a"))


if __name__ == "__main__":
    unittest.main()
