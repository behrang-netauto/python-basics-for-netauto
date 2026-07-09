# Topology Notes

## Purpose

This file documents the working topology assumptions for the NX-OS fabric automation lab.

The current phase is discovery and evidence collection. These notes are intentionally lightweight and may be updated after reviewing the collected raw evidence.

## Scenario source

The lab is based on a VXLAN EVPN multisite scenario.

The reference scenario contains two EVPN sites connected through a DCI layer:

- Site 1 uses AS 65001.
- Site 2 uses AS 65002.
- The DCI node uses AS 65003.
- BGW nodes connect each site to the DCI layer.
- The overlay uses BGP EVPN.
- The internal site underlay uses OSPF and PIM.
- The DCI side uses external BGP connectivity.

## High-level topology

```text
                 +----------------+
                 |   DCI / NXOS19 |
                 |     AS 65003   |
                 +-------+--------+
                         |
              +----------+----------+
              |                     |
        +-----+-----+         +-----+-----+
        |   BGW1    |         |   BGW2    |
        |   AS65001 |         |   AS65002 |
        +-----+-----+         +-----+-----+
              |                     |
        +-----+-----+         +-----+-----+
        |  Spine1   |         |  Spine2   |
        |  Site 1   |         |  Site 2   |
        +-----+-----+         +-----+-----+
              |                     |
        +-----+-----+       +------+------+
        |   Leaf1   |       | Leaf2/Leaf3 |
        |  Site 1   |       |   Site 2    |
        +-----------+       +-------------+

                         +----------+
                         | WAN / R9 |
                         +----------+
```

## Lab node mapping

The EVE-NG management addresses used by this project are:

| Logical name | EVE node | Role | Management IP | Notes |
|---|---|---|---:|---|
| `spine1` | NXOS | Spine | `192.168.2.140` | Site 1 spine |
| `bgw1` | NXOS2 | Border gateway | `192.168.2.141` | Site 1 BGW |
| `leaf1` | NXOS3 | Leaf | `192.168.2.142` | Site 1 leaf |
| `leaf2` | NXOS5 | Leaf | `192.168.2.143` | Site 2 leaf |
| `leaf3` | NXOS6 | Leaf | `192.168.2.144` | Site 2 leaf |
| `bgw2` | NXOS17 | Border gateway | `192.168.2.145` | Site 2 BGW |
| `spine2` | NXOS18 | Spine | `192.168.2.146` | Site 2 spine |
| `dci` | NXOS19 | DCI | `192.168.2.147` | DCI / inter-site node |
| `wan_r9` | R9 | WAN router | `192.168.2.148` | Present in the EVE-NG lab; not part of the original reference topology |

## Site model

### Site 1

Expected role grouping:

```text
Site 1 / AS 65001
├── BGW1
├── Spine1
└── Leaf1
```

Known addressing from the reference design:

```text
Leaf1:
  Lo0: 10.2.0.2/32
  Lo1: 10.3.0.1/32

Spine1:
  Lo0: 10.2.0.3/32
  Lo254: 10.254.254.1/32

BGW1:
  Lo0: 10.2.0.1/32
  Lo1: 10.3.0.2/32
  Lo100: 10.10.0.2/32
```

### Site 2

Expected role grouping:

```text
Site 2 / AS 65002
├── BGW2
├── Spine2
├── Leaf2
└── Leaf3
```

Known addressing from the reference design:

```text
BGW2:
  Lo0: 20.2.0.1/32
  Lo1: 20.3.0.2/32
  Lo100: 10.10.0.1/32

Spine2:
  Lo0: 20.2.0.4/32
  Lo254: 20.254.254.1/32

Leaf2:
  Lo0: 20.2.0.2/32
  Lo1: 20.3.0.1/32

Leaf3:
  Lo0: 20.2.0.3/32
  Lo1: 20.3.0.3/32
```

### DCI

Expected role grouping:

```text
DCI / AS 65003
└── DCI node
```

Known addressing from the reference design:

```text
DCI:
  Lo0: 100.100.100.100/32
```

### WAN node

The current EVE-NG lab also includes a WAN router:

```text
WAN / R9:
  Management IP: 192.168.2.148
```

The WAN node is included in the inventory model for completeness, but the current evidence collection playbook targets the NX-OS fabric nodes.

## Tenant and VNI notes

The reference scenario includes:

| Item | Value |
|---|---|
| VRF | `myvrf_50000` |
| L3VNI | `50000` |
| VLAN 250 | L2VNI `30001` |
| VLAN 300 | L2VNI `30000` |

Known gateway examples:

```text
VLAN 250:
  Anycast gateway: 10.10.10.1

VLAN 300:
  Anycast gateway: 10.10.11.1
```

Known server examples from the reference scenario:

```text
Server-1: 10.10.10.10
Server-2: 10.10.10.11
Server-3: 10.10.11.11
```

## Automation scope

The current playbook only collects read-only evidence.

It does not:

- configure NX-OS devices
- repair the fabric
- validate tenant reachability
- prove that the EVPN control plane is correct
- prove that the VXLAN data plane is correct

The first review step after collection is to inspect the raw evidence files under:

```text
evidence_pack/raw/<run_id>/
```

## Notes for later review

After reviewing raw evidence, update this file with:

- confirmed hostname mapping
- confirmed loopback addresses
- confirmed BGP AS numbers
- confirmed NVE peer state
- confirmed VNI state
- confirmed EVPN route types
- any mismatch between the reference topology and the active EVE-NG lab
