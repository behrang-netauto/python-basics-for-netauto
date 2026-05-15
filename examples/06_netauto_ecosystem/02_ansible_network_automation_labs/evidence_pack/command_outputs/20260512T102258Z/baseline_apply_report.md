# IOS Baseline Apply Report

Run ID: `20260512T102258Z`

| Host | Mgmt IP | Platform | Global changed | Loopback changed | Any changed |
|---|---|---|---|---|---|---|
| csr1000v | 192.168.2.64 | ios | True | True | True |
| iol_r1 | 192.168.2.65 | ios | True | True | True |

## Expected idempotency behavior

First run may show `changed=true`.

A second run with the same variables should normally return `changed=false`
if the device configuration already matches the intended baseline.

## Baseline scope

- logging buffered
- service timestamps
- no ip domain-lookup
- Loopback100 description and IP address
