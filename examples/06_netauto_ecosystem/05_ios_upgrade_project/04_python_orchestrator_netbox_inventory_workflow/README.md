
# 04_python_orchestrator_netbox_inventory_workflow

Stage1/Stage2 Python orchestrators (ThreadPool) with:
- **runtime-selected CLI backend**
- **runtime-selected transfer method**
- **NetBox-driven inventory**
- **minimal NetBox write-back**

This workflow is the NetBox-based evolution of Scenario 3.

---

## Runtime strategy (pairing rules)

Supported runtime pairings:
- `cli.backend=netmiko` → `transfer.method=scp`
- `cli.backend=scrapli` → `transfer.method=copy_command`

`config.yml` and `ctx` contain only metadata and source selection.
Runtime objects (`cli`, `xfer`) are built by `src/runtime_factory.py`.

---

## Inventory strategy

This scenario is intentionally designed around the following convention:
- `inventory.source: "netbox"`
- `inventory.site: "lab-primary"`

That convention is part of the current design contract and should be kept explicit in notes / docs.

Inventory providers are selected by `src/inventory_provider_factory.py`.

Current provider implementations:
- `src/netbox_inventory_provider.py`
- `src/yaml_inventory_provider.py`

In the current scenario, **NetBox is the primary Source of Truth**.

---

# Stage1

## What it does (Stage1)

For each selected device (max parallel = `behavior.max_workers`):

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
- orchestrator → writes handoff: `artifacts/<run_id>/stage1/stage1_handoff.json`

Stage1 handoff contains device records used later by Stage2.

At minimum, Stage2 depends on Stage1 handoff keeping these fields on each device record:
- `inventory_hostname`
- `host`
- `port`
- `os`
- `platform`
- `status`

### Stage1 write-back (v1)

Stage1 performs **best-effort** NetBox write-back when `inventory.source=netbox`.

#### 1) `precheck_status`

Write-back point:
- immediately after precheck result is known

Precheck is currently defined as:
- A) auth sanity
- B) flash space check

Exact value set:
- `passed`
- `failed`

#### 2) `backup_path`

Write-back point:
- only after backup succeeds

#### 3) `backup_timestamp`

Write-back point:
- only after backup succeeds

Format:
- ISO-8601 UTC string, e.g. `2026-04-01T12:00:00Z`

### Stage1 write-back failure policy

If Stage1 write-back fails:
- only a warning is recorded
- Stage1 itself does **not** fail
- device execution result is **not** rolled back

Write-back is best-effort synchronization, not an execution gate.

---

## Quick checks (optional)

```bash
cat artifacts/<run_id>/stage1/stage1_handoff.json | head -50
jq '.devices[0] | {inventory_hostname,host,port,os,platform,status}' artifacts/<run_id>/stage1/stage1_handoff.json
```

### Dry-run import (import/syntax check)

```bash
python -c "from src.stage1_orchestrator import stage1; print('OK')"
```

---

## Quick start

```bash
cd 04_python_orchestrator_netbox_inventory_workflow
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## GitHub Actions CI — Phase 1 baseline quality gate

This workflow adds a first CI quality gate for the NetBox inventory workflow.

It runs on `push` and `pull_request` events when changes affect either the workflow file itself or this project directory:

- `.github/workflows/netbox-inventory-ci.yml`
- `examples/06_netauto_ecosystem/05_ios_upgrade_project/04_python_orchestrator_netbox_inventory_workflow/**`

Phase 1 intentionally focuses on offline-safe checks that do not require a live NetBox instance, device reachability, or secrets.

Current checks:

- Python dependency installation
- Python syntax compilation
- Stage1 / Stage2 dry-run import checks
- Ruff linting
- YAML linting

NetBox-dependent smoke tests and write-back checks remain local/lab validation steps for now because they require a live NetBox environment, credentials, and the expected custom-field context.

CI evidence for the first successful run is stored under `artifacts/ci_foundation/`.

---

## Configuration notes

### `config.yml`

This scenario currently expects a full Stage1/Stage2 config.
Important fields include:
- `inventory.source`
- `inventory.site`
- `netbox.base_url`
- `image.local_full_path`
- `image.filename`
- `image.expected_md5`
- `image.remote_path`
- `cli.backend`
- `transfer.method`

### `vault` files

Recommended approach:
- `vault.readonly.yml` → for read-only smoke tests
- `vault.rw.yml` → for write-back tests / runs

Both keep the same schema:

```yaml
credentials:
  username: "..."
  password: "..."
  secret: "..."

netbox:
  token: "nbt_<key>.<token>"
```

Do **not** push real API tokens to Git.
Commit only redacted / placeholder token values.

---

## Run Stage1

```bash
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
python run_stage1.py --run-id "$RUN_ID" --config config.yml --vault vault.rw.yml
```

> For purely read-only preflight/provider checks, use `vault.readonly.yml`.

---

## copy_command prerequisite (Scrapli backend)

When `transfer.method=copy_command`, the device pulls the image from your machine via HTTP.
Start a simple HTTP server on the machine that holds the image file:

```bash
cd /path/to/image-directory
python3 -m http.server 8000
```

The device will run a `copy http://<server>/<filename> <remote_path>` command over the existing CLI session.

---

## Diagram (runtime-based)

run_stage1.py (CLI entrypoint)
|
| parses args: config/vault/run_id
v
stage1_orchestrator.py (flow + concurrency + artifacts + Stage1 write-back orchestration)
|
| build_runtime(ctx) -> (cli, xfer)
| build_inventory_provider(ctx)
| runs ThreadPoolExecutor over devices
v
worker.py (per-device pipeline A..H)
|
| cli.* for device operations
| xfer.upload(...) for image upload (scp or copy_command)
v
netmiko_driver.py / scrapli_driver.py (CLI backend)
file_transfer.py (transfer strategies)
netbox_client.py (NetBox transport/write-back helper)
netbox_inventory_provider.py / yaml_inventory_provider.py
|
v
Device (IOS-XE routers) + NetBox

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
- **PASS condition:** `stage2_post_system_image` must contain the **new image filename** (`image.filename` from config)

Output:
- `artifacts/<run_id>/stage2/stage2_results.json`

Stage2 is still **handoff-driven**.
It does **not** need to rebuild inventory from NetBox in order to execute the device workflow.
In v1, when `inventory.source=netbox`, Stage2 may still build the NetBox provider only for **device ID mapping and best-effort write-back**. It does **not** use NetBox to build or refresh Stage2 execution targets.
---

## Stage2 write-back (v1)

Stage2 performs a minimal **final-result** write-back when `inventory.source=netbox`.

### `stage2_result`

Custom field:
- type: `Selection`
- allowed values:
  - `passed`
  - `failed`

Semantics:
- `passed` only when:
  - reload accepted
  - SSH came back
  - post-check passed
- `failed` if any of those fail

### `--precheck-no-reload`

When Stage2 is run with:

```bash
--precheck-no-reload
```

it **does not write back** `stage2_result`, because a final Stage2 result does not yet exist.

### Stage2 write-back failure policy

If Stage2 write-back fails:
- only a warning is recorded
- Stage2 itself does **not** fail
- Stage2 execution result is **not** rolled back

### Stage2 reason handling

Current v1 behavior:
- final state is written as `stage2_result=passed|failed`
- detailed reason remains in `stage2_results.json` via `stage2_reason`

Future work:
- mirror failure reasons to **NetBox journaling**
- keep `stage2_result` as the structured final state
- keep journaling for explanatory / operator-facing detail

---

## Quick checks (optional)

```bash
cat artifacts/<run_id>/stage2/stage2_results.json | head -80
jq '.devices[] | {inventory_hostname,stage2_status,stage2_reason,stage2_pre_system_image,stage2_post_system_image}' artifacts/<run_id>/stage2/stage2_results.json
```

### Dry-run import (import/syntax check)

```bash
python -c "from src.stage2_orchestrator import stage2; print('OK')"
```

---

## Run Stage2

```bash
python run_stage2.py \
  --handoff artifacts/<run_id>/stage1/stage1_handoff.json \
  --config config.yml \
  --vault vault.rw.yml
```

### Precheck-only (no reload)

```bash
python run_stage2.py \
  --handoff artifacts/<run_id>/stage1/stage1_handoff.json \
  --config config.yml \
  --vault vault.readonly.yml \
  --precheck-no-reload
```

---

## Diagram (Stage1 + Stage2)

run_stage1.py / run_stage2.py (CLI entrypoints)
|
| parses args (config/vault/run_id or handoff)
v
stage1_orchestrator.py / stage2_orchestrator.py
(flow + concurrency + artifacts + best-effort write-back)
|
| build_runtime(ctx) -> (cli, xfer) [Stage2 uses cli only]
| runs ThreadPoolExecutor over devices
| runs reload serially (Stage2)
v
worker.py / stage2_worker.py (per-device pipeline)
|
v
netmiko_driver.py / scrapli_driver.py
file_transfer.py
netbox_client.py
netbox_inventory_provider.py / yaml_inventory_provider.py
|
v
Device (IOS-XE routers) + NetBox

---

## Test files

### 1) `tests/read_only_netbox_inventory_smoke.py`

Purpose:
- validates basic NetBox read path
- validates `NetBoxClient` auth + device listing
- validates provider normalization

### 2) `tests/preflight_stage1_netbox_provider.py`

Purpose:
- validates `ctx.py` + provider factory + `load_devices()`
- confirms `inventory.source=netbox` wiring before full Stage1 run

### 3) `tests/writeback_wiring_netbox_smoke.py`

Purpose:
- validates Stage1 write-back wiring
- writes `precheck_status`, `backup_path`, `backup_timestamp`
- re-reads the same device from NetBox to verify the custom fields were updated

### 4) `tests/writeback_wiring_stage2_netbox_smoke.py`

Purpose:
- validates Stage2 final-result write-back wiring
- writes `stage2_result` for two devices (`passed` / `failed`)
- re-reads each device from NetBox to verify the custom field was updated

---

## Operational notes

- For `copy_command`, the image source must be reachable by the device.
- For `scp`, upload is performed via Netmiko and SCP enable/disable steps are executed only in the SCP pairing.
- `inventory.source="netbox"` with `site="lab-primary"` is the current scenario convention and should stay explicit in docs/notes.
- Stage2 execution remains handoff-driven even though Stage2 final result can be written back to NetBox.

---

## Future work

- NetBox journaling for Stage2 failure reasons
- optional Stage1 journaling for richer operational trace
- stronger SSL/TLS handling (`verify_ssl=true` with trusted certs)
- broader contract cleanup for provider-independent test helpers
