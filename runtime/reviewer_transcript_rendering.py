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


def build_rendered_reviewer_transcript(state: dict, renderer_name: str) -> str:
    turns = "\n".join(_render_turn(turn) for turn in state["trace_buffer"])
    return (
        "Reviewer Transcript\n"
        "Source Note: reviewer-facing rendered transcript derived from the structured interaction trace\n"
        f"Renderer: {renderer_name}\n"
        f"Case ID: {state['meta']['case_id']}\n"
        f"Session ID: {state['meta']['session_id']}\n\n"
        f"{turns}\n"
    )
