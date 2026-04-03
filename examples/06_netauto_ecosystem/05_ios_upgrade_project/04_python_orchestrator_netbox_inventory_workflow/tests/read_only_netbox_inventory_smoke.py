# This is a simple smoke test to verify that we can connect to NetBox and read inventory data.
# for running this test, in root of this project, run:
# python -m tests.read_only_netbox_inventory_smoke
from pathlib import Path
import yaml

from src.netbox_client import NetBoxClient, NetBoxClientConfig
from src.netbox_inventory_provider import (
    NetBoxInventoryProvider,
    NetBoxInventoryProviderConfig,
)

def load_yaml_file(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    config_data = load_yaml_file(project_root / "config.yml")
    vault_data = load_yaml_file(project_root / "vault.yml")

    client_cfg = NetBoxClientConfig(
        base_url=config_data["netbox"]["base_url"],
        token=vault_data["netbox"]["token"],
        verify_ssl=config_data["netbox"].get("verify_ssl", True),
        timeout=config_data["netbox"].get("timeout", 20),
    )

    provider_cfg = NetBoxInventoryProviderConfig(
        site=config_data["inventory"]["site"],
        status=config_data["inventory"].get("status", "active"),
        default_port=config_data["inventory"].get("default_port", 22),
    )

    with NetBoxClient(client_cfg) as client:
        provider = NetBoxInventoryProvider(client=client, config=provider_cfg)

        devices = provider.load_devices()

        print(f"device_count={len(devices)}")
        for item in devices:
            print(item)

        print("R1 device_id =", provider.get_device_id_by_name("R1"))

if __name__ == "__main__":
    main()
