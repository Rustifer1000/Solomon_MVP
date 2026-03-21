from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class RiskCheck:
    triggered: bool
    signals: list[str]
    severity: int
    notes: str


@dataclass(slots=True)
class StateDelta:
    facts_added: list[str] = field(default_factory=list)
    facts_revised: list[str] = field(default_factory=list)
    positions_added_or_updated: list[str] = field(default_factory=list)
    open_questions_added: list[str] = field(default_factory=list)
    open_questions_resolved: list[str] = field(default_factory=list)
    issue_map_updates: list[str] = field(default_factory=list)
    option_state_updates: list[str] = field(default_factory=list)
    escalation_state_updates: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CandidateTurn:
    turn_index: int
    timestamp: str
    role: str
    phase: str
    message_summary: str
    state_delta: StateDelta
    risk_check: RiskCheck
    candidate_escalation_category: str | None = None
    candidate_escalation_mode: str | None = None
    confidence_note: str | None = None


def validate_candidate_turn(turn: CandidateTurn) -> None:
    if turn.turn_index < 1:
        raise ValueError("turn_index must be positive")
    if turn.role not in {"assistant", "client"}:
        raise ValueError(f"Unsupported role: {turn.role}")
    if turn.phase not in {"info_gathering", "interest_exploration", "option_generation", "agreement_building"}:
        raise ValueError(f"Unsupported phase: {turn.phase}")
    if not turn.message_summary.strip():
        raise ValueError("message_summary cannot be empty")
    if turn.risk_check.severity < 1 or turn.risk_check.severity > 5:
        raise ValueError("risk_check severity must be between 1 and 5")
    if turn.candidate_escalation_mode is not None and turn.candidate_escalation_mode not in {"M0", "M1", "M2", "M3", "M4", "M5"}:
        raise ValueError(f"Unsupported escalation mode: {turn.candidate_escalation_mode}")


def serialize_candidate_turn(turn: CandidateTurn) -> dict:
    payload = asdict(turn)
    return payload
