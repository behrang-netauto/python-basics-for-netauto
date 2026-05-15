# IOS Baseline Apply Report

Run ID: `20260515T115850Z`

| Host | Mgmt IP | Platform | Global changed | Loopback changed | Any changed |
|---|---|---|---|---|---|---|
| csr1000v | 192.168.2.64 | iosxe | False | False | False |
| iol_r1 | 192.168.2.65 | iosxe | False | False | False |

## Expected idempotency behavior

First run may show `changed=true`.

A second run with the same variables should normally return `changed=false`
if the device configuration already matches the intended baseline.

## Baseline scope

- logging buffered
- service timestamps
- no ip domain-lookup
- data-driven loopback interface configuration from `baseline_loopbacks`

## Baseline interface targets

### csr1000v

- Loopback100: 10.255.100.1 255.255.255.255
- Loopback200: 10.255.200.1 255.255.255.255

### iol_r1

- Loopback100: 10.255.100.2 255.255.255.255
- Loopback200: 10.255.200.2 255.255.255.255

