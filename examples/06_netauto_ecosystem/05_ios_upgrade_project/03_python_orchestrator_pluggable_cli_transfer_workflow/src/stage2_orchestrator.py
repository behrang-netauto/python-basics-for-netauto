
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

from .ctx import build_ctx
from .io_utils import load_yaml, write_json
from .vault import extract_creds
from .stage2_worker import (
    stage2_device_precheck_worker,
    stage2_reload_one,
    wait_for_ssh_connect,
    stage2_device_postcheck_worker,
)

from .runtime_factory import build_runtime

def prepare_stage2_dirs(ctx) -> None:
    Path(ctx.stage2_dir).mkdir(parents=True, exist_ok=True)


def init_stage2_handoff(ctx) -> Dict[str, Any]:
    return {
        "run_id": ctx.run_id,
        "image": {
            "filename": ctx.image.get("filename"),
            "md5": ctx.image.get("expected_md5"),
            "size_mb": ctx.image.get("size_mb"),
        },
        "devices": [],  # list[Stage2Result]
    }


def load_stage1_handoff(path: str) -> Dict[str, Any]:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Stage1 handoff not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def stage2(stage1_handoff_path: str, config_path: str, vault_path: str, precheck_no_reload: bool = False) -> str:
    # ---- load stage1 handoff ----
    stage1_handoff = load_stage1_handoff(stage1_handoff_path)
    """{
  "run_id": "...",
  "image": {...},
  "devices": [
     { device1 },
     { device2 },
     ...
        ]
    }
    """
    run_id = stage1_handoff.get("run_id")
    if not run_id:
        raise ValueError("Stage1 handoff missing run_id")

    # ---- ctx + dirs ----
    ctx = build_ctx(run_id=run_id, config_path=config_path)
    prepare_stage2_dirs(ctx)

    # ---- runtime + cli backend ----
    cli, _ = build_runtime(ctx)

    # ---- creds ----
    vault = load_yaml(vault_path)
    creds = extract_creds(vault)

    # ---- targets: READY only ----
    devices_in = stage1_handoff.get("devices", [])
    targets = [d for d in devices_in if d.get("status") == "READY_FOR_RELOAD"]

    # Ensure required fields exist in targets
    for d in targets:
        if "port" not in d or "os" not in d or "platform" not in d:
            raise ValueError("Stage1 handoff devices must include 'port', 'os', and 'platform' for Stage2")

    # ---- stage2 output ----
    handoff = init_stage2_handoff(ctx)
    reload_queue: List[Dict[str, Any]] = []   # list[Stage2Result]

    max_workers = int(ctx.behavior.get("max_workers", 5))

    # =========================
    # Phase A: precheck_show_version (parallel)
    # =========================
    def pre_worker(dev):
        return stage2_device_precheck_worker(ctx=ctx, device=dev, creds=creds, cli=cli)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(pre_worker, dev) for dev in targets]
        for fut in as_completed(futures):
            res = fut.result()  # Stage2Result
            handoff["devices"].append(res)
            if res.get("stage2_status"):
                reload_queue.append(res)
    
    if precheck_no_reload:
        write_json(str(ctx.stage2_results_path), handoff)
        return str(ctx.stage2_results_path)

    # =========================
    # Phase B: reload (serial)
    # =========================
    for res in reload_queue:
        stage2_reload_one(ctx=ctx, result=res, creds=creds, cli=cli)

    # =========================
    # Phase C: wait_for_ssh_connect (parallel)
    # =========================
    reload_timeout = int(ctx.behavior.get("reload_timeout", 900))
    probe_interval = int(ctx.behavior.get("probe_interval", 10))

    ok_for_post = [r for r in reload_queue if r.get("stage2_status")]

    def wait_worker(res):
        #return tuple => (res, ok_bool) 
        return (res, wait_for_ssh_connect(res, creds=creds, cli=cli, timeout_sec=reload_timeout, probe_interval_sec=probe_interval))

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(wait_worker, r) for r in ok_for_post]
        for fut in as_completed(futures):
            res, ok = fut.result()
            #tuple unpacking: res is the Stage2Result dict, come from ok_for_post; ok is the boolean result of wait_for_ssh_connect
            if not ok:
                res["stage2_status"] = False
                res["stage2_reason"] = "error by wait_for_ssh_connect: timeout"

    # =========================
    # Phase D: postcheck_show_version + compare (parallel)
    # =========================
    ok_for_post2 = [r for r in ok_for_post if r.get("stage2_status")]

    def post_worker(res):
        return stage2_device_postcheck_worker(ctx=ctx, result=res, creds=creds, cli=cli)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(post_worker, r) for r in ok_for_post2]
        for fut in as_completed(futures):
            _ = fut.result()
            # post_worker updates res in-place, so no need to capture the result here (assign the return value to "_")

    # ---- write stage2 results ----
    write_json(str(ctx.stage2_results_path), handoff)
    return str(ctx.stage2_results_path)
  