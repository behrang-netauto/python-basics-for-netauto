#!/usr/bin/env python3

"""
uptime_job_parallel_per_device_json.py
- Run uptime test case from genie_uptime_parallel_per_device_json_aetest module
- Testcase per device
- CommonSetup: parallel device connection
- Run with --clean-file
Run:
    source /path/to/your/pyats/venv/bin/activate
    pyats run job ... --clean-file clean.yml --invoke-clean
"""

from pyats.easypy import run
from pathlib import Path

def main(runtime) -> None:
    JOB_DIR = Path(__file__).resolve().parent
    SCRIPT_DIR = JOB_DIR.parent / "scripts"

    testscript = str((SCRIPT_DIR / "genie_uptime_parallel_per_device_json_aetest.py").resolve())

    run(testscript=testscript,
        runtime=runtime,
        check_all_devices_up=True,
        clean_file=str((SCRIPT_DIR / "clean.yml").resolve()),
        parrallel=True,
        parrallel_limit=5,
    )

#if __name__ == "__main__": 
#   main(None)