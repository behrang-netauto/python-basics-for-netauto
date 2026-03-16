from __future__ import annotations

from typing import Any, Dict, List


def normalize_devices_from_inventory(inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalized driver-agnostic device contract:
    {
        "inventory_hostname": "R1",
        "host": "192.168.56.20",
        "port": 22,
        "os": "iosxe",
        "platform": "cat8k",
    }
    """
    devices = inventory.get("devices", {})
    if not isinstance(devices, dict) or not devices:
        raise ValueError("inventory.yml must contain top-level key 'devices' with at least one device")

    out: List[Dict[str, Any]] = []
    for name, spec in devices.items():
        try:
            ssh = spec["connections"]["ssh"]
            host = ssh["ip"]
            port = int(ssh.get("port", 22))

            alias = str(spec.get("alias", name)).strip()
            os_name = str(spec["os"]).strip().lower()
            platform = str(spec["platform"]).strip().lower()
        except Exception as e:
            raise ValueError(f"Invalid device entry for '{name}': {e}")

        if not os_name:
            raise ValueError(f"Invalid device entry for '{name}': os must be non-empty")
        if not platform:
            raise ValueError(f"Invalid device entry for '{name}': platform must be non-empty")

        out.append(
            {
                "inventory_hostname": name,
                "alias": alias,
                "host": host,
                "port": port,
                "os": os_name,
                "platform": platform,
            }
        )
    return out
