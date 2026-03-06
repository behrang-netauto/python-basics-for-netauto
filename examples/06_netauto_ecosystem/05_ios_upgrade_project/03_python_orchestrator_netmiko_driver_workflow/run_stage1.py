#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime

from src.netmiko_driver import NetmikoDriver
from src.stage1_orchestrator import stage1


def main() -> int:
    p = argparse.ArgumentParser(description="Stage1 - Python orchestrator + Netmiko driver")
    p.add_argument("--run-id", default=None, help="Run identifier (default: timestamp)")
    p.add_argument("--config", required=True, help="Path to config.yml")
    p.add_argument("--inventory", required=True, help="Path to inventory.yml")
    p.add_argument("--vault", required=True, help="Path to vault.yml")
    args = p.parse_args()

    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    driver = NetmikoDriver()

    out_path = stage1(
        run_id=run_id,
        config_path=args.config,
        inventory_path=args.inventory,
        vault_path=args.vault,
        driver=driver,
    )
    print(f"Stage1 handoff written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
