
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from .ctx import RunContext, build_ctx
from .io_utils import load_yaml, md5_file, file_size_bytes, write_json
from .vault import extract_creds
from .worker import stage1_device_worker
from .runtime_factory import build_runtime
from .inventory_provider_factory import build_inventory_provider


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
    
    ctx.image["size_bytes"] = size_b

    md5 = md5_file(local_path).strip().lower()
    if md5 != expected_md5:
        raise ValueError(f"local MD5 mismatch: computed={md5} expected={expected_md5}")

    ctx.image["size_mb"] = round(size_b / (1024 * 1024), 3)


def prepare_artifacts_dirs(ctx: RunContext) -> None:
    from pathlib import Path
    Path(ctx.stage1_dir).mkdir(parents=True, exist_ok=True)


def init_handoff(ctx: RunContext) -> Dict[str, Any]:
    return {
        "run_id": ctx.run_id,
        "image": {
            "filename": ctx.image.get("filename"),
            "md5": ctx.image.get("expected_md5"),
            "size_mb": ctx.image.get("size_mb"),
        },
        "devices": [],
    }

def _writeback_v1_best_effort(ctx: RunContext, provider, device_state: Dict[str, Any]) -> None:
    if str(ctx.inventory.get("source", "")).strip().lower() != "netbox":
        return

    device_name = device_state.get("inventory_hostname")
    if not device_name:
        return

    warnings = device_state.setdefault("warnings", [])

    device_id = provider.get_device_id_by_name(device_name)
    if device_id is None:
        warnings.append("netbox_writeback_skipped:no_device_id")
        return

    precheck_status = device_state.get("precheck_status")
    if precheck_status in {"passed", "failed"}:
        try:
            provider.client.write_precheck_status(device_id, precheck_status)
        except Exception as exc:
            warnings.append(f"netbox_writeback_precheck_failed:{exc}")

    backup_path = device_state.get("backup_path")
    backup_timestamp = device_state.get("backup_timestamp")
    if backup_path and backup_timestamp:
        try:
            provider.client.write_backup_metadata(
                device_id=device_id,
                backup_path=backup_path,
                backup_timestamp=backup_timestamp,
            )
        except Exception as exc:
            warnings.append(f"netbox_writeback_backup_failed:{exc}")

def run_stage1_parallel(
    *,
    ctx: RunContext,
    provider,
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

            _writeback_v1_best_effort(
                ctx=ctx,
                provider=provider,
                device_state=device_state,
            )

def stage1(run_id: str, config_path: str, vault_path: str) -> str:
    """
    Flow:
    1. build ctx
    2. build runtime (cli + transfer)
    3. prepare artifact directories
    4. build inventory provider
    5. load devices from selected source
    6. load vault and extract credentials
    7. validate image
    8. initialize handoff
    9. run stage1 workers in parallel
    10. write handoff JSON
    11. cleanup provider/client if needed
    """
    ctx = build_ctx(
        run_id=run_id,
        config_path=config_path,
        vault_path=vault_path,
    )

    cli, xfer = build_runtime(ctx)
    prepare_artifacts_dirs(ctx)

    provider = build_inventory_provider(ctx)
    try:
        # IMPORTANT:
        # provider must stay alive until the end of Stage 1.
        # Reason: later Stage 1 integration/write-back is needed
        # provider-held state such as name -> device_id mapping.
        devices = provider.load_devices()

        vault = load_yaml(vault_path)
        creds = extract_creds(vault)

        global_validate_image(ctx)
        handoff = init_handoff(ctx)

        def worker_fn(device: Dict[str, Any]) -> Dict[str, Any]:
            return stage1_device_worker(
                ctx=ctx,
                device=device,
                creds=creds,
                cli=cli,
                xfer=xfer,
            )

        run_stage1_parallel(
            ctx=ctx,
            provider=provider,
            devices=devices,
            worker_fn=worker_fn,
            max_workers=int(ctx.behavior.get("max_workers", 5)),
            handoff=handoff,
        )

        write_json(ctx.stage1_handoff_path, handoff)
        return ctx.stage1_handoff_path

    finally:
        # For now:
        # - YAML provider likely has no close() and no external resources
        # - NetBox-backed provider may hold a client/session underneath
        #
        # We close only after Stage 1 is completely finished.
        close_fn = getattr(provider, "close", None)
        if callable(close_fn):
            close_fn()