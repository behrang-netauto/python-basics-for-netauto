# 03_python_orchestrator_netmiko_driver_workflow

Stage1 Python orchestrator (ThreadPool) + Netmiko driver workflow.

## What it does (Stage1)
For each device (max parallel = `behavior.max_workers`):
A) SSH connect + privilege check (>=15)  
B) Flash free-space check vs image size * space_factor  
C) Backup running-config to `artifacts/<run_id>/stage1/<device>.cfg`  
D) (Optional) enable SCP if it was disabled  
E) Upload image via SCP to `device_fs.remote_dir`  
F) Verify MD5 on device  
G) Boot prep (new image first + fallback existing boot system if present) + write mem  
H) (Optional) disable SCP if we enabled it (non-fatal warning if fails)

Output:
worker.py  -> writes backups: `artifacts/<run_id>/stage1/<device>.cfg`
orchestrator -> writes handoff:
`artifacts/<run_id>/stage1/stage1_handoff.json` with:
`{run_id, image, devices:[DeviceState,...]}`

## Quick start
```bash
cd 03_python_orchestrator_netmiko_driver_workflow
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# create your real vault.yml (ignored by git)
cp vault.example.yml vault.yml

# run stage1
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
python run_stage1.py --run-id "$RUN_ID" --config config.yml --inventory inventory.yml --vault vault.yml
```

## Diagram (Stage1)
run_stage1.py  (CLI / composition root)
   |
   |  creates: driver = NetmikoDriver()
   |  parses args: config/inventory/vault/run_id
   v
stage1_orchestrator.py  (Stage1 flow + concurrency + handoff/artifacts)
   |
   |  defines worker_fn(device) -> stage1_device_worker(...)
   |  runs ThreadPoolExecutor over devices
   v
worker.py  (per-device pipeline A..H)
   |
   |  calls driver methods (connect / show / scp / verify / boot_prep / disconnect)
   v
netmiko_driver.py  (low-level device operations using Netmiko)
   |
   |  Netmiko ConnectHandler / file_transfer / send_command_timing / parsing
   v
Device (IOS-XE routers)

=========================================**STAGE_2**=========================================

## Stage2 (Reload + Post-check)

Stage2 consumes the Stage1 handoff and reloads only devices that are `READY_FOR_RELOAD`.

### What it does (Stage2)
For each target device (filtered from Stage1 handoff):
1) **Precheck (parallel, max = `behavior.max_workers`)**
   - SSH connect + `show version`
   - parse and store `stage2_pre_system_image`

2) **Reload (serial, one-by-one)**
   - send `reload` and confirm prompts

3) **Wait for SSH back (parallel)**
   - SSH is considered “back” when a real Netmiko connect succeeds
   - timeout: `behavior.reload_timeout` (default 900s)
   - probe interval: `behavior.probe_interval` (default 10s)

4) **Postcheck + Compare (parallel)**
   - SSH connect + `show version`
   - parse and store `stage2_post_system_image`
   - **PASS Condition:** `stage2_post_system_image` must contain the **new image filename** (`image.filename` from config)

Output:
`artifacts/<run_id>/stage2/stage2_results.json` with:
`{run_id, image, devices:[Stage2Result,...]}`
   - check the Outout: 
      # cat artifacts/<RUN_ID>/stage2/stage2_results.json | head -80
      # jq '.devices[] | {inventory_hostname,stage2_status,stage2_reason,stage2_pre_system_image,stage2_post_system_image}' artifacts/<RUN_ID>/stage2/stage2_results.json
*** Dry-run import:
   - (.venv) python -c "from src.stage2_orchestrator import stage2; print('OK')"

### Run Stage2
```bash
python run_stage2.py \
  --handoff artifacts/<run_id>/stage1/stage1_handoff.json \
  --config config.yml \
  --vault vault.yml


## Diagram (Stage1 + Stage2)
run_stage1.py / run_stage2.py (CLI entrypoints)
|
| creates: driver = NetmikoDriver()
| parses args (config/inventory/vault/run_id or handoff)
v
stage1_orchestrator.py / stage2_orchestrator.py (flow + concurrency + artifacts)
|
| runs ThreadPoolExecutor over devices (prechecks/postchecks)
| runs reload serially (Stage2)
v
worker.py / stage2_worker.py (per-device pipeline)
|
v
netmiko_driver.py (low-level ops)
|
v
Device (IOS-XE routers)

