from __future__ import annotations

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


def stage1_device_worker(ctx, device: Dict[str, Any], creds: Dict[str, Any], driver) -> Dict[str, Any]:
    state: Dict[str, Any] = {
        "inventory_hostname": device["inventory_hostname"],
        "host": device["host"],
        "port": device.get("port", 22),
        "device_type": device.get("device_type"),
        "status": "READY_FOR_RELOAD",
        "warnings": [],
    }

    handle = None
    scp_initial = None
    enabled_by_us = False

    try:
        # A) auth_sanity
        try:
            handle = driver.connect(device=device, creds=creds, timeout=ctx.behavior["connect_timeout"])
            priv = driver.get_privilege_level(handle, timeout=ctx.behavior["cmd_timeout"])
            if priv < 15:
                state["status"] = "NOT_READY"
                state["failed_step"] = "auth_sanity"
                state["reason"] = "error by auth_sanity: privilege level < 15"
                return state
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "auth_sanity"
            state["reason"] = f"error by auth_sanity: {e}"
            return state

        # B) flash_space
        try:
            free_bytes = driver.get_free_space_bytes(
                handle, remote_fs=ctx.device_fs["remote_fs"], timeout=ctx.behavior["cmd_timeout"]
            )
            required = int(ctx.image["size_bytes"] * float(ctx.device_fs.get("space_factor", 1.0)))
            if free_bytes < required:
                state["status"] = "NOT_READY"
                state["failed_step"] = "flash_space"
                state["reason"] = "error by flash_space: insufficient free space"
                return state
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "flash_space"
            state["reason"] = f"error by flash_space: {e}"
            return state

        # C) backup_running_config -> stage1_dir/<device>.cfg
        try:
            running_cfg = driver.get_running_config(handle, timeout=ctx.behavior["cmd_timeout"])
            backup_path = f"{ctx.stage1_dir}/{device['inventory_hostname']}.cfg"
            write_text(backup_path, running_cfg)
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "backup_running_config"
            state["reason"] = f"error by backup_running_config: {e}"
            return state

        # D) enable_scp (conditional) + capture initial SCP state
        try:
            scp_initial = driver.is_scp_enabled(handle, timeout=ctx.behavior["cmd_timeout"])
            if bool(ctx.behavior.get("scp_enable_before_upload", False)) and scp_initial is False:
                driver.set_scp_enabled(handle, enable=True, timeout=ctx.behavior["cmd_timeout"])
                enabled_by_us = True
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "enable_scp"
            state["reason"] = f"error by enable_scp: {e}"
            return state

        # E) upload_image
        try:
            driver.file_transfer(
                handle,
                local_full_path=ctx.image["local_full_path"],
                remote_dir=ctx.device_fs["remote_dir"],
                filename=ctx.image["filename"],
            )
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "upload_image"
            state["reason"] = f"error by upload_image: {e}"
            return state

        # F) verify_md5_on_device
        try:
            dev_md5 = driver.verify_md5(
                handle, 
                remote_path=ctx.image["remote_path"], 
                timeout=ctx.behavior["cmd_timeout"]
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
            driver.boot_prep(
                handle, 
                new_image_remote_path=ctx.image["remote_path"], 
                timeout=ctx.behavior["cmd_timeout"]
            )
        except Exception as e:
            state["status"] = "NOT_READY"
            state["failed_step"] = "boot_prep"
            state["reason"] = f"error by boot_prep: {e}"
            return state

        # H) disable_scp (conditional restore) - non-fatal if fails
        if bool(ctx.behavior.get("scp_disable_after_upload", False)) and enabled_by_us and scp_initial is False:
            try:
                driver.set_scp_enabled(handle, enable=False, timeout=ctx.behavior["cmd_timeout"])
            except Exception:
                state["warnings"].append("disable_scp_failed")

        return state

    finally:
        if handle is not None:
            try:
                driver.disconnect(handle)
            except Exception:
                pass
