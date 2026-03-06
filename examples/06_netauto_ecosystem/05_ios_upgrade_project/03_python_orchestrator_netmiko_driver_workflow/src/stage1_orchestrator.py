from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from .ctx import RunContext, build_ctx
from .io_utils import load_yaml, md5_file, file_size_bytes, write_json
from .inventory import normalize_devices_from_inventory
from .vault import extract_creds
from .worker import stage1_device_worker


def global_validate_image(ctx: RunContext) -> None:
    local_path = ctx.image.get("local_full_path")
    expected_md5 = str(ctx.image.get("expected_md5", "")).strip().lower()
    if not local_path:
        raise ValueError("config.yml image.local_full_path is required")
    if not expected_md5 or len(expected_md5) != 32:
        raise ValueError("config.yml image.expected_md5 must be a 32-hex MD5 string")

    size_b = file_size_bytes(local_path)
    if size_b <= 0:
        raise ValueError(f"image file has invalid size: {size_b}")

    md5 = md5_file(local_path).strip().lower()
    if md5 != expected_md5:
        raise ValueError(f"local MD5 mismatch: computed={md5} expected={expected_md5}")

    ctx.image["size_mb"] = round(size_b / (1024 * 1024), 3)


def prepare_artifacts_dirs(ctx: RunContext) -> None:
    from pathlib import Path
    Path(ctx.stage1_dir).mkdir(parents=True, exist_ok=True)

# handoff = {run_id, image, devices:[DeviceState,...]}
def init_handoff(ctx: RunContext) -> Dict[str, Any]:
    """
{
  "run_id": "<run_id>",
  "image": {
    "filename": "<image_filename>",
    "md5": "<expected_md5>",
    "size_mb": <float>
  },
  "devices": [
    {
      "inventory_hostname": "<R1>",
      "host": "<ip>",
      "status": "READY_FOR_RELOAD",
      "warnings": []
    },
    {
      "inventory_hostname": "<R3>",
      "host": "<ip>",
      "status": "NOT_READY",
      "failed_step": "upload_image",
      "reason": "error by upload_image: <detail>",
      "warnings": ["disable_scp_failed"]
    }
  ]
}"""
    return {
        "run_id": ctx.run_id,
        "image": {
            "filename": ctx.image.get("filename"),
            "md5": ctx.image.get("expected_md5"),
            "size_mb": ctx.image.get("size_mb"),
        },
        "devices": [],
    }

def run_stage1_parallel(
    devices: List[Dict[str, Any]],
    worker_fn,
    max_workers: int,
    handoff: Dict[str, Any],
) -> None:
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(worker_fn, dev) for dev in devices]
        for fut in as_completed(futures):
            device_state = fut.result()
            handoff["devices"].append(device_state)


def stage1(run_id: str, config_path: str, inventory_path: str, vault_path: str, driver) -> str:
    """
    1. build ctx
    2. prepare_artifacts_dirs
    3. load inventory → normalize devices
    4. load vault → extract creds
    5. global_validate_image(ctx) (size_mb/size_bytes)
    6. init_handoff(ctx)
    7. worker_fn as a closure
    8. run_stage1_parallel
    9. write_json(...)"""
    ctx = build_ctx(run_id=run_id, config_path=config_path)

    prepare_artifacts_dirs(ctx)

    inventory = load_yaml(inventory_path)
    devices = normalize_devices_from_inventory(inventory)

    vault = load_yaml(vault_path)
    creds = extract_creds(vault)

    global_validate_image(ctx)
    handoff = init_handoff(ctx)

    def worker_fn(device):
        return stage1_device_worker(ctx=ctx, device=device, creds=creds, driver=driver)

    run_stage1_parallel(
        devices=devices,
        worker_fn=worker_fn,
        max_workers=int(ctx.behavior.get("max_workers", 5)),
        handoff=handoff,
    )

    write_json(ctx.stage1_handoff_path, handoff)
    return ctx.stage1_handoff_path
