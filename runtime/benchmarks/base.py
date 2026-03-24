from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from runtime.contracts import CandidateTurn


@dataclass(frozen=True)
class RuntimeTurnPlanEntry:
    turn_index: int
    role: str
    timestamp: str


class BenchmarkSimulation(Protocol):
    case_id: str

    def default_session_id(self) -> str:
        ...

    def reference_session_dir(self, case_dir):
        ...

    def build_turns(self, source: str, case_bundle: dict, timestamp_prefix: str) -> list[CandidateTurn]:
        ...

    def get_process_variant(self, source: str, timestamp_prefix: str) -> str | None:
        ...

    def plugin_policy_descriptor(self, case_bundle: dict) -> dict | None:
        ...

    def artifact_narrative_policy(self, case_bundle: dict) -> dict | None:
        ...

    def support_artifact_policy(self, case_bundle: dict) -> dict | None:
        ...

    def benchmark_descriptor(self, case_bundle: dict) -> dict | None:
        ...

    def build_runtime_turn_plan(self, case_bundle: dict, timestamp_prefix: str) -> list[RuntimeTurnPlanEntry]:
        ...

    def generate_runtime_assistant_turn(
        self,
        turn_index: int,
        timestamp: str,
        state: dict,
        plugin_assessment: dict | None = None,
    ) -> dict:
        ...

    def generate_runtime_client_turn(
        self,
        turn_index: int,
        timestamp: str,
        state: dict,
        case_bundle: dict,
    ) -> dict:
        ...

    def finalize_next_step(self, state: dict) -> str | None:
        ...


@dataclass(frozen=True)
class BenchmarkRegistryEntry:
    case_id: str
    simulation: BenchmarkSimulation
