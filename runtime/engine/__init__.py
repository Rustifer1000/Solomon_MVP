"""
runtime.engine
==============
LLM integration layer for Solomon.

Stage 1 of the multi-agent evolution (ARCH-007).  Provides:

  perception   — PerceptionContext builder (party state from session state)
  prompt       — Structured five-step prompt builder enforcing cognitive separation
  lm_engine    — Anthropic API call + output parser → CandidateTurn

The orchestrator uses source="lm_runtime" to route through this layer
instead of the deterministic benchmark simulation functions.
"""
