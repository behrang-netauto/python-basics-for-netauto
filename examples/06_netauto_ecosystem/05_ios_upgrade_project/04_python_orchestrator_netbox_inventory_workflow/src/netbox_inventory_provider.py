
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from src.netbox_client import NetBoxClient


class NetBoxInventoryError(RuntimeError):
    """Raised when NetBox inventory data is invalid for orchestrator use."""


@dataclass(frozen=True)
class NetBoxInventoryProviderConfig:
    site: str
    status: str = "active"
    default_port: int = 22


class NetBoxInventoryProvider:
    """
    Build orchestrator-ready inventory from NetBox device objects.

    Responsibilities:
    - read devices through netbox_client
    - enforce upgrade_candidate=true
    - validate required fields for selected devices
    - strip CIDR from primary_ip4.address
    - expose name -> device_id map for same-run write-back
    - shape device records for orchestrator consumption

        {
    "inventory_hostname": "R1",
    "host": "192.168.56.20",
    "port": 22,
    "os": "iosxe",
    "platform": "iosxe",
    "device_type": "Cisco Catalyst 8000V",
    "upgrade_candidate": True,
    "transfer_method": "scp",
            }
    """

    def __init__(
        self,
        client: NetBoxClient,
        config: NetBoxInventoryProviderConfig,
    ) -> None:
        self.client = client
        self.config = config
        self._name_to_device_id: Dict[str, int] = {}

    def load_devices(self) -> List[Dict[str, Any]]:
        raw_devices = self.client.list_devices(
            site=self.config.site,
            status=self.config.status,
        )

        self._build_name_to_id_map(raw_devices)

        selected_devices = [
            device for device in raw_devices
            if self._is_upgrade_candidate(device)
        ]

        normalized: List[Dict[str, Any]] = []
        for device in selected_devices:
            self._validate_selected_device(device)
            normalized.append(self._normalize_device(device))

        return normalized

    def get_device_id_by_name(self, name: str) -> int | None:
        return self._name_to_device_id.get(name)
    
    def close(self) -> None:
        """Delegate cleanup to the underlying NetBoxClient."""
        self.client.close()

    def _build_name_to_id_map(self, raw_devices: List[Dict[str, Any]]) -> None:
        mapping: Dict[str, int] = {}

        for device in raw_devices:
            device_name = device.get("name")
            device_id = device.get("id")

            if isinstance(device_name, str) and isinstance(device_id, int):
                mapping[device_name] = device_id

        self._name_to_device_id = mapping

    def _is_upgrade_candidate(self, device: Dict[str, Any]) -> bool:
        custom_fields = device.get("custom_fields") or {}
        return custom_fields.get("upgrade_candidate") is True

    def _validate_selected_device(self, device: Dict[str, Any]) -> None:
        name = device.get("name")
        device_id = device.get("id")
        platform = device.get("platform") or {}
        device_type = device.get("device_type") or {}
        primary_ip4 = device.get("primary_ip4") or {}
        custom_fields = device.get("custom_fields") or {}

        errors: List[str] = []

        if not isinstance(name, str) or not name.strip():
            errors.append("missing device.name")

        if not isinstance(device_id, int):
            errors.append("missing device.id")

        if not isinstance(platform.get("slug"), str) or not platform.get("slug"):
            errors.append("missing device.platform.slug")

        if not isinstance(device_type.get("model"), str) or not device_type.get("model"):
            errors.append("missing device.device_type.model")

        if not isinstance(primary_ip4.get("address"), str) or not primary_ip4.get("address"):
            errors.append("missing device.primary_ip4.address")

        transfer_method = custom_fields.get("transfer_method")
        if not isinstance(transfer_method, str) or not transfer_method.strip():
            errors.append("missing custom_fields.transfer_method")

        if errors:
            label = name if isinstance(name, str) and name else "<unknown>"
            raise NetBoxInventoryError(
                f"Selected device {label} failed validation: {', '.join(errors)}"
            )

    def _normalize_device(self, device: Dict[str, Any]) -> Dict[str, Any]:
        platform = device.get("platform") or {}
        device_type = device.get("device_type") or {}
        primary_ip4 = device.get("primary_ip4") or {}
        custom_fields = device.get("custom_fields") or {}

        return {
            "inventory_hostname": device["name"],
            "host": self._strip_cidr(primary_ip4["address"]),
            "port": self.config.default_port,
            "os": platform["slug"],
            "platform": platform["slug"],
            "device_type": device_type["model"],
            "upgrade_candidate": True,
            "transfer_method": custom_fields["transfer_method"],
        }

    @staticmethod
    def _strip_cidr(address: str) -> str:
        return address.split("/", 1)[0]