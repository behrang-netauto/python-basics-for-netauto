
from __future__ import annotations

from src.netbox_client import NetBoxClient, NetBoxClientConfig
from src.netbox_inventory_provider import (
    NetBoxInventoryProvider,
    NetBoxInventoryProviderConfig,
)
from src.yaml_inventory_provider import (
    YamlInventoryProvider,
    YamlInventoryProviderConfig,
)


class InventoryProviderFactoryError(RuntimeError):
    """Raised when inventory provider construction fails."""


def build_inventory_provider(ctx):
    """
    Build the inventory provider from explicit source selection.

    Expected ctx fields (v1):

    ctx.inventory.source: "yaml" | "netbox"

    If source == "yaml":
      ctx.inventory.inventory_path
      ctx.inventory.default_port (optional)
      ctx.inventory.default_upgrade_candidate (optional)
      ctx.inventory.default_transfer_method (optional)

    If source == "netbox":
      ctx.netbox.base_url
      ctx.netbox.token
      ctx.netbox.verify_ssl (optional)
      ctx.netbox.timeout (optional)
      ctx.inventory.site
      ctx.inventory.status (optional)
      ctx.inventory.default_port (optional)
    """
    source = str(ctx.inventory.get("source", "")).strip().lower()

    if source == "yaml":
        provider_cfg = YamlInventoryProviderConfig(
            inventory_path=ctx.inventory["inventory_path"],
            default_port=ctx.inventory.get("default_port", 22),
            default_upgrade_candidate=ctx.inventory.get(
                "default_upgrade_candidate", False
            ),
            default_transfer_method=ctx.inventory.get(
                "default_transfer_method", None
            ),
        )
        return YamlInventoryProvider(provider_cfg)

    if source == "netbox":
        client_cfg = NetBoxClientConfig(
            base_url=ctx.netbox["base_url"],
            token=ctx.netbox["token"],
            verify_ssl=ctx.netbox.get("verify_ssl", True),
            timeout=ctx.netbox.get("timeout", 20),
        )
        client = NetBoxClient(client_cfg)

        provider_cfg = NetBoxInventoryProviderConfig(
            site=ctx.inventory["site"],
            status=ctx.inventory.get("status", "active"),
            default_port=ctx.inventory.get("default_port", 22),
        )
        return NetBoxInventoryProvider(client=client, config=provider_cfg)

    raise InventoryProviderFactoryError(
        f"Unsupported inventory source: {source}"
    )