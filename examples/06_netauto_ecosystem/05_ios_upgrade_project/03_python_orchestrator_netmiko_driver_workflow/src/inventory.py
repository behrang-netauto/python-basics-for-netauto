from __future__ import annotations

from typing import Any, Dict, List


def normalize_devices_from_inventory(inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
    """{
  "inventory_hostname": "R1",
  "host": "192.168.56.20",
  "port": 22,
  "device_type": "cisco_xe"
    }"""
    devices = inventory.get("devices", {})
    if not isinstance(devices, dict) or not devices:
        raise ValueError("inventory.yml must contain top-level key 'devices' with at least one device")

    out: List[Dict[str, Any]] = []
    for name, spec in devices.items():
        try:
            ssh = spec["connections"]["ssh"]
            host = ssh["ip"]
            port = ssh.get("port", 22)
            device_type = spec["netmiko"]["device_type"]
        except Exception as e:
            raise ValueError(f"Invalid device entry for '{name}': {e}")

        out.append({
            "inventory_hostname": name,
            "host": host,
            "port": int(port),
            "device_type": device_type,
        })
    return out
