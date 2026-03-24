from __future__ import annotations

from runtime.benchmarks.base import BenchmarkSimulation
from runtime.benchmarks.d_b04 import D_B04_SIMULATION
from runtime.benchmarks.d_b05 import D_B05_SIMULATION
from runtime.benchmarks.d_b06 import D_B06_SIMULATION
from runtime.benchmarks.d_b07 import D_B07_SIMULATION
from runtime.benchmarks.d_b08 import D_B08_SIMULATION
from runtime.benchmarks.d_b09 import D_B09_SIMULATION
from runtime.benchmarks.d_b10 import D_B10_SIMULATION
from runtime.benchmarks.d_b11 import D_B11_SIMULATION
from runtime.benchmarks.d_b12 import D_B12_SIMULATION
from runtime.benchmarks.d_b13 import D_B13_SIMULATION
from runtime.benchmarks.d_b14 import D_B14_SIMULATION
from runtime.benchmarks.scaffold import build_benchmark_registry


_REGISTRY = build_benchmark_registry(
    D_B04_SIMULATION,
    D_B05_SIMULATION,
    D_B06_SIMULATION,
    D_B07_SIMULATION,
    D_B08_SIMULATION,
    D_B09_SIMULATION,
    D_B10_SIMULATION,
    D_B11_SIMULATION,
    D_B12_SIMULATION,
    D_B13_SIMULATION,
    D_B14_SIMULATION,
)


def get_benchmark_simulation(case_bundle: dict) -> BenchmarkSimulation:
    case_id = case_bundle["case_metadata"]["case_id"]
    try:
        return _REGISTRY[case_id].simulation
    except KeyError as exc:
        raise NotImplementedError(f"No benchmark simulation is registered for case {case_id}.") from exc
