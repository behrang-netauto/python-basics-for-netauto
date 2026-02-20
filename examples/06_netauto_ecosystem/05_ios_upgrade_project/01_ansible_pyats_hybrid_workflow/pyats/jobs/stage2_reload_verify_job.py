
#!/usr/bin/env python3
import argparse
from pathlib import Path

from pyats.easypy import run
from genie.testbed import load


def main(runtime):
    """
    Stage2 job runner:
      - loads testbed from --testbed-file
      - passes handoff_file + max_workers + timeouts into the testscript
    """

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--testbed-file",
        required=True,
        help="Path to pyATS testbed YAML (e.g. pyats/testbeds/testbed.yml)",
    )
    parser.add_argument(
        "--handoff-file",
        required=True,
        help="Path to Stage1 handoff JSON (e.g. artifacts/<RUN_ID>/stage1_handoff.json)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="ThreadPoolExecutor max_workers for pre/post stages (default: 5)",
    )
    parser.add_argument(
        "--reload-timeout",
        type=int,
        default=1200,
        help="Reload timeout seconds (default: 1200)",
    )
    parser.add_argument(
        "--reconnect-timeout",
        type=int,
        default=900,
        help="Reconnect timeout seconds after reload (default: 900)",
    )
    parser.add_argument(
        "--reconnect-interval",
        type=int,
        default=20,
        help="Seconds between reconnect attempts (default: 20)",
    )

    # pyATS passes CLI args to runtime.args
    args, _ = parser.parse_known_args(runtime.args)

    # 1) load testbed object
    testbed = load(args.testbed_file)

    # 2) locate testscript file (pyats/tests/stage2_reload_verify.py)
    this_file = Path(__file__).resolve()
    testscript_path = this_file.parents[1] / "tests" / "stage2_reload_verify.py"

    # 3) run testscript with injected parameters
    run(
        testscript=str(testscript_path),
        runtime=runtime,
        testbed=testbed,
        handoff_file=args.handoff_file,
        max_workers=args.max_workers,
        reload_timeout=args.reload_timeout,
        reconnect_timeout=args.reconnect_timeout,
        reconnect_interval=args.reconnect_interval,
    )
