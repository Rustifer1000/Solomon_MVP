"""
runtime.engine.prompt_builder
==============================
Builds the structured five-step prompt for Solomon's LLM turn generator.

The prompt enforces cognitive separation:

  Step 1 — PERCEPTION PASS    (must complete before anything else)
  Step 2 — DOMAIN ANALYSIS
  Step 3 — OPTION SPACE SCAN
  Step 4 — SAFETY CHECK
  Step 5 — RESPONSE SYNTHESIS

This is the core of Stage 1 (ARCH-007).  The perception pass is structurally
required — the model cannot skip to option generation without first recording
its assessment of party state.

The prompt is designed so that the model's Step 1 output is explicit and
readable in the response, making it evaluable against PQ1–PQ4 dimensions
without needing a separate party state artifact (that comes in Stage 2).
"""

from __future__ import annotations

from .perception import PerceptionContext

_PHASE_ORDER = [
    "info_gathering",
    "interest_exploration",
    "option_generation",
    "agreement_building",
]
_CANONICAL_PHASES = set(_PHASE_ORDER)


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Solomon, an AI-assisted mediation system designed to support structured divorce and separation mediation sessions.

Your role is process support — you are a neutral facilitator, not a judge, legal advisor, or therapist. You help parties surface their interests, identify shared ground, generate options, and move toward bounded agreements. You do not take sides, offer legal advice, or push parties toward any particular outcome.

You operate under a strict escalation framework. When you detect signals that exceed your safe handling threshold — safety concerns, coercion, participation incapacity, irrecoverable process breakdown — you escalate rather than continue. Escalating correctly is more important than completing the session.

COGNITIVE SEQUENCE — REQUIRED

Every response you generate must follow this five-step sequence. You must work through all five steps explicitly before producing your final response. Do not skip steps or merge them.

STEP 1 — PERCEPTION PASS (complete this before any other step)
Assess the current psychological and relational state of both parties. For each party record:
  - Emotional state: what psychological state do they appear to be in right now?
  - Underlying interests: what do you believe they actually need beneath their stated positions?
  - Risk signals: any signals of vulnerability, distress, power imbalance, or incapacity?
  - Relational posture: how are they engaging — assertive, deferential, withdrawn, escalating?
Then record the cross-party relational dynamic: what pattern is operating between them?

STEP 2 — DOMAIN ANALYSIS
Given the party states from Step 1 and the plugin assessment provided, what are the most relevant domain considerations for this turn? What feasibility constraints apply? What information gaps remain material?

STEP 3 — OPTION SPACE SCAN
Without filtering yet: what options could plausibly serve both parties' underlying interests (from Step 1)? Then apply domain qualification from Step 2 — which options survive? If information gaps from Step 2 prevent responsible option work, name that explicitly rather than generating premature options.

STEP 4 — SAFETY CHECK
Does anything in Steps 1–3 require escalation or a mode change? Check:
  - Is the current escalation mode still appropriate?
  - Are there signals in party state (Step 1) that cross a threshold?
  - Would generating options (Step 3) be safe to do at this moment?
If escalation is needed, state it explicitly and do not proceed to Step 5.

STEP 5 — RESPONSE SYNTHESIS
Given Steps 1–4, generate Solomon's actual response. The response must be consistent with what you recorded in Step 1 — do not contradict your perception of party state in how you speak to the parties.

OUTPUT FORMAT

Your response must be a JSON object with this structure:
{
  "perception": {
    "party_a": {
      "emotional_state": "...",
      "inferred_interests": ["...", "..."],
      "risk_signals": ["..."],
      "relational_posture": "..."
    },
    "party_b": {
      "emotional_state": "...",
      "inferred_interests": ["...", "..."],
      "risk_signals": ["..."],
      "relational_posture": "..."
    },
    "relational_dynamic": "...",
    "perception_notes": ["..."]
  },
  "domain_analysis": {
    "key_constraints": ["..."],
    "material_gaps": ["..."],
    "domain_notes": "..."
  },
  "option_scan": {
    "candidate_options": ["..."],
    "qualified_options": ["..."],
    "premature_option_work": false
  },
  "safety_check": {
    "escalation_needed": false,
    "candidate_mode": "M0",
    "candidate_category": "E0",
    "signals": [],
    "notes": "..."
  },
  "response": {
    "phase": "...",
    "message_summary": "...",
    "message_text": "...",
    "confidence_note": null
  }
}

The message_text field is the actual text Solomon speaks to the parties. Keep it focused, neutral, and grounded in what you observed in Step 1. Do not introduce options that did not survive Step 3. Do not contradict the safety check from Step 4."""


# ---------------------------------------------------------------------------
# Turn context builder
# ---------------------------------------------------------------------------

def build_turn_prompt(
    state: dict,
    plugin_assessment: dict,
    perception: PerceptionContext,
    turn_index: int,
    session_history: list[dict],
) -> list[dict]:
    """
    Build the messages list for the LLM call.

    Returns a list of message dicts suitable for anthropic.messages.create().

    Parameters
    ----------
    state:
        Current session state.
    plugin_assessment:
        Plugin's assessment dict for this turn.
    perception:
        PerceptionContext built by perception.build_perception_context().
    turn_index:
        The turn about to be generated.
    session_history:
        List of prior turns as dicts with 'role' and 'content' keys.
    """
    user_content = _build_user_message(
        state=state,
        plugin_assessment=plugin_assessment,
        perception=perception,
        turn_index=turn_index,
        session_history=session_history,
    )
    return [{"role": "user", "content": user_content}]


def _build_user_message(
    state: dict,
    plugin_assessment: dict,
    perception: PerceptionContext,
    turn_index: int,
    session_history: list[dict],
) -> str:
    parts: list[str] = []

    # --- Session context ---
    meta = state.get("meta", {})
    # Compute current mediation phase from trace buffer max (not state["phase"]
    # which may regress when scripted client turns set an earlier phase).
    trace_phases = [
        t.get("phase") for t in state.get("trace_buffer", [])
        if t.get("phase") in _CANONICAL_PHASES
    ]
    if trace_phases:
        current_phase = max(trace_phases, key=lambda p: _PHASE_ORDER.index(p))
    else:
        current_phase = "info_gathering"

    parts.append("=== SESSION CONTEXT ===")
    parts.append(f"Case: {meta.get('case_id', 'unknown')}")
    parts.append(f"Turn: {turn_index}")
    parts.append(f"Current mediation phase: {current_phase}")
    parts.append(f"Current escalation mode: {state.get('escalation', {}).get('mode', 'M0')}")
    parts.append(f"Current escalation category: {state.get('escalation', {}).get('category', 'E0')}")
    parts.append("")

    # --- Session history (last 6 turns max to manage context) ---
    if session_history:
        parts.append("=== RECENT SESSION HISTORY ===")
        recent = session_history[-6:]
        for turn in recent:
            role = turn.get("role", "unknown").upper()
            summary = turn.get("message_summary") or turn.get("content", "")
            parts.append(f"[{role} turn {turn.get('turn_index', '?')}]: {summary[:300]}")
        parts.append("")

    # --- Current positions ---
    positions = state.get("positions", {})
    if positions:
        parts.append("=== CURRENT POSITIONS ===")
        for party_id, party_data in positions.items():
            proposals = party_data.get("proposals", [])
            if proposals:
                parts.append(f"{party_id}:")
                for p in proposals[:3]:
                    if isinstance(p, dict):
                        stmt = p.get("statement") or p.get("summary", "")
                        conf = p.get("confidence", "")
                        parts.append(f"  - {stmt[:120]} (confidence: {conf})")
        parts.append("")

    # --- Open missing information ---
    missing = state.get("missing_info", [])
    open_missing = [m for m in missing if isinstance(m, dict)
                    and m.get("status") not in ("resolved", "withdrawn")]
    if open_missing:
        parts.append("=== OPEN INFORMATION GAPS ===")
        for item in open_missing[:5]:
            topic = item.get("topic") or item.get("item", "")
            imp = item.get("importance", "")
            parts.append(f"  - {topic} (importance: {imp})")
        parts.append("")

    # --- Plugin assessment ---
    parts.append("=== PLUGIN ASSESSMENT ===")
    parts.append(f"Plugin confidence: {plugin_assessment.get('plugin_confidence', 'unknown')}")
    parts.append(f"Option posture: {plugin_assessment.get('option_posture', 'none')}")
    active_flag_types = plugin_assessment.get("active_flag_types", [])
    if active_flag_types:
        parts.append(f"Active flag types: {', '.join(active_flag_types)}")
    issue_families = plugin_assessment.get("issue_families", [])
    if isinstance(issue_families, dict):
        issue_families = [k for k, v in issue_families.items() if v]
    if issue_families:
        parts.append(f"Active issue families: {', '.join(issue_families)}")
    parts.append("")

    # --- Pre-built perception context (Stage 1 scaffold) ---
    parts.append("=== PERCEPTION CONTEXT (pre-computed scaffold) ===")
    parts.append(
        "The following perception context was derived from session state. "
        "Use it as a starting point for your Step 1 perception pass — "
        "you may refine or expand it based on the session history above."
    )
    parts.append(f"Party A ({perception.party_a.party_id}):")
    parts.append(f"  Emotional state: {perception.party_a.emotional_state}")
    parts.append(f"  Relational posture: {perception.party_a.relational_posture}")
    parts.append(f"  Risk signals: {', '.join(perception.party_a.risk_signals)}")
    parts.append(f"Party B ({perception.party_b.party_id}):")
    parts.append(f"  Emotional state: {perception.party_b.emotional_state}")
    parts.append(f"  Relational posture: {perception.party_b.relational_posture}")
    parts.append(f"  Risk signals: {', '.join(perception.party_b.risk_signals)}")
    parts.append(f"Relational dynamic: {perception.relational_dynamic}")
    parts.append(f"Perception confidence: {perception.perception_confidence}")
    if perception.perception_notes:
        parts.append("Perception notes:")
        for note in perception.perception_notes:
            parts.append(f"  - {note}")
    parts.append("")

    # --- Instruction ---
    parts.append("=== YOUR TASK ===")
    parts.append(
        f"Generate Solomon's turn {turn_index} response. "
        "Follow the five-step cognitive sequence exactly as specified in the system prompt. "
        "Begin with Step 1 (Perception Pass) — record your assessment of both parties' "
        "psychological state before proceeding. "
        "Return your response as a JSON object matching the specified output format."
    )

    return "\n".join(parts)
