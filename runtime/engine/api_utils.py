"""
runtime.engine.api_utils
========================
Shared API utilities for Solomon engine modules.

All engine modules must route Anthropic API calls through ``cached_create``
rather than calling ``client.messages.create`` directly.  This ensures
prompt caching (cache_control=ephemeral) is applied consistently without
each caller needing to remember the list-format wrapping.

CI enforcement
--------------
``tools/check_messages_create.py`` will fail the build if any file in
``runtime/engine/`` calls ``.messages.create(`` directly, except this
module itself.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Client / key / model helpers  (shared across all engine modules)
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    """Load the Anthropic API key from environment or project .env file."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        from dotenv import dotenv_values
        key = dotenv_values(env_path).get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not found in environment or .env file. "
            "Set it before using lm_runtime mode."
        )
    return key


def make_client() -> Any:
    """Return a configured ``anthropic.Anthropic`` client."""
    import anthropic
    return anthropic.Anthropic(api_key=load_api_key())


def get_model(*agent_env_vars: str) -> str:
    """
    Return the model to use for an engine agent.

    Checks each ``agent_env_vars`` in order, then falls back to the shared
    ``SOLOMON_LM_MODEL`` environment variable, then to the default model.

    Examples
    --------
    Main engine (no override):
        get_model()  →  SOLOMON_LM_MODEL or "claude-sonnet-4-5"

    Domain reasoner (agent-specific override first):
        get_model("SOLOMON_DOMAIN_MODEL")

    Option generator (three-level chain):
        get_model("SOLOMON_OPTION_MODEL", "SOLOMON_DOMAIN_MODEL")
    """
    for var in agent_env_vars:
        model = os.environ.get(var)
        if model:
            return model
    return os.environ.get("SOLOMON_LM_MODEL", "claude-sonnet-4-5")


# ---------------------------------------------------------------------------
# Cached API call wrapper
# ---------------------------------------------------------------------------

def cached_create(client: Any, *, system: str | list, **kwargs: Any) -> Any:
    """
    Wrapper around ``client.messages.create`` that applies prompt caching.

    Converts a plain string system prompt to the list format required for
    ``cache_control``.  An already-structured list is passed through
    unchanged so callers can pre-build complex system blocks if needed.

    Parameters
    ----------
    client:
        An ``anthropic.Anthropic`` instance.
    system:
        System prompt as a plain string or a pre-structured content list.
    **kwargs:
        Forwarded verbatim to ``client.messages.create`` (model, max_tokens,
        messages, etc.).
    """
    if isinstance(system, str):
        system = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
    return client.messages.create(system=system, **kwargs)
