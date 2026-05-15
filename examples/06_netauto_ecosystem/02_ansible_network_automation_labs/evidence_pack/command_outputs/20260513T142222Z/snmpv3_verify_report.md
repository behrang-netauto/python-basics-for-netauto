# IOS SNMPv3 Verification Report

Run ID: `20260513T142222Z`

Commands used:

`show snmp user`, `show snmp group`, `show snmp engineID`, `show running-config | section snmp`

| Host | Mgmt IP | User verified | Group verified | View in config | EngineID seen | SNMP config lines | Passed |
|---|---|---|---|---|---|---|---|
| csr1000v | 192.168.2.64 | True | True | True | True | 2 | True |
| iol_r1 | 192.168.2.65 | True | True | True | True | 2 | True |

## Notes

This playbook collects SNMPv3 verification evidence after configuration.

It uses:
- `map(attribute='command')` to extract command strings from structured verification checks
- `join()` to list verification commands in the report
- `regex_search` to verify user, group, and view presence
- `split('\n')`, `reject()`, `list`, and `length` to count non-empty SNMP config lines

Raw command outputs are stored under:

`evidence_pack/command_outputs/20260513T142222Z/snmpv3_verify_outputs/`

Review raw outputs before committing.
