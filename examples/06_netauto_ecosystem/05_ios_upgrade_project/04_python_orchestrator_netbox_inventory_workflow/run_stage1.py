#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime

from src.stage1_orchestrator import stage1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage1 - Python orchestrator with YAML/NetBox inventory provider"
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run identifier (default: timestamp)",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to config.yml",
    )
    parser.add_argument(
        "--vault",
        required=True,
        help="Path to vault.yml",
    )

    args = parser.parse_args()

    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")

    out_path = stage1(
        run_id=run_id,
        config_path=args.config,
        vault_path=args.vault,
    )

    print(f"Stage1 handoff written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())