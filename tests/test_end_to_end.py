from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from runtime.benchmarks import get_benchmark_simulation
from runtime.benchmarks.d_b04 import (
    build_mock_model_raw_turns,
    build_mock_model_turns,
    build_reference_raw_turns,
    build_reference_turns,
    build_varied_mock_model_raw_turns,
    build_varied_mock_model_turns,
    generate_runtime_client_turn,
    get_varied_mock_process_variant,
)
from runtime.contracts import CandidateTurn, validate_candidate_turn
from runtime.loaders import load_case_bundle
from runtime.normalization import normalize_core_output


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = REPO_ROOT / "annexes" / "benchmark_cases" / "D-B04"


class EndToEndScaffoldTest(unittest.TestCase):
    def test_benchmark_registry_returns_d_b04_simulation(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        simulation = get_benchmark_simulation(case_bundle)

        self.assertEqual(simulation.case_id, "D-B04")

    def test_initialize_session_state_records_source(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="mock_model")

        self.assertEqual(state["meta"]["source"], "mock_model")

    def test_normalize_core_output_builds_candidate_turn(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        raw_turn = build_reference_raw_turns(case_bundle, "2026-03-19")[0]

        normalized = normalize_core_output(raw_turn)

        self.assertIsInstance(normalized, CandidateTurn)
        self.assertEqual(normalized.turn_index, 1)
        self.assertEqual(normalized.role, "assistant")

    def test_runtime_client_turn_uses_case_and_persona_context(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        from runtime.state import initialize_session_state

        state = initialize_session_state(case_bundle, "D-B04-S01-generated", "sim_minimal", source="runtime")
        raw_turn = generate_runtime_client_turn(2, "2026-03-19T00:01:30Z", state, case_bundle)

        self.assertEqual(raw_turn["role"], "client")
        self.assertIn("Parent A", raw_turn["message_summary"])
        self.assertIn("child", raw_turn["message_summary"].lower())
        self.assertIn("positions_added_or_updated", raw_turn["state_delta"])

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

    def test_mock_model_raw_turns_normalize_successfully(self) -> None:
        case_bundle = load_case_bundle(CASE_DIR)
        raw_turns = build_mock_model_raw_turns(case_bundle, "2026-03-19")
        normalized_turns = build_mock_model_turns(case_bundle, "2026-03-19")

        self.assertEqual(len(raw_turns), 8)
        self.assertEqual(len(normalized_turns), 8)
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
        turns = build_reference_turns(case_bundle, "2026-03-19")

        self.assertEqual(len(turns), 8)
        for turn in turns:
            self.assertIsInstance(turn, CandidateTurn)
            validate_candidate_turn(turn)

    def test_d_b04_runner_writes_required_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "D-B04-S01-generated"
            command = [
                sys.executable,
                "-m",
                "runtime.cli.run_benchmark",
                "--case-dir",
                str(CASE_DIR),
                "--output-dir",
                str(output_dir),
                "--generated-at",
                "2026-03-19T12:00:00Z",
            ]
            subprocess.run(command, cwd=REPO_ROOT, check=True)

            required_files = [
                "run_meta.json",
                "interaction_trace.json",
                "positions.json",
                "facts_snapshot.json",
                "flags.json",
                "missing_info.json",
                "summary.txt",
            ]
            for file_name in required_files:
                self.assertTrue((output_dir / file_name).exists(), f"Missing {file_name}")

            run_meta = json.loads((output_dir / "run_meta.json").read_text(encoding="utf-8"))
            flags = json.loads((output_dir / "flags.json").read_text(encoding="utf-8"))
            trace = json.loads((output_dir / "interaction_trace.json").read_text(encoding="utf-8"))
            summary = (output_dir / "summary.txt").read_text(encoding="utf-8")

            self.assertEqual(run_meta["case_id"], "D-B04")
            self.assertEqual(run_meta["policy_profile"], "sim_minimal")
            self.assertEqual(run_meta["case_context"]["source"], "runtime")
            self.assertEqual(len(flags["active_flags"]), 3)
            self.assertEqual(len(trace["turns"]), 8)
            self.assertIn("Run Source: runtime", summary)
            self.assertIn("Process Variant:", summary)
            self.assertIn("Current Escalation Posture", summary)
            self.assertIn("Unresolved:", summary)
            self.assertIn("Missing Information", summary)
            self.assertIn("Plugin confidence remains limited", summary)
            self.assertTrue(
                any(flag["flag_type"] == "plugin_low_confidence" for flag in flags["active_flags"]),
                "Expected plugin_low_confidence to remain visible as an anti-overreach guardrail.",
            )

    def test_runtime_runner_records_runtime_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "D-B04-S01-runtime"
            command = [
                sys.executable,
                "-m",
                "runtime.cli.run_benchmark",
                "--case-dir",
                str(CASE_DIR),
                "--output-dir",
                str(output_dir),
                "--source",
                "runtime",
                "--generated-at",
                "2026-03-19T12:00:00Z",
            ]
            subprocess.run(command, cwd=REPO_ROOT, check=True)

            run_meta = json.loads((output_dir / "run_meta.json").read_text(encoding="utf-8"))
            self.assertEqual(run_meta["case_context"]["source"], "runtime")
            self.assertIn(run_meta["case_context"]["process_variant"], {"interest_first", "logistics_first"})

    def test_mock_model_runner_writes_required_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "D-B04-S01-mock"
            command = [
                sys.executable,
                "-m",
                "runtime.cli.run_benchmark",
                "--case-dir",
                str(CASE_DIR),
                "--output-dir",
                str(output_dir),
                "--source",
                "mock_model",
                "--generated-at",
                "2026-03-19T12:00:00Z",
            ]
            subprocess.run(command, cwd=REPO_ROOT, check=True)

            run_meta = json.loads((output_dir / "run_meta.json").read_text(encoding="utf-8"))
            trace = json.loads((output_dir / "interaction_trace.json").read_text(encoding="utf-8"))

            self.assertEqual(run_meta["case_context"]["source"], "mock_model")
            self.assertEqual(trace["turns"][0]["role"], "assistant")
            self.assertEqual(trace["turns"][-1]["candidate_escalation_mode"], "M1")

    def test_varied_mock_model_runner_writes_required_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "D-B04-S01-varied"
            command = [
                sys.executable,
                "-m",
                "runtime.cli.run_benchmark",
                "--case-dir",
                str(CASE_DIR),
                "--output-dir",
                str(output_dir),
                "--source",
                "varied_mock_model",
                "--generated-at",
                "2026-03-19T12:00:00Z",
            ]
            subprocess.run(command, cwd=REPO_ROOT, check=True)

            run_meta = json.loads((output_dir / "run_meta.json").read_text(encoding="utf-8"))
            summary = (output_dir / "summary.txt").read_text(encoding="utf-8")
            trace = json.loads((output_dir / "interaction_trace.json").read_text(encoding="utf-8"))

            self.assertEqual(run_meta["case_context"]["source"], "varied_mock_model")
            self.assertIn("Run Source: varied_mock_model", summary)
            self.assertIn(f"Process Variant: {run_meta['case_context']['process_variant']}", summary)
            self.assertIn(run_meta["case_context"]["process_variant"], {"interest_first", "logistics_first"})
            self.assertEqual(trace["turns"][-1]["candidate_escalation_mode"], "M1")


if __name__ == "__main__":
    unittest.main()
