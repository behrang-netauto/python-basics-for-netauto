
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


class NetBoxAPIError(RuntimeError):
    """Raised when a NetBox API request fails."""


@dataclass(frozen=True)
class NetBoxClientConfig:
    base_url: str
    token: str
    verify_ssl: bool = True
    timeout: int = 20


class NetBoxClient:
    """
    Minimal NetBox REST client for v1 integration.

    Responsibilities:
    - build a stable api_root from base_url
    - use NetBox v2 token authentication
    - keep a shared requests session
    - send requests and parse JSON
    - fail fast on HTTP/API errors
    - provide minimal device read methods
    - provide minimal device custom-field write-back methods

    Non-goals:
    - business filtering
    - orchestrator shaping
    - device-id caching
    """

    DEVICES_PATH = "/dcim/devices/"
    INTERFACES_PATH = "/dcim/interfaces/"
    IP_ADDRESSES_PATH = "/ipam/ip-addresses/"

    def __init__(self, config: NetBoxClientConfig) -> None:
        self.config = config

        # Build api_root inline, per latest agreement.
        cleaned = config.base_url.strip().rstrip("/")
        if cleaned.endswith("/api"):
            self.api_root = cleaned
        else:
            self.api_root = f"{cleaned}/api"

        # v2-only token policy.
        token = config.token.strip()
        if not token.startswith("nbt_"):
            raise ValueError("Expected a NetBox v2 token starting with 'nbt_'")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        self.session.verify = config.verify_ssl

    def _build_url(self, path: str) -> str:
        normalized = path.strip()
        if not normalized.startswith("/"):
            normalized = f"/{normalized}"
        return f"{self.api_root}{normalized}"

    def _request(
        self,
        method: str,
        *,
        path: Optional[str] = None,
        url: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute one HTTP request.

        Exactly one of `path` or `url` must be provided:
        - use `path` for normal API paths like /dcim/devices/
        - use `url` for absolute pagination URLs returned by NetBox
        """
        if (path is None and url is None) or (path is not None and url is not None):
            raise ValueError("Exactly one of 'path' or 'url' must be provided")

        target_url = url if url is not None else self._build_url(path)

        try:
            response = self.session.request(
                method=method,
                url=target_url,
                params=params,
                json=json_body,
                timeout=self.config.timeout,
            )
        except requests.RequestException as exc:
            raise NetBoxAPIError(
                f"NetBox request failed: {method} {target_url}: {exc}"
            ) from exc

        if not response.ok:
            body_preview = response.text[:500]
            raise NetBoxAPIError(
                f"NetBox returned {response.status_code} for {method} {target_url}: "
                f"{body_preview}"
            )

        if response.status_code == 204:
            return None

        try:
            return response.json()
        except ValueError as exc:
            raise NetBoxAPIError(
                f"NetBox returned non-JSON content for {method} {target_url}"
            ) from exc

    def _get_paginated(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Read all pages from a paginated NetBox list endpoint.
        """
        first_page = self._request("GET", path=path, params=params)

        if not isinstance(first_page, dict) or "results" not in first_page:
            raise NetBoxAPIError(f"Unexpected paginated response shape for GET {path}")

        results: List[Dict[str, Any]] = list(first_page.get("results", []))
        next_url = first_page.get("next")

        while next_url:
            page = self._request("GET", url=next_url)

            if not isinstance(page, dict) or "results" not in page:
                raise NetBoxAPIError(
                    f"Unexpected paginated response shape for {next_url}"
                )

            results.extend(page.get("results", []))
            next_url = page.get("next")

        return results

    def list_devices(
        self,
        *,
        site: Optional[str] = None,
        status: Optional[str] = "active",
        name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Read devices from NetBox with basic server-side filters.

        Returns:
            A list of NetBox-shaped device objects.

            [
    {
        "id": 1,
        "name": "R1",
        "platform": {"slug": "iosxe", ...},
        "device_type": {"model": "Cisco Catalyst 8000V", ...},
        "primary_ip4": {"address": "192.168.56.20/24", ...},
        "custom_fields": {
            "upgrade_candidate": True,
            "transfer_method": "scp",
            "stage2_result": "passed",
            ...
        },
        ...
    }
]
        """
        params: Dict[str, Any] = {}

        if site:
            params["site"] = site
        if status:
            params["status"] = status
        if name:
            params["name"] = name

        return self._get_paginated(self.DEVICES_PATH, params=params)

    def patch_device_custom_fields(
        self,
        device_id: int,
        custom_fields: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Patch custom_fields on one device.

        Caller must provide a valid NetBox device_id.
        """
        if not isinstance(device_id, int):
            raise ValueError("device_id must be an integer")
        if not custom_fields:
            raise ValueError("custom_fields must not be empty")

        payload = {"custom_fields": custom_fields}
        result = self._request(
            "PATCH",
            path=f"{self.DEVICES_PATH}{device_id}/",
            json_body=payload,
        )

        if not isinstance(result, dict):
            raise NetBoxAPIError(
                f"Unexpected PATCH response shape for device_id={device_id}"
            )

        return result

    def write_precheck_status(self, device_id: int, status: str) -> Dict[str, Any]:
        """
        Write back precheck_status for one device.

        Note:
            Allowed values are enforced outside the client.
        """
        return self.patch_device_custom_fields(
            device_id=device_id,
            custom_fields={"precheck_status": status},
        )

    def write_backup_metadata(
        self,
        device_id: int,
        backup_path: str,
        backup_timestamp: str,
    ) -> Dict[str, Any]:
        """
        Write back backup metadata for one device.
        """
        return self.patch_device_custom_fields(
            device_id=device_id,
            custom_fields={
                "backup_path": backup_path,
                "backup_timestamp": backup_timestamp,
            },
        )

    def write_stage2_result(self, device_id: int, stage2_result: str) -> Dict[str, Any]:
        """
        Write back final Stage 2 result for one device.
        Allowed values are enforced outside the client.
        """
        return self.patch_device_custom_fields(
            device_id=device_id,
            custom_fields={"stage2_result": stage2_result},
        )

    def __enter__(self) -> "NetBoxClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self) -> None:
        self.session.close()