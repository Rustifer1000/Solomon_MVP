"""
list_review_queue.py
--------------------
Scan a sessions directory tree and report which sessions are pending escalation
confirmation review, which have been reviewed, and the current corpus status.

Usage
-----
    python -m runtime.cli.list_review_queue \\
        --sessions-dir annexes/benchmark_cases \\
        [--show-reviewed] \\
        [--corpus-only]

The tool scans recursively for evaluation.json files and reports:
  - Sessions with requires_calibration_review=true and no confirmation record
  - Sessions with no confirmation record at all (unreviewed pool)
  - Sessions with a completed escalation_confirmation.json (reviewed)
  - Corpus-eligible count (confirmed_correct / confirmed_correct_with_notes)

Exit code is non-zero if any session has requires_calibration_review=true
and no confirmation record (i.e. the urgent queue is non-empty).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime.evaluator_artifact_validation import validate_escalation_confirmation


REPO_ROOT = Path(__file__).resolve().parents[2]

_CONFIRMED_VERDICTS = {"confirmed_correct", "confirmed_correct_with_notes"}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _scan_sessions(root: Path) -> list[dict]:
    """
    Walk root recursively and return one entry per evaluation.json found.
    """
    entries: list[dict] = []
    for eval_path in sorted(root.rglob("evaluation.json")):
        session_dir = eval_path.parent
        try:
            evaluation = _load_json(eval_path)
        except Exception as e:
            entries.append({
                "session_dir": session_dir,
                "case_id": session_dir.parent.name if session_dir.parent else "?",
                "session_id": session_dir.name,
                "requires_calibration_review": False,
                "has_confirmation": False,
                "confirmation": None,
                "has_expert_review": False,
                "error": str(e),
            })
            continue

        confirmation_path = session_dir / "escalation_confirmation.json"
        has_confirmation = confirmation_path.exists()
        confirmation: dict | None = None
        confirmation_error: str | None = None
        if has_confirmation:
            try:
                confirmation = _load_json(confirmation_path)
                schema_errors = validate_escalation_confirmation(confirmation)
                if schema_errors:
                    confirmation_error = f"schema validation failed: {'; '.join(schema_errors[:3])}"
                    has_confirmation = False
                    confirmation = None
            except Exception as exc:
                has_confirmation = False
                confirmation_error = str(exc)

        entries.append({
            "session_dir": session_dir,
            "case_id": evaluation.get("case_id", "?"),
            "session_id": evaluation.get("session_id", session_dir.name),
            "requires_calibration_review": bool(
                evaluation.get("final_judgment", {}).get("requires_calibration_review")
                or evaluation.get("requires_calibration_review")
            ),
            "has_confirmation": has_confirmation,
            "confirmation": confirmation,
            "confirmation_error": confirmation_error,
            "has_expert_review": (session_dir / "expert_review.json").exists(),
            "error": None,  # only set for evaluation load failures (above)
        })
    return entries


def _verdict(entry: dict) -> str | None:
    if entry["confirmation"] is None:
        return None
    return entry["confirmation"].get("escalation_confirmation", {}).get("verdict")


def _corpus_eligible(entry: dict) -> bool:
    if entry["confirmation"] is None:
        return False
    return bool(entry["confirmation"].get("training_corpus_eligible"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List Solomon sessions pending escalation confirmation review."
    )
    parser.add_argument(
        "--sessions-dir",
        type=Path,
        default=REPO_ROOT / "annexes" / "benchmark_cases",
        help="Root directory to scan for evaluation.json files (default: annexes/benchmark_cases).",
    )
    parser.add_argument(
        "--show-reviewed",
        action="store_true",
        help="Also show sessions that already have a confirmation record.",
    )
    parser.add_argument(
        "--corpus-only",
        action="store_true",
        help="Only show corpus-eligible sessions (confirmed_correct*).",
    )
    args = parser.parse_args()

    sessions_dir = args.sessions_dir.resolve()
    if not sessions_dir.is_dir():
        raise SystemExit(f"ERROR: sessions-dir not found: {sessions_dir}")

    entries = _scan_sessions(sessions_dir)
    if not entries:
        print("No evaluation.json files found.")
        sys.exit(0)

    # Partition
    errors = [e for e in entries if e["error"]]
    urgent = [e for e in entries if not e["error"] and e["requires_calibration_review"] and not e["has_confirmation"]]
    unreviewed = [e for e in entries if not e["error"] and not e["requires_calibration_review"] and not e["has_confirmation"]]
    reviewed = [e for e in entries if not e["error"] and e["has_confirmation"]]
    corpus_eligible = [e for e in reviewed if _corpus_eligible(e)]

    if args.corpus_only:
        print(f"Corpus-eligible sessions ({len(corpus_eligible)} of {len(reviewed)} reviewed)")
        print("=" * 60)
        if not corpus_eligible:
            print("  [none]")
        for e in corpus_eligible:
            record_id = (e["confirmation"] or {}).get("corpus_record_id") or "not assigned"
            print(f"  {e['session_id']:<20}  {e['case_id']:<10}  corpus_record_id: {record_id}")
        sys.exit(0)

    print(f"Solomon review queue — {len(entries)} sessions scanned")
    print(f"Scanning: {sessions_dir}")
    print()

    if errors:
        print(f"LOAD ERRORS ({len(errors)})")
        print("-" * 60)
        for e in errors:
            print(f"  {e['session_id']:<20}  {e['session_dir']}  ERROR: {e['error']}")
        print()

    print(f"URGENT — calibration review requested, no confirmation ({len(urgent)})")
    print("-" * 60)
    if not urgent:
        print("  [none]")
    for e in urgent:
        expert = "expert_review: yes" if e["has_expert_review"] else "expert_review: no"
        print(f"  {e['session_id']:<20}  {e['case_id']:<10}  {expert}")
    print()

    print(f"UNREVIEWED — no escalation confirmation ({len(unreviewed)})")
    print("-" * 60)
    if not unreviewed:
        print("  [none]")
    for e in unreviewed:
        expert = "expert_review: yes" if e["has_expert_review"] else "expert_review: no"
        print(f"  {e['session_id']:<20}  {e['case_id']:<10}  {expert}")
    print()

    if args.show_reviewed or not urgent:
        print(f"REVIEWED ({len(reviewed)}  |  corpus-eligible: {len(corpus_eligible)})")
        print("-" * 60)
        if not reviewed:
            print("  [none]")
        for e in reviewed:
            v = _verdict(e) or "?"
            eligible = "corpus: YES" if _corpus_eligible(e) else "corpus: no"
            print(f"  {e['session_id']:<20}  {e['case_id']:<10}  verdict: {v:<35}  {eligible}")
        print()

    print("Summary")
    print("-" * 60)
    print(f"  Total sessions scanned:        {len(entries)}")
    print(f"  Urgent (calibration + unconf): {len(urgent)}")
    print(f"  Unreviewed:                    {len(unreviewed)}")
    print(f"  Reviewed:                      {len(reviewed)}")
    print(f"  Corpus-eligible:               {len(corpus_eligible)}")
    if errors:
        print(f"  Load errors:                   {len(errors)}")

    if urgent:
        print()
        print(f"ACTION REQUIRED: {len(urgent)} session(s) need escalation confirmation review.")
        sys.exit(1)


if __name__ == "__main__":
    main()
