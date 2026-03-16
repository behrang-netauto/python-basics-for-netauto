# 03_python_orchestrator_pluggable_cli_transfer_workflow

Stage1/Stage2 Python orchestrators (ThreadPool) with **runtime-selected CLI backend** and **runtime-selected transfer method**.

## Runtime strategy (pairing rules)

Supported runtime pairings:

- `cli.backend=netmiko`  → `transfer.method=scp`
- `cli.backend=scrapli`  → `transfer.method=copy_command`

`config.yml` and `ctx` contain only metadata. Runtime objects (`cli`, `xfer`) are built by `src/runtime_factory.py`.

---

# Stage1

## What it does (Stage1)

For each device (max parallel = `behavior.max_workers`):

A) SSH connect + privilege check (>=15)  
B) Flash free-space check vs image size * space_factor  
C) Backup running-config to `artifacts/<run_id>/stage1/<device>.cfg`

D) **SCP-only**: enable SCP if it was disabled (only when `transfer.method=scp`)  
E) Upload image using the selected transfer method:
   - `scp`: SCP upload (`ScpTransfer`)
   - `copy_command`: IOS `copy` command (`CopyCommandTransfer`)

F) Verify MD5 on device (`verify /md5 <remote_path>`)  
G) Boot prep (new image first + fallback existing boot system if present) + write mem  
H) **SCP-only**: disable SCP only if we enabled it (non-fatal warning if fails)

Output:
- `worker.py` → writes backups: `artifacts/<run_id>/stage1/<device>.cfg`
- orchestrator → writes handoff:
  `artifacts/<run_id>/stage1/stage1_handoff.json` with:
  `{run_id, image, devices:[DeviceState,...]}`

### Quick checks (optional)
```bash
cat artifacts/<RUN_ID>/stage1/stage1_handoff.json | head -50
jq '.devices[0] | {inventory_hostname,host,port,os,platform,status}' artifacts/<RUN_ID>/stage1/stage1_handoff.json
```

### Dry-run import (import/syntax check)
```bash
python -c "from src.stage1_orchestrator import stage1; print('OK')"
```

## Quick start
```bash
cd 03_python_orchestrator_pluggable_cli_transfer_workflow
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Stage1
```bash
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
python run_stage1.py --run-id "$RUN_ID" --config config.yml --inventory inventory.yml --vault vault.yml
```

## copy_command prerequisite (Scrapli backend)

When `transfer.method=copy_command`, the device pulls the image from your laptop via HTTP.
Start a simple HTTP server on your laptop:

```bash
cd /Volumes/EXTDISK/Cisco-IOS
python3 -m http.server 8000
```

The device will run a `copy http://<server>/<filename> <remote_path>` command over the existing CLI session.

## Diagram (runtime-based)

run_stage1.py  (CLI entrypoint)
   |
   |  parses args: config/inventory/vault/run_id
   v
stage1_orchestrator.py  (flow + concurrency + artifacts)
   |
   |  build_runtime(ctx) -> (cli, xfer)
   |  runs ThreadPoolExecutor over devices
   v
worker.py  (per-device pipeline A..H)
   |
   |  cli.* for device operations
   |  xfer.upload(...) for image upload (scp or copy_command)
   v
netmiko_driver.py / scrapli_driver.py  (CLI backend)
file_transfer.py  (transfer strategies)
   |
   v
Device (IOS-XE routers)

---

# Stage2 (Reload + Post-check)

Stage2 consumes the Stage1 handoff and reloads only devices that are `READY_FOR_RELOAD`.

## What it does (Stage2)

For each target device (filtered from Stage1 handoff):

1) **Precheck (parallel, max = `behavior.max_workers`)**
   - SSH connect + `show version`
   - parse and store `stage2_pre_system_image`

2) **Reload (serial, one-by-one)**
   - send `reload` and confirm prompts

3) **Wait for SSH back (parallel)**
   - SSH is considered “back” when a real CLI connect succeeds
   - timeout: `behavior.reload_timeout` (default 900s)
   - probe interval: `behavior.probe_interval` (default 10s)

4) **Postcheck + Compare (parallel)**
   - SSH connect + `show version`
   - parse and store `stage2_post_system_image`
   - **PASS Condition:** `stage2_post_system_image` must contain the **new image filename** (`image.filename` from config)

Output:
`artifacts/<run_id>/stage2/stage2_results.json` with:
`{run_id, image, devices:[Stage2Result,...]}`

### Quick checks (optional)
```bash
cat artifacts/<RUN_ID>/stage2/stage2_results.json | head -80
jq '.devices[] | {inventory_hostname,stage2_status,stage2_reason,stage2_pre_system_image,stage2_post_system_image}' artifacts/<RUN_ID>/stage2/stage2_results.json
```

### Dry-run import (import/syntax check)
```bash
python -c "from src.stage2_orchestrator import stage2; print('OK')"
```

### Run Stage2
```bash
python run_stage2.py   --handoff artifacts/<run_id>/stage1/stage1_handoff.json   --config config.yml   --vault vault.yml
```

### Precheck-only (no reload)
```bash
python run_stage2.py   --handoff artifacts/<run_id>/stage1/stage1_handoff.json   --config config.yml   --vault vault.yml   --precheck-no-reload
```

## Diagram (Stage1 + Stage2)

run_stage1.py / run_stage2.py (CLI entrypoints)
   |
   |  parses args (config/inventory/vault/run_id or handoff)
   v
stage1_orchestrator.py / stage2_orchestrator.py (flow + concurrency + artifacts)
   |
   |  build_runtime(ctx) -> (cli, xfer)   [Stage2 uses cli only]
   |  runs ThreadPoolExecutor over devices (prechecks/postchecks)
   |  runs reload serially (Stage2)
   v
worker.py / stage2_worker.py (per-device pipeline)
   |
   v
netmiko_driver.py / scrapli_driver.py (CLI backend)
file_transfer.py (transfer strategies)
   |
   v
Device (IOS-XE routers)

---

## Operational note

- For `copy_command`, the image source must be reachable by the device (e.g., HTTP server on your laptop).
- For `scp`, upload is performed via Netmiko and SCP enable/disable steps are executed only in the SCP pairing.
