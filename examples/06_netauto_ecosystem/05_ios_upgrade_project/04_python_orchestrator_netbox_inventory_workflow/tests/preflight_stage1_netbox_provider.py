
from src.ctx import build_ctx
from src.inventory_provider_factory import build_inventory_provider


def main() -> None:
    ctx = build_ctx(
        run_id="preflight_netbox_provider",
        config_path="config.yml",
        vault_path="vault.yml",
    )

    provider = build_inventory_provider(ctx)
    try:
        devices = provider.load_devices()

        print(f"inventory_source={ctx.inventory['source']}")
        print(f"device_count={len(devices)}")

        if devices:
            print("first_device=", devices[0])

        print("R1 device_id =", provider.get_device_id_by_name("R1"))
    finally:
        close_fn = getattr(provider, "close", None)
        if callable(close_fn):
            close_fn()


if __name__ == "__main__":
    main()