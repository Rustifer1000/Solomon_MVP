from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from runtime.contracts import CandidateTurn


class BenchmarkSimulation(Protocol):
    case_id: str

    def build_turns(self, source: str, case_bundle: dict, timestamp_prefix: str) -> list[CandidateTurn]:
        ...

    def get_process_variant(self, source: str, timestamp_prefix: str) -> str | None:
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


@dataclass(frozen=True)
class BenchmarkRegistryEntry:
    case_id: str
    simulation: BenchmarkSimulation
