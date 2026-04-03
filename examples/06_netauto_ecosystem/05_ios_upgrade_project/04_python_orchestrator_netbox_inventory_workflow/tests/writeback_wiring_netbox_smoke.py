
from src.ctx import build_ctx
from src.inventory_provider_factory import build_inventory_provider
from src.stage1_orchestrator import _writeback_v1_best_effort


def main() -> None:
    ctx = build_ctx(
        run_id="writeback_wiring_smoke",
        config_path="config.yml",
        vault_path="vault.yml",
    )

    provider = build_inventory_provider(ctx)
    try:
        devices = provider.load_devices()
        print(f"loaded_devices={len(devices)}")

        target_name = "R1"
        device_id = provider.get_device_id_by_name(target_name)
        print(f"{target_name} device_id={device_id}")

        device_state = {
            "inventory_hostname": target_name,
            "warnings": [],
            "precheck_status": "passed",
            "backup_path": f"{ctx.stage1_dir}/{target_name}.cfg",
            "backup_timestamp": "2026-04-01T12:00:00Z",
        }

        _writeback_v1_best_effort(
            ctx=ctx,
            provider=provider,
            device_state=device_state,
        )

        print("warnings_after_writeback =", device_state["warnings"])

        refreshed = provider.client.list_devices(
            site=ctx.inventory["site"],
            status=ctx.inventory.get("status", "active"),
            name=target_name,
        )

        if not refreshed:
            raise RuntimeError(f"Device not found after write-back: {target_name}")

        raw = refreshed[0]
        custom_fields = raw.get("custom_fields", {})

        print("refreshed_custom_fields =")
        print({
            "precheck_status": custom_fields.get("precheck_status"),
            "backup_path": custom_fields.get("backup_path"),
            "backup_timestamp": custom_fields.get("backup_timestamp"),
        })

    finally:
        close_fn = getattr(provider, "close", None)
        if callable(close_fn):
            close_fn()


if __name__ == "__main__":
    main()

