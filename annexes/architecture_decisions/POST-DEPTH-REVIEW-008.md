## Post-Depth Divorce Review

### Findings

#### P1. Shared divorce qualification is still schedule-centric at the top level
The shared divorce plugin is now meaningfully better for non-logistics slices, but `qualify_case_shared(...)` still advertises feasibility constraints almost entirely in school-week and exchange-logistics terms. That no longer reflects the real breadth of the current divorce slice set.

Primary location:
- `runtime/plugins/divorce_shared.py`

Why it matters:
- The shared domain framing now understates what the divorce plugin can actually support.
- It keeps a logistics-first mental model at the top of the plugin even after communication and reimbursement packages are working.

#### P1. Authored and runtime slice content are now the main duplication hotspot
The benchmark scaffold solved simulation plumbing, but the next maintenance hotspot is the parallel authored/runtime slice content. `D-B05`, `D-B06`, and `D-B07` each still keep closely mirrored turn content in two files.

Primary locations:
- `runtime/benchmarks/d_b05_authored.py`
- `runtime/benchmarks/d_b05_runtime.py`
- `runtime/benchmarks/d_b06_authored.py`
- `runtime/benchmarks/d_b06_runtime.py`
- `runtime/benchmarks/d_b07_authored.py`
- `runtime/benchmarks/d_b07_runtime.py`

Why it matters:
- Slice edits frequently need to be mirrored twice.
- The next likely drift problem is “same slice, almost same content” rather than shared-runtime correctness.

#### P2. Summary richness improved, but the artifact layer is still selective rather than state-complete
The summary now preserves more bounded-package detail, which is the right direction. But it still only surfaces a small subset of state, especially on the fact side. That is not wrong, but it remains a deliberate lossy view rather than a fuller evaluator narrative.

Primary location:
- `runtime/artifacts.py`

Why it matters:
- This is now a design tradeoff rather than a bug.
- If evaluator demands grow, summary selectivity will likely become the next artifact-layer decision point.

#### P2. Shared divorce package reasoning is present, but still pattern-matched from option markers
The new shared package logic is valuable and clearly better than before, but it still depends on string-pattern option markers rather than more structured package objects.

Primary locations:
- `runtime/plugins/divorce_shared.py`
- `runtime/state.py`

Why it matters:
- This is acceptable for MVP.
- It is the next place to watch if package logic becomes more complex.

### What Is Healthy Here

- Four divorce slices are now genuinely exercising shared domain logic, not just shared runtime wiring.
- The benchmark scaffold significantly reduced simulation and registry boilerplate.
- Plugin-neutral runtime, benchmark-owned policy, and benchmark-owned narrative posture are all still holding up after the latest depth changes.
- The current test suite is broad enough that architectural improvements are now easier to land safely.

### Readiness Judgment

The divorce path is no longer bottlenecked by architecture shape. It is now bottlenecked by content maintainability and by how broadly the shared divorce framing reflects the slices you already support. That is a good sign: the system is behaving more like a maintained domain runtime than a fragile prototype.

### Recommended Next Moves

1. Broaden shared divorce qualification framing so it reflects all current slice families.
2. Reduce safe duplication between authored and runtime slice content.
3. Decide whether summary selectivity should remain intentionally narrow or grow one step richer.
4. Only then consider a fifth divorce slice.
