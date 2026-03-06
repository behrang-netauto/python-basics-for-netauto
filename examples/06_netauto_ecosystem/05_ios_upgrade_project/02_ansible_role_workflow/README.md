# IOS Upgrade — Ansible Role Workflow (Stage1 + Stage2)

This workflow implements a two-stage IOS upgrade pipeline using Ansible.

- **Stage 1** (Ansible): pre-checks + upload IOS image + boot preparation + generates a handoff file
- **Stage 2** (Ansible): reads the handoff file, runs pre-verify, performs **serial reload**, runs post-verify, and writes a single summary report

A single `run_id` is generated **outside** the playbooks (wrapper/shell) and passed to both Stage 1 and Stage 2.

---

## Directory Layout

- `ansible/`  
  Playbooks, inventory, roles, and configuration.

- `artifacts/`  
  All run outputs, grouped by `run_id`.

Output paths per run:

- Stage 1 handoff:
  - `artifacts/<run_id>/stage1/stage1_handoff.json`
- Stage 2 summary:
  - `artifacts/<run_id>/stage2/stage2_summary.json`

---

## Requirements

- Ansible installed
- Cisco Ansible collection available (e.g., `cisco.ios`)
- Inventory configured under: `ansible/inventory/hosts.yml`
- Variables under: `ansible/inventory/group_vars/all.yml`
- Secrets under: `ansible/inventory/group_vars/vault.yml`

---

## Run Commands

Run from inside the `ansible/` directory so `ansible.cfg` is automatically used:

```bash
cd ansible

!!!!!!!!!!!! Create a Run ID (UTC)

RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
echo $RUN_ID


!!!!!!!!!!!! Stage 1 — Prepare (pre-check + upload + boot prep + handoff)

ansible-playbook -i inventory/hosts.yml playbooks/stage1_prepare.yml -e run_id=$RUN_ID


!!!!!!!!!!!! Stage 2 — Reload + Verify (pre/post show version + serial reload)

ansible-playbook -i inventory/hosts.yml playbooks/stage2_reload_verify.yml -e run_id=$RUN_ID


---


## Dry-Run Note (Stage 2)

A true dry-run is not possible for device reload. However, you can run Stage 2 in interactive step mode and 
manually skip reload-related tasks:

ansible-playbook -i inventory/hosts.yml playbooks/stage2_reload_verify.yml -e run_id=$RUN_ID --step

----> When prompted on reload tasks, choose skip.
