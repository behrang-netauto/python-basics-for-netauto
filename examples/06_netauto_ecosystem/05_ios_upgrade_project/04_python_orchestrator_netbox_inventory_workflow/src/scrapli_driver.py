
from __future__ import annotations

import re
from typing import Any, Dict, List

from scrapli import Scrapli
"""
connect / disconnect / send_command / send_config / get_privilege_level / get_free_space_bytes / 
get_running_config / verify_md5 / boot_prep / get_system_image / reload
"""

class ScrapliDriver:
    _SCRAPLI_OS_MAP = {
        "iosxe": "cisco_iosxe",
        "ios": "cisco_ios",
        "nxos": "cisco_nxos",
        "iosxr": "cisco_iosxr",
    }

    @staticmethod
    def _to_scrapli_platform(device: Dict[str, Any]) -> str:
        os_name = str(device.get("os", "")).strip().lower()
        platform = str(device.get("platform", "")).strip().lower()

        # primary mapping: os -> scrapli platform
        if os_name in ScrapliDriver._SCRAPLI_OS_MAP:
            return ScrapliDriver._SCRAPLI_OS_MAP[os_name]

        raise ValueError(
            f"Cannot map to scrapli platform from os={os_name!r}, platform={platform!r}"
        )

    @staticmethod
    def _build_connect_params(device: Dict[str, Any], creds: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        return {
            "host": device["host"],
            "port": int(device.get("port", 22)),
            "auth_username": creds["username"],
            "auth_password": creds["password"],
            "auth_secondary": creds.get("secret", ""),
            "auth_strict_key": False,
            "platform": ScrapliDriver._to_scrapli_platform(device),
            "timeout_socket": timeout,
            "timeout_transport": timeout,
            "timeout_ops": timeout,
        }

    def connect(self, device: Dict[str, Any], creds: Dict[str, Any], timeout: int):
        params = ScrapliDriver._build_connect_params(device, creds, timeout)
        conn = Scrapli(**params)
        conn.open()
        return conn

    def disconnect(self, handle) -> None:
        handle.close()

    def send_command(self, handle, command: str, timeout: int) -> str:
        r = handle.send_command(command, timeout_ops=timeout)
        return r.result

    def send_config(self, handle, commands: List[str], timeout: int) -> str:
        r = handle.send_configs(commands, timeout_ops=timeout)
        return r.result

    def get_privilege_level(self, handle, timeout: int) -> int:
        out = self.send_command(handle, "show privilege", timeout=timeout)
        m = re.search(r"privilege level is\s+(\d+)", out, re.IGNORECASE)
        if not m:
            raise ValueError(f"Could not parse privilege level from output: {out!r}")
        return int(m.group(1))

    def get_free_space_bytes(self, handle, remote_fs: str, timeout: int) -> int:
        out = self.send_command(handle, f"dir {remote_fs}", timeout=timeout)
        m = re.search(r"(\d+)\s+bytes free", out, re.IGNORECASE)
        if not m:
            raise ValueError(f"Could not parse free bytes from dir output: {out!r}")
        return int(m.group(1))

    def get_running_config(self, handle, timeout: int) -> str:
        return self.send_command(handle, "show running-config", timeout=timeout)

    # --- Common ops used by Stage1/Stage2 ---
    def verify_md5(self, handle, remote_path: str, timeout: int) -> str:
        out = self.send_command(handle, f"verify /md5 {remote_path}", timeout=timeout)
        m = re.search(r"=\s*([a-fA-F0-9]{32})", out)
        if not m:
            m = re.search(r"\b([a-fA-F0-9]{32})\b", out)
        if not m:
            raise ValueError(f"Could not parse md5 from verify output: {out!r}")
        return m.group(1).lower()

    def boot_prep(self, handle, new_image_remote_path: str, timeout: int) -> None:
        out = self.send_command(handle, r"show running-config | include ^boot system", timeout=timeout)
        existing = []
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("boot system"):
                existing.append(line)

        fallback_lines = []
        for line in existing:
            m = re.search(r"(\S+:\S+)\s*$", line)
            if m:
                fallback_lines.append(m.group(1))

        cmds = ["no boot system", f"boot system {new_image_remote_path}"]
        if fallback_lines:
            fb = fallback_lines[0]
            if fb != new_image_remote_path:
                cmds.append(f"boot system {fb}")

        self.send_config(handle, cmds, timeout=timeout)
        self.send_command(handle, "write memory", timeout=timeout)

    def get_system_image(self, handle, timeout: int) -> str:
        out = self.send_command(handle, "show version", timeout=timeout)
        m = re.search(r'System image file is\s+"([^"]+)"', out)
        if not m:
            m = re.search(r"System image file is\s+(\S+)", out)
        if not m:
            raise ValueError(f"Could not parse system image from show version output: {out!r}")
        return m.group(1).strip()

    def reload(self, handle, timeout: int) -> None:
        # Minimal interactive reload using send_interactive
        interactions = [
            ("reload", r"\[yes/no\]|\[confirm\]|Proceed with reload", False),
            ("no", r"\[confirm\]|Proceed with reload", False),
            ("", r".*", False),  # Enter to confirm if asked
        ]
        try:
            handle.send_interactive(interactions, timeout_ops=timeout)
        except Exception:
            # After confirming reload, session may drop -> acceptable
            return