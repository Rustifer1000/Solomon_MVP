from __future__ import annotations


def _sentence(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text if text.endswith((".", "?", "!")) else f"{text}."


def _normalize_people(text: str) -> str:
    return text.replace("parent a", "Parent A").replace("parent b", "Parent B")


def _rewrite_assistant(summary: str) -> str:
    text = summary.strip()
    if text.startswith("Solomon frames the session around "):
        text = "Let's start by " + text.removeprefix("Solomon frames the session around ")
    elif text.startswith("Solomon pauses the exchange, reflects the participation imbalance directly, and attempts to restore a workable process before continuing."):
        text = "I want to pause here. I'm noticing a participation imbalance, and I want to restore a workable process before we continue."
    elif text.startswith("Solomon slows the exchange, reflects the need for both clarity and equal space to speak, and tries to re-establish a mutual process before option work begins."):
        text = "I want to slow this down. I'm hearing a need for both clarity and equal space to speak before we move into solutions."
    elif text.startswith("Solomon concludes that a human mediator should join for co-handling because "):
        text = "At this point, I think a human mediator should join us because " + text.removeprefix(
            "Solomon concludes that a human mediator should join for co-handling because "
        )
    elif text.startswith("Solomon ends autonomous mediation and routes the matter to protected human handling because "):
        text = "At this point, I do not think this should continue without direct human handling because " + text.removeprefix(
            "Solomon ends autonomous mediation and routes the matter to protected human handling because "
        )
    elif text.startswith("Solomon ends autonomous mediation and routes the matter to human handling because "):
        text = "At this point, I do not think this should continue without direct human handling because " + text.removeprefix(
            "Solomon ends autonomous mediation and routes the matter to human handling because "
        )
    text = _normalize_people(text)
    text = text.replace("option work", "we move into solutions")
    text = text.replace("continue autonomously", "continue on our own here")
    text = text.replace("autonomous handling", "continuing without a human mediator")
    return _sentence(text)


def _position_statements(turn: dict) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    for position in turn.get("state_delta", {}).get("positions_structured", []):
        participant_ids = position.get("participant_ids", [])
        if participant_ids == ["spouse_A"]:
            speaker = "Spouse A"
        elif participant_ids == ["spouse_B"]:
            speaker = "Spouse B"
        else:
            speaker = "Spouses"
        statement = position.get("statement")
        if isinstance(statement, str):
            lines.append((speaker, _sentence(_normalize_people(statement))))
    return lines


def _split_joint_client_summary(summary: str) -> list[tuple[str, str]]:
    text = _normalize_people(summary.strip())
    if "Parent B agrees" in text and ", and Parent A says " in text:
        left, right = text.split(", and Parent A says ", 1)
        left = left.removeprefix("Parent B agrees ").strip()
        right = right.strip()
        return [
            ("Spouse B", _sentence(f"I agree {left}")),
            ("Spouse A", _sentence(right)),
        ]
    if "Parent A says " in text:
        return [("Spouse A", _sentence(text.removeprefix("Parent A says ").strip()))]
    if "Parent B says " in text:
        return [("Spouse B", _sentence(text.removeprefix("Parent B says ").strip()))]
    return [("Client", _sentence(text))]


def _render_turn(turn: dict) -> str:
    if turn["role"] == "assistant":
        body_lines = [f"Solomon: {_rewrite_assistant(turn['message_summary'])}"]
    else:
        position_lines = _position_statements(turn)
        if position_lines:
            body_lines = [f"{speaker}: {line}" for speaker, line in position_lines]
        else:
            body_lines = [f"{speaker}: {line}" for speaker, line in _split_joint_client_summary(turn["message_summary"])]
    body = "\n".join(body_lines)
    return f"Turn {turn['turn_index']} [{turn.get('phase', 'unknown')}]\n{body}\n"


def _render_safety_monitor_summary(state: dict) -> str:
    """
    Build a brief safety monitor section for the review packet.
    Only included when at least one assistant turn has a safety_monitor_result.
    """
    monitor_turns = [
        t for t in state["trace_buffer"]
        if t.get("role") == "assistant"
        and (t.get("reasoning_trace") or {}).get("safety_monitor_result") is not None
    ]
    if not monitor_turns:
        return ""

    lines: list[str] = ["Safety Monitor Log", "---"]
    for turn in monitor_turns:
        smr = turn["reasoning_trace"]["safety_monitor_result"]
        tidx = turn["turn_index"]
        confidence = smr.get("monitor_confidence", "?")
        veto = smr.get("veto_recommendation")
        notes = smr.get("monitor_notes", "")[:200]

        if veto:
            veto_reason = smr.get("veto_reason", "")[:150]
            lines.append(f"T{tidx} [{confidence}] VETO {veto}: {veto_reason}")
        elif smr.get("_null_result"):
            lines.append(f"T{tidx} [low] null result (insufficient history or call failed)")
        else:
            lines.append(f"T{tidx} [{confidence}] {notes}")

    return "\n".join(lines) + "\n"


def _render_perception_agent_summary(state: dict) -> str:
    """
    Build a brief perception agent section for the review packet.
    Only included when at least one assistant turn has a perception_agent_result.
    """
    perception_turns = [
        t for t in state["trace_buffer"]
        if t.get("role") == "assistant"
        and (t.get("reasoning_trace") or {}).get("perception_agent_result") is not None
        and not (t.get("reasoning_trace") or {}).get("perception_agent_result", {}).get("_null_result")
    ]
    if not perception_turns:
        return ""

    lines: list[str] = ["Perception Agent Log", "---"]
    for turn in perception_turns:
        par = turn["reasoning_trace"]["perception_agent_result"]
        tidx = turn["turn_index"]
        confidence = par.get("confidence", "?")
        dynamic = par.get("relational_dynamic", "")
        trajectory = par.get("dynamic_trajectory", "")
        notes = par.get("perception_notes", [])

        pa = par.get("party_a") or {}
        pb = par.get("party_b") or {}
        pa_eq = pa.get("engagement_quality", "")
        pb_eq = pb.get("engagement_quality", "")

        summary_parts = []
        if dynamic:
            summary_parts.append(f"dynamic={dynamic}")
        if trajectory:
            summary_parts.append(f"trajectory={trajectory}")
        if pa_eq:
            summary_parts.append(f"A:engagement={pa_eq}")
        if pb_eq:
            summary_parts.append(f"B:engagement={pb_eq}")

        divergence = par.get("scaffold_divergence")
        if divergence:
            summary_parts.append(f"divergence={divergence[:80]}")

        line = f"T{tidx} [{confidence}] {', '.join(summary_parts)}"
        lines.append(line)
        for note in notes[:2]:
            lines.append(f"  NOTE: {note[:150]}")

    return "\n".join(lines) + "\n"


def build_rendered_reviewer_transcript(state: dict, renderer_name: str) -> str:
    turns = "\n".join(_render_turn(turn) for turn in state["trace_buffer"])
    monitor_section = _render_safety_monitor_summary(state)
    monitor_block = f"\n{monitor_section}" if monitor_section else ""
    perception_section = _render_perception_agent_summary(state)
    perception_block = f"\n{perception_section}" if perception_section else ""
    return (
        "Reviewer Transcript\n"
        "Source Note: reviewer-facing rendered transcript derived from the structured interaction trace\n"
        f"Renderer: {renderer_name}\n"
        f"Case ID: {state['meta']['case_id']}\n"
        f"Session ID: {state['meta']['session_id']}\n\n"
        f"{turns}\n"
        f"{monitor_block}"
        f"{perception_block}"
    )
