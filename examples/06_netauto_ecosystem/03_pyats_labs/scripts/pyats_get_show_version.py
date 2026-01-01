#!/usr/bin/env python3
import os
import json
from datetime import datetime

from pyats.topology import loader


TESTBED_FILE = "testbed.yml"
OUT_DIR = "output"
SHOW_CMD = "show version"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    run_st = datetime.now().strftime("%Y%m%dT%H%M%S")

    tb = loader.load(TESTBED_FILE)    # load testbed

    ensure_dir(OUT_DIR)     # base output dir

    for dev_name, dev in tb.devices.items():
        per_dev_dir = os.path.join(OUT_DIR, f"{dev_name}_{run_st}")
        ensure_dir(per_dev_dir)

        raw_file = os.path.join(per_dev_dir, f"{dev_name}_show_version_{run_st}.txt")
        parsed_file = os.path.join(per_dev_dir, f"{dev_name}_show_version_{run_st}.json")
        err_file = os.path.join(per_dev_dir, f"{dev_name}_error_{run_st}.txt")

        print(f"\n=== {dev_name} ===")

        try:
            dev.connect(via="cli", log_stdout=False)

            raw = dev.execute(SHOW_CMD)
            write_text(raw_file, raw + "\n")
            print(f"RAW saved: {raw_file}")

            parsed = dev.parse(SHOW_CMD)
            write_json(parsed_file, parsed)
            print(f"PARSED saved: {parsed_file}")

        except Exception as e:
            write_text(err_file, f"{type(e).__name__}: {e}\n")
            print(f"ERROR saved: {err_file}")

        finally:
            try:
                dev.disconnect()
            except Exception:
                pass


if __name__ == "__main__":
    main()
