# NX-OS Fabric Automation Lab

This project is a multi-phase network automation lab for an NX-OS VXLAN EVPN fabric.

The first phase is intentionally read-only. It connects to the existing NX-OS fabric, collects operational evidence, and writes raw command outputs plus a lightweight Markdown report.

The goal is not to prove that the fabric is correct yet. The goal is to create a clean evidence baseline that can be reviewed before deeper validation, troubleshooting, or future API-based automation phases.

## Current phase

Phase 1 focuses on:

- connecting to NX-OS fabric nodes over SSH
- collecting read-only operational command output
- grouping evidence by device and command category
- writing raw evidence files under `evidence_pack/raw/`
- rendering a Markdown evidence report under `evidence_pack/reports/`
- avoiding any configuration changes

No configuration is pushed by the current playbook.

## Lab context

This lab is based on a VXLAN EVPN multisite scenario.

At a high level, the topology contains:

- Site 1 / AS 65001
- Site 2 / AS 65002
- a DCI node / AS 65003
- border gateways between the sites and the DCI layer
- VXLAN EVPN overlay with L2VNI and L3VNI services
- OSPF/PIM underlay inside the sites
- BGP EVPN overlay
- external WAN/router node in the EVE-NG lab environment

The current Ansible phase collects evidence from the NX-OS devices only.

## Project structure

```text
11_nxos_fabric_automation_lab/
├── README.md
├── ansible.cfg
├── requirements.txt
├── requirements.yml
├── inventory/
│   ├── inventory.yml
│   └── group_vars/
│       ├── all/
│       │   └── vault.yml
│       └── nxos.yml
├── playbooks/
│   └── collect_vxlan_evpn_evidence.yml
├── templates/
│   └── evidence_report.md.j2
├── evidence_pack/
│   ├── raw/
│   └── reports/
└── docs/
    ├── topology_notes.md
    └── topology_multisite_lab.png
```

## Inventory scope

The inventory currently models the lab devices by role:

- spines
- border gateways
- leaves
- DCI node
- external WAN router

The playbook currently targets the `nxos` group.

## Main playbook

```text
playbooks/collect_vxlan_evpn_evidence.yml
```

The playbook has three stages:

1. Prepare the local evidence directories.
2. Collect read-only command output from NX-OS devices.
3. Render a Markdown evidence report.

## Run the playbook

From the project directory:

```bash
source .venv-nxos-fabric/bin/activate
ansible-playbook playbooks/collect_vxlan_evpn_evidence.yml
```

The project `ansible.cfg` defines the inventory and vault password file, so the playbook command does not need an explicit `--vault-password-file` flag when it is executed from this directory.

## Future phases

Possible next phases:

- review raw evidence and document fabric state
- compare actual state with expected topology
- add lightweight validation checks
- add expected-state YAML data
- add RESTCONF/NX-API read-only checks
- add structured JSON reports
- add tests for report rendering and inventory shape
- add troubleshooting notes based on failed or partial fabric state
