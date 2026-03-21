# FUTURE-IDEA-001: Voice Emotional-Signal and Negotiation-Style Layer

**Status**  
Speculative future idea / informative only

**Purpose**  
This note records a plausible future direction for Solomon: a voice-enabled assistive analysis layer that detects emotional posture and negotiation-style signals from speech and feeds those signals into session-state logic.

This document does **not** change the current MVP evaluation-phase scope.  
It exists so the idea is captured in-repo without being confused for an active requirement.

---

## 1. Plain-language idea

A future version of Solomon could analyze live or recorded speech for soft signals such as:

- rising conflict
- tension
- uncertainty
- defensiveness
- cooperation
- abrupt pacing changes
- long pauses
- possible negotiation-style shifts

The strongest use would be to treat those signals as **assistive state inputs**, not as authoritative truth claims.

---

## 2. Best-fit framing for Solomon

The right framing is:

- speech-level emotional and negotiation-style analysis as a **soft signal layer**
- confidence-limited inputs into the mediation runtime
- support for pacing changes, calmer prompts, summaries, or mediator attention cues
- optional evaluator-visible signal traces for controlled review

This fits Solomon best when used to improve:

- escalation sensitivity
- pacing and turn management
- mediator review prompts
- bounded session-state updates

It does **not** fit well as:

- a direct readout of inner emotional truth
- a psychological diagnosis engine
- an authoritative lie detector
- a substitute for human judgment about intent, fear, anger, or coercion

---

## 3. Why this is plausible

Current speech analytics systems are already capable of extracting structured conversational signals such as:

- stress or tension indicators
- tone shifts
- pacing changes
- interruption patterns
- escalation markers

That makes the general direction realistic enough to consider for future Solomon evaluation work, especially in controlled settings.

---

## 4. Main caution

The key risk is **overclaiming what the model knows**.

Even strong speech analytics systems remain:

- probabilistic
- context-dependent
- speaker-dependent
- sensitive to recording conditions
- vulnerable to cultural and interpersonal variation

So a safe Solomon framing would be:

- `possible tension increase detected`
- `speech pattern suggests rising defensiveness`
- `confidence-limited signal of reduced cooperation`

and **not**:

- `the user is angry`
- `the speaker is being deceptive`
- `the person is emotionally unsafe`

---

## 5. Strongest future integration pattern

If pursued later, the best integration pattern would likely be:

1. detect emotional-posture and negotiation-style speech signals
2. map them into bounded session-state updates
3. let those updates influence pacing, summaries, prompts, and escalation review
4. expose them to human mediators or evaluators as confidence-limited signals
5. preserve human judgment as authoritative

This would keep the feature aligned with Solomon's expert-in-the-middle philosophy.

---

## 6. Recommended future evaluation posture

If this idea is explored, it should begin in a controlled evaluation setting rather than in a product-facing workflow.

Recommended sequence:

1. pilot on synthetic or replayed sessions
2. test whether the signals improve evaluator reconstruction or escalation quality
3. measure false positives and overreading risk
4. test cultural and speaker-variation sensitivity
5. only then consider mediator-facing or live-session integration

---

## 7. Relationship to the current MVP phase

This idea is **out of scope for the current MVP evaluation baseline**.

Reasons:

- the current phase is already narrowly anchored to artifact quality, bounded offline sessions, and core/plugin/runtime separation
- adding voice interpretation now would widen the evaluation target too early
- the feature is best treated as a later experimental layer once the baseline evaluation runtime is stable

For now, this should be treated as:

- a future architecture/input idea
- a possible later benchmark dimension
- a candidate evaluator-side or mediator-side augmentation layer

---

## 8. Short take

This is a good future idea if Solomon treats it as a **soft assistive signal layer**.

It becomes a bad idea if Solomon treats it as an authority on what people truly feel.
