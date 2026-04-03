
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class YamlInventoryError(RuntimeError):
    """Raised when YAML inventory data is invalid."""


@dataclass(frozen=True)
class YamlInventoryProviderConfig:
    inventory_path: str
    default_port: int = 22
    default_upgrade_candidate: bool = False
    default_transfer_method: Optional[str] = None


class YamlInventoryProvider:
    """
    Read device inventory from a YAML file and normalize it to the
    orchestrator-ready shape.

    Expected source structure (minimum):
    devices:
      R1:
        os: iosxe
        platform: cat8k
        device_type: cat8k
        connections:
          ssh:
            ip: 192.168.56.20
            port: 22
        upgrade_candidate: true
        transfer_method: scp

    Notes:
    - `device_type` may be provided directly.
    - If `device_type` is missing, we fall back to `platform`.
    - YAML source does not have NetBox device IDs, so
      get_device_id_by_name(...) always returns None.
    """

    def __init__(self, config: YamlInventoryProviderConfig) -> None:
        self.config = config
        self.inventory_path = Path(config.inventory_path)

    def load_devices(self) -> List[Dict[str, Any]]:
        data = self._read_yaml_file()

        devices = data.get("devices")
        if not isinstance(devices, dict):
            raise YamlInventoryError("YAML inventory must contain a top-level 'devices' mapping")

        normalized: List[Dict[str, Any]] = []
        for inventory_hostname, device_data in devices.items():
            if not isinstance(device_data, dict):
                raise YamlInventoryError(
                    f"Device entry for {inventory_hostname!r} must be a mapping"
                )

            normalized.append(
                self._normalize_device(
                    inventory_hostname=inventory_hostname,
                    device_data=device_data,
                )
            )

        return normalized

    def get_device_id_by_name(self, name: str) -> int | None:
        """
        YAML inventory has no NetBox device IDs.
        """
        return None
    
    def close(self) -> None:
        """
        No-op for YAML provider.
        Exists only so Stage 1 can call provider.close() uniformly.
        """
        return None

    def _read_yaml_file(self) -> Dict[str, Any]:
        if not self.inventory_path.exists():
            raise YamlInventoryError(
                f"YAML inventory file does not exist: {self.inventory_path}"
            )

        try:
            with self.inventory_path.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        except OSError as exc:
            raise YamlInventoryError(
                f"Failed to read YAML inventory file: {self.inventory_path}: {exc}"
            ) from exc
        except yaml.YAMLError as exc:
            raise YamlInventoryError(
                f"Failed to parse YAML inventory file: {self.inventory_path}: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise YamlInventoryError("YAML inventory root must be a mapping")

        return data

    def _normalize_device(
        self,
        *,
        inventory_hostname: str,
        device_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        ssh = self._extract_ssh_mapping(device_data)
        host = ssh.get("ip")
        port = ssh.get("port", self.config.default_port)

        os_value = device_data.get("os")
        platform = device_data.get("platform")
        device_type = device_data.get("device_type") or platform

        upgrade_candidate = self._extract_upgrade_candidate(device_data)
        transfer_method = self._extract_transfer_method(device_data)

        errors: List[str] = []

        if not isinstance(inventory_hostname, str) or not inventory_hostname.strip():
            errors.append("missing inventory hostname")

        if not isinstance(host, str) or not host.strip():
            errors.append("missing connections.ssh.ip")

        if not isinstance(port, int):
            errors.append("invalid connections.ssh.port")

        if not isinstance(os_value, str) or not os_value.strip():
            errors.append("missing os")

        if not isinstance(device_type, str) or not device_type.strip():
            errors.append("missing device_type/platform")

        if upgrade_candidate is True:
            if not isinstance(transfer_method, str) or not transfer_method.strip():
                errors.append("missing transfer_method for selected device")

        if errors:
            raise YamlInventoryError(
                f"Device {inventory_hostname} failed validation: {', '.join(errors)}"
            )

        return {
            "inventory_hostname": inventory_hostname,
            "host": host,
            "port": port,
            "os": os_value,
            "platform": platform,
            "device_type": device_type,
            "upgrade_candidate": bool(upgrade_candidate),
            "transfer_method": transfer_method,
        }

    def _extract_ssh_mapping(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        connections = device_data.get("connections") or {}
        if not isinstance(connections, dict):
            return {}
        ssh = connections.get("ssh") or {}
        if not isinstance(ssh, dict):
            return {}
        return ssh

    def _extract_upgrade_candidate(self, device_data: Dict[str, Any]) -> bool:
        custom_fields = device_data.get("custom_fields") or {}
        if not isinstance(custom_fields, dict):
            custom_fields = {}

        if "upgrade_candidate" in device_data:
            return bool(device_data["upgrade_candidate"])

        if "upgrade_candidate" in custom_fields:
            return bool(custom_fields["upgrade_candidate"])

        return self.config.default_upgrade_candidate

    def _extract_transfer_method(self, device_data: Dict[str, Any]) -> Optional[str]:
        custom_fields = device_data.get("custom_fields") or {}
        if not isinstance(custom_fields, dict):
            custom_fields = {}

        if "transfer_method" in device_data:
            value = device_data["transfer_method"]
            return value if isinstance(value, str) else None

        if "transfer_method" in custom_fields:
            value = custom_fields["transfer_method"]
            return value if isinstance(value, str) else None

        return self.config.default_transfer_method