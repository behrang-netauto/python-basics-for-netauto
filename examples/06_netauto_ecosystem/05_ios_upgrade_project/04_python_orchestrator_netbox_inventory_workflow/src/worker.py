from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from .io_utils import write_text


FAILED_STEPS = {
    "auth_sanity",
    "flash_space",
    "backup_running_config",
    "enable_scp",
    "upload_image",
    "verify_md5_on_device",
    "boot_prep",
    "disable_scp",
}


def _utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def stage1_device_worker(ctx, device: Dict[str, Any], creds: Dict[str, Any], cli, xfer) -> Dict[str, Any]:
    state: Dict[str, Any] = {
        "inventory_hostname": device["inventory_hostname"],
        "host": device["host"],
        "port": device.get("port", 22),
        "os": device.get("os"),
        "platform": device.get("platform"),
        "device_type": device.get("device_type"),
        "status": "READY_FOR_RELOAD",
        "warnings": [],
        "precheck_status": None,
        "backup_path": None,
        "backup_timestamp": None,
    }

    method = str(ctx.transfer.get("method", "")).strip().lower()
    handle = None
    scp_initial = None
    enabled_by_us = False

    try:
        # A) auth_sanity
        try:
            handle = cli.connect(device=device, creds=creds, timeout=ctx.behavior["connect_timeout"])
            priv = cli.get_privilege_level(handle, timeout=ctx.behavior["cmd_timeout"])
            if priv < 15:
                state["status"] = "NOT_READY"
                state["failed_step"] = "auth_sanity"
                state["reason"] = "error by auth_sanity: privilege level < 15"
                state["precheck_status"] = "failed"
                return state
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "auth_sanity"
            state["reason"] = f"error by auth_sanity: {e}"
            state["precheck_status"] = "failed"
            return state

        # B) flash_space
        try:
            free_bytes = cli.get_free_space_bytes(
                handle,
                remote_fs=ctx.device_fs["remote_fs"],
                timeout=ctx.behavior["cmd_timeout"],
            )
            required = int(ctx.image["size_bytes"] * float(ctx.device_fs.get("space_factor", 1.0)))
            if free_bytes < required:
                state["status"] = "NOT_READY"
                state["failed_step"] = "flash_space"
                state["reason"] = "error by flash_space: insufficient free space"
                state["precheck_status"] = "failed"
                return state
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "flash_space"
            state["reason"] = f"error by flash_space: {e}"
            state["precheck_status"] = "failed"
            return state

        # A+B passed => precheck passed
        state["precheck_status"] = "passed"

        # C) backup_running_config -> stage1_dir/<device>.cfg
        try:
            running_cfg = cli.get_running_config(handle, timeout=ctx.behavior["cmd_timeout"])
            backup_path = f"{ctx.stage1_dir}/{device['inventory_hostname']}.cfg"
            write_text(backup_path, running_cfg)
            state["backup_path"] = backup_path
            state["backup_timestamp"] = _utc_now_iso()
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "backup_running_config"
            state["reason"] = f"error by backup_running_config: {e}"
            return state

        # D) enable_scp (conditional) + capture initial SCP state
        if method == "scp":
            try:
                scp_initial = cli.is_scp_enabled(handle, timeout=ctx.behavior["cmd_timeout"])
                if bool(ctx.behavior.get("scp_enable_before_upload", False)) and scp_initial is False:
                    cli.set_scp_enabled(handle, enable=True, timeout=ctx.behavior["cmd_timeout"])
                    enabled_by_us = True
            except Exception as e:
                state["status"] = "NOT_READY"
                state["failed_step"] = "enable_scp"
                state["reason"] = f"error by enable_scp: {e}"
                return state

        # E) upload_image
        try:
            xfer.upload(
                handle=handle,
                ctx=ctx,
                device=device,
                creds=creds,
            )
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "upload_image"
            state["reason"] = f"error by upload_image: {e}"
            return state

        # F) verify_md5_on_device
        try:
            dev_md5 = cli.verify_md5(
                handle,
                remote_path=ctx.image["remote_path"],
                timeout=ctx.behavior["cmd_timeout"],
            )
            if dev_md5.strip().lower() != str(ctx.image["expected_md5"]).strip().lower():
                state["status"] = "NOT_READY"
                state["failed_step"] = "verify_md5_on_device"
                state["reason"] = "error by verify_md5_on_device: md5 mismatch"
                return state
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "verify_md5_on_device"
            state["reason"] = f"error by verify_md5_on_device: {e}"
            return state

        # G) boot_prep
        try:
            cli.boot_prep(
                handle,
                new_image_remote_path=ctx.image["remote_path"],
                timeout=ctx.behavior["cmd_timeout"],
            )
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "boot_prep"
            state["reason"] = f"error by boot_prep: {e}"
            return state

        # H) disable_scp (conditional restore) - non-fatal if fails
        if (
            method == "scp"
            and bool(ctx.behavior.get("scp_disable_after_upload", False))
            and enabled_by_us
            and scp_initial is False
        ):
            try:
                cli.set_scp_enabled(handle, enable=False, timeout=ctx.behavior["cmd_timeout"])
            except Exception as e:
                state["warnings"].append(f"disable_scp_failed: {e}")

        return state

    finally:
        if handle is not None:
            try:
                cli.disconnect(handle)
            except Exception:
                pass