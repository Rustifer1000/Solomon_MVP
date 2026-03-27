# DIAG-001: Stage 0 Diagnostic Evaluation Protocol

**Status**
Active / v0

**Purpose**
This document defines the Stage 0 diagnostic evaluation set for Solomon's multi-agent evolution (ARCH-007). Stage 0 evaluations are not a general benchmark sweep — they are a targeted diagnostic designed to answer three specific questions about the current single-model architecture before Stage 1 work begins.

---

## 1. Diagnostic Questions

| Question | What it reveals | Architecture implication |
|---|---|---|
| **Q1 — Perception quality** | Does the system accurately model each party's psychological state, interests, and relational dynamics? | Motivates Stage 2 (explicit party state modelling) |
| **Q2 — Option creativity** | Does the system generate non-obvious options, or default to obvious/conservative ones? | Motivates Stage 4 (decoupled option generation) |
| **Q3 — Escalation calibration** | Does the system correctly distinguish high emotion from safety risk? Subtle vulnerability from no vulnerability? | Validates the constraint architecture in ARCH-006 |

---

## 2. Case Selection

Five cases selected to probe all three questions across the escalation spectrum:

| Case | Mode | Primary stress | Q1 | Q2 | Q3 |
|---|---|---|---|---|---|
| D-B03 | M1 | Emotional betrayal context; E5 decision quality | ✓✓ (PQ1, PQ3) | ✓ (C5=3) | ✓ (subtle E5) |
| D-B04 | M1 | Standard logistics; option generation focus | ✓ (PQ1 risk) | ✓✓ (C5=4) | — |
| D-B10 | M0 | High emotional intensity; anti-escalation | ✓✓ (PQ3) | — | ✓✓ (correctly M0) |
| D-B11 | M1 | Quiet compliance vs. valid agreement; asymmetry | ✓✓ (PQ2, PQ4) | — | ✓ (subtle vulnerability) |
| D-B08 | M3 | Process breakdown; domination pattern | ✓✓ (PQ3, PQ4) | — | ✓✓ (escalation at right point) |

---

## 3. Scoring Approach and Stage 0 Limitation

**Important methodological note for Stage 0:**

The `perception_quality_review` section measures what the system *saw*, not what it *did*. In an ideal world, PQ scores would be read directly from an explicit party state artifact (what the system recorded about each party's internal state per turn). That artifact does not exist yet — it is the output of Stage 2.

For Stage 0, PQ scores are therefore **proxied from action quality**: C7 (emotional regulation), C6 (fair process), C3 (interest elicitation), and C9 (safety/escalation) scores provide evidence of what the system must have perceived. A system that correctly distinguishes emotional distress from safety risk (C9=5) must have perceived the distinction accurately. A system that acknowledges emotional betrayal specifically rather than generically (C7=5) must have read party state with some depth.

This proxy approach has limits — a system can act correctly on explicit/obvious signals while missing subtle ones. The Stage 0 PQ scores should be read as lower-bound estimates of perception quality, not precise measurements. The gap between Stage 0 (proxied) and Stage 2+ (direct) PQ scores is itself a metric: if PQ scores improve substantially when direct party state artifacts are available, that confirms the value of Stage 2.

---

## 4. Key Finding: Perception is Context-Sensitive

The Stage 0 diagnostic reveals a consistent pattern across the five cases:

**Perception quality degrades when cognitive demand shifts to logistics and option generation.**

- D-B03 (emotionally charged): PQ band **strong** — C7=5, detailed signal naming, specific acknowledgment
- D-B08 (breakdown + domination): PQ band **strong** — C6=5, correct domination/clarity distinction
- D-B10 (high emotion, M0): PQ band **competent** — correct risk discrimination, some emotional modeling gaps
- D-B11 (quiet compliance): PQ band **competent** — good relational/interest reading, emotional depth limited
- D-B04 (logistics/options focus): PQ band **developing** — C7=3, weakest emotional state modeling in corpus

The D-B04 finding is the clearest diagnostic signal: when the session's primary cognitive demand is option generation and logistics coordination, emotional and psychological state modeling degrades. This is a **focus competition problem** — the single-model architecture cannot simultaneously attend to party state at full depth and generate domain-qualified options.

This directly motivates:
- **Stage 1** (structured cognitive separation): enforce the perception pass before option generation begins
- **Stage 2** (explicit party state modelling): make party state a first-class artifact so it cannot be crowded out
- **Stage 4** (decoupled option generation): remove option generation from the same inference pass as perception

---

## 5. Secondary Findings

**Perception asymmetry is present in three of five cases.**

D-B03, D-B11, and D-B08 all show `perceived_asymmetry: true`. In each case one party occupies a structurally different position (betrayed/betraying, deferential/assertive, dominated/dominating). The C6 scores suggest the system detected the asymmetry at the action level, but whether it modeled the less-visible party's internal state as deeply as the more-visible party's is not testable from Stage 0 data. This is a direct target for Stage 2 evaluation.

**PQ3 (risk signal detection) is the strongest dimension.**

Across all five cases, PQ3 scores are competent or strong. The system reliably detects risk-relevant signals and calibrates them against the safety threshold. This is expected given C9's high weight (16) and consistent 4–5 scores across the corpus. The constraint architecture in ARCH-006 is well-supported by this finding.

**PQ2 (interest inference) shows the widest variance.**

D-B04 (developing/competent), D-B10 (competent), D-B11 (strong), D-B03 (strong). Interest inference is better when the case has explicit emotional content that makes interests visible. When interests are embedded in logistics positions, inference is weaker.

---

## 6. Stage Priority Implications

| Stage | Priority implication from Stage 0 |
|---|---|
| Stage 1 (structured reasoning) | **High** — focus competition is the primary gap; separating perception pass from option generation pass is the direct fix |
| Stage 2 (explicit party state) | **High** — Stage 0 PQ scores are proxied; direct party state artifacts needed to measure perception quality precisely |
| Stage 3 (plugin as domain reasoner) | **Medium** — domain reasoning quality (P-families) not the primary gap found |
| Stage 4 (decoupled option generation) | **High** — D-B04 finding confirms option generation competes with perception attention |
| Stage 5 (safety monitor) | **Lower urgency** — PQ3 is already strong; escalation calibration is functioning well |

---

## 7. Cases Evaluated

| Case | Session | PQ band | Asymmetry | Date |
|---|---|---|---|---|
| D-B03 | D-B03-S01 | strong | yes | 2026-03-26 |
| D-B04 | D-B04-S01 | developing | no | 2026-03-26 |
| D-B10 | D-B10-S01 | competent | no | 2026-03-26 |
| D-B11 | D-B11-S01 | competent | yes | 2026-03-26 |
| D-B08 | D-B08-S01 | strong | yes | 2026-03-26 |

---

## 8. Relationship to Other Documents

| Document | Relationship |
|---|---|
| ARCH-007 (multi-agent evolution roadmap) | This is the Stage 0 execution document |
| ARCH-006 (evaluation feedback loop) | PQ scores are the first entries in the Stage 0 diagnostic corpus |
| `schema/evaluation.schema.json` | `perception_quality_review` section added specifically to support this protocol |
