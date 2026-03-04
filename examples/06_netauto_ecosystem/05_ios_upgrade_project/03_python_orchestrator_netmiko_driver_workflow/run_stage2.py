#!/usr/bin/env python3
from __future__ import annotations

import argparse

from src.netmiko_driver import NetmikoDriver
from src.stage2_orchestrator import stage2


def main() -> int:
    p = argparse.ArgumentParser(description="Stage2 - Reload READY devices from Stage1 handoff")
    p.add_argument("--handoff", required=True, help="Path to Stage1 stage1_handoff.json")
    p.add_argument("--config", required=True, help="Path to config.yml")
    p.add_argument("--vault", required=True, help="Path to vault.yml")
    p.add_argument(
    "--precheck-no-reload",
    action="store_true",
    help="Run only Phase A (precheck) and write results; do NOT reload devices."
    )
    args = p.parse_args()

    driver = NetmikoDriver()

    out_path = stage2(
        stage1_handoff_path=args.handoff,
        config_path=args.config,
        vault_path=args.vault,
        driver=driver,
        precheck_no_reload=args.precheck_no_reload,
    )
    
    print(f"Stage2 results written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())