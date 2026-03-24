from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from runtime.benchmarks.base import BenchmarkRegistryEntry, RuntimeTurnPlanEntry
from runtime.contracts import CandidateTurn


@dataclass(frozen=True)
class BenchmarkSourceBuilders:
    reference: Callable[[dict, str], list[CandidateTurn]]
    mock_model: Callable[[dict, str], list[CandidateTurn]]
    varied_mock_model: Callable[[dict, str], list[CandidateTurn]] | None = None
    process_variant: Callable[[str, str], str | None] | None = None


@dataclass(frozen=True)
class BenchmarkRuntimeBuilders:
    turn_plan: Callable[[str], list[RuntimeTurnPlanEntry]]
    assistant_turn: Callable[[int, str, dict, dict | None], dict]
    client_turn: Callable[[int, str, dict, dict], dict]


@dataclass(frozen=True)
class ConfiguredBenchmarkSimulation:
    case_id: str
    default_session: str
    reference_session: str
    sources: BenchmarkSourceBuilders
    runtime: BenchmarkRuntimeBuilders
    benchmark_metadata: dict | None = None
    plugin_policy: dict | None = None
    artifact_narrative: dict | None = None
    support_artifact: dict | None = None
    next_step: str | None = None

    def default_session_id(self) -> str:
        return self.default_session

    def reference_session_dir(self, case_dir: Path) -> Path:
        return case_dir / "sessions" / self.reference_session

    def build_turns(self, source: str, case_bundle: dict, timestamp_prefix: str) -> list[CandidateTurn]:
        builders = {
            "reference": self.sources.reference,
            "mock_model": self.sources.mock_model,
        }
        if self.sources.varied_mock_model is not None:
            builders["varied_mock_model"] = self.sources.varied_mock_model
        try:
            return builders[source](case_bundle, timestamp_prefix)
        except KeyError as exc:
            raise ValueError(f"Unsupported source for {self.case_id}: {source}") from exc

    def get_process_variant(self, source: str, timestamp_prefix: str) -> str | None:
        if self.sources.process_variant is None:
            return None
        return self.sources.process_variant(source, timestamp_prefix)

    def plugin_policy_descriptor(self, case_bundle: dict) -> dict | None:
        return dict(self.plugin_policy) if self.plugin_policy is not None else None

    def artifact_narrative_policy(self, case_bundle: dict) -> dict | None:
        return dict(self.artifact_narrative) if self.artifact_narrative is not None else None

    def support_artifact_policy(self, case_bundle: dict) -> dict | None:
        return dict(self.support_artifact) if self.support_artifact is not None else None

    def benchmark_descriptor(self, case_bundle: dict) -> dict | None:
        return dict(self.benchmark_metadata) if self.benchmark_metadata is not None else None

    def build_runtime_turn_plan(self, case_bundle: dict, timestamp_prefix: str) -> list[RuntimeTurnPlanEntry]:
        return self.runtime.turn_plan(timestamp_prefix)

    def generate_runtime_assistant_turn(
        self,
        turn_index: int,
        timestamp: str,
        state: dict,
        plugin_assessment: dict | None = None,
    ) -> dict:
        return self.runtime.assistant_turn(turn_index, timestamp, state, plugin_assessment)

    def generate_runtime_client_turn(
        self,
        turn_index: int,
        timestamp: str,
        state: dict,
        case_bundle: dict,
    ) -> dict:
        return self.runtime.client_turn(turn_index, timestamp, state, case_bundle)

    def finalize_next_step(self, state: dict) -> str | None:
        return self.next_step


def build_benchmark_registry(*simulations: ConfiguredBenchmarkSimulation) -> dict[str, BenchmarkRegistryEntry]:
    return {
        simulation.case_id: BenchmarkRegistryEntry(
            case_id=simulation.case_id,
            simulation=simulation,
        )
        for simulation in simulations
    }
