# NX-OS Fabric Evidence Report

## 1. Run overview

This report documents a non-configuring evidence acquisition run against the
NX-OS VXLAN EVPN fabric. It combines read-only device commands with controlled
active reachability probes and running-configuration snapshots. No device
configuration changes were applied.

| Item | Value |
|---|---|
| Fabric | `nxos_multisite_evpn_lab` |
| Site | `multisite_lab` |
| Run ID | `20260723T155701Z` |
| Started | `2026-07-23T15:57:01Z` |
| Completed | `2026-07-23T16:03:22Z` |
| Collection status | **complete** |

`Collection status` describes evidence completeness only. It is not a verdict
about fabric health.

---

## 2. Collection summary

| Stage | Planned | Completed or executed | Collection errors |
|---|---:|---:|---:|
| Baseline | 180 | 180 | 0 |
| Configuration snapshots | 8 | 8 | 0 |
| Traffic probes | 9 | 9 | 0 |
| Post-probe | 23 | 23 | 0 |

The measured probe output is retained as evidence. Warmup traffic may be sent
before measurement to populate ARP and MAC learning state, but its output is
intentionally not stored.

---

## 3. Baseline evidence

The baseline stage contains platform, underlay, EVPN, VXLAN, tenant, Multisite,
DCI, and pre-traffic learning evidence selected according to device role.

| Device | Role | Management IP | Commands | Result | Raw path |
|---|---|---|---:|---|---|
| `spine1` | spine | `192.168.2.140` | 16/16 | complete | `raw/20260723T155701Z/baseline/spine1/` |
| `spine2` | spine | `192.168.2.146` | 16/16 | complete | `raw/20260723T155701Z/baseline/spine2/` |
| `bgw1` | border_gateway | `192.168.2.141` | 29/29 | complete | `raw/20260723T155701Z/baseline/bgw1/` |
| `bgw2` | border_gateway | `192.168.2.145` | 29/29 | complete | `raw/20260723T155701Z/baseline/bgw2/` |
| `leaf1` | leaf | `192.168.2.142` | 25/25 | complete | `raw/20260723T155701Z/baseline/leaf1/` |
| `leaf2` | leaf | `192.168.2.143` | 25/25 | complete | `raw/20260723T155701Z/baseline/leaf2/` |
| `leaf3` | leaf | `192.168.2.144` | 25/25 | complete | `raw/20260723T155701Z/baseline/leaf3/` |
| `dci` | dci | `192.168.2.147` | 15/15 | complete | `raw/20260723T155701Z/baseline/dci/` |

---

## 4. Running-configuration snapshots

Each NX-OS device has a plain-text running-configuration snapshot for the
subsequent configuration compliance assessment.

| Device | Role | Management IP | Result | Raw file |
|---|---|---|---|---|
| `spine1` | spine | `192.168.2.140` | collected | `raw/20260723T155701Z/configuration_snapshots/spine1/running_config.cfg` |
| `spine2` | spine | `192.168.2.146` | collected | `raw/20260723T155701Z/configuration_snapshots/spine2/running_config.cfg` |
| `bgw1` | border_gateway | `192.168.2.141` | collected | `raw/20260723T155701Z/configuration_snapshots/bgw1/running_config.cfg` |
| `bgw2` | border_gateway | `192.168.2.145` | collected | `raw/20260723T155701Z/configuration_snapshots/bgw2/running_config.cfg` |
| `leaf1` | leaf | `192.168.2.142` | collected | `raw/20260723T155701Z/configuration_snapshots/leaf1/running_config.cfg` |
| `leaf2` | leaf | `192.168.2.143` | collected | `raw/20260723T155701Z/configuration_snapshots/leaf2/running_config.cfg` |
| `leaf3` | leaf | `192.168.2.144` | collected | `raw/20260723T155701Z/configuration_snapshots/leaf3/running_config.cfg` |
| `dci` | dci | `192.168.2.147` | collected | `raw/20260723T155701Z/configuration_snapshots/dci/running_config.cfg` |

---

## 5. Measured traffic probes

The probe return code and command output are recorded as observations. This
report does not translate them into `PASS`, `FAIL`, or `NOT TESTED`; that belongs
to the assessment phase.

| Probe | Category | Source | Source interface | Destination | Execution | Return code | Raw file |
|---|---|---|---|---|---|---:|---|
| `server1_to_gateway` | gateway | `server1` | `eth0` | `10.10.10.1` | completed | 1 | `raw/20260723T155701Z/traffic_probes/server1_to_gateway.txt` |
| `server2_to_gateway` | gateway | `server2` | `eth0` | `10.10.10.1` | completed | 0 | `raw/20260723T155701Z/traffic_probes/server2_to_gateway.txt` |
| `server3_to_gateway` | gateway | `server3` | `eth0` | `10.10.11.1` | completed | 0 | `raw/20260723T155701Z/traffic_probes/server3_to_gateway.txt` |
| `server1_to_server2` | same_subnet | `server1` | `eth0` | `10.10.10.11` | completed | 1 | `raw/20260723T155701Z/traffic_probes/server1_to_server2.txt` |
| `server2_to_server1` | same_subnet | `server2` | `eth0` | `10.10.10.10` | completed | 1 | `raw/20260723T155701Z/traffic_probes/server2_to_server1.txt` |
| `server1_to_server3` | inter_subnet | `server1` | `eth0` | `10.10.11.11` | completed | 1 | `raw/20260723T155701Z/traffic_probes/server1_to_server3.txt` |
| `server3_to_server1` | inter_subnet | `server3` | `eth0` | `10.10.10.10` | completed | 1 | `raw/20260723T155701Z/traffic_probes/server3_to_server1.txt` |
| `server2_to_server3` | inter_subnet | `server2` | `eth0` | `10.10.11.11` | completed | 0 | `raw/20260723T155701Z/traffic_probes/server2_to_server3.txt` |
| `server3_to_server2` | inter_subnet | `server3` | `eth0` | `10.10.10.11` | completed | 0 | `raw/20260723T155701Z/traffic_probes/server3_to_server2.txt` |

Important distinction:

- A measured Ping that returns packet loss is still a successfully collected observation.
- A probe without a registered measurement is a collection error.

---

## 6. Post-probe evidence

Post-probe collection repeats the same comparison command groups and filenames
used in the baseline stage. The separate stage directories prevent overwrite
and make direct file comparison possible.

| Device | Role | Management IP | Commands | Result | Raw path |
|---|---|---|---:|---|---|
| `spine1` | spine | `192.168.2.140` | 1/1 | complete | `raw/20260723T155701Z/post_probe/spine1/` |
| `spine2` | spine | `192.168.2.146` | 1/1 | complete | `raw/20260723T155701Z/post_probe/spine2/` |
| `bgw1` | border_gateway | `192.168.2.141` | 4/4 | complete | `raw/20260723T155701Z/post_probe/bgw1/` |
| `bgw2` | border_gateway | `192.168.2.145` | 4/4 | complete | `raw/20260723T155701Z/post_probe/bgw2/` |
| `leaf1` | leaf | `192.168.2.142` | 4/4 | complete | `raw/20260723T155701Z/post_probe/leaf1/` |
| `leaf2` | leaf | `192.168.2.143` | 4/4 | complete | `raw/20260723T155701Z/post_probe/leaf2/` |
| `leaf3` | leaf | `192.168.2.144` | 4/4 | complete | `raw/20260723T155701Z/post_probe/leaf3/` |
| `dci` | dci | `192.168.2.147` | 1/1 | complete | `raw/20260723T155701Z/post_probe/dci/` |

Example comparison:

```bash
diff -u \
  evidence_pack/raw/20260723T155701Z/baseline/leaf1/tenant_learning.txt \
  evidence_pack/raw/20260723T155701Z/post_probe/leaf1/tenant_learning.txt
```

---

## 7. Artifact locations

| Artifact | Path |
|---|---|
| Raw evidence | `evidence_pack/raw/20260723T155701Z/` |
| Structured results | `evidence_pack/structured/20260723T155701Z/collection_results.json` |
| This report | `evidence_pack/reports/20260723T155701Z/evidence_report.md` |

---

## 8. Collection plan reference

### Baseline-only command groups

#### platform

**Roles:** `spine, leaf, border_gateway, dci`

- `show version`
- `show running-config | include ^hostname`
- `show feature`
- `show interface brief`
- `show ip interface brief vrf all`
- `show vrf`

#### site_underlay

**Roles:** `spine, leaf, border_gateway`

- `show ip ospf neighbors`
- `show ip route`
- `show ip pim neighbor`
- `show ip pim interface`

#### evpn_control_plane

**Roles:** `spine, leaf, border_gateway, dci`

- `show bgp l2vpn evpn summary`
- `show bgp l2vpn evpn`
- `show bgp l2vpn evpn route-type 3`
- `show bgp l2vpn evpn route-type 5`

#### bgp_configuration

**Roles:** `spine, leaf, border_gateway, dci`

- `show running-config | section bgp`

#### vxlan_nve

**Roles:** `leaf, border_gateway`

- `show nve peers`
- `show nve vni`
- `show interface nve1`
- `show running-config interface nve1`

#### tenant_state

**Roles:** `leaf, border_gateway`

- `show vlan brief`
- `show ip route vrf all`

#### multisite_state

**Roles:** `border_gateway`

- `show running-config | include evpn`
- `show running-config | include fabric-tracking`
- `show running-config | include dci-tracking`
- `show running-config interface loopback100`

#### dci_state

**Roles:** `dci`

- `show bgp ipv4 unicast summary`
- `show ip route`
- `show running-config interface loopback0`


### Pre/post comparison command groups

#### tenant_learning

**Roles:** `leaf, border_gateway`

- `show mac address-table`
- `show ip arp vrf all`
- `show l2route evpn mac-ip all`

#### evpn_type2_learning

**Roles:** `spine, leaf, border_gateway, dci`

- `show bgp l2vpn evpn route-type 2`


---

## 9. Report limits

This report is an evidence index and collection overview. It confirms what was
attempted, what was captured, and where the artifacts were written. It does not
determine whether OSPF, BGP EVPN, NVE/VNI state, endpoint learning, or end-to-end
reachability are correct. Deterministic parsing and expected-state comparison
belong to the subsequent assessment phase.
