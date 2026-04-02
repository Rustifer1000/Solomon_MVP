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

PERCEPTION-RESPONSE COUPLING RULE: After completing Step 1, identify the single most important insight from your assessment and state explicitly how it will shape your Step 5 response. Record this as your perception_coupling_note. The coupling must be:
1. Specific to this party, this turn, this signal — not a generic observation that would apply to any session. "Party B appears engaged" is not a coupling note. "Party B's shift to deferential posture after raising their concern means I will explicitly invite their reaction before proceeding rather than assuming acceptance" is.
2. Actionable — it names a concrete response move, not a general intention.
3. Visible — a reviewer reading your Step 5 response should be able to identify where the coupling note's specific move appears in the message_text. If your coupling note says "I will name the reframe before presenting options," the message_text must do that.

Common coupling patterns (examples only — use your own observation):
- Deferential posture: "I will check in with [party] before moving forward rather than assuming readiness"
- Unresolved risk signal: "I will acknowledge [Party]'s stated concern directly before any substantive content"
- Scaffold divergence (you assessed differently from the expected pattern): "I will name the pattern I'm observing before inviting reaction"
- Relational dynamic shift: "I will address the underlying [trust/control/fairness] dimension explicitly before option framing"
- Emotional escalation: "I will regulate the temperature before any substantive content"

COMPLIANCE REQUIREMENT: perception_coupling_note MUST be populated on every turn — it is not optional. An empty or null perception_coupling_note is a format compliance failure regardless of how well the other fields are completed. If no strong coupling signal is present, use the most applicable default from the examples above.

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

IMPORTANT: If premature_option_work was true in Step 3, the response must not reference, present, or discuss specific options. Limit the response to process moves — eliciting information, clarifying interests, framing next steps. No option language when option work is premature.

RESPONSE DESIGN FOR OPTION-READY TURNS: When option_readiness is "ready" and qualified options exist, the response must do three things:
1. Name the process transition explicitly — acknowledge that both parties have been heard and that the session is ready to move to option exploration. This is a substantive process marker, not filler ("Both of you have now put your core concerns on the table — I want to move us toward some structural ideas to react to").
2. Connect each option you introduce to the specific interest it addresses for a specific party. Do not present options as an abstract list. For each option: name what problem it solves and for whom ("a tiered notice system addresses [Party A]'s need for advance predictability while preserving [Party B]'s ability to object to expenses above a threshold").
3. Use tentative, exploratory framing that preserves party ownership of the process ("I want to put a few ideas on the table for you both to react to" rather than "here are the options").

RESPONSE DESIGN FOR NON-OPTION TURNS: When option work is premature or deferred, the response must advance the session with a concrete next step — a specific question, a named information gap to resolve, or an explicit invitation for the unheard party to speak. Generic acknowledgments that do not move the process forward are a quality failure.

GROUNDING RULE: Every interest you name in the response must trace back to something a party actually said or a signal you explicitly recorded in Step 1. Do not insert concerns that neither party has expressed.

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
    "perception_confidence": "low | moderate | high",
    "perception_notes": ["..."],
    "perception_coupling_note": "REQUIRED — Because I assess [specific observation], I will [specific response move in Step 5]."
  },
  "domain_analysis": {
    "key_constraints": ["..."],
    "material_gaps": ["..."],
    "domain_notes": "...",
    "option_readiness": "ready | deferred | blocked"
  },
  "option_scan": {
    "candidate_options": ["..."],
    "qualified_options": ["..."],
    "premature_option_work": false,
    "deferral_reason": null
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
    "grounded_in_perception": true,
    "options_introduced": [],
    "confidence_note": null
  }
}

The message_text field is the actual text Solomon speaks to the parties. Keep it focused, neutral, and grounded in what you observed in Step 1. Do not introduce options that did not survive Step 3. Do not contradict the safety check from Step 4.

perception_confidence: your confidence in the Step 1 assessment — "low" for early turns or limited signal, "moderate" for some evidence, "high" for multiple converging signals.
option_readiness: "ready" if constraints are understood and gaps don't block option work; "deferred" if material gaps are unresolved; "blocked" if safety signals prevent option work.
grounded_in_perception: true if the response explicitly draws on your Step 1 party state assessment; false if the response is generic and does not reflect the specific party states you identified.
options_introduced: list the labels of any options from qualified_options that you reference or present in message_text. Must be empty when premature_option_work is true."""


# ---------------------------------------------------------------------------
# Turn context builder
# ---------------------------------------------------------------------------

def build_turn_prompt(
    state: dict,
    plugin_assessment: dict,
    perception: PerceptionContext,
    turn_index: int,
    session_history: list[dict],
    party_state: dict | None = None,
    domain_analysis: dict | None = None,
    perception_agent_notes: list[str] | None = None,
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
    party_state:
        Optional accumulated party state from prior turns (CONTRACT-015).
        When provided, included as a standing prior for the Step 1 perception
        pass. Only supplied when at least one prior lm_runtime turn has
        contributed a reasoning_trace.
    domain_analysis:
        Optional pre-computed domain analysis from the Stage 3 domain
        reasoner (CONTRACT-016). When provided, replaces the plugin
        assessment section with structured option_readiness + qualified
        candidates. Falls back to plugin assessment when absent.
    """
    user_content = _build_user_message(
        state=state,
        plugin_assessment=plugin_assessment,
        perception=perception,
        turn_index=turn_index,
        session_history=session_history,
        party_state=party_state,
        domain_analysis=domain_analysis,
        perception_agent_notes=perception_agent_notes,
    )
    return [{"role": "user", "content": user_content}]


def _build_user_message(
    state: dict,
    plugin_assessment: dict,
    perception: PerceptionContext,
    turn_index: int,
    session_history: list[dict],
    party_state: dict | None = None,
    domain_analysis: dict | None = None,
    perception_agent_notes: list[str] | None = None,
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

    # --- Domain analysis (Stage 3/4 pre-computed) or plugin assessment fallback ---
    if domain_analysis is not None and not domain_analysis.get("_fallback"):
        parts.append("=== DOMAIN ANALYSIS (pre-computed by domain reasoner) ===")
        readiness = domain_analysis.get("option_readiness", "deferred")
        parts.append(f"Option readiness: {readiness}")
        parts.append(f"Readiness rationale: {domain_analysis.get('readiness_rationale', '')}")
        if domain_analysis.get("safety_veto_applied"):
            parts.append(f"SAFETY VETO APPLIED: {domain_analysis.get('safety_veto_reason', '')}")
        parts.append(f"Domain confidence: {domain_analysis.get('domain_confidence', 'unknown')}")
        dn = domain_analysis.get("domain_notes", "")
        if dn:
            parts.append(f"Domain notes: {dn[:200]}")
        constraints = domain_analysis.get("blocking_constraints", [])
        if constraints:
            parts.append("Blocking constraints:")
            for bc in constraints:
                parts.append(f"  [{bc.get('severity','?')}] {bc.get('constraint','')}: resolve via {bc.get('what_would_resolve_it','')[:80]}")
        gaps = domain_analysis.get("material_gaps", [])
        if gaps:
            parts.append("Material gaps:")
            for g in gaps[:4]:
                parts.append(f"  [{g.get('importance','?')}] {g.get('gap','')}: blocks {g.get('what_it_blocks','')[:60]}")
        parts.append("")

        # Stage 4: full option pool when qualification data is present
        opq = domain_analysis.get("option_pool_qualification")
        if opq and isinstance(opq, dict):
            _render_option_pool(parts, opq)
        else:
            # Stage 3 path: compact qualified_candidates list
            candidates = domain_analysis.get("qualified_candidates", [])
            if candidates:
                parts.append(f"Qualified candidates ({len(candidates)}):")
                for c in candidates:
                    parts.append(
                        f"  [{c.get('confidence','?')}] {c.get('label','?')}: "
                        f"{c.get('feasibility_rationale','')[:120]}"
                    )
                parts.append("")

        parts.append(
            "INSTRUCTION: Your Step 2 (Domain Analysis) should confirm, extend, or challenge this "
            "pre-computed assessment. Do not simply repeat it. Your Step 3 (Option Scan) should draw "
            "from the qualified options above and may add candidates not in the pool if important — "
            "note that additions have not been domain-qualified. "
            "When option_readiness is 'ready', qualified options exist — present them in Step 5 "
            "unless your Step 4 safety check finds a reason not to. "
            "When presenting options in Step 5: select 2–4 structurally distinct options from the "
            "qualified pool (not all of them), connect each one explicitly to the party interest it "
            "serves, and use tentative framing that invites the parties to react rather than accept. "
            "Record labels of options you include in message_text in the options_introduced field."
        )
        parts.append("")
    else:
        # Fallback to plugin assessment when domain reasoner unavailable
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

    # --- Stage 6: Perception agent notes (LM-assessed, higher priority than scaffold) ---
    # When the perception agent produced a non-null result, its perception_notes
    # replace the scaffold notes as the primary actionable prior for Step 1.
    # The scaffold section above remains as structural context; the agent notes
    # are the richer, LM-assessed items the mediator must hold before responding.
    if perception_agent_notes:
        parts.append("=== PERCEPTION AGENT NOTES (Stage 6 — act on these) ===")
        parts.append(
            "The following perception notes were produced by the dedicated perception agent, "
            "which assessed party state at depth from the full interaction history. "
            "These are the most important things to hold before generating your response."
        )
        for note in perception_agent_notes:
            parts.append(f"  - {note}")
        parts.append("")

    # --- Accumulated party state (feedback loop — CONTRACT-015) ---
    if party_state is not None:
        parts.append("=== ACCUMULATED PARTY STATE (prior turns) ===")
        parts.append(
            "The following party state model was accumulated from all prior assistant turns "
            "in this session. Use it as a standing prior when completing your Step 1 "
            "perception pass — do not discard prior assessments without explicit reason."
        )
        for pid in ("party_a", "party_b"):
            pb = party_state.get(pid, {})
            if not pb:
                continue
            parts.append(f"{pid.upper()} accumulated model:")

            # Projection guard: detect whether this party has ever been heard.
            # A party is "unheard" if all accumulated interests are 'unknown' variants
            # and the latest posture is an unknown variant. In that case, explicitly
            # signal epistemic uncertainty rather than rendering speculative inferences.
            acc_interests = pb.get("accumulated_interests", [])
            observed_interest_texts = [
                i.get("interest", "")
                for i in acc_interests
                if i.get("interest") and not i.get("interest", "").startswith("unknown")
            ]
            latest_posture = ""
            arc = pb.get("relational_posture_progression", [])
            if arc:
                latest_posture = arc[-1].get("posture", "")
            party_has_been_heard = bool(observed_interest_texts) or (
                latest_posture and not latest_posture.startswith("unknown")
            )

            if not party_has_been_heard:
                parts.append(
                    f"  NOTE: {pid.upper()} has not yet been heard in prior turns. "
                    "No observed signal. Hold as epistemically uncertain — do not infer "
                    "interests, posture, or emotional state from the baseline prior alone."
                )
            else:
                parts.append(f"  Current emotional state: {pb.get('current_emotional_state', 'unknown')}")
                parts.append(f"  Current relational posture: {latest_posture or 'unknown'}")
                if observed_interest_texts:
                    parts.append(f"  Accumulated interests ({len(observed_interest_texts)}): {'; '.join(observed_interest_texts[:6])}")
                risk_history = pb.get("risk_signal_history", [])
                active_risks = [
                    r.get("signal", "")
                    for r in risk_history
                    if r.get("signal") and r.get("signal") not in ("", "none")
                ]
                if active_risks:
                    parts.append(f"  Risk signals seen: {'; '.join(active_risks[:4])}")
                if arc:
                    last = arc[-1]
                    parts.append(f"  Posture arc (latest): T{last.get('turn_index','?')} — {last.get('posture','?')}")

        cross = party_state.get("cross_party", {})
        dyn_arc = cross.get("relational_dynamic_arc", [])
        if dyn_arc:
            last_dyn = dyn_arc[-1]
            assessment = last_dyn.get("assessment") or last_dyn.get("dynamic", "?")
            parts.append(f"Cross-party dynamic (latest): T{last_dyn.get('turn_index','?')} — {assessment}")
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


# ---------------------------------------------------------------------------
# Option pool renderer (Stage 4)
# ---------------------------------------------------------------------------

def _render_option_pool(parts: list[str], opq: dict) -> None:
    """
    Render the pre-qualified option pool into the prompt.

    Called when domain_analysis contains an option_pool_qualification block
    (Stage 4 path).  Presents the full qualified/blocked pool so the main
    model selects from it rather than generating options from scratch.
    """
    qualified = opq.get("domain_qualified", [])
    blocked = opq.get("domain_blocked", [])
    expert = opq.get("domain_expert_candidates", [])

    # Combined pool count for the header
    # (brainstormer count inferred as qualified+blocked minus expert count)
    total = len(qualified) + len(blocked)
    parts.append(f"=== OPTION POOL (pre-qualified — {total} candidates reviewed) ===")

    if qualified:
        parts.append(f"QUALIFIED ({len(qualified)}) — draw from these in Step 3:")
        for q in qualified:
            cid = q.get("candidate_id", "?")
            label = q.get("label", "?")
            source = q.get("source", "?")
            conf = q.get("confidence", "?")
            rationale = q.get("feasibility_rationale", "")[:140]
            parts.append(f"  [{cid}] {label}  (source: {source}, confidence: {conf})")
            parts.append(f"    Feasibility: {rationale}")
            prereqs = q.get("prerequisite_parameters", [])
            if prereqs:
                parts.append(f"    Prerequisite parameters: {', '.join(prereqs[:4])}")
            conditions = q.get("conditions", [])
            if conditions:
                parts.append(f"    Conditions: {', '.join(conditions[:3])}")
        parts.append("")

    if blocked:
        parts.append(f"BLOCKED ({len(blocked)}) — not viable now, but note what would unblock:")
        for b in blocked:
            label = b.get("label", "?")
            blocking = b.get("blocking_rationale", "")[:100]
            unblock = b.get("what_would_unblock", "")[:100]
            parts.append(f"  {label} — blocked: {blocking}")
            parts.append(f"    Would unblock if: {unblock}")
        parts.append("")

    if not qualified and not blocked:
        parts.append("  (No candidates in pool — option work deferred or blocked)")
        parts.append("")
