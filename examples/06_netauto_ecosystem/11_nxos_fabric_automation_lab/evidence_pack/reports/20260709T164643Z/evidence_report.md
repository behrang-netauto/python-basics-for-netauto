# NX-OS Fabric Evidence Report


## 1. What this report is

This report documents a read-only evidence collection run against the NX-OS EVPN fabric.

The playbook collected operational command output from the devices in scope and stored the raw evidence files for later review.  
No configuration changes were applied by this playbook.

**Fabric:** `nxos_multisite_evpn_lab`  
**Site:** `multisite_lab`  
**Run ID:** `20260709T164643Z`  
**Generated from:** Ansible evidence collection

---

## 2. Collection summary

This run included **8** device(s).  
Collection results were registered for **8** device(s).

| Item | Value |
|---|---|
| Collection type | Read-only |
| Configuration changes | None |
| Raw evidence root | `evidence_pack/raw/20260709T164643Z/` |
| Report purpose | Evidence index and collection overview |

---

## 3. Devices in scope

| Device | Role | Management IP | EVE node | Result |
|---|---|---:|---|---|
| `spine1` | spine | `192.168.2.140` | NXOS | collected |
| `spine2` | spine | `192.168.2.146` | NXOS18 | collected |
| `bgw1` | border_gateway | `192.168.2.141` | NXOS2 | collected |
| `bgw2` | border_gateway | `192.168.2.145` | NXOS17 | collected |
| `leaf1` | leaf | `192.168.2.142` | NXOS3 | collected |
| `leaf2` | leaf | `192.168.2.143` | NXOS5 | collected |
| `leaf3` | leaf | `192.168.2.144` | NXOS6 | collected |
| `dci` | dci | `192.168.2.147` | NXOS19 | collected |

---

## 4. Per-device collection notes


### spine1

**Role:** spine  
**Management IP:** `192.168.2.140`  
**EVE node:** NXOS  
**Raw evidence path:** `evidence_pack/raw/20260709T164643Z/spine1/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `underlay` | collected | 5 |
| `bgp_evpn` | collected | 4 |
| `vxlan_nve` | collected | 4 |
| `vlan_vni_vrf` | collected | 5 |
| `host_learning` | collected | 3 |



### spine2

**Role:** spine  
**Management IP:** `192.168.2.146`  
**EVE node:** NXOS18  
**Raw evidence path:** `evidence_pack/raw/20260709T164643Z/spine2/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `underlay` | collected | 5 |
| `bgp_evpn` | collected | 4 |
| `vxlan_nve` | collected | 4 |
| `vlan_vni_vrf` | collected | 5 |
| `host_learning` | collected | 3 |



### bgw1

**Role:** border_gateway  
**Management IP:** `192.168.2.141`  
**EVE node:** NXOS2  
**Raw evidence path:** `evidence_pack/raw/20260709T164643Z/bgw1/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `underlay` | collected | 5 |
| `bgp_evpn` | collected | 4 |
| `vxlan_nve` | collected | 4 |
| `vlan_vni_vrf` | collected | 5 |
| `host_learning` | collected | 3 |



### bgw2

**Role:** border_gateway  
**Management IP:** `192.168.2.145`  
**EVE node:** NXOS17  
**Raw evidence path:** `evidence_pack/raw/20260709T164643Z/bgw2/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `underlay` | collected | 5 |
| `bgp_evpn` | collected | 4 |
| `vxlan_nve` | collected | 4 |
| `vlan_vni_vrf` | collected | 5 |
| `host_learning` | collected | 3 |



### leaf1

**Role:** leaf  
**Management IP:** `192.168.2.142`  
**EVE node:** NXOS3  
**Raw evidence path:** `evidence_pack/raw/20260709T164643Z/leaf1/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `underlay` | collected | 5 |
| `bgp_evpn` | collected | 4 |
| `vxlan_nve` | collected | 4 |
| `vlan_vni_vrf` | collected | 5 |
| `host_learning` | collected | 3 |



### leaf2

**Role:** leaf  
**Management IP:** `192.168.2.143`  
**EVE node:** NXOS5  
**Raw evidence path:** `evidence_pack/raw/20260709T164643Z/leaf2/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `underlay` | collected | 5 |
| `bgp_evpn` | collected | 4 |
| `vxlan_nve` | collected | 4 |
| `vlan_vni_vrf` | collected | 5 |
| `host_learning` | collected | 3 |



### leaf3

**Role:** leaf  
**Management IP:** `192.168.2.144`  
**EVE node:** NXOS6  
**Raw evidence path:** `evidence_pack/raw/20260709T164643Z/leaf3/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `underlay` | collected | 5 |
| `bgp_evpn` | collected | 4 |
| `vxlan_nve` | collected | 4 |
| `vlan_vni_vrf` | collected | 5 |
| `host_learning` | collected | 3 |



### dci

**Role:** dci  
**Management IP:** `192.168.2.147`  
**EVE node:** NXOS19  
**Raw evidence path:** `evidence_pack/raw/20260709T164643Z/dci/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `underlay` | collected | 5 |
| `bgp_evpn` | collected | 4 |
| `vxlan_nve` | collected | 4 |
| `vlan_vni_vrf` | collected | 5 |
| `host_learning` | collected | 3 |



---

## 5. Command reference

The following command groups were used by the playbook.  
This section is a reference only; the raw command outputs are stored under the evidence directory.

### platform

- `show version`
- `show running-config | include ^hostname`
- `show feature`
- `show interface brief`
- `show ip interface brief vrf all`
- `show vrf`

### underlay

- `show ip ospf neighbors`
- `show ip route`
- `show ip route vrf all`
- `show ip pim neighbor`
- `show ip pim interface`

### bgp_evpn

- `show bgp l2vpn evpn summary`
- `show bgp l2vpn evpn`
- `show bgp l2vpn evpn route-type 2`
- `show bgp l2vpn evpn route-type 5`

### vxlan_nve

- `show nve peers`
- `show nve vni`
- `show interface nve1`
- `show running-config interface nve1`

### vlan_vni_vrf

- `show vlan brief`
- `show vn-segment`
- `show vrf`
- `show running-config bgp`
- `show running-config | section nv overlay`

### host_learning

- `show mac address-table`
- `show l2route evpn mac all`
- `show ip arp vrf all`


---

## 6. Limits of this report

This report is an evidence index, not a validation verdict.

It confirms which devices were included in the collection run, which command groups were attempted, and where the raw outputs were saved.  
It does not by itself prove that the EVPN control plane, VXLAN data plane, tenant reachability, or fabric redundancy are fully correct.

Further interpretation should be done by reviewing the raw command outputs and, if needed, adding manual observations in a separate analysis note.
