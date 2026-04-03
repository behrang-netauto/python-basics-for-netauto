from __future__ import annotations

import re
from typing import Any, Dict, List

from netmiko import ConnectHandler

"""
connect / send_command / send_config / get_privilege_level / get_free_space_bytes / 
get_running_config / is_scp_enabled / set_scp_enabled / verify_md5 / boot_prep / reload
"""
class NetmikoDriver:

    _NETMIKO_OS_MAP = {
        "iosxe": "cisco_xe",
        "ios": "cisco_ios",
        "nxos": "cisco_nxos",
        "iosxr": "cisco_xr",
    }
    
    @staticmethod
    def _to_netmiko_device_type(device: Dict[str, Any]) -> str:
        os_name = str(device.get("os", "")).strip().lower()
        platform = str(device.get("platform", "")).strip().lower()

        if os_name in NetmikoDriver._NETMIKO_OS_MAP:
            return NetmikoDriver._NETMIKO_OS_MAP[os_name]

        raise ValueError(
            f"Cannot map to netmiko device_type from os={os_name!r}, platform={platform!r}"
        )
    
    @staticmethod
    def _build_connect_params(device: Dict[str, Any], creds: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        return {
            "device_type": NetmikoDriver._to_netmiko_device_type(device),
            "host": device["host"],
            "port": int(device.get("port", 22)),
            "username": creds["username"],
            "password": creds["password"],
            "secret": creds.get("secret", ""),
            "timeout": timeout,
            "conn_timeout": timeout,
            "banner_timeout": timeout,
            "auth_timeout": timeout,
        }

    def connect(self, device: Dict[str, Any], creds: Dict[str, Any], timeout: int):
        params = NetmikoDriver._build_connect_params(device, creds, timeout)
        handle = ConnectHandler(**params)
        # If enable secret is provided, try enable mode
        secret = creds.get("secret")
        if secret:
            try:
                handle.enable()
            except Exception:
                # If enable fails, privilege check later will catch it
                pass
        return handle

    def disconnect(self, handle) -> None:
        handle.disconnect()

    def send_command(self, handle, command: str, timeout: int) -> str:
        return handle.send_command(command, read_timeout=timeout)

    def send_config(self, handle, commands: List[str], timeout: int) -> str:
        return handle.send_config_set(commands, read_timeout=timeout)

    def get_privilege_level(self, handle, timeout: int) -> int:
        out = self.send_command(handle, "show privilege", timeout=timeout)
        m = re.search(r"privilege level is\s+(\d+)", out, re.IGNORECASE)
        if not m:
            raise ValueError(f"Could not parse privilege level from output: {out!r}")
        return int(m.group(1))

    def get_free_space_bytes(self, handle, remote_fs: str, timeout: int) -> int:
        # IOS-XE usually: "xxxx bytes total (yyyy bytes free)"
        out = self.send_command(handle, f"dir {remote_fs}", timeout=timeout)
        m = re.search(r"(\d+)\s+bytes free", out, re.IGNORECASE)
        if not m:
            raise ValueError(f"Could not parse free bytes from dir output: {out!r}")
        return int(m.group(1))

    def get_running_config(self, handle, timeout: int) -> str:
        return self.send_command(handle, "show running-config", timeout=timeout)

    def is_scp_enabled(self, handle, timeout: int) -> bool:
        out = self.send_command(handle, r"show running-config | include ^ip scp server enable", timeout=timeout)
        return "ip scp server enable" in out

    def set_scp_enabled(self, handle, enable: bool, timeout: int) -> None:
        cmd = "ip scp server enable" if enable else "no ip scp server enable"
        self.send_config(handle, [cmd], timeout=timeout)

    def verify_md5(self, handle, remote_path: str, timeout: int) -> str:
        out = self.send_command(handle, f"verify /md5 {remote_path}", timeout=timeout)
        m = re.search(r"=\s*([a-fA-F0-9]{32})", out)
        if not m:
            m = re.search(r"\b([a-fA-F0-9]{32})\b", out)
        if not m:
            raise ValueError(f"Could not parse md5 from verify output: {out!r}")
        return m.group(1).lower()

    def boot_prep(self, handle, new_image_remote_path: str, timeout: int) -> None:
        # Read existing boot system lines as fallback
        out = self.send_command(handle, r"show running-config | include ^boot system", timeout=timeout)
        existing = []
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("boot system"):
                existing.append(line)

        # Extract existing image paths (very basic; keep the line)
        fallback_lines = []
        for line in existing:
            # Keep only file paths that look like <fs>:/something
            m = re.search(r"(\S+:\S+)\s*$", line)
            if m:
                fallback_lines.append(m.group(1))

        cmds = ["no boot system"]
        cmds.append(f"boot system {new_image_remote_path}")

        # Add first fallback path if present and different
        if fallback_lines:
            fb = fallback_lines[0]
            if fb != new_image_remote_path:
                cmds.append(f"boot system {fb}")

        self.send_config(handle, cmds, timeout=timeout)
        self.send_command(handle, "write memory", timeout=timeout)

    def get_system_image(self, handle, timeout: int) -> str:
        out = self.send_command(handle, "show version", timeout=timeout)
        # IOS-XE common: System image file is "bootflash:packages.conf"
        m = re.search(r'System image file is\s+"([^"]+)"', out)
        if not m:
            # fallback: without quotes
            m = re.search(r"System image file is\s+(\S+)", out)
        if not m:
            raise ValueError(f"Could not parse system image from show version output: {out!r}")
        return m.group(1).strip()
    
    def reload(self, handle, timeout: int) -> None:
        out = handle.send_command_timing("reload")
        
        if re.search(r"\[yes/no\]", out, re.IGNORECASE) or re.search(r"System configuration has been modified", out, re.IGNORECASE):
            out = handle.send_command_timing("no")

        if re.search(r"\[confirm\]", out, re.IGNORECASE) or re.search(r"Proceed with reload", out, re.IGNORECASE):
            handle.send_command_timing("")
        return