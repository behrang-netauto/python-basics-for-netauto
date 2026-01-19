#!/usr/bin/env python3

"""
uptime_job.py
- Run uptime test case from genie_uptime_serial_aetest module
Run:
    source /path/to/your/pyats/venv/bin/activate
    pyats run job ...
"""

from pyats.easypy import run
from pathlib import Path

def main(runtime) -> None:
    JOB_DIR = Path(__file__).resolve().parent
    SCRIPT_DIR = JOB_DIR.parent / "scripts"

    testscript = str((SCRIPT_DIR / "genie_uptime_serial_aetest.py").resolve())

    run(testscript=testscript,
        runtime=runtime
    )

#if __name__ == "__main__": 
#   main(None)