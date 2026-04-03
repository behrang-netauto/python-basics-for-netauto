# Phase 2 — Automated NetBox Bootstrap

## status
Phase 2 has not been implemented yet, this phase remains deferred.
Current project progression moved directly from Phase 1 to Phase 3/4 due to time priorities.

This document is a design/planning note for the future NetBox bootstrap automation track.
It does not represent a completed or validated implementation.

## purpose
Automate the manual bring-up learned in Phase 1 so that a clean Ubuntu snapshot can be turned into a working NetBox platform with one controlled run.

## scope
Phase 2 is the **bootstrap automation track**.

It is intentionally separate from the upgrade workflow code.
The purpose is platform provisioning, not device orchestration.

## target outcome
Starting from a clean VM snapshot, one bootstrap run should be able to:

- prepare the host
- install or wire required dependencies
- place and configure NetBox
- initialize database/application state
- install and enable services
- run health checks
- report clearly where failure happened if the run stops

## design principles

### 1) configuration must not be hardcoded
Values such as:

- hostname
- base URL
- secrets
- passwords
- version
- environment-specific paths

must come from config files, templates, or vault-like inputs.

### 2) secrets stay outside code
Database passwords, Django secret key, API-related secrets, and similar values must not be embedded in scripts or templates in plaintext.

### 3) idempotent-first mindset
Absolute perfection is not required in v1, but steps should be designed to be as repeatable as practical.

Examples:

- safe package install
- templated config files
- service enable/start with predictable outcomes
- “create if missing / update if present” logic where reasonable

### 4) explicit logging
The bootstrap must make it obvious:

- which step started
- which step passed
- which step failed
- where the operator should look next

### 5) health checks are first-class
Health checks are not an afterthought.
A bootstrap that installs everything but does not prove the platform is healthy is incomplete.

## suggested repo / directory shape
Suggested dedicated project path:

```text
04_netbox_bootstrap/
  tasks/
  templates/
  config/
  bootstrap.sh
  vault.yml
  README.md
```

### directory intent

#### `tasks/`
Task-level scripts or step runners.

Examples:
- OS preparation
- dependency installation
- NetBox source placement
- config rendering
- service install
- health checks

#### `templates/`
Templated config or service files.

Examples:
- NetBox config fragments
- systemd units
- Nginx site config

#### `config/`
Non-secret environment-specific configuration.

Examples:
- NetBox version
- install path
- public hostname
- service toggles

#### `vault.yml`
Secret values used by the bootstrap.
Keep real secrets out of Git history when possible.

#### `bootstrap.sh`
Top-level entrypoint for a full run.

#### `README.md`
Operator guide:
- prerequisites
- expected inputs
- run command
- validation steps
- troubleshooting notes

## recommended bootstrap flow

### Phase 2.1 — preflight
Validate the environment before making changes.

Checks may include:

- running as expected user / privilege level
- expected OS family/version
- network reachability assumptions
- required tools available
- required config files present

### Phase 2.2 — host preparation
Prepare the Ubuntu VM with the required packages, users, directories, and permissions.

### Phase 2.3 — NetBox source and version
Fetch or place the exact NetBox version defined by config.
Version pinning should remain explicit, just as in Phase 1.

### Phase 2.4 — configuration rendering
Render config files and service definitions from templates + config + vault inputs.

### Phase 2.5 — application initialization
Run the application setup sequence:

- environment prep
- dependency install
- migrations
- static assets
- superuser creation if needed

### Phase 2.6 — service activation
Install / reload / enable / start the required services.

### Phase 2.7 — health validation
Verify the platform from bottom to top:

- PostgreSQL
- Redis
- NetBox app service
- NetBox RQ worker
- Nginx
- local HTTP/HTTPS response
- optional UI/API smoke checks

## failure model
If bootstrap fails:

- fail fast at the current step
- print the failing step clearly
- preserve logs/artifacts useful for debugging
- do not pretend success
- do not continue blindly into later phases

The operator should immediately know:
- what failed
- where it failed
- what subsystem is implicated

## logging expectations
Minimum logging style:

- step start
- step success
- step failure
- summary at the end

A useful bootstrap log should answer:
- how far the run got
- whether retry is safe
- whether rollback to snapshot is preferable

## health-check contract
At minimum, the bootstrap should expose a health-check phase that can be run independently.

A healthy result should mean:

- services are up
- reverse proxy responds
- app is reachable
- login/API path is plausible
- system is ready for later Phase 3/4 work

## relationship to later phases
Phase 2 does **not** model lab inventory and does **not** integrate the orchestrator yet.

Its job is simply:
- produce a working NetBox platform
- make that process repeatable
- make future rebuilds cheaper and less stressful

Phase 3 then models the minimum lab inventory.
Phase 4 connects the orchestrator to NetBox.

## minimum v1 success criteria
Phase 2 is successful when a single bootstrap run can, from a clean snapshot:

- bring NetBox up
- make the UI reachable
- allow login
- pass health checks
- identify failure point clearly if something breaks

## future enhancements
Future improvements may include:

- stronger idempotency guarantees
- better rollback/retry behavior
- certificate automation
- API-based post-bootstrap smoke checks
- automated first object creation for validation
- richer structured logs / artifacts

## exit criteria
Phase 2 is done when the operator can reliably rebuild the NetBox platform from a clean base image with one documented bootstrap process and clear health validation.

## current state
What has been completed so far:
- Phase 1 manual bring-up
- Phase 3 minimum data model
- Phase 4 orchestrator integration

What is still deferred:
- automated NetBox bootstrap from a clean snapshot
- idempotent bootstrap execution
- bootstrap health-check automation
