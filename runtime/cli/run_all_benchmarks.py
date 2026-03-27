"""
run_all_benchmarks.py
---------------------
Batch-run all registered benchmark cases through the Solomon runtime scaffold.

Usage
-----
    python -m runtime.cli.run_all_benchmarks \\
        --corpus-dir  annexes/benchmark_cases \\
        --output-root /tmp/solomon_batch_run \\
        [--source runtime] \\
        [--policy-profile sim_minimal] \\
        [--seed <seed>] \\
        [--review-transcript-renderer none] \\
        [--generated-at <ISO-timestamp>] \\
        [--fail-fast]

Each case is written to <output-root>/<case-id>-S01-<source>/.
A summary table is printed on completion. Exit code is non-zero if any case fails.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch-run all Solomon benchmark cases through the runtime scaffold."
    )
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=REPO_ROOT / "annexes" / "benchmark_cases",
        help="Directory containing benchmark case subdirectories (default: annexes/benchmark_cases).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        required=True,
        help="Root directory to write per-case output folders into.",
    )
    parser.add_argument(
        "--source",
        choices=["runtime", "reference", "mock_model", "varied_mock_model"],
        default="runtime",
        help="Turn-output source to run through the runtime loop (default: runtime).",
    )
    parser.add_argument(
        "--policy-profile",
        default="sim_minimal",
        help="Persistence/policy profile to apply to every run (default: sim_minimal).",
    )
    parser.add_argument(
        "--seed",
        default=None,
        help="Optional reproducibility seed passed to each run.",
    )
    parser.add_argument(
        "--review-transcript-renderer",
        choices=["none", "prototype_local_v0"],
        default="none",
        help="Optional reviewer-facing transcript renderer (default: none).",
    )
    parser.add_argument(
        "--generated-at",
        default=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        help="UTC timestamp applied to every run (default: now).",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Abort the batch run on the first case failure.",
    )
    return parser.parse_args()


def discover_case_dirs(corpus_dir: Path) -> list[Path]:
    """Return all immediate subdirectories that contain a case_metadata.json."""
    return sorted(
        p for p in corpus_dir.iterdir()
        if p.is_dir() and (p / "case_metadata.json").exists()
    )


def run_single_case(
    case_dir: Path,
    output_root: Path,
    source: str,
    policy_profile: str,
    generated_at: str,
    seed: str | None,
    review_transcript_renderer: str,
) -> tuple[str, bool, str]:
    """Run one case and return (case_id, success, message)."""
    case_id = case_dir.name
    output_dir = output_root / f"{case_id}-S01-{source}"
    cmd = [
        sys.executable, "-m", "runtime.cli.run_benchmark",
        "--case-dir", str(case_dir),
        "--output-dir", str(output_dir),
        "--source", source,
        "--policy-profile", policy_profile,
        "--generated-at", generated_at,
        "--review-transcript-renderer", review_transcript_renderer,
    ]
    if seed is not None:
        cmd += ["--seed", seed]

    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if result.returncode == 0:
        return case_id, True, "ok"
    error_tail = (result.stderr or result.stdout or "").strip().splitlines()
    short_error = error_tail[-1] if error_tail else "unknown error"
    return case_id, False, short_error


def main() -> None:
    args = parse_args()

    corpus_dir = args.corpus_dir.resolve()
    if not corpus_dir.is_dir():
        raise SystemExit(f"ERROR: corpus-dir not found: {corpus_dir}")

    case_dirs = discover_case_dirs(corpus_dir)
    if not case_dirs:
        raise SystemExit(f"ERROR: no case directories with case_metadata.json found under {corpus_dir}")

    args.output_root.mkdir(parents=True, exist_ok=True)

    print(f"Solomon batch run — {len(case_dirs)} cases — source={args.source} profile={args.policy_profile}")
    print(f"Output root: {args.output_root.resolve()}")
    print()

    results: list[tuple[str, bool, str]] = []
    for case_dir in case_dirs:
        case_id = case_dir.name
        print(f"  Running {case_id} ... ", end="", flush=True)
        case_id_out, success, message = run_single_case(
            case_dir=case_dir,
            output_root=args.output_root,
            source=args.source,
            policy_profile=args.policy_profile,
            generated_at=args.generated_at,
            seed=args.seed,
            review_transcript_renderer=args.review_transcript_renderer,
        )
        status = "PASS" if success else "FAIL"
        print(f"{status}" + (f"  [{message}]" if not success else ""))
        results.append((case_id_out, success, message))
        if not success and args.fail_fast:
            print("\nAborted: --fail-fast is set.")
            break

    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed

    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(results)} cases run.")

    if failed:
        print("\nFailed cases:")
        for case_id, ok, msg in results:
            if not ok:
                print(f"  {case_id}: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
