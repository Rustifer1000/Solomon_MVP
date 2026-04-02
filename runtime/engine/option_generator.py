"""
runtime.engine.option_generator
=================================
Stage 4 option brainstorming call.

Produces the ``brainstormer_candidates`` section of ``option_pool.json``
(CONTRACT-017) before the domain reasoner's qualification pass runs.

Design
------
* Runs BEFORE the domain reasoner so the brainstormed pool can be
  passed in as input (Option B: additive pool — domain reasoner adds its
  own expert candidates then qualifies the combined list).
* Does NOT receive ``domain_analysis`` as input.  Passing feasibility
  context to the brainstormer re-introduces constraint-checking and
  defeats the purpose of the generation/qualification separation.
* Receives party_state (accumulated interests) and session state only.
* Explicitly instructed to suspend domain feasibility checking.
* Returns a list of ``generatedCandidate`` dicts per CONTRACT-017 §3.
  The ``source`` field is set to ``"option_generator"`` on all returned
  candidates.
* Failures degrade gracefully — empty list returned so the domain
  reasoner falls back to its Stage 3 path (self-generated candidates
  only) without crashing the session.

Guard
-----
The caller (``lm_engine.py``) is responsible for checking whether option
work is appropriate before calling this function.  If the most recent
domain_analysis shows ``option_readiness == "blocked"``, the caller
should skip this call entirely and pass ``option_pool=[]`` to the domain
reasoner.  This function does not enforce that guard — it will generate
candidates regardless, which is correct brainstormer behaviour.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .api_utils import cached_create, make_client, get_model


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_OPTION_GENERATOR_SYSTEM_PROMPT = """You are a creative option generator supporting an AI-assisted mediation system called Solomon. Your role is to brainstorm a wide set of possible options that could help the parties in this mediation session move toward resolution.

YOU ARE NOT THE DOMAIN QUALIFIER. You do not assess whether options are legally or financially feasible. You do not assess whether parties are ready to consider options. You do not filter options because information is incomplete. Those are the domain reasoner's jobs, which run after you.

YOUR ONLY JOB: generate creative, party-interest-aligned option candidates from the session context. Cast widely. Include both obvious structural options and non-obvious creative ones.

SUSPEND CONSTRAINT-CHECKING

Do not reject options because:
- You don't know if they're legally viable
- Information gaps exist
- One party hasn't expressed explicit support
- The option seems ambitious or premature

If a thought occurs to you — "this might work if the logistics could be sorted" or "this addresses Party A's concern but Party B might resist" — include it anyway. The domain reasoner will filter. Your job is to generate, not to pre-filter.

DRAW ON PARTY INTERESTS

The most valuable candidates come from:
1. Options that directly address a stated interest of one party without harming the other's
2. Options that reframe the issue so both parties can say yes to a different question
3. Options that package multiple concerns together (process + substance, timing + control)
4. Options that introduce a phased or conditional structure when parties disagree on timing or trust
5. Options that give one party procedural control and the other substantive protection (or vice versa)

Non-obvious options are more valuable than obvious ones. An experienced mediator in this domain would not only think of "split the difference" — they would think of restructuring, sequencing, contingency triggers, review mechanisms, information-sharing protocols, and role-clarification devices.

WHAT TO INCLUDE IN EACH CANDIDATE

For each candidate:
- A short label (5-10 words)
- A rationale: what problem does this option solve, and why does it fit these parties' interests?
- Party interest alignment: how does this specifically address Party A's stated or inferred interests, and how does it address Party B's?
- Related issues: which active issue clusters does this option address?

AIM FOR BREADTH

Generate between 5 and 10 candidates. Fewer than 5 is too narrow. More than 10 starts to be noise. Prioritise candidates that cover different option families — do not generate 8 variations of the same basic idea.

OUTPUT FORMAT

Return a JSON object with this structure:
{
  "brainstormer_candidates": [
    {
      "candidate_id": "opt-gen-001",
      "label": "short option label",
      "rationale": "what problem this solves and why it fits the situation",
      "party_interest_alignment": {
        "party_a": "how this addresses Party A's interests",
        "party_b": "how this addresses Party B's interests"
      },
      "related_issues": ["issue_id_1", "issue_id_2"]
    }
  ]
}

Use sequential candidate_ids: opt-gen-001, opt-gen-002, etc.
Do not include a "source" field — it will be added automatically.
Return only the JSON object. No preamble, no explanation after the JSON."""


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def _build_brainstorm_context(
    state: dict,
    party_state: dict | None,
    plugin_assessment: dict,
    session_history: list[dict],
    turn_index: int,
    perception_agent_result: dict | None = None,
) -> str:
    """Build the user message for the option generator call."""
    parts: list[str] = []

    meta = state.get("meta", {})
    parts.append("=== SESSION CONTEXT ===")
    parts.append(f"Case: {meta.get('case_id', 'unknown')}")
    parts.append(f"Turn: {turn_index}")
    parts.append(f"Phase: {state.get('phase', 'unknown')}")
    parts.append(f"Domain: {plugin_assessment.get('domain', 'divorce')}")
    families = plugin_assessment.get("issue_families", [])
    if isinstance(families, dict):
        families = [k for k, v in families.items() if v]
    if families:
        parts.append(f"Active issue families: {', '.join(families)}")
    parts.append("")

    # Session history — the narrative context for brainstorming
    if session_history:
        parts.append("=== RECENT SESSION HISTORY ===")
        for turn in session_history[-8:]:
            role = turn.get("role", "unknown").upper()
            summary = turn.get("message_summary", "")[:250]
            parts.append(f"[{role} T{turn.get('turn_index', '?')}]: {summary}")
        parts.append("")

    # Current positions — what each party has stated
    positions = state.get("positions", {})
    if positions:
        parts.append("=== CURRENT POSITIONS ===")
        for party_id, pdata in positions.items():
            proposals = pdata.get("proposals", [])
            for p in proposals[:3]:
                if isinstance(p, dict):
                    stmt = p.get("statement") or p.get("summary", "")
                    if stmt:
                        parts.append(f"{party_id}: {stmt[:150]}")
        parts.append("")

    # Open information gaps — for context only, NOT for filtering
    missing = [m for m in state.get("missing_info", [])
               if isinstance(m, dict) and m.get("status") not in ("resolved", "withdrawn")]
    if missing:
        parts.append("=== OPEN INFORMATION GAPS (context only — do NOT use to exclude options) ===")
        for item in missing[:5]:
            topic = item.get("topic") or item.get("item") or item.get("question", "")
            if topic:
                parts.append(f"  - {topic}")
        parts.append("")

    # Party state — the most important brainstorming input
    if party_state is not None:
        parts.append("=== PARTY STATE (use this to align options with interests) ===")
        for pid in ("party_a", "party_b"):
            pb = party_state.get(pid, {})
            if not pb:
                continue
            parts.append(f"{pid.upper()}:")
            parts.append(f"  Emotional state: {pb.get('current_emotional_state', 'unknown')}")

            acc = pb.get("accumulated_interests", [])
            interests = [i.get("interest", "") for i in acc
                         if i.get("interest") and not i.get("interest", "").startswith("unknown")]
            if interests:
                parts.append(f"  Accumulated interests: {'; '.join(interests[:8])}")
            else:
                parts.append("  Accumulated interests: not yet observed")

            arc = pb.get("relational_posture_progression", [])
            if arc:
                last = arc[-1]
                parts.append(f"  Current posture: T{last.get('turn_index', '?')} — {last.get('posture', '?')}")
        parts.append("")

        cross = party_state.get("cross_party", {})
        dyn = cross.get("current_relational_dynamic", "")
        if dyn:
            parts.append(f"Relational dynamic: {dyn}")
            parts.append("")

    elif state.get("trace_buffer"):
        # Fallback: extract interest signals from the trace buffer if party_state unavailable
        parts.append("=== PARTY SIGNALS FROM SESSION (party_state not yet available) ===")
        for turn in state.get("trace_buffer", [])[-6:]:
            if turn.get("role") == "client":
                summary = turn.get("message_summary", "")[:150]
                if summary:
                    parts.append(f"  T{turn.get('turn_index', '?')}: {summary}")
        parts.append("")

    # Accepted facts — structural context
    facts = state.get("facts", [])
    if facts:
        parts.append("=== ACCEPTED FACTS ===")
        for fact in facts[:6]:
            if isinstance(fact, dict):
                stmt = fact.get("statement", "")
            else:
                stmt = str(fact)
            if stmt:
                parts.append(f"  - {stmt[:120]}")
        parts.append("")

    # Stage 6: perception agent signals — richer interests and concerns than
    # the deterministic party_state can provide.  Injected as additive context
    # so the brainstormer has the deepest available interest/concern picture.
    if (
        perception_agent_result
        and not perception_agent_result.get("_null_result")
    ):
        pa_perception = perception_agent_result.get("party_a") or {}
        pb_perception = perception_agent_result.get("party_b") or {}
        has_signals = (
            pa_perception.get("inferred_interests")
            or pa_perception.get("inferred_concerns")
            or pb_perception.get("inferred_interests")
            or pb_perception.get("inferred_concerns")
            or perception_agent_result.get("relational_dynamic")
        )
        if has_signals:
            parts.append("=== PERCEPTION AGENT SIGNALS (Stage 6) ===")
            parts.append(
                "The dedicated perception agent has produced deeper interest and concern "
                "signals than the structural party state above. Use these to generate more "
                "precisely interest-aligned options."
            )
            if pa_perception.get("inferred_interests"):
                parts.append(f"Party A deeper interests: {'; '.join(pa_perception['inferred_interests'][:5])}")
            if pa_perception.get("inferred_concerns"):
                parts.append(f"Party A underlying concerns: {'; '.join(pa_perception['inferred_concerns'][:4])}")
            if pb_perception.get("inferred_interests"):
                parts.append(f"Party B deeper interests: {'; '.join(pb_perception['inferred_interests'][:5])}")
            if pb_perception.get("inferred_concerns"):
                parts.append(f"Party B underlying concerns: {'; '.join(pb_perception['inferred_concerns'][:4])}")
            lm_dynamic = perception_agent_result.get("relational_dynamic")
            if lm_dynamic:
                parts.append(f"Relational dynamic (LM-assessed): {lm_dynamic}")
            unsaid_a = pa_perception.get("unsaid_signals", [])
            unsaid_b = pb_perception.get("unsaid_signals", [])
            if unsaid_a:
                parts.append(f"Party A unsaid signals: {'; '.join(unsaid_a[:3])}")
            if unsaid_b:
                parts.append(f"Party B unsaid signals: {'; '.join(unsaid_b[:3])}")
            parts.append("")

    # Task
    parts.append("=== YOUR TASK ===")
    parts.append(
        f"Brainstorm option candidates for turn {turn_index}. "
        "Draw on the party interests and session context above. "
        "Generate 5-10 candidates covering different option families. "
        "Do NOT filter for domain feasibility — generate freely. "
        "Return as a JSON object with a brainstormer_candidates list."
    )

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_option_pool(
    turn_index: int,
    timestamp: str,
    state: dict,
    party_state: dict | None,
    plugin_assessment: dict,
    session_history: list[dict],
    perception_agent_result: dict | None = None,
) -> list[dict]:
    """
    Call the option generator and return a list of brainstormer candidate dicts.

    Each returned dict matches the ``generatedCandidate`` schema in
    CONTRACT-017, with ``source`` set to ``"option_generator"``.

    On any failure (API error, parse failure), returns an empty list so
    the domain reasoner can fall back to its Stage 3 self-generation path.
    """
    try:
        client = _make_client()
        model = _get_model()

        user_content = _build_brainstorm_context(
            state=state,
            party_state=party_state,
            plugin_assessment=plugin_assessment,
            session_history=session_history,
            turn_index=turn_index,
            perception_agent_result=perception_agent_result,
        )

        response = cached_create(
            client,
            model=model,
            max_tokens=2048,
            system=_OPTION_GENERATOR_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )

        raw = response.content[0].text
        candidates = _parse_response(raw)

        # Stamp source field on every candidate (schema invariant)
        for candidate in candidates:
            candidate["source"] = "option_generator"

        return candidates

    except Exception as exc:  # noqa: BLE001
        # Degrade gracefully — empty list causes domain reasoner to use
        # its own candidates only (Stage 3 path), which is safe.
        # Log the failure so it is observable without crashing the session.
        print(
            f"[option_generator] T{turn_index} brainstormer failed "
            f"({type(exc).__name__}: {exc})",
            file=sys.stderr,
        )
        return []


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

def _extract_json_object(text: str) -> str | None:
    """Find the first complete JSON object in text using bracket counting."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape_next = False
    for i, c in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue
        if c == "\\" and in_string:
            escape_next = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _parse_response(raw: str) -> list[dict[str, Any]]:
    """
    Extract the brainstormer_candidates list from the model's response.

    Handles both raw JSON and code-fenced JSON. Returns an empty list on
    any parse failure so the caller can degrade gracefully.
    """
    parsed: dict | None = None

    try:
        parsed = json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    if parsed is None:
        candidate_text = _extract_json_object(raw)
        if candidate_text:
            try:
                parsed = json.loads(candidate_text)
            except json.JSONDecodeError:
                pass

    if parsed is None:
        return []

    candidates = parsed.get("brainstormer_candidates", [])
    if not isinstance(candidates, list):
        return []

    # Validate each candidate has the minimum required fields
    valid: list[dict] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        if not item.get("candidate_id") or not item.get("label"):
            continue
        # Ensure party_interest_alignment exists with both keys
        alignment = item.get("party_interest_alignment")
        if not isinstance(alignment, dict):
            item["party_interest_alignment"] = {"party_a": "", "party_b": ""}
        else:
            alignment.setdefault("party_a", "")
            alignment.setdefault("party_b", "")
        # Ensure related_issues is a list
        if not isinstance(item.get("related_issues"), list):
            item["related_issues"] = []
        valid.append(item)

    return valid


def _make_client():
    return make_client()


def _get_model() -> str:
    # Option generator: overridable via SOLOMON_OPTION_MODEL, then SOLOMON_DOMAIN_MODEL.
    return get_model("SOLOMON_OPTION_MODEL", "SOLOMON_DOMAIN_MODEL")
