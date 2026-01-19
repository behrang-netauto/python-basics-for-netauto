#!/usr/bin/env python3

"""genie_uptime_parallel_once_json_aetest.py
- Load testbed.yml
- Connect to all devices, parallel if specified
- Testcase per device
- Parse and Execute "show version" to get uptime
- Save results and errors to separate JSON files
"""

import json
from pathlib import Path
from genie.testbed import load
from pyats import aetest
import logging
#logging.basicConfig(
#    level=logging.WARNING,
#    format="%(levelname)s %(name)s: %(message)s"
#)
log = logging.getLogger(__name__)
#log.setLevel(logging.WARNING)

SHOW_CMD = "show version"

def write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def load_testbed(self, testbed_file: str | None = None):
        
        from datetime import datetime, timezone
        self.parent.parameters["run_start"] = datetime.now(timezone.utc)

        try:
            self.parent.parameters["testbed"] = load(testbed_file)
        except Exception:
            self.failed("No testbed or testbed_file was accessible!!!!")
        
    @aetest.subsection
    def connect_all_devices(self, testbed, parallel: bool = False, max_parallel: int = 5):
        from concurrent.futures import ThreadPoolExecutor, as_completed

        failed_devices = []
        failed_names = set()
        connected_names = set()

        def _connect_one(dev_name, dev) -> None:
            dev.connect(via="cli", log_stdout=False, timeout=10, learn_hostname=True)

        items = list(testbed.devices.items())

        if parallel:
            with ThreadPoolExecutor(max_workers=max_parallel) as ex:
                futures = {
                    ex.submit(_connect_one, dev_name, dev): dev_name 
                    for dev_name, dev in items
                }

            for fut in as_completed(futures):
                dev_name = futures[fut]
                try:
                    fut.result()
                    connected_names.add(dev_name)
                except Exception as e:
                    failed_devices.append(f"{dev_name}: {type(e).__name__}: {e}")
                    failed_names.add(dev_name)
            
        else:
            for dev_name, dev in items:
                try:
                    _connect_one(dev_name, dev)
                    connected_names.add(dev_name)
                except Exception as e:
                    failed_devices.append(f"{dev_name}: {type(e).__name__}: {e}")
                    failed_names.add(dev_name)

        self.parent.parameters["connect_failed"] = failed_devices
        self.parent.parameters["connect_failed_names"] = failed_names
        self.parent.parameters["connect_ok_names"] = connected_names
        
        if len(failed_names) == len(testbed.devices):
            self.failed("All device connections failed.\n" + "\n".join(failed_devices))

    @aetest.subsection
    def mark_connected_devices(self, connect_ok_names=None):
        aetest.loop.mark(UptimeTestcase, dev_name=sorted(connect_ok_names or []))

class UptimeTestcase(aetest.Testcase):

    @aetest.test
    def parse_uptime(self, testbed, dev_name):
        dev = testbed.devices[dev_name]
      
        try:
            parsed = dev.parse(SHOW_CMD)
            up_time = parsed["version"].get("uptime", "N/A")

            results = self.parent.parameters.setdefault("uptime_result", [])
            results.append({"device": dev_name, "uptime": up_time})

            if up_time != "N/A":
                self.passed(f"{dev_name} uptime: {up_time}")
            else:
                self.failed(f"{dev_name} uptime not found")
        
        except Exception as e:
            errors = self.parent.parameters.setdefault("uptime_parse_errors", [])
            errors.append(f"{dev_name}: {type(e).__name__}: {e}")
            self.failed(f"{dev_name} parse error: {type(e).__name__}: {e}")

class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def save_json_once(self, uptime_result=None, uptime_parse_errors=None):
        run_st = self.parent.parameters["run_start"].strftime("%Y%m%dT%H%M%S")
        SCRIPT_DIR = Path(__file__).resolve().parent
        OUT_DIR = SCRIPT_DIR.parent / "output"
        per_test_dir = OUT_DIR / f"uptime_{run_st}"
        
        try:
            per_test_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.failed(f"Failed to create output directory {per_test_dir}: {type(e).__name__}: {e}")

        try:
            write_json(str(per_test_dir / f"uptime_results_{run_st}.json"), uptime_result or [])
        except Exception as e:
            self.failed(f"Failed to write uptime results : {type(e).__name__}: {e}")

        try:
            write_json(str(per_test_dir / f"uptime_errors_{run_st}.json"), uptime_parse_errors or [])
        except Exception as e:
            self.failed(f"Failed to write uptime errors : {type(e).__name__}: {e}")

    @aetest.subsection
    def disconnect_all_devices(self,testbed):
        for _, dev in testbed.devices.items():
            try:
                dev.disconnect()
            except Exception:
                pass
    