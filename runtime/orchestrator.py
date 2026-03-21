from __future__ import annotations

from runtime.artifacts import write_artifacts
from runtime.benchmarks import get_benchmark_simulation
from runtime.contracts import validate_candidate_turn
from runtime.escalation import determine_escalation
from runtime.normalization import normalize_core_output
from runtime.plugins.divorce import assess_state, qualify_case
from runtime.state import apply_turn


def _run_runtime_generated_session(case_bundle: dict, state: dict, generated_at: str) -> None:
    simulation = get_benchmark_simulation(case_bundle)
    timestamp_prefix = generated_at[:10]
    assistant_timestamps = {
        1: f"{timestamp_prefix}T00:00:10Z",
        3: f"{timestamp_prefix}T00:02:25Z",
        5: f"{timestamp_prefix}T00:04:55Z",
        7: f"{timestamp_prefix}T00:07:35Z",
    }
    client_timestamps = {
        2: f"{timestamp_prefix}T00:01:30Z",
        4: f"{timestamp_prefix}T00:03:40Z",
        6: f"{timestamp_prefix}T00:06:10Z",
        8: f"{timestamp_prefix}T00:08:50Z",
    }

    for turn_index in range(1, 9):
        if turn_index in assistant_timestamps:
            plugin_assessment = assess_state(state)
            raw_turn = simulation.generate_runtime_assistant_turn(
                turn_index=turn_index,
                timestamp=assistant_timestamps[turn_index],
                state=state,
                plugin_assessment=plugin_assessment,
            )
        else:
            raw_turn = simulation.generate_runtime_client_turn(
                turn_index=turn_index,
                timestamp=client_timestamps[turn_index],
                state=state,
                case_bundle=case_bundle,
            )

        turn = normalize_core_output(raw_turn)
        validate_candidate_turn(turn)
        apply_turn(state, turn)

        plugin_assessment = assess_state(state)
        state["plugin_assessment"] = plugin_assessment
        escalation = determine_escalation(state, plugin_assessment)
        state["escalation"].update(escalation)


def run_session(case_bundle: dict, state: dict, output_dir, generated_at: str, source: str = "runtime") -> None:
    simulation = get_benchmark_simulation(case_bundle)
    plugin_result = qualify_case(case_bundle)
    state["issue_map"] = plugin_result["issue_taxonomy"]
    state["meta"]["source"] = source
    state["meta"]["process_variant"] = simulation.get_process_variant(source, generated_at[:10])

    if source == "runtime":
        _run_runtime_generated_session(case_bundle, state, generated_at)
    else:
        for turn in simulation.build_turns(source, case_bundle, generated_at[:10]):
            validate_candidate_turn(turn)
            apply_turn(state, turn)
        plugin_assessment = assess_state(state)
        state["plugin_assessment"] = plugin_assessment
        state["escalation"] = determine_escalation(state, plugin_assessment)

    write_artifacts(output_dir, state, generated_at)
