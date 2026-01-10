#!/usr/bin/env python3

"""
genie_get_up_time.py
- Load testbed.yml
- Parse "show version"
- Save uptime to CSV and TXT table

Run:
  source /Users/behrang/Documents/Python/.venv/bin/activate
  python scripts/genie_get_up_time.py
"""

from genie.testbed import load
from datetime import datetime
import csv
from pathlib import Path
from typing import TypedDict

class GenieCsvResult(TypedDict):
    host_name: str|None
    result_command: str|None

TESTBED_FILE = "testbed.yml"
SHOW_CMD = "show version"

def genie_parse(file: str, cmd: str) -> list[GenieCsvResult]:
    
    tb = load(file)
    
    result: list[GenieCsvResult] = []
    
    for dev_name, dev in tb.devices.items():
        print(f"\n-----{dev_name}-----")

        up_time: str | None = None

        try:
            dev.connect(via="cli", log_stdout=False)
            parsed = dev.parse(cmd)
            up_time = parsed["version"]["uptime"]
            print(f"Uptime: {up_time}")
        
        except Exception as e:
            up_time = f"{type(e).__name__}: {e}"
            print(f"{type(e).__name__}: {e}\n")
       
        finally:
            try:
                dev.disconnect()
            except Exception:
                pass
        
        result.append({"host_name": dev_name, "result_command": up_time})

    return result

def write_csv(out_file: Path, result: list[GenieCsvResult]) -> None:
    fieldnames = ["host_name", "result_command"]
    
    with open(out_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for dev in result:
            writer.writerow(dev)
        
    print("up_time.csv written successfully!!!")

def text_table(out_file: Path, result: list[GenieCsvResult]) -> None:
    header_1 = "host_name"
    header_2 = "result_command"

    col1_width = max(len(header_1), *(len(str(dev["host_name"] or "")) for dev in result))
    col2_width = max(len(header_2), *(len(str(dev["result_command"] or "")) for dev in result))

    sep = f"{'-' * col1_width}-+-{'-' * col2_width}"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"{header_1.ljust(col1_width)} | {header_2}\n")
        f.write(sep + "\n")

        for dev in result:
            host = str(dev["host_name"] or "")
            out = str(dev["result_command"] or "")
            out = out.replace("\n", " ")
            f.write(f"{host.ljust(col1_width)} | {out}\n")
        
    print("up_time.txt written successfully!!!")

def main():
    run_st = datetime.now().strftime("%Y%m%dT%H%M%S")
    SCR_DIR = Path(__file__).resolve().parent
    LAB_DIR = SCR_DIR.parent
    OUT_DIR = LAB_DIR / "outputs"
    OUT_DIR.mkdir(exist_ok=True, parents=True)

    tb_file = str(LAB_DIR / TESTBED_FILE)    

    result = genie_parse(tb_file, SHOW_CMD)

    text_table(OUT_DIR / f"genie_get_up_time_{run_st}.txt", result)

    write_csv(OUT_DIR / f"genie_get_up_time_{run_st}.csv", result)

if __name__ == "__main__":
    main()

