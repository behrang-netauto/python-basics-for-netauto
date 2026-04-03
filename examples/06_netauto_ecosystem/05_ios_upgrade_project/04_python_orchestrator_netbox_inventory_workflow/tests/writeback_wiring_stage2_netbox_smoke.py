
"""
###   Smoke test for Stage 2 NetBox write-back wiring.
###   Writes stage2_result for two devices (R1=passed, R2=failed), 
    then re-reads each device from NetBox to verify the custom field was actually updated.
# for running this test, in root of this project, run:
# python -m tests.writeback_wiring_stage2_netbox_smoke

output:
loaded_devices=5
R1 device_id=1
R2 device_id=2
warnings_after_R1_writeback = []
stage2_result_after_R1 = passed
warnings_after_R2_writeback = []
stage2_result_after_R2 = failed
"""
from src.ctx import build_ctx
from src.inventory_provider_factory import build_inventory_provider
from src.stage2_orchestrator import _writeback_stage2_result_best_effort


def _read_stage2_result(provider, ctx, target_name: str):
    refreshed = provider.client.list_devices(
        site=ctx.inventory["site"],
        status=ctx.inventory.get("status", "active"),
        name=target_name,
    )
    if not refreshed:
        raise RuntimeError(f"Device not found after write-back: {target_name}")

    raw = refreshed[0]
    custom_fields = raw.get("custom_fields", {})
    return custom_fields.get("stage2_result")


def main() -> None:
    ctx = build_ctx(
        run_id="writeback_stage2_wiring_smoke",
        config_path="config.yml",
        vault_path="vault.rw.yml",
    )
    provider = build_inventory_provider(ctx)

    try:
        devices = provider.load_devices()
        print(f"loaded_devices={len(devices)}")

        target_passed = "R1"
        target_failed = "R2"

        device_id_passed = provider.get_device_id_by_name(target_passed)
        device_id_failed = provider.get_device_id_by_name(target_failed)

        print(f"{target_passed} device_id={device_id_passed}")
        print(f"{target_failed} device_id={device_id_failed}")

        if device_id_passed is None:
            raise RuntimeError(f"No NetBox device_id found for {target_passed}")
        if device_id_failed is None:
            raise RuntimeError(f"No NetBox device_id found for {target_failed}")

        # ---- case 1: R1 -> passed ----
        result_passed = {
            "inventory_hostname": target_passed,
            "stage2_status": True,
            "stage2_reason": "",
            "warnings": [],
        }
        _writeback_stage2_result_best_effort(
            ctx=ctx,
            provider=provider,
            result=result_passed,
        )
        print(f"warnings_after_{target_passed}_writeback =", result_passed["warnings"])

        actual_passed = _read_stage2_result(provider, ctx, target_passed)
        print(f"stage2_result_after_{target_passed} =", actual_passed)

        # ---- case 2: R2 -> failed ----
        result_failed = {
            "inventory_hostname": target_failed,
            "stage2_status": False,
            "stage2_reason": "error by compare: post system image does not contain target image",
            "warnings": [],
        }
        _writeback_stage2_result_best_effort(
            ctx=ctx,
            provider=provider,
            result=result_failed,
        )
        print(f"warnings_after_{target_failed}_writeback =", result_failed["warnings"])

        actual_failed = _read_stage2_result(provider, ctx, target_failed)
        print(f"stage2_result_after_{target_failed} =", actual_failed)

    finally:
        close_fn = getattr(provider, "close", None)
        if callable(close_fn):
            close_fn()


if __name__ == "__main__":
    main()