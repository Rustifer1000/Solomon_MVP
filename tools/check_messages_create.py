"""
tools/check_messages_create.py
================================
CI check: fail if any engine module calls client.messages.create directly.

All Anthropic API calls in runtime/engine/ must go through
``cached_create`` in ``api_utils.py``.  Direct calls to
``.messages.create(`` bypass prompt caching.

Usage
-----
    python tools/check_messages_create.py          # from project root
    python tools/check_messages_create.py --verbose

Exit codes
----------
0 — no violations found
1 — one or more violations found (prints file:line for each)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Pattern to detect: any use of .messages.create( in engine Python files.
# We allow only the one canonical call inside api_utils.py itself.
_PATTERN = re.compile(r"\.messages\.create\s*\(")
_ENGINE_DIR = Path(__file__).resolve().parents[1] / "runtime" / "engine"
_ALLOWED_FILE = "api_utils.py"


def check() -> list[tuple[Path, int, str]]:
    """Return a list of (file, line_number, line_text) violations."""
    violations: list[tuple[Path, int, str]] = []
    for path in sorted(_ENGINE_DIR.glob("**/*.py")):
        if path.name == _ALLOWED_FILE:
            continue
        in_multiline_string = False
        quote_char = ""
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            # Track entry/exit of triple-quoted strings (docstrings, multiline strings).
            for marker in ('"""', "'''"):
                count = line.count(marker)
                if not in_multiline_string:
                    if count % 2 == 1:          # odd occurrences → entering a block
                        in_multiline_string = True
                        quote_char = marker
                elif quote_char == marker:
                    if count % 2 == 1:          # odd occurrences → exiting the block
                        in_multiline_string = False
                        quote_char = ""
            # Skip lines inside docstrings/multiline strings and comment lines
            if in_multiline_string:
                continue
            if stripped.startswith("#"):
                continue
            if _PATTERN.search(line):
                violations.append((path, lineno, line.rstrip()))
    return violations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    violations = check()

    if not violations:
        if args.verbose:
            print("check_messages_create: OK — no direct messages.create calls found.")
        sys.exit(0)

    print(
        f"check_messages_create: FAILED — {len(violations)} direct .messages.create() "
        f"call(s) found outside api_utils.py.\n"
        f"Use cached_create() from runtime.engine.api_utils instead.\n"
    )
    for path, lineno, line in violations:
        rel = path.relative_to(_ENGINE_DIR.parent.parent)
        print(f"  {rel}:{lineno}:  {line.strip()}")

    sys.exit(1)


if __name__ == "__main__":
    main()
