
# Nornir Mini Workflow: Precheck → Backup → Reload → JSON Report

A small, resume-ready Nornir project that demonstrates:
- parallel precheck (`show version`)
- parallel config backup (`show running-config`)
- serial reload (command accepted + SSH returns)
- a stable JSON report contract per run

## Project layout

```
examples/06_netauto_ecosystem/06_nornir_project/
  README.md
  config.yaml
  vault.yml “demo creds only”
  inventory/
    hosts.yaml
    groups.yaml
    defaults.yaml
  scripts/
    run_precheck_backup_reload.py
  artifacts/
    .keep
  requirements.txt
```

## Output layout

Each run creates a new run directory:

- `artifacts/<run_id>/`
- `artifacts/<run_id>/backups/<host>.cfg`
- `artifacts/<run_id>/report.json`

`run_id` is a UTC timestamp (e.g. `20260317T120501Z`).

## Pipeline (per device)

1) **precheck_show_version**
   - SSH connect succeeds
   - `show version` succeeds
   - `system_image` line is parsed
   - If precheck fails → device exits pipeline

2) **backup_running_config**
   - `show running-config` succeeds
   - backup file is written to disk
   - If backup fails → device exits pipeline

3) **reload_serial** (only for devices that passed 1 & 2)
   - **reload command accepted** (fail → exit)
   - **SSH returns** within timeout (fail → exit)
   - **reload.ok = true only if both substeps succeed:
        ***reload command accepted
        ***SSH returns within timeout

## Report contract (report.json)

For each device we keep a stable structure. Steps that did not run remain:

- `ok: false`
- `error: "not_run"`

Example:

```json
{
  "run_id": "...",
  "started_utc": "...",
  "devices": {
    "R1": {
      "precheck": {"ok": false, "system_image": "", "error": "not_run"},
      "backup":   {"ok": false, "path": "", "error": "not_run"},
      "reload":   {"ok": false, "error": "not_run"},
      "final":    {"ok": false, "reason": ""}
    }
  },
  "finished_utc": "..."
}
```

### final.reason values
`final.reason` is set only when the device fails:
- `precheck_failed`
- `backup_failed`
- `reload_failed`

## Execution model (Nornir)

- Phase A: precheck in parallel (`nr.run(...)`)
- Phase B: backup in parallel (`nr.run(...)`)
- Phase C: reload serial (loop over targets, one-by-one)
- Write `report.json`

## Run

```bash
python scripts/run_precheck_backup_reload.py
```

Optionally set `RUN_ID` manually:

```bash
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ) python scripts/run_precheck_backup_reload.py
```
