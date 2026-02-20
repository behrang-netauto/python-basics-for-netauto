"""
{
  "r1": {
    "status": true,
    "reason": "",
    "pre_system_image": "bootflash:/old.bin",
    "post_system_image": "bootflash:/new.bin"
  }
}
"""
#!/usr/bin/env python3
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from pyats import aetest
from unicon.eal.dialogs import Dialog, Statement


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_reload_dialog() -> Dialog:
    statements = [
        Statement(
            pattern=r".*System configuration has been modified.*Save\? \[yes/no\].*",
            action="sendline(no)",
            loop_continue=True,
            continue_timer=False,
        ),
        Statement(
            pattern=r".*Proceed with reload\? \[confirm\].*",
            action="sendline()",
            loop_continue=True,
            continue_timer=False,
        ),
        Statement(
            pattern=r".*\[confirm\].*",
            action="sendline()",
            loop_continue=True,
            continue_timer=False,
        ),
    ]
    return Dialog(statements)


def extract_system_image(parsed_show_version: Dict[str, Any]) -> Optional[str]:
    if not isinstance(parsed_show_version, dict):
        return None

    v = parsed_show_version.get("system_image")
    if isinstance(v, str) and v.strip():
        return v

    v = parsed_show_version.get("system_image_file")
    if isinstance(v, str) and v.strip():
        return v

    ver = parsed_show_version.get("version")
    if isinstance(ver, dict):
        v = ver.get("system_image")
        if isinstance(v, str) and v.strip():
            return v
        v = ver.get("system_image_file")
        if isinstance(v, str) and v.strip():
            return v

    return None


def connect_parse_show_version(device) -> Tuple[bool, Dict[str, Any]]:
    """
      - return False, {"error": "..."}
      - return True,  {"system_image": "..."}
    """
    try:
        device.connect(
            log_stdout=False,
            init_exec_commands=[],
            init_config_commands=[],
        )
        parsed = device.parse("show version")
        system_image = extract_system_image(parsed)
        if not system_image:
            return False, {"error": "Could not extract system image from parsed 'show version'"}
        return True, {"system_image": system_image}
    except Exception as e:
        return False, {"error": str(e)}
    finally:
        try:
            device.disconnect()
        except Exception:
            pass


class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def load_inputs(
        self,
        testbed,
        handoff_file: str,
        max_workers: int = 5,
        reload_timeout: int = 1200,
        reconnect_timeout: int = 900,
        reconnect_interval: int = 20,
    ):
        self.parent.parameters["testbed"] = testbed
        self.parent.parameters["handoff_file"] = handoff_file
        self.parent.parameters["max_workers"] = int(max_workers)
        self.parent.parameters["reload_timeout"] = int(reload_timeout)
        self.parent.parameters["reconnect_timeout"] = int(reconnect_timeout)
        self.parent.parameters["reconnect_interval"] = int(reconnect_interval)

    @aetest.subsection
    def read_handoff(self):
        handoff_path = Path(self.parent.parameters["handoff_file"]).resolve()
        handoff = json.loads(handoff_path.read_text(encoding="utf-8"))

        self.parent.parameters["handoff_path"] = handoff_path
        self.parent.parameters["handoff"] = handoff

        out_dir = handoff_path.parent / "stage2_pyats"
        out_dir.mkdir(parents=True, exist_ok=True)
        self.parent.parameters["out_dir"] = out_dir

        # Directly go to ready_for_reload (no not_ready checks)
        ready_list = handoff.get("ready_for_reload", []) or []
        self.parent.parameters["ready_list"] = ready_list

        image = handoff.get("image", {}) or {}
        expected_filename = (image.get("filename") or "").strip()
        if not expected_filename:
            self.failed(f"handoff.image.filename is missing. Check: {handoff_path}", goto=["exit"])
        self.parent.parameters["expected_filename"] = expected_filename

        # device_state only for devices existing in testbed (ignore missing)
        tb = self.parent.parameters["testbed"]
        device_state: Dict[str, Dict[str, Any]] = {}

        for entry in ready_list:
            name = (entry or {}).get("inventory_hostname")
            if not name:
                continue
            if name not in tb.devices:
                continue
            device_state[name] = {
                "status": True,
                "reason": "",
                "pre_system_image": None,
                "post_system_image": None,
            }

        self.parent.parameters["device_state"] = device_state


class Stage2ReloadVerify(aetest.Testcase):

    @aetest.setup
    def setup(self):
        self.tb = self.parent.parameters["testbed"]
        self.out_dir: Path = self.parent.parameters["out_dir"]
        self.ready_list = self.parent.parameters.get("ready_list", [])
        self.expected_filename: str = self.parent.parameters["expected_filename"]

        self.max_workers: int = self.parent.parameters["max_workers"]
        self.reload_timeout: int = self.parent.parameters["reload_timeout"]
        self.reconnect_timeout: int = self.parent.parameters["reconnect_timeout"]
        self.reconnect_interval: int = self.parent.parameters["reconnect_interval"]

        self.device_state: Dict[str, Dict[str, Any]] = self.parent.parameters.get("device_state", {})

    @aetest.test
    def pre_stage_parallel(self):
        if not self.device_state:
            return

        devices = [self.tb.devices[name] for name in self.device_state.keys()]

        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(connect_parse_show_version, dev): dev.name for dev in devices}
            for fut in as_completed(futures):
                name = futures[fut]
                ok, payload = fut.result()

                if ok:
                    self.device_state[name]["pre_system_image"] = payload["system_image"]
                    self.device_state[name]["status"] = True
                else:
                    self.device_state[name]["status"] = False
                    self.device_state[name]["reason"] = f"PRE failed: {payload.get('error', '')}"

    @aetest.test
    def reload_serial(self):
        dialog = build_reload_dialog()

        for entry in self.ready_list:
            name = (entry or {}).get("inventory_hostname")
            if not name or name not in self.device_state:
                continue

            # ONLY condition: status must be True
            if self.device_state[name]["status"] is not True:
                continue

            device = self.tb.devices[name]
            try:
                device.connect(
                    log_stdout=False,
                    init_exec_commands=[],
                    init_config_commands=[],
                )

                device.reload(timeout=self.reload_timeout, dialog=dialog)

                deadline = time.time() + self.reconnect_timeout
                last_err = None
                connected = False

                while time.time() < deadline:
                    try:
                        if device.is_connected():
                            connected = True
                            break
                        device.connect(
                            log_stdout=False,
                            init_exec_commands=[],
                            init_config_commands=[],
                        )
                        connected = True
                        break
                    except Exception as e:
                        last_err = e
                        time.sleep(self.reconnect_interval)

                if not connected:
                    self.device_state[name]["status"] = False
                    self.device_state[name]["reason"] = "RELOAD failed: device did not reconnect after reload"
                    continue

            except Exception as e:
                self.device_state[name]["status"] = False
                self.device_state[name]["reason"] = f"RELOAD failed: {str(e)}"
            
            finally:
                try:
                    device.disconnect()
                except Exception:
                    pass

    @aetest.test
    def post_stage_parallel(self):
        eligible_names = [n for n, st in self.device_state.items() if st.get("status") is True]
        if not eligible_names:
            return

        devices = [self.tb.devices[name] for name in eligible_names]

        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(connect_parse_show_version, dev): dev.name for dev in devices}
            for fut in as_completed(futures):
                name = futures[fut]
                ok, payload = fut.result()

                if not ok:
                    self.device_state[name]["status"] = False
                    self.device_state[name]["reason"] = f"POST failed: {payload.get('error', '')}"
                    continue

                post_img = payload["system_image"]
                self.device_state[name]["post_system_image"] = post_img

                post_ok = (self.expected_filename in (post_img or ""))
                if post_ok:
                    self.device_state[name]["status"] = True
                else:
                    self.device_state[name]["status"] = False
                    self.device_state[name]["reason"] = "FINAL failed: expected image filename not found in post_system_image"

    @aetest.test
    def write_summary(self):
        summary_path = self.out_dir / "stage2_summary.json"
        write_json(summary_path, self.device_state)


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def cleanup(self):
        pass
