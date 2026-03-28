# CONTRACT-017: Option Pool Artifact — v0

**Stage:** 4
**Status:** Active
**Date:** 2026-03-28
**Supersedes:** None (new artifact)
**Related:** CONTRACT-016 (domain analysis), CONTRACT-014 (reasoning trace), CONTRACT-015 (party state), TASKLIST-040

---

## 1. Purpose

This contract defines the `option_pool.json` artifact produced by Stage 4's decoupled option generation pipeline. It specifies:

- The three-layer option pool structure (brainstormer → domain qualification → response selection)
- The field schema and field semantics
- The relationship between the option generator (new) and the domain reasoner (updated)
- Which policy profiles emit the artifact
- How the artifact integrates with the existing domain analysis and five-step prompt

---

## 2. Motivation

**Stage 3 finding:** The domain reasoner correctly qualifies options when it knows which options to evaluate. But the domain reasoner's candidate generation is constrained by domain expertise — it foregrounds well-known structural options (tiered notice, phased trial) and may not generate creative options that aren't standard domain patterns.

**Stage 4 hypothesis:** Separating generation from qualification produces a wider, more creative candidate set while maintaining domain qualification discipline. A brainstorming pass that explicitly suspends constraint-checking generates options the domain reasoner would not produce on its own. The domain reasoner then qualifies this wider pool.

**Option B (confirmed):** The domain reasoner also adds its own domain-expert candidates before qualification. The brainstormer's pool and the domain reasoner's expert additions are combined before the qualification pass. This ensures standard domain options are never lost while creative options are added.

---

## 3. Artifact Schema

```
option_pool.v0 {
  schema_version: "option_pool.v0"
  case_id: string
  session_id: string
  turn_index: int
  generated_at: ISO 8601 timestamp
  option_readiness: "ready" | "deferred" | "blocked"   // inherited from domain_analysis
  safety_veto_applied: bool
  safety_veto_reason: string | null

  brainstormer_candidates: [
    {
      candidate_id: string           // e.g. "opt-gen-001"
      label: string                  // short name
      rationale: string              // why this option addresses the parties' interests
      party_interest_alignment: {
        party_a: string              // how this addresses party A's interests
        party_b: string              // how this addresses party B's interests
      }
      related_issues: [string]       // issue_ids from session state
      source: "option_generator"
    }
  ]

  domain_expert_candidates: [
    {
      candidate_id: string           // e.g. "opt-dom-001"
      label: string
      rationale: string
      party_interest_alignment: {
        party_a: string
        party_b: string
      }
      related_issues: [string]
      source: "domain_reasoner"
    }
  ]

  combined_pool_count: int           // len(brainstormer_candidates) + len(domain_expert_candidates)

  domain_qualified: [
    {
      candidate_id: string           // reference to candidate in brainstormer or domain_expert lists
      label: string                  // repeated for evaluator readability
      source: "option_generator" | "domain_reasoner"
      feasibility_rationale: string  // why viable given current session state
      confidence: "low" | "moderate" | "high"
      prerequisite_parameters: [string]   // parameters not yet known; options can still be presented
      conditions: [string]           // conditions that must hold for viability
    }
  ]

  domain_blocked: [
    {
      candidate_id: string
      label: string
      source: "option_generator" | "domain_reasoner"
      blocking_rationale: string     // why not viable
      what_would_unblock: string     // what information or session development is needed
    }
  ]

  presented_to_parties: [string]     // candidate_ids included in the main model's response
                                     // filled post-hoc after main model response is parsed
                                     // null if not yet determined (written before main model call)
}
```

---

## 4. Field Semantics

### `brainstormer_candidates`

The raw output of `option_generator.py`. Generated without domain feasibility filtering — the brainstormer is explicitly instructed to suspend constraint-checking. Candidates here are not yet qualified and may be infeasible. They are inputs to the qualification pass.

### `domain_expert_candidates`

Candidates added by the domain reasoner during qualification. These are domain-practitioner options that the brainstormer may not produce (well-known structural options in the domain). In Option B, the domain reasoner adds these before qualifying the combined pool.

These are NOT a separate qualification pass — they are added to the combined pool and qualified on the same basis as brainstormer candidates.

### `combined_pool_count`

The total candidate count before qualification (len(brainstormer_candidates) + len(domain_expert_candidates)). Stored as a summary field for evaluator readability — evaluators can quickly check whether the brainstormer is expanding the pool beyond what the domain reasoner produces alone.

**The Stage 4 hypothesis is falsified if `combined_pool_count <= domain_expert_candidates` count at T5 on complex cases.** If the brainstormer adds nothing the domain reasoner doesn't produce, Stage 4 provides no benefit.

### `domain_qualified`

Candidates that passed the domain reasoner's qualification pass. Each entry references a candidate from either the brainstormer or domain_expert lists (by `candidate_id`). The `label` is repeated for evaluator readability without cross-referencing.

`prerequisite_parameters` captures unknowns that refine but do not block presentation (e.g. "specific transport routing not yet established"). These are parameters the parties will calibrate when engaging with the option. They are distinct from `blocking_rationale` (which blocks presentation entirely).

### `domain_blocked`

Candidates reviewed and found not viable given current session state. The `what_would_unblock` field is used by the main model's Step 3 to understand what to elicit — it is the forward signal from a blocked candidate.

### `presented_to_parties`

A list of `candidate_id` values corresponding to candidates the main model included in its response. This field is filled post-hoc after parsing the main model's response. It enables the evaluation question: "what fraction of qualified options did the main model present, and which unqualified options (if any) did it present anyway?"

**This field is null in option_pool.json as written before the main model call.** A second write updates it after the response is parsed. Evaluators should check this field — a model that consistently presents only 1 of 4 qualified options suggests a response brevity issue separate from qualification quality.

### `safety_veto_applied`

Inherited from `domain_analysis`. If the safety veto fires, `option_readiness = "blocked"`, `domain_qualified` is empty, and `presented_to_parties` must be empty. The option generator call is skipped entirely when `option_readiness` is pre-determined to be `blocked` based on the most recent party state.

---

## 5. Derivation Logic

### Stage 4 call sequence in `lm_engine.py`

```
1. Check domain_analysis.option_readiness from prior context
   → If "blocked" by safety veto: skip option_generator call; write empty option_pool

2. Call option_generator.generate_option_pool(state, party_state, plugin_assessment)
   → Returns: brainstormer_candidates list

3. Call domain_reasoner.generate_domain_analysis(
       state, party_state, plugin_assessment,
       option_pool=brainstormer_candidates   ← new parameter
   )
   → Domain reasoner:
       a. Adds domain_expert_candidates
       b. Qualifies combined pool → domain_qualified, domain_blocked
       c. Returns full domain_analysis with option qualification embedded

4. Write option_pool.json with presented_to_parties=null

5. Call main model (build_turn_prompt with domain_analysis + qualified pool)

6. Parse main model response → extract which options referenced in message_text
   Update option_pool.json: presented_to_parties = [candidate_ids mentioned]
```

### Option generator input

```
{
  party_state: {
    party_a: { accumulated_interests, current_emotional_state },
    party_b: { same }
  },
  session_state: {
    current_phase, positions, facts_snapshot, issue_families, missing_info
  },
  domain_context: {
    domain: "divorce" | ...,
    active_issue_families: [string],
    plugin_confidence: "low" | "moderate" | "high"
  }
}
```

Note: the option generator does NOT receive `domain_analysis` as input — it would re-introduce constraint-checking. It receives only party state and session state.

### Domain reasoner interface change

`generate_domain_analysis(state, party_state, plugin_assessment, option_pool=None)`

When `option_pool` is provided, the domain reasoner:
1. Generates its own domain-expert candidates (as before in Stage 3)
2. Combines incoming `option_pool` with its own candidates
3. Qualifies the combined pool
4. Returns the full domain_analysis schema (CONTRACT-016) with `qualified_candidates` now populated from the combined qualification pass

When `option_pool` is absent (backward compatibility), behavior is identical to Stage 3.

---

## 6. Integration with Five-Step Prompt

The main model's Step 3 prompt (in `prompt_builder.py`) is updated to present the full qualified pool:

**Stage 4 Step 3 section:**
```
=== OPTION POOL (pre-qualified) ===
Combined pool: N candidates reviewed
Qualified: M candidates

[For each qualified candidate:]
  [candidate_id] [label] (source: brainstormer | domain_expert)
  Feasibility: [feasibility_rationale]
  Confidence: [confidence]
  Prerequisite parameters: [if any]

Blocked: K candidates
[For each blocked candidate:]
  [label] — blocked: [blocking_rationale]
  Would unblock if: [what_would_unblock]

INSTRUCTION: Your Step 3 (Option Scan) should draw from the qualified candidates above.
You may present all or a subset, based on what is appropriate for this turn.
Record the candidates you include in your response in the options_introduced field.
You may identify options not in the qualified list if you believe they are important —
note that new additions have not been domain-qualified.
```

The `=== DOMAIN ANALYSIS (pre-computed) ===` section from Stage 3 remains for the domain-level read (option_readiness rationale, blocking constraints, domain confidence). The option pool section is additive.

---

## 7. Invariants

- `option_readiness == "blocked"` whenever `safety_veto_applied == true`
- `domain_qualified` is empty whenever `option_readiness != "ready"`
- `presented_to_parties` only contains `candidate_id` values that appear in `domain_qualified` — the main model must not present unqualified candidates (if it does, this is a P6 evaluation concern)
- `safety_veto_reason` is non-null whenever `safety_veto_applied == true`
- `schema_version` is always `"option_pool.v0"`
- `candidate_id` values are unique across `brainstormer_candidates` and `domain_expert_candidates` — no ID collisions in the combined pool

---

## 8. Policy Profile Emission

| Profile | `option_pool.json` emitted | Notes |
|---|---|---|
| `dev_verbose` | yes | Full artifact, all layers |
| `eval_support` | yes | Full artifact, all layers |
| `sim_minimal` | no | Option generator not called; domain_reasoner Stage 3 path used |
| `redacted` | no | Not emitted |

Option generator is called only for `lm_runtime` sessions. `runtime` and `reference` sessions use the existing deterministic pipeline unchanged.

---

## 9. Evaluation Targets

The option_pool.json artifact enables precise evaluation of Stage 4's hypothesis:

| Question | Field to check |
|---|---|
| Did the brainstormer expand the pool? | `combined_pool_count` vs Stage 3 `qualified_candidates` count |
| Did any brainstormer candidates qualify? | `domain_qualified[].source == "option_generator"` |
| Did the domain reasoner's qualification quality hold? | `domain_blocked` rationales are coherent; `domain_qualified` rationales are substantive |
| Did the main model use the wider pool? | `presented_to_parties` count vs Stage 3 options count in response |
| Were any unqualified options presented? | `presented_to_parties` values all appear in `domain_qualified` |

**Primary Stage 4 success signal:** At T5 on D-B07-S11, at least one `domain_qualified` candidate has `source == "option_generator"` and is referenced in `presented_to_parties`. This demonstrates the full pipeline: brainstormer generates → domain reasoner qualifies → main model presents.

---

## 10. Relationship to Existing Contracts

| Contract | Relationship |
|---|---|
| CONTRACT-016 (domain analysis) | `option_pool.json` extends and supplements domain_analysis; `option_readiness` and `safety_veto_applied` are inherited from domain_analysis. The domain_analysis `qualified_candidates` field (Stage 3) is superseded by `option_pool.domain_qualified` in Stage 4 sessions. Both artifacts are written for Stage 4 sessions. |
| CONTRACT-014 (reasoning trace) | `reasoning_trace.option_scan.options_introduced` is populated from `presented_to_parties`; these must agree. |
| CONTRACT-015 (party state) | Party state is an input to the option generator (party interests inform what options to brainstorm). |
| ARCH-007 Stage 4 | This contract defines the interface that Stage 4 implements. |
| ARCH-007 Stage 5 | The safety veto rule in this contract is the Stage 4 bridge to Stage 5. Stage 5's dedicated safety monitor will eventually hold the `safety_veto_applied` determination rather than the domain reasoner reading party_state directly. |
