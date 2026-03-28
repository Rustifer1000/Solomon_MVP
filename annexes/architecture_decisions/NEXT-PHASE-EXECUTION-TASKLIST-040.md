# Next-Phase Execution Tasklist 040

## Purpose

This tasklist sequences Stage 4 work for Solomon's multi-agent evolution (ARCH-007), following:

- Stage 3 implementation and diagnostics complete: [STAGE3-FINDINGS-039](./STAGE3-FINDINGS-039.md)
- ROADMAP-037 updated to reflect Stage 3 closed: [ROADMAP-037](./ROADMAP-037-forward-from-stage2b.md)
- All three adversarial red-team cases authored and first sessions run (D-B-RT01, D-B-RT02, D-B-RT03)

---

## Stage 3 status: complete — all items closed

| Item | Status |
|---|---|
| domain_reasoner.py | **CLOSED** — bracket-counter parser, reactive interest sufficiency, process vs. substantive distinction, scope restriction |
| D-B07-S10 P6 bottleneck | **CLOSED** — option_readiness=ready at T5, 4 qualified candidates |
| D-B11-S06 safety veto regression check | **CLOSED** — veto correctly withheld for passive asymmetry |
| D-B04-S04 regression check | **CLOSED** — T7=ready with 2 bounded candidates, no regressions |
| Adversarial red-team cases (AF-1, AF-2, AF-3) | **CLOSED** — D-B-RT01/02/03 authored and S01/S02 evaluated |
| STAGE3-FINDINGS-039 memo | **CLOSED** |

---

## Stage 4 context

Stage 4 (ARCH-007 §4) decouples creative option generation from response generation. A dedicated brainstorming pass runs after the domain reasoner but before the main five-step pass. It takes the party state model and domain reasoner output and generates a broad unconstrained option pool. The domain reasoner then qualifies that pool. The main model selects from qualified options rather than generating them in the moment.

**The key principle:** good brainstorming requires temporarily suspending constraint-checking. Currently the domain reasoner both generates candidates and qualifies them in a single call. Separating generation from qualification produces more creative options that are then filtered to the domain-viable ones.

**What Stage 4 does NOT change:**
- Party state (Stage 2) — unchanged
- Domain reasoner's qualification logic — qualification becomes the primary role; generation is moved to the option generator
- Main model's five-step structure — unchanged; Step 3 (option scan) now receives a pre-qualified pool
- Safety veto in domain reasoner — unchanged

**How you know Stage 4 worked:** Evaluators note that options presented are more creative and less obvious than in Stage 3 while domain-feasibility qualification is maintained. C5 scores improve on complex cases. The option_pool.json artifact shows a wider unconstrained_candidates list than the domain_reasoner alone produces, with the domain_qualified subset maintaining or improving qualification quality.

---

## Open design question: domain reasoner interface change

Stage 4 requires a decision on how the domain reasoner and option generator divide responsibility.

**Current state (Stage 3):** domain_reasoner.py generates candidates AND qualifies them in a single call.

**Stage 4 options:**

Option A — Full handoff: option_generator.py generates the unconstrained pool; domain_reasoner.py receives the pool as input and qualifies it (no longer generates its own candidates).

Option B — Additive: option_generator.py generates an unconstrained pool; domain_reasoner.py receives it but may also add its own domain-expert candidates before qualifying the combined list.

**Decision: Option B (confirmed 2026-03-28).** The domain reasoner's current candidate generation is domain-expert output (e.g. "tiered notice requirement" — a domain reasoner knows this option pattern exists). The brainstormer's value is creativity across option families the domain reasoner might not foreground. Combining both pools before qualification maximises coverage. Option A risks losing domain-specific candidates the brainstormer won't naturally produce.

---

## Ranked worklist

### 1. Define CONTRACT-017 (option_pool artifact schema) — CLOSED 2026-03-28

**Design decision: Option B (additive/combined pool) — confirmed 2026-03-28.**

**CONTRACT-017 minimum fields:**

`option_pool.json`:
- `session_id`, `case_id`, `turn_index`
- `unconstrained_candidates` — brainstormer's raw output; list of `{candidate_id, label, rationale, party_interest_alignment, related_issues}`
- `domain_expert_candidates` — domain reasoner's own additions (domain-specialist options the brainstormer may not foreground)
- `combined_pool` — union of the above two lists before qualification
- `domain_qualified` — subset that passed domain reasoner qualification; list with added `{feasibility_rationale, confidence, prerequisite_parameters}`
- `domain_blocked` — candidates reviewed but not qualified, with explicit blocking rationale
- `presented_to_parties` — subset selected for inclusion in response (filled by main model post-hoc)
- `safety_veto_applied` — bool (if veto fires, domain_qualified and presented_to_parties are empty)

Write `schema/option_pool.schema.json`.

Reference this contract from artifact validation in `artifacts.py`.

---

### 2. Build `runtime/engine/option_generator.py`

A focused LLM call. Separate system prompt that positions the model as a creative brainstormer, explicitly NOT filtering for domain feasibility.

**System prompt key principles:**
- Generate options freely — feasibility qualification happens after, not during
- Draw on party interests, stated positions, and identified issue clusters
- Include non-obvious options (creative packaging, phasing, sequencing)
- Do NOT reject options because they seem legally or logistically uncertain — that is the domain reasoner's job
- Output is a list of candidate options with party interest alignment notes, not a response draft

**Input (structured context):**
- `party_state` — accumulated interests for both parties (from party_state.json)
- `session_state` — current positions, facts, issues, missing_info
- `domain_analysis` — from domain_reasoner (provides issue family context and blocking constraints as framing, NOT as qualification filters)
- `turn_index` — brainstormer only runs when option_readiness is not blocked

**Output:** `unconstrained_candidates` list matching CONTRACT-017 schema.

**max_tokens:** 2048 (generous — brainstormer should produce 5-10 candidates with alignment notes).

**Parser:** use the existing `_extract_json_object()` bracket-counter (same pattern as domain_reasoner.py and lm_engine.py).

**Guard:** if `domain_analysis.option_readiness == "blocked"`, return empty list immediately — do not call the LM.

---

### 3. Update `runtime/engine/domain_reasoner.py` to accept and qualify an option pool

Extend `generate_domain_analysis()` to:

1. Accept an `option_pool` parameter (list of `unconstrained_candidates` from option_generator)
2. If Option B (recommended), combine incoming pool with domain reasoner's own expert candidates
3. Qualify the combined pool — for each candidate: domain-feasibility check, confidence rating, blocking rationale if not qualified
4. Return `domain_qualified` and `domain_blocked` subsets in the domain_analysis output

The domain_reasoner's system prompt needs a new section:

```
OPTION QUALIFICATION MODE

You have received a candidate option pool from the brainstorming pass. Your job is to:
1. Review each candidate against domain realities (legal constraints, financial feasibility, parenting practice standards)
2. Mark as qualified (with confidence and any prerequisite parameters) or blocked (with explicit blocking rationale)
3. Add your own domain-expert candidates if any obvious options were missed

Do NOT filter options because they seem psychologically premature for these parties — that is the mediator's concern. Your scope is domain feasibility only.
```

**Interface change:** `generate_domain_analysis(state, party_state, plugin_assessment, option_pool=None)` — `option_pool` is optional for backward compatibility. When provided (Stage 4), the domain reasoner combines it with its own domain-expert candidates before qualification. When absent (Stage 3 path), behavior is unchanged.

---

### 4. Update `runtime/engine/lm_engine.py` to call option_generator before domain_reasoner

New call sequence before `build_turn_prompt`:

```python
# 1. Generate unconstrained option pool (if option_readiness is not yet blocked)
raw_option_pool = option_generator.generate_option_pool(state, party_state, plugin_assessment)

# 2. Run domain reasoner with option pool
domain_analysis = domain_reasoner.generate_domain_analysis(
    state, party_state, plugin_assessment, option_pool=raw_option_pool
)

# 3. Build prompt with domain_analysis (which now includes qualified pool)
```

Write `option_pool.json` to session output (under `eval_support` and `dev_verbose` profiles) after domain reasoner qualification and before main model call — so evaluators can see the full pool independent of what the main model selects.

---

### 5. Update `runtime/engine/prompt_builder.py` to include qualified option pool

The main model's Step 3 prompt changes:

**Before (Stage 3):**
```
Step 3 — Option scan: What options are available? Pre-computed domain analysis shows:
[domain_analysis summary with qualified_candidates]
```

**After (Stage 4):**
```
Step 3 — Option scan: Review the pre-qualified option pool and select candidates for response inclusion.
[option_pool.domain_qualified — full list with feasibility rationale]
[option_pool.domain_blocked — list of blocked candidates with blocking rationale, for completeness]

Select from the qualified candidates. You may also identify options not in the pool if you believe they are important, but note that new additions have not been domain-qualified.
```

The `presented_to_parties` field in option_pool.json is filled after the main model's response is parsed — record which qualified options the main model included in its response synthesis.

---

### 6. Update `artifacts.py` and `policy_profiles.py`

- Add `write_option_pool(session_dir, option_pool)` to `artifacts.py`
- Add `option_pool.json` to artifact manifest under `eval_support` and `dev_verbose` profiles
- Absent under `sim_minimal` and `redacted`
- Add `option_pool.schema.json` reference to artifact validation

---

### 7. Run Stage 4 diagnostic: D-B07-S11

Primary diagnostic case. D-B07 is the primary Stage 3 target and the clearest test of option quality improvement.

**Diagnostic questions:**
- Does `option_pool.unconstrained_candidates` at T5 contain more candidates than the domain reasoner alone produced in S10 (S10: 4 candidates)?
- Does `option_pool.domain_qualified` at T5 maintain qualification quality (all qualified candidates are still domain-viable)?
- Does the main model's T5 response text reference options from the wider pool?
- Does C5 score improve beyond S10's score of 4?

**Success criteria:**
- `unconstrained_candidates` count > S10's domain_reasoner candidate count at T5
- `domain_qualified` count >= S10's qualified count (no regression)
- At least one qualified candidate in S11 that was NOT present in S10 (demonstrating creative expansion)
- No regressions in C1-C9 scores

Write `annexes/benchmark_cases/D-B07/sessions/D-B07-S11/evaluation.json` and `evaluation_summary.txt`.

---

### 8. Run Stage 4 regression check: D-B04-S05

Simpler baseline regression check (same function as D-B04-S04 was for Stage 3).

**Diagnostic questions:**
- Does T7 option_pool at D-B04-S05 maintain or expand the 2 bounded candidates from S04?
- Does the logistics-conditioned framing of options remain correct after adding the brainstormer?
- No new automatic fails or C9 regressions.

---

### 9. Write Stage 4 findings memo: `STAGE4-FINDINGS-041.md`

Cover:
- Option generator calibration notes (what worked in the system prompt, what needed revision)
- Option pool artifact: unconstrained vs qualified vs presented counts at key turns
- C5 score comparison Stage 3 vs Stage 4 across diagnostic cases
- Whether domain reasoner qualification quality was maintained when receiving external pool
- `presented_to_parties` analysis: what fraction of qualified options did the main model include?
- Open questions for Stage 5 (safety monitor)

---

### 10. Update ROADMAP-037 tracking table

Mark Stage 4 complete once items 1–9 are closed.

---

## Guiding constraints

**Stage 4 must not change deterministic simulation paths.** `option_pool.json` is produced only for `lm_runtime` sessions under `eval_support` and `dev_verbose` profiles. Existing benchmark sessions remain schema-valid without it.

**Stage 4 must not degrade domain qualification quality.** The domain reasoner's qualification logic is the gate between creative generation and option presentation. Adding more input candidates must not lower the qualification bar — the domain_blocked list is evidence that the qualification gate is functioning.

**Stage 5 constraint:** ARCH-007 §4 specifies that Stage 5 (safety monitor as dedicated agent) must be complete before any quality agent undergoes training-based improvement. Stage 4 completes the quality agent stack for the option generation function. After Stage 4, the Stage 5 prerequisite becomes active — Stage 5 design should begin in parallel with Stage 4 diagnostics.

---

## Status: COMPLETE — all items closed 2026-03-28

| Item | Status |
|---|---|
| 1. CONTRACT-017 + option_pool.schema.json | **CLOSED** 2026-03-28 |
| 2. Build option_generator.py | **CLOSED** 2026-03-28 |
| 3. Update domain_reasoner.py | **CLOSED** 2026-03-28 |
| 4. Update lm_engine.py | **CLOSED** 2026-03-28 |
| 5. Update prompt_builder.py | **CLOSED** 2026-03-28 |
| 6. Update artifacts.py + policy_profiles.py | **CLOSED** 2026-03-28 |
| 7. D-B07-S11 diagnostic | **CLOSED** 2026-03-28 |
| 8. D-B04-S05 regression check | **CLOSED** 2026-03-28 |
| 9. STAGE4-FINDINGS-041 memo | **CLOSED** 2026-03-28 |
| 10. Update ROADMAP-037 | **CLOSED** 2026-03-28 |
