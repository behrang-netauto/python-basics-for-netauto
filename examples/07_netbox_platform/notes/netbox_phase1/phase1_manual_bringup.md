# Phase 1 — Manual NetBox Bring-Up

## purpose
Bring up a working NetBox instance manually, verify that the platform is healthy, and capture the operational facts needed later for Phase 2 automation and Phase 4 integration.

## scope
Phase 1 is intentionally manual.

The goal is **not** idempotent automation yet.
The goal is:

- install NetBox manually on the Ubuntu lab VM
- verify that core services are healthy
- verify that UI login works
- verify that basic object creation works
- record enough facts and pitfalls so Phase 2 can automate the same flow from a clean snapshot

## target outcome
At the end of Phase 1, all of these should be true:

- NetBox UI is reachable
- login works
- PostgreSQL is healthy
- Redis is healthy
- NetBox application service is healthy
- NetBox RQ worker is healthy
- Nginx is healthy
- a basic test object can be created in the UI
- reboot validation passes
- notes and operational facts are captured for later reuse

## platform assumptions
Current lab assumptions for Phase 1:

- Ubuntu VM on VirtualBox
- NetBox installed under `/opt/netbox`
- current working lab version pinned during bring-up
- local lab access is sufficient
- self-signed TLS is acceptable for early lab validation

## step flow

### Step 1 — snapshot and baseline capture
Before touching the system:

- take a VM snapshot
- capture host identity and network facts
- capture Ubuntu version, kernel, IPs, and interface details
- record current Python/runtime assumptions relevant to the VM

Keep this snapshot as the clean rollback point for future retries.

### Step 2 — package and dependency preparation
Install and verify the system packages required by NetBox and its service stack.

Typical areas include:

- PostgreSQL
- Redis
- Nginx
- system libraries
- Python build/runtime prerequisites, if needed by the chosen install path

The purpose here is not elegance; it is to make the machine able to host NetBox reliably.

### Step 3 — obtain NetBox source and pin version
Clone the NetBox source and pin the lab to the chosen version.

Important design note:

- pinning the version is deliberate
- this is a lab platform track, so reproducibility matters more than “latest available”

Record the exact version used in notes and README.

- actual lab install path = /opt/netbox
- source via git clone + release tag pin
- versioned install dirs were not used in Phase 1

### Step 4 — application configuration
Prepare NetBox configuration:

- database connection settings
- Redis settings
- secret key
- allowed hosts
- optional API token pepper / security settings as needed by the chosen version

Keep secrets outside reusable docs when possible.
In notes, record **what** was configured, not the secret values.

### Step 5 — initialize the application
Run the first-time setup steps needed by NetBox, such as:

- Python environment preparation
- dependency install
- database migration
- static file collection
- superuser creation

At this phase, manual execution is acceptable.

### Step 6 — system service wiring
Wire the application into the VM using system services.

Minimum expected service set:

- PostgreSQL
- Redis
- NetBox application service
- NetBox RQ worker
- Nginx

The objective is simple:
the platform should survive shell exit and later reboot.

### Step 7 — health checks
Verify the stack from the bottom up.

Minimum checks:

- PostgreSQL status
- Redis status
- NetBox service status
- NetBox RQ worker status
- Nginx status
- local HTTPS response from Nginx
- UI reachability in a browser

If a `502 Bad Gateway` or equivalent appears, record:

- root cause
- exact fix
- service affected
- whether the fix is structural or environment-specific

### Step 8 — UI validation
Log in to NetBox and confirm the app is usable.

Minimum UI checks:

- login succeeds
- admin menus load
- API token creation page works
- a basic object can be created successfully

This proves that the platform is not merely “service up”, but actually operational.

### Step 9 — reboot validation
Reboot the VM and verify the platform comes back cleanly.

Minimum reboot checks:

- services auto-start
- UI still loads
- login still works
- test object is still present

This is a required Phase 1 closure check.

## validation checklist
Phase 1 should be considered complete only if all of the following are true:

- VM snapshot taken before install work
- NetBox source pinned to an explicit version
- service stack healthy
- browser login validated
- one test object created
- reboot validation passed
- key installation facts and pitfalls documented

## artifacts and notes to preserve for Phase 2
Preserve these facts because Phase 2 automation depends on them:

- exact NetBox version used
- install path
- service names
- systemd unit details
- final config file locations
- any Python/runtime workaround that was needed
- TLS/Nginx assumptions
- health-check command set
- known failure modes seen during bring-up
- cleanup actions that were required
- what a “healthy system” looks like after reboot

## lessons captured from this lab track
Phase 1 revealed several practical realities that matter for later automation:

- version pinning matters
- service ownership and permissions matter
- Python/runtime assumptions must be explicit
- bring-up success is not proven until UI + login + reboot all pass
- notes from real execution are more valuable than imagined bootstrap steps

## exit criteria
Phase 1 is done when:

- the platform is manually operational
- the operator can log in and create objects
- the VM survives reboot cleanly
- enough concrete notes exist to automate the process in Phase 2
