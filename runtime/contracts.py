from __future__ import annotations

from datetime import datetime
from dataclasses import asdict, dataclass, field

ALLOWED_ISSUE_IDS = {
    # Parenting and schedule cluster
    "parenting_schedule",
    "school_logistics",
    "communication_protocol",
    "fairness_and_parent_role",
    "child_expense_coordination",
    "meaningful_parent_role",
    "child_stability",
    # Activity and coordination cluster (D-B01)
    "activity_coordination",
    # Financial and property cluster (D-B02)
    "shared_debt_allocation",
    "housing_cost_division",
    "financial_documentation",
    # Separation structure and emotional register cluster (D-B03)
    "process_legitimacy",
    "emotional_acknowledgment",
    "separation_structure",
}


@dataclass(slots=True)
class RiskCheck:
    triggered: bool
    signals: list[str]
    severity: int
    notes: str


@dataclass(slots=True)
class FactDelta:
    statement: str
    category: str | None = None
    status: str | None = None
    related_issues: list[str] = field(default_factory=list)
    note: str | None = None


@dataclass(slots=True)
class PositionDelta:
    participant_ids: list[str]
    kind: str
    issue_id: str
    statement: str
    status: str
    confidence: str | None = None
    proposal_id: str | None = None
    position_id: str | None = None


@dataclass(slots=True)
class MissingInfoDelta:
    action: str
    missing_id: str
    question: str
    importance: str | None = None
    reason_type: str | None = None
    related_issues: list[str] = field(default_factory=list)
    note: str | None = None


@dataclass(slots=True)
class IssueUpdate:
    issue_id: str
    label: str


@dataclass(slots=True)
class PackageDelta:
    package_id: str
    family: str
    status: str
    summary: str
    elements: list[str] = field(default_factory=list)
    related_issues: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StateDelta:
    facts_added: list[str] = field(default_factory=list)
    facts_revised: list[str] = field(default_factory=list)
    facts_structured: list[FactDelta] = field(default_factory=list)
    positions_added_or_updated: list[str] = field(default_factory=list)
    positions_structured: list[PositionDelta] = field(default_factory=list)
    open_questions_added: list[str] = field(default_factory=list)
    open_questions_resolved: list[str] = field(default_factory=list)
    missing_info_structured: list[MissingInfoDelta] = field(default_factory=list)
    issue_map_updates: list[str] = field(default_factory=list)
    issue_updates_structured: list[IssueUpdate] = field(default_factory=list)
    packages_structured: list[PackageDelta] = field(default_factory=list)
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
    message_text: str | None = None
    interaction_observations_delta: list[str] = field(default_factory=list)
    reasoning_trace: dict | None = None


def _validate_timestamp(timestamp: str) -> None:
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Unsupported timestamp format: {timestamp}") from exc


def validate_candidate_turn(turn: CandidateTurn) -> None:
    if turn.turn_index < 1:
        raise ValueError("turn_index must be positive")
    _validate_timestamp(turn.timestamp)
    if turn.role not in {"assistant", "client"}:
        raise ValueError(f"Unsupported role: {turn.role}")
    if turn.phase not in {"info_gathering", "interest_exploration", "option_generation", "agreement_building"}:
        raise ValueError(f"Unsupported phase: {turn.phase}")
    if not turn.message_summary.strip():
        raise ValueError("message_summary cannot be empty")
    if turn.risk_check.severity < 1 or turn.risk_check.severity > 5:
        raise ValueError("risk_check severity must be between 1 and 5")
    if turn.risk_check.triggered and not turn.risk_check.signals:
        raise ValueError("risk_check.triggered cannot be true when no signals are present")
    if turn.risk_check.triggered and turn.risk_check.severity < 2:
        raise ValueError("triggered risk_check severity must be at least 2")
    if turn.candidate_escalation_mode is not None and turn.candidate_escalation_mode not in {"M0", "M1", "M2", "M3", "M4", "M5"}:
        raise ValueError(f"Unsupported escalation mode: {turn.candidate_escalation_mode}")
    if turn.candidate_escalation_category is not None and turn.candidate_escalation_category not in {"E0", "E1", "E2", "E3", "E4", "E5", "E6"}:
        raise ValueError(f"Unsupported escalation category: {turn.candidate_escalation_category}")
    if (turn.candidate_escalation_category is None) != (turn.candidate_escalation_mode is None):
        raise ValueError("candidate escalation category and mode must either both be set or both be omitted")
    if turn.candidate_escalation_mode == "M0" and turn.candidate_escalation_category is not None:
        raise ValueError("M0 turns should not carry a non-null escalation category")
    if turn.state_delta.open_questions_added and turn.state_delta.open_questions_resolved:
        overlap = set(turn.state_delta.open_questions_added) & set(turn.state_delta.open_questions_resolved)
        if overlap:
            raise ValueError("A turn cannot add and resolve the same open question")
    if turn.state_delta.facts_added and turn.state_delta.facts_revised:
        overlap = set(turn.state_delta.facts_added) & set(turn.state_delta.facts_revised)
        if overlap:
            raise ValueError("A turn cannot add and revise the same fact statement")
    for fact in turn.state_delta.facts_structured:
        if fact.status is not None and fact.status not in {"accepted", "uncertain", "disputed"}:
            raise ValueError(f"Unsupported fact status: {fact.status}")
    for position in turn.state_delta.positions_structured:
        if position.kind not in {"position", "proposal"}:
            raise ValueError(f"Unsupported position kind: {position.kind}")
        if not position.participant_ids:
            raise ValueError("Structured positions must identify at least one participant")
    for missing_info in turn.state_delta.missing_info_structured:
        if missing_info.action not in {"open", "resolve"}:
            raise ValueError(f"Unsupported missing info action: {missing_info.action}")
    for issue_update in turn.state_delta.issue_updates_structured:
        if issue_update.issue_id not in ALLOWED_ISSUE_IDS:
            raise ValueError(f"Unsupported issue id: {issue_update.issue_id}")
    for package in turn.state_delta.packages_structured:
        if package.status not in {"proposed", "workable", "bounded_only", "qualified"}:
            raise ValueError(f"Unsupported package status: {package.status}")
        if not package.family.strip():
            raise ValueError("Structured packages must declare a package family")
        if not package.summary.strip():
            raise ValueError("Structured packages must declare a package summary")


def serialize_candidate_turn(turn: CandidateTurn) -> dict:
    payload = asdict(turn)
    return payload
