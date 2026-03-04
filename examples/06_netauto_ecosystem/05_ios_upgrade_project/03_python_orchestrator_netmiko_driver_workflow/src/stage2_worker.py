
from __future__ import annotations

import time
from typing import Any, Dict


def _mk_result(device: Dict[str, Any]) -> Dict[str, Any]:
    # Stage2Result (from Stage1 handoff)
    return {
        "inventory_hostname": device["inventory_hostname"],
        "host": device["host"],
        "port": device.get("port", 22),
        "device_type": device.get("device_type"),

        "stage2_status": True,
        "stage2_reason": "",
        
        "stage2_pre_system_image": "",
        "stage2_post_system_image": "",
    }


def _fail(result: Dict[str, Any], step: str, detail: str) -> Dict[str, Any]:
    result["stage2_status"] = False
    result["stage2_reason"] = f"error by {step}: {detail}"
    return result


def _device_from_result(result: Dict[str, Any]) -> Dict[str, Any]:
    # Build normalized device dict for driver.connect()
    return {
        "inventory_hostname": result["inventory_hostname"],
        "host": result["host"],
        "port": result.get("port", 22),
        "device_type": result.get("device_type"),
    }


def stage2_device_precheck_worker(ctx, device: Dict[str, Any], creds: Dict[str, Any], driver) -> Dict[str, Any]:
    """
    Step: precheck_show_version
    Connect + show version + parse system image.
    Returns Stage2Result.
    """
    result = _mk_result(device)
    handle = None
    try:
        try:
            dev = _device_from_result(result)
            handle = driver.connect(device=dev, creds=creds, timeout=ctx.behavior["connect_timeout"])
            sysimg = driver.get_system_image(handle, timeout=ctx.behavior["cmd_timeout"])
            result["stage2_pre_system_image"] = sysimg
            return result
        except Exception as e:
            return _fail(result, "precheck_show_version", str(e))
    finally:
        if handle is not None:
            try:
                driver.disconnect(handle)
            except Exception:
                pass


def stage2_reload_one(ctx, result: Dict[str, Any], creds: Dict[str, Any], driver) -> Dict[str, Any]:
    """
    Step: reload (serial)
    Updates Stage2Result in-place; and returns it.
    """
    if not result.get("stage2_status", False):
        return result

    handle = None
    try:
        try:
            dev = _device_from_result(result)
            handle = driver.connect(device=dev, creds=creds, timeout=ctx.behavior["connect_timeout"])
            driver.reload(handle, timeout=ctx.behavior["cmd_timeout"])
            return result
        except Exception as e:
            return _fail(result, "reload", str(e))
    finally:
        # best-effort disconnect (session may drop after reload)
        if handle is not None:
            try:
                driver.disconnect(handle)
            except Exception:
                pass


def wait_for_ssh_connect(
    result: Dict[str, Any],
    creds: Dict[str, Any],
    driver,
    timeout_sec: int,
    probe_interval_sec: int = 10
) -> bool:
    """
    Step: wait_for_ssh_connect
    SSH is considered "back" when a real Netmiko connect succeeds.
    """
    dev = _device_from_result(result)
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        handle = None
        try:
            handle = driver.connect(device=dev, creds=creds, timeout=probe_interval_sec)
            return True
        except Exception:
            time.sleep(probe_interval_sec)
        finally:
            if handle is not None:
                try:
                    driver.disconnect(handle)
                except Exception:
                    pass
    return False


def stage2_device_postcheck_worker(ctx, result: Dict[str, Any], creds: Dict[str, Any], driver) -> Dict[str, Any]:
    """
    Steps: postcheck_show_version + compare
    Condition: post system image must CONTAIN ctx.image["filename"]
    """
    if not result.get("stage2_status", False):
        return result

    handle = None
    try:
        try:
            dev = _device_from_result(result)
            handle = driver.connect(device=dev, creds=creds, timeout=ctx.behavior["connect_timeout"])
            sysimg = driver.get_system_image(handle, timeout=ctx.behavior["cmd_timeout"])
            result["stage2_post_system_image"] = sysimg
        except Exception as e:
            return _fail(result, "postcheck_show_version", str(e))
    finally:
        if handle is not None:
            try:
                driver.disconnect(handle)
            except Exception:
                pass

    new_fn = str(ctx.image.get("filename", "")).strip()
    post_img = str(result.get("stage2_post_system_image", ""))

    if new_fn and (new_fn in post_img):
        return result

    return _fail(result, "compare", f"post system image does not contain '{new_fn}'")
    #f"post system image does not contain {new_fn!r}"