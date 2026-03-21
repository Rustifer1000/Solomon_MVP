from __future__ import annotations

from runtime.benchmarks.base import BenchmarkRegistryEntry, BenchmarkSimulation
from runtime.benchmarks.d_b04 import D_B04_SIMULATION


_REGISTRY: dict[str, BenchmarkRegistryEntry] = {
    D_B04_SIMULATION.case_id: BenchmarkRegistryEntry(
        case_id=D_B04_SIMULATION.case_id,
        simulation=D_B04_SIMULATION,
    )
}


def get_benchmark_simulation(case_bundle: dict) -> BenchmarkSimulation:
    case_id = case_bundle["case_metadata"]["case_id"]
    try:
        return _REGISTRY[case_id].simulation
    except KeyError as exc:
        raise NotImplementedError(f"No benchmark simulation is registered for case {case_id}.") from exc
