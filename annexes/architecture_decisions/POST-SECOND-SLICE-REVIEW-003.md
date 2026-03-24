# Post-Second-Slice Review 003

## Findings

### [P1] Evaluator-facing artifact language still hardcodes a caution-heavy D-B04 narrative

The runtime now supports both `D-B04` and `D-B05`, but several artifact builders still assume a caution-oriented, feasibility-limited session shape even when the state does not support that posture.

- `runtime/artifacts.py`
  - `_position_note(...)` always frames proposals as "only conditional openness to phased option work"
  - `_missing_info_note(...)` always frames open items as blocking "stronger schedule recommendation"
  - `_summary_intro(...)` always says Solomon "avoided presenting a fixed recommendation"
  - `_summary_positions(...)` always says both parents showed openness to phased option work if proposals exist

This was acceptable with only `D-B04`, but `D-B05` shows the problem clearly: the system can now end in `M0` with no active caution flags, yet parts of the artifact language still sound like a caution-constrained overnight-schedule case.

### [P1] Flag generation remains D-B04-specific and will not generalize cleanly across slices

`runtime/state.py` still builds flags through hardcoded `flag-db04-*` templates and titles tied to unresolved school logistics and fixed-recommendation caution. That means:

- flag ids are slice-specific inside generic state logic
- flag titles/notes are still D-B04 flavored
- future benchmarks either inherit the wrong flags or require more hardcoded exceptions in the generic layer

The second slice passed because it stays in `M0` and does not trigger those templates, but that success masks the architectural problem rather than solving it.

### [P2] The state layer still contains a D-B04-specific `turn_index == 8` summary override

`runtime/state.py` still sets a special hardcoded next step when `turn_index == 8`. That is now clearly benchmark-specific behavior living in the generic state layer.

The generic agreement-phase fallback added for `D-B05` is a good step, but the old D-B04 branch should move into benchmark-specific behavior or summary policy rather than staying in shared state logic.

### [P2] The divorce plugin is still too logistics-centric to serve as a clean shared divorce-layer abstraction

`runtime/plugins/divorce.py` is better than before, but it still treats logistics clarification as the central caution axis:

- `LOGISTICS_ISSUES` and `LOGISTICS_KEYWORDS` dominate state interpretation
- warnings focus on feasibility/logistics
- `supports_fixed_recommendation` still reflects a D-B04-style caution question more than a general divorce-plugin question

That still works for `D-B04` and does not break `D-B05`, but it suggests the current "plugin" is really a `D-B04-derived divorce caution helper`, not yet a convincingly reusable divorce plugin layer.

### [P2] Session-level validation is solid, but it still validates the trace more than the artifact story built on top of it

`runtime/session_validation.py` now does good cross-turn coherence checks, but there is still no comparable "artifact narrative coherence" validator. The second slice shows this gap:

- session trace can be internally valid
- final escalation can be correct
- summary language can still overfit the older benchmark narrative

The runtime now needs a lightweight state-to-artifact narrative sanity layer, not just turn/session validation.

### [P3] Benchmark duplication is now organized, but still fairly manual

The `D-B05` split follows the right pattern and proves the architecture is reusable. But adding a benchmark still requires copying and editing multiple files manually:

- case files
- authored module
- runtime module
- simulation module
- facade export
- registry entry
- tests

That is acceptable now, but the repo is reaching the point where a small benchmark creation template or checklist would reduce accidental drift.

## What Is Healthy Here

- The benchmark registry and simulation seam are real.
- The runtime survived a second slice with a different turn count and different end posture.
- Case-aware source metadata is now cleaner.
- Session-level validation is now meaningful and catches full-run coherence issues.

## MVP Readiness Update

The codebase is now convincingly multi-slice, which is a major architectural milestone. The next bottleneck is no longer "can the runtime support another slice?" but "can generic layers stop telling a D-B04-shaped story when the slice is different?"

The next phase should focus on making artifacts, flags, and benchmark-specific policy more slice-aware and less hardcoded inside generic runtime/state logic.
