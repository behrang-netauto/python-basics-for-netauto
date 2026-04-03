# Write-Back Contract

## purpose
Define the minimum Stage 1 and Stage 2 write-back behavior for the first NetBox integration pass.

## write-back target
Device-level custom fields in NetBox.

## required write-back fields
- `precheck_status`
- `backup_path`
- `backup_timestamp`
- `stage2_result`

## field semantics

### precheck_status
Represents the result of the device precheck phase.

allowed values in v1:
- `passed`
- `failed`

### backup_path
Stores the artifact path of the saved backup/config file for the device.

### backup_timestamp
Stores the UTC timestamp when the backup artifact was created.

Suggested format:
- ISO-8601 UTC string

### stage2_result
Represents the final result of the Stage 2 reload/post-check workflow.

allowed values in v1:
- `passed`
- `failed`

meaning:
- `passed` only when reload was accepted, SSH came back, and post-check passed
- `failed` if any of those failed

## write timing

### write-back 1
After Stage 1 precheck result is determined:
- write `precheck_status`

### write-back 2
After backup artifact is successfully created:
- write `backup_path`
- write `backup_timestamp`

### write-back 3
After Stage 2 final result is known:
- write `stage2_result`

## write scope
- Write-back is device-level
- Updates are performed per device
- v1 does not require bulk or batched write-back

## failure behavior
- Write-back failure must not silently pass
- Write-back failure must be logged
- Write-back failure must be surfaced in the run summary as a sync warning
- A successful device operation is not rolled back only because NetBox write-back failed
- In `precheck_no_reload` mode, Stage 2 does not write `stage2_result`

## non-goals
- No journal entries in v1
- No detailed operator trace in NetBox in v1
- No historical multi-record logging model in v1
- No Stage 2 reason mirroring in NetBox custom fields in v1
