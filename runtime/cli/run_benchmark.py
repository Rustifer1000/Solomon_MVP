from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

from runtime.loaders import load_case_bundle
from runtime.orchestrator import run_session
from runtime.state import initialize_session_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Solomon D-B04 baseline scaffold.")
    parser.add_argument("--case-dir", type=Path, required=True, help="Path to the benchmark case directory.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Path to write generated artifacts.")
    parser.add_argument("--session-id", default="D-B04-S01-generated", help="Session identifier for the output run.")
    parser.add_argument("--policy-profile", default="sim_minimal", help="Persistence/policy profile to apply.")
    parser.add_argument(
        "--source",
        choices=["runtime", "reference", "mock_model", "varied_mock_model"],
        default="runtime",
        help="Turn-output source to run through the runtime loop.",
    )
    parser.add_argument(
        "--generated-at",
        default=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        help="UTC timestamp for artifact generation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    case_bundle = load_case_bundle(args.case_dir)
    state = initialize_session_state(case_bundle, args.session_id, args.policy_profile, source=args.source)
    run_session(case_bundle, state, args.output_dir, args.generated_at, source=args.source)


if __name__ == "__main__":
    main()
