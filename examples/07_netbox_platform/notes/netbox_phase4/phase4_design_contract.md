# Phase 4 Design Contract

## goal
Connect the Scenario-3 orchestrator to NetBox as a source of truth for inventory resolution, with minimal operational write-back.

## inputs
- A working NetBox instance
- API base URL
- API token
- inventory source selection in config: `yaml | netbox`
- A populated minimum lab inventory in NetBox
- Required device custom fields:
  - `upgrade_candidate`
  - `transfer_method`
- Required write-back custom fields:
  - `precheck_status`
  - `backup_path`
  - `backup_timestamp`

## outputs
- Device records resolved from NetBox in orchestrator-compatible shape
- Minimal device-level write-back after Stage 1 operations
- Stage 2 remains handoff-driven for execution
- Minimal final-result write-back after Stage 2 completion
- A clear source-of-truth path for future provider-driven execution

## source selection policy
- `inventory.source` is explicit: `yaml` or `netbox`
- v1 does not enable automatic fallback
- If `source=netbox`, YAML is ignored for runtime inventory resolution
- If NetBox read fails, the run fails
- Fallback-chain behavior is deferred to a later version

## minimal read use cases
- Read active devices from NetBox for the target lab/site
- Read device identity, management IP, OS/platform-related metadata, and selection metadata
- Filter devices by `upgrade_candidate=true`
- Normalize NetBox records into orchestrator inventory shape

## Stage 2 execution model
- Stage 2 execution remains handoff-driven
- Stage 2 does not rebuild runtime targets from NetBox for device execution
- Stage 2 consumes Stage 1 handoff as its operational input
- In v1, NetBox is used in Stage 2 only for device ID mapping and final result write-back when `inventory.source=netbox`

## minimal write-back use cases
- Write back `precheck_status`
- Write back `backup_path`
- Write back `backup_timestamp`
- Write back final `stage2_result`

## failure policy
- Read path is fail-closed
- If a selected device (`upgrade_candidate=true`) is missing required fields, the run fails validation before Stage 1 execution
- Write-back failures do not invalidate completed device work, but they must be logged and surfaced as sync warnings
- `precheck_no_reload` does not write a final Stage 2 result because no final Stage 2 outcome exists yet
- Silent fallback to YAML is not allowed in v1
