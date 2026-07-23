# NX-OS Fabric Automation Lab

This project is a multi-phase automation lab built around an NX-OS VXLAN EVPN Multisite fabric in EVE-NG.

Phase 1 collects operational evidence from the fabric, captures the running configuration of each NX-OS device and runs controlled reachability probes from Linux endpoints. It does not decide whether the network is healthy. Its job is to capture a complete, reviewable record that can be assessed later without reconnecting to the lab.

No device configuration is changed during this phase.

## Lab scope

The topology includes:

- Site 1 in AS 65001
- Site 2 in AS 65002
- a DCI node in AS 65003
- two border gateways
- three leaf switches and two spines
- OSPF and PIM in the site underlays
- BGP EVPN across the overlay and DCI
- L2VNI and L3VNI tenant services
- three Alpine Linux endpoints connected to the leaf switches

The endpoint addressing used by the probes is:

| Endpoint | Attached leaf | Data-plane address | Default gateway |
|---|---|---|---|
| `server1` | `leaf1` | `10.10.10.10/24` | `10.10.10.1` |
| `server2` | `leaf2` | `10.10.10.11/24` | `10.10.10.1` |
| `server3` | `leaf3` | `10.10.11.11/24` | `10.10.11.1` |

Each endpoint has a separate management interface for Ansible and uses `eth0` for test traffic.

## Phase 1 workflow

The collection flow is:

```text
running-configuration snapshot and baseline collection
        ↓
endpoint traffic probes
        ↓
post-probe learning collection
        ↓
structured results and Markdown report
```

### Baseline collection

NX-OS commands are selected by device role and executed independently. The baseline covers:

- platform and interface state
- OSPF/PIM underlay state
- BGP EVPN control plane
- BGP configuration
- NVE peers and VNIs
- tenant VLAN and routing state
- Multisite and DCI state
- MAC, ARP and EVPN Type-2 learning before the probes

If an individual command fails, the remaining commands still run. The failure is preserved in the raw output and the run is marked `partial` instead of being silently discarded.

### Running-configuration snapshots

The playbook runs `show running-config` once on every in-scope NX-OS device and stores the returned configuration separately from the operational command output:

```text
raw/<RUN_ID>/configuration_snapshots/<device>/running_config.cfg
```

These snapshots provide the configuration input for the section-aware compliance checks planned for Phase 2. They are observed device state, not golden configurations.

Snapshot files are written with mode `0600`. Because a running configuration can still contain sensitive values, the files should be reviewed and sanitized before they are added to a public repository.

### Endpoint traffic probes

Nine reachability measurements are run from the Alpine endpoints:

- three endpoint-to-gateway probes
- two same-subnet probes, one in each direction
- four inter-subnet probes, covering both directions between the sites

Before each measurement, two preliminary packets are sent to populate ARP and MAC state. Only the following five-packet measurement is retained in the evidence pack.

Each measured probe uses a fixed packet count:

```bash
ping -I <interface> -c 5 -i 1 -W 2 <destination>
```

The command, standard output, standard error and return code are stored for every probe. A return code of `1` is still a successfully collected measurement; it means the ping did not meet its success condition. A missing execution result is a collection error.

### Post-probe collection

After the traffic tests, the playbook collects the learning-related command groups again. Baseline and post-probe files use the same names, so changes in MAC, ARP and EVPN Type-2 state can be compared directly.

For example:

```bash
diff -u \
  evidence_pack/raw/<RUN_ID>/baseline/leaf1/tenant_learning.txt \
  evidence_pack/raw/<RUN_ID>/post_probe/leaf1/tenant_learning.txt
```

## Collection plan

`collection_plan.yml` is the declarative input for Phase 1. It defines:

- baseline-only command groups
- command groups collected both before and after the probes
- probe defaults
- probe source, destination and category

The playbook combines this data with the inventory at runtime. The rendered command used for a probe is also the command written to the raw and structured artifacts.

## Evidence layout

Every execution receives a UTC run ID and writes all artifacts under that ID:

```text
evidence_pack/
├── raw/
│   └── <RUN_ID>/
│       ├── baseline/
│       │   └── <device>/
│       │       └── <command_group>.txt
│       ├── configuration_snapshots/
│       │   └── <device>/
│       │       └── running_config.cfg
│       ├── traffic_probes/
│       │   └── <probe_id>.txt
│       └── post_probe/
│           └── <device>/
│               └── <command_group>.txt
├── structured/
│   └── <RUN_ID>/
│       └── collection_results.json
└── reports/
    └── <RUN_ID>/
        └── evidence_report.md
```

The three output forms serve different purposes:

- `raw/` preserves command-level evidence, configuration snapshots and probe output for review and troubleshooting.
- `collection_results.json` provides a stable input for automated assessment.
- `evidence_report.md` is a concise index of what ran, what was captured and where the files were written.

The report describes collection completeness only. It does not translate operational state or probe results into `PASS` or `FAIL`.

## Project structure

```text
11_nxos_fabric_automation_lab/
├── README.md
├── ansible.cfg
├── collection_plan.yml
├── requirements.txt
├── requirements.yml
├── inventory/
│   ├── inventory.yml
│   └── group_vars/
│       ├── all/
│       │   └── vault.yml
│       ├── nxos.yml
│       └── traffic_endpoints.yml
├── playbooks/
│   └── collect_vxlan_evpn_evidence.yml
├── templates/
│   └── evidence_report.md.j2
├── evidence_pack/
│   ├── raw/
│   ├── structured/
│   └── reports/
└── docs/
    ├── topology_notes.md
    └── topology_multisite_lab.png
```

The external WAN router remains in the inventory for topology context but is outside the current collection scope.

## Running Phase 1

From the project directory, activate the existing virtual environment and check the playbook syntax:

```bash
source .venv-nxos-fabric/bin/activate

ansible-playbook --syntax-check \
  playbooks/collect_vxlan_evpn_evidence.yml
```

Run the collection:

```bash
ansible-playbook \
  playbooks/collect_vxlan_evpn_evidence.yml
```

The project `ansible.cfg` supplies the inventory and Vault password file when the command is run from this directory.

To verify that the structured artifact contains valid JSON:

```bash
python -m json.tool \
  evidence_pack/structured/<RUN_ID>/collection_results.json
```

`json.tool` checks JSON syntax and prints the document in a readable form. It does not validate the network state or the meaning of the collected values.

## Phase 2

Phase 2 will consume the Phase 1 artifacts through two separate check families.

Operational command output will be parsed with Genie or a small custom parser where Genie coverage is not available. The normalized observed state will be evaluated against `expected_state.yml`. The first operational assessment checks are planned for:

- OSPF neighbors
- BGP EVPN sessions
- NVE state
- VNI state
- EVPN route types
- endpoint learning
- endpoint reachability

Running-configuration snapshots will follow a separate path. `ciscoconfparse2` will extract the relevant configuration sections, normalize them and compare them with the corresponding golden configuration.

Both operational assessment checks and configuration compliance checks will feed the same deterministic Check Engine. It will assign statuses such as `PASS`, `FAIL`, `WARNING`, `NOT TESTED` and `NOT APPLICABLE`.

Keeping assessment separate from collection means a fabric can produce a complete evidence run even when some of its control-plane, data-plane or configuration checks fail.

## Later work

Phase 3 will introduce human-approved remediation. An AI-assisted layer may propose a structured remediation plan, but a policy check and explicit operator approval will be required before an automation executor applies it.

Each approved change cycle will reuse the existing workflow:

```text
remediation
    ↓
Phase 1 recollection
    ↓
Phase 2 reassessment
    ↓
healthy or another approved plan
```

Backups, rollback, allowed-command policies and stop conditions are deliberately outside the current read-only workflow.
