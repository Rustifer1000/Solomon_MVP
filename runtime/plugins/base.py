from __future__ import annotations

from typing import Protocol

from runtime.contracts import CandidateTurn


class PluginRuntime(Protocol):
    plugin_type: str

    def qualify_case(self, case_bundle: dict) -> dict:
        ...

    def assess_state(self, state: dict) -> dict:
        ...

    def sync_flags_for_turn(self, state: dict, turn: CandidateTurn) -> None:
        ...

    def package_element_labels(self) -> dict[str, str]:
        ...

    def evaluator_helper_policy(self) -> dict | None:
        ...
