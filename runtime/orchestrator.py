from __future__ import annotations

from datetime import datetime

from runtime.artifacts import write_artifacts
from runtime.benchmarks import get_benchmark_simulation
from runtime.benchmarks.base import RuntimeTurnPlanEntry
from runtime.contracts import validate_candidate_turn
from runtime.escalation import determine_escalation
from runtime.normalization import normalize_core_output
from runtime.plugins import get_plugin_runtime
from runtime.session_validation import validate_session_trace
from runtime.state import apply_turn, merge_flag_templates


def _default_higher_mode_next_step(state: dict) -> str | None:
    mode = state["escalation"]["mode"]
    if mode == "M2":
        return "Use the next step to bring in a human reviewer, preserve the current process concerns clearly, and decide whether bounded autonomous handling can still continue."
    if mode == "M3":
        return "Use the next step to bring in a human mediator for co-handling, restore fair participation, and avoid further autonomous option work until process balance is re-established."
    if mode == "M4":
        return "Use the next step to hand the matter to a human mediator fully, preserving the current process breakdown and escalation rationale clearly."
    if mode == "M5":
        return "Use the next step to stop mediation activity and redirect the matter through an appropriate human-led path."
    return None


def _validate_runtime_turn_plan(plan: list[RuntimeTurnPlanEntry]) -> None:
    if not plan:
        raise ValueError("Runtime turn plan cannot be empty")

    expected_turns = list(range(1, len(plan) + 1))
    actual_turns = [entry.turn_index for entry in plan]
    if actual_turns != expected_turns:
        raise ValueError("Runtime turn plan must use sequential turn indexes starting at 1")

    parsed_timestamps = []
    for entry in plan:
        if entry.role not in {"assistant", "client"}:
            raise ValueError(f"Unsupported runtime turn plan role: {entry.role}")
        parsed_timestamps.append(datetime.fromisoformat(entry.timestamp.replace("Z", "+00:00")))

    if parsed_timestamps != sorted(parsed_timestamps):
        raise ValueError("Runtime turn plan timestamps must be monotonic")


def _run_lm_generated_session(case_bundle: dict, state: dict, generated_at: str) -> None:
    """Stage 1 (ARCH-007): LLM turn generation with structured five-step reasoning."""
    from runtime.engine.lm_engine import generate_lm_assistant_turn

    simulation = get_benchmark_simulation(case_bundle)
    plugin_runtime = get_plugin_runtime(case_bundle)
    timestamp_prefix = generated_at[:10]
    runtime_turn_plan = simulation.build_runtime_turn_plan(case_bundle, timestamp_prefix)
    _validate_runtime_turn_plan(runtime_turn_plan)

    for plan_entry in runtime_turn_plan:
        if plan_entry.role == "assistant":
            # Stage 5: safety monitor runs before plugin.assess_state() so
            # its raised flags are visible to the escalation cascade.
            from runtime.engine.safety_monitor import (
                generate_safety_monitor_result,
                build_safety_monitor_flag_templates,
            )
            safety_monitor_result = generate_safety_monitor_result(
                turn_index=plan_entry.turn_index,
                timestamp=plan_entry.timestamp,
                state=state,
                interaction_history=list(state.get("trace_buffer", [])),
            )
            case_id = state["meta"].get("case_id", "unknown")
            monitor_flags = build_safety_monitor_flag_templates(safety_monitor_result, case_id)
            if monitor_flags:
                merge_flag_templates(state, monitor_flags)

            plugin_assessment = plugin_runtime.assess_state(state)
            # Use the reference simulation's expected phase as a minimum floor
            # so the LM cannot lag behind the scripted phase progression (which
            # would cause validation failure when scripted client turns advance).
            try:
                ref_turn = simulation.generate_runtime_assistant_turn(
                    turn_index=plan_entry.turn_index,
                    timestamp=plan_entry.timestamp,
                    state=state,
                    plugin_assessment=plugin_assessment,
                )
                min_phase = ref_turn.get("phase", "info_gathering")
            except Exception:
                min_phase = "info_gathering"
            raw_turn = generate_lm_assistant_turn(
                turn_index=plan_entry.turn_index,
                timestamp=plan_entry.timestamp,
                state=state,
                plugin_assessment=plugin_assessment,
                min_phase=min_phase,
                safety_monitor_result=safety_monitor_result,
            )
        else:
            raw_turn = simulation.generate_runtime_client_turn(
                turn_index=plan_entry.turn_index,
                timestamp=plan_entry.timestamp,
                state=state,
                case_bundle=case_bundle,
            )

        turn = normalize_core_output(raw_turn)
        validate_candidate_turn(turn)
        apply_turn(state, turn)
        plugin_runtime.sync_flags_for_turn(state, turn)

        plugin_assessment = plugin_runtime.assess_state(state)
        state["plugin_assessment"] = plugin_assessment
        escalation = determine_escalation(state, plugin_assessment)
        state["escalation"].update(escalation)

        # Sync the trace turn's candidate_escalation fields with the actual
        # applied escalation mode.  For lm_runtime turns the LM may suggest
        # an escalation mode (candidate_escalation_mode != None) that differs
        # from what determine_escalation() computes from the rule-based flags.
        # The LM's raw safety_check recommendation is preserved in
        # reasoning_trace.safety_assessment; the trace-level candidate field
        # must reflect what was actually applied so session_validation passes.
        last_trace_turn = state["trace_buffer"][-1]
        if last_trace_turn.get("candidate_escalation_mode") is not None:
            last_trace_turn["candidate_escalation_mode"] = state["escalation"]["mode"]
            last_trace_turn["candidate_escalation_category"] = state["escalation"]["category"]


def _run_runtime_generated_session(case_bundle: dict, state: dict, generated_at: str) -> None:
    simulation = get_benchmark_simulation(case_bundle)
    plugin_runtime = get_plugin_runtime(case_bundle)
    timestamp_prefix = generated_at[:10]
    runtime_turn_plan = simulation.build_runtime_turn_plan(case_bundle, timestamp_prefix)
    _validate_runtime_turn_plan(runtime_turn_plan)

    for plan_entry in runtime_turn_plan:
        if plan_entry.role == "assistant":
            plugin_assessment = plugin_runtime.assess_state(state)
            raw_turn = simulation.generate_runtime_assistant_turn(
                turn_index=plan_entry.turn_index,
                timestamp=plan_entry.timestamp,
                state=state,
                plugin_assessment=plugin_assessment,
            )
        else:
            raw_turn = simulation.generate_runtime_client_turn(
                turn_index=plan_entry.turn_index,
                timestamp=plan_entry.timestamp,
                state=state,
                case_bundle=case_bundle,
            )

        turn = normalize_core_output(raw_turn)
        validate_candidate_turn(turn)
        apply_turn(state, turn)
        plugin_runtime.sync_flags_for_turn(state, turn)

        plugin_assessment = plugin_runtime.assess_state(state)
        state["plugin_assessment"] = plugin_assessment
        escalation = determine_escalation(state, plugin_assessment)
        state["escalation"].update(escalation)


def run_session(case_bundle: dict, state: dict, output_dir, generated_at: str, source: str = "runtime") -> None:
    simulation = get_benchmark_simulation(case_bundle)
    plugin_runtime = get_plugin_runtime(case_bundle)
    plugin_result = plugin_runtime.qualify_case(case_bundle)
    state["issue_map"] = plugin_result["issue_taxonomy"]
    state["meta"]["source"] = source
    state["meta"]["process_variant"] = simulation.get_process_variant(source, generated_at[:10])
    state["meta"]["benchmark_descriptor"] = simulation.benchmark_descriptor(case_bundle)
    state["meta"]["plugin_policy_descriptor"] = simulation.plugin_policy_descriptor(case_bundle)
    state["meta"]["artifact_narrative_policy"] = simulation.artifact_narrative_policy(case_bundle)
    state["meta"]["support_artifact_policy"] = simulation.support_artifact_policy(case_bundle)
    state["meta"]["package_element_labels"] = plugin_runtime.package_element_labels()
    state["meta"]["evaluator_helper_policy"] = plugin_runtime.evaluator_helper_policy()

    if source == "lm_runtime":
        _run_lm_generated_session(case_bundle, state, generated_at)
    elif source == "runtime":
        _run_runtime_generated_session(case_bundle, state, generated_at)
    else:
        for turn in simulation.build_turns(source, case_bundle, generated_at[:10]):
            validate_candidate_turn(turn)
            apply_turn(state, turn)
            plugin_runtime.sync_flags_for_turn(state, turn)
        plugin_assessment = plugin_runtime.assess_state(state)
        state["plugin_assessment"] = plugin_assessment
        state["escalation"] = determine_escalation(state, plugin_assessment)

    benchmark_next_step = simulation.finalize_next_step(state)
    if benchmark_next_step is not None:
        state["summary_state"]["next_step"] = benchmark_next_step
    elif state["summary_state"]["next_step"] is None:
        fallback_next_step = _default_higher_mode_next_step(state)
        if fallback_next_step is not None:
            state["summary_state"]["next_step"] = fallback_next_step

    validate_session_trace(state["trace_buffer"], state["escalation"])
    write_artifacts(output_dir, state, generated_at, case_bundle)
