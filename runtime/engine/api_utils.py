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

from typing import Any


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
