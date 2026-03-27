"""
redaction.py
------------
Write-time redaction hooks for the ``redacted`` policy profile.

When ``PolicyProfile.require_redaction`` is ``True``, every text artifact and
every string value inside JSON artifacts is passed through ``redact_text``
before being written to disk.  This prevents PII from appearing in outputs
even when real party names or contact details are loaded into a session.

Redaction strategy (v0)
-----------------------
1. Regex-based scrubbing of common PII patterns (email, US phone, SSN,
   credit-card-like digit blocks).
2. Participant-name scrubbing: any display name in ``state["participants"]``
   that looks like a real proper name (not an anonymised code such as
   ``spouse_A``) is replaced with the redaction marker.

The marker ``[REDACTED]`` is used in all cases so reviewers can tell that
content was deliberately removed rather than missing.

Note
----
The benchmark corpus uses anonymised labels (``Spouse A``, ``Parent A``, etc.)
so the name-scrubbing pass is typically a no-op in evaluation runs.  The
hook's primary purpose is to provide a safe write boundary when non-anonymised
data is loaded in production-adjacent deployments.
"""

from __future__ import annotations

import re
from typing import Any


REDACT_MARKER = "[REDACTED]"

# Ordered from most-specific to least-specific to avoid double-replacement.
_PII_PATTERNS: list[re.Pattern[str]] = [
    # Credit-card-like 16-digit blocks (XXXX-XXXX-XXXX-XXXX or XXXX XXXX …)
    re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    # US Social Security Number (XXX-XX-XXXX)
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    # US phone numbers in several common formats
    re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"),
    # Email addresses
    re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
]

# Labels that are already anonymised — do not treat as real names.
_ANONYMISED_PREFIXES = (
    "spouse_",
    "parent_",
    "party_",
    "participant_",
)


def _collect_sensitive_names(state: dict) -> list[str]:
    """
    Return participant display names that look like real proper names.

    Names that begin with an anonymised prefix (``spouse_a``, ``parent_b``,
    etc.) are excluded because they are already safe to publish.
    """
    names: list[str] = []
    for participant in state.get("participants", []):
        display = str(participant).strip()
        lower = display.lower()
        if display and not any(lower.startswith(p) for p in _ANONYMISED_PREFIXES):
            names.append(display)
    return names


def redact_text(text: str, state: dict) -> str:
    """Apply all PII-scrubbing passes to a plain-text string."""
    for pattern in _PII_PATTERNS:
        text = pattern.sub(REDACT_MARKER, text)
    for name in _collect_sensitive_names(state):
        if len(name) > 3:  # Ignore single-character or very short labels.
            text = re.sub(re.escape(name), REDACT_MARKER, text, flags=re.IGNORECASE)
    return text


def redact_json_values(payload: Any, state: dict) -> Any:
    """
    Recursively walk a JSON-serialisable structure and redact all string values.

    Mapping keys are left untouched; only values are scrubbed.
    """
    if isinstance(payload, str):
        return redact_text(payload, state)
    if isinstance(payload, dict):
        return {k: redact_json_values(v, state) for k, v in payload.items()}
    if isinstance(payload, list):
        return [redact_json_values(item, state) for item in payload]
    return payload
