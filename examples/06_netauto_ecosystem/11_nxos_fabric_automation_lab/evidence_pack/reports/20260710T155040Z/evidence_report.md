# NX-OS Fabric Evidence Report


## 1. What this report is

This report documents a read-only evidence collection run against the NX-OS EVPN fabric.

The playbook collected operational command output from the devices in scope and stored the raw evidence files for later review.  
No configuration changes were applied by this playbook.

**Fabric:** `nxos_multisite_evpn_lab`  
**Site:** `multisite_lab`  
**Run ID:** `20260710T155040Z`  
**Generated from:** Ansible evidence collection

---

## 2. Collection summary

This run included **8** device(s).  
Collection results were registered for **8** device(s).

| Item | Value |
|---|---|
| Collection type | Read-only |
| Configuration changes | None |
| Raw evidence root | `evidence_pack/raw/20260710T155040Z/` |
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
**Raw evidence path:** `evidence_pack/raw/20260710T155040Z/spine1/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `site_underlay` | collected | 4 |
| `evpn_control_plane` | collected | 5 |
| `bgp_configuration` | collected | 1 |



### spine2

**Role:** spine  
**Management IP:** `192.168.2.146`  
**EVE node:** NXOS18  
**Raw evidence path:** `evidence_pack/raw/20260710T155040Z/spine2/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `site_underlay` | collected | 4 |
| `evpn_control_plane` | collected | 5 |
| `bgp_configuration` | collected | 1 |



### bgw1

**Role:** border_gateway  
**Management IP:** `192.168.2.141`  
**EVE node:** NXOS2  
**Raw evidence path:** `evidence_pack/raw/20260710T155040Z/bgw1/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `site_underlay` | collected | 4 |
| `evpn_control_plane` | collected | 5 |
| `bgp_configuration` | collected | 1 |
| `vxlan_nve` | collected | 4 |
| `tenant_state` | collected | 5 |
| `multisite_state` | collected | 4 |



### bgw2

**Role:** border_gateway  
**Management IP:** `192.168.2.145`  
**EVE node:** NXOS17  
**Raw evidence path:** `evidence_pack/raw/20260710T155040Z/bgw2/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `site_underlay` | collected | 4 |
| `evpn_control_plane` | collected | 5 |
| `bgp_configuration` | collected | 1 |
| `vxlan_nve` | collected | 4 |
| `tenant_state` | collected | 5 |
| `multisite_state` | collected | 4 |



### leaf1

**Role:** leaf  
**Management IP:** `192.168.2.142`  
**EVE node:** NXOS3  
**Raw evidence path:** `evidence_pack/raw/20260710T155040Z/leaf1/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `site_underlay` | collected | 4 |
| `evpn_control_plane` | collected | 5 |
| `bgp_configuration` | collected | 1 |
| `vxlan_nve` | collected | 4 |
| `tenant_state` | collected | 5 |



### leaf2

**Role:** leaf  
**Management IP:** `192.168.2.143`  
**EVE node:** NXOS5  
**Raw evidence path:** `evidence_pack/raw/20260710T155040Z/leaf2/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `site_underlay` | collected | 4 |
| `evpn_control_plane` | collected | 5 |
| `bgp_configuration` | collected | 1 |
| `vxlan_nve` | collected | 4 |
| `tenant_state` | collected | 5 |



### leaf3

**Role:** leaf  
**Management IP:** `192.168.2.144`  
**EVE node:** NXOS6  
**Raw evidence path:** `evidence_pack/raw/20260710T155040Z/leaf3/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `site_underlay` | collected | 4 |
| `evpn_control_plane` | collected | 5 |
| `bgp_configuration` | collected | 1 |
| `vxlan_nve` | collected | 4 |
| `tenant_state` | collected | 5 |



### dci

**Role:** dci  
**Management IP:** `192.168.2.147`  
**EVE node:** NXOS19  
**Raw evidence path:** `evidence_pack/raw/20260710T155040Z/dci/`

The playbook registered command output for this device in the following category group(s):

| Category | Result | Commands attempted |
|---|---|---:|
| `platform` | collected | 6 |
| `evpn_control_plane` | collected | 5 |
| `bgp_configuration` | collected | 1 |
| `dci_state` | collected | 3 |



---

## 5. Command reference

The following command groups were used by the playbook.  
This section is a reference only; the raw command outputs are stored under the evidence directory.

### platform

**Roles:** `spine, leaf, border_gateway, dci`

- `show version`
- `show running-config | include ^hostname`
- `show feature`
- `show interface brief`
- `show ip interface brief vrf all`
- `show vrf`

### site_underlay

**Roles:** `spine, leaf, border_gateway`

- `show ip ospf neighbors`
- `show ip route`
- `show ip pim neighbor`
- `show ip pim interface`

### evpn_control_plane

**Roles:** `spine, leaf, border_gateway, dci`

- `show bgp l2vpn evpn summary`
- `show bgp l2vpn evpn`
- `show bgp l2vpn evpn route-type 2`
- `show bgp l2vpn evpn route-type 3`
- `show bgp l2vpn evpn route-type 5`

### bgp_configuration

**Roles:** `spine, leaf, border_gateway, dci`

- `show running-config | section bgp`

### vxlan_nve

**Roles:** `leaf, border_gateway`

- `show nve peers`
- `show nve vni`
- `show interface nve1`
- `show running-config interface nve1`

### tenant_state

**Roles:** `leaf, border_gateway`

- `show vlan brief`
- `show ip route vrf all`
- `show mac address-table`
- `show l2route evpn mac-ip all`
- `show ip arp vrf all`

### multisite_state

**Roles:** `border_gateway`

- `show running-config | include evpn`
- `show running-config | include fabric-tracking`
- `show running-config | include dci-tracking`
- `show running-config interface loopback100`

### dci_state

**Roles:** `dci`

- `show bgp ipv4 unicast summary`
- `show ip route`
- `show running-config interface loopback0`


---

## 6. Limits of this report

This report is an evidence index, not a validation verdict.

It confirms which devices were included in the collection run, which command groups were attempted, and where the raw outputs were saved.  
It does not by itself prove that the EVPN control plane, VXLAN data plane, tenant reachability, or fabric redundancy are fully correct.

Further interpretation should be done by reviewing the raw command outputs and, if needed, adding manual observations in a separate analysis note.
