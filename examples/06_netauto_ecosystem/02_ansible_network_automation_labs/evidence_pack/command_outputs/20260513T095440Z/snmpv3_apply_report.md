# IOS SNMPv3 Apply Report

Run ID: `20260513T095440Z`

| Host | Mgmt IP | View existed before | Group existed before | User existed before | View changed | Group changed | User changed | Any changed |
|---|---|---|---|---|---|---|---|---|
| csr1000v | 192.168.2.64 | True | True | True | False | False | False | False |
| iol_r1 | 192.168.2.65 | True | True | True | False | False | False | False |

## Notes

This playbook checks existing SNMP server configuration with:

`show running-config | include ^snmp-server`

It then uses name-based regex checks to decide whether the SNMPv3 view, group, or user already exists.

Current behavior is existence-based by object name, not full drift correction.

The SNMPv3 user task uses `no_log: true` because it contains authentication and privacy passwords.
