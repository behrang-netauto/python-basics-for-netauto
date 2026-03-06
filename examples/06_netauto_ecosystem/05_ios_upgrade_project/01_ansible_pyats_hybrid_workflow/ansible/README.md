________Stage 1 (Ansible) — Prepare + Upload + Gates (Operational)________

!!!!!!!!!!!!Purpose

Stage 1 validates prerequisites (“gates”), optionally enables SCP, uploads the IOS/IOS-XE image to the device, and produces a handoff JSON that Stage 2 (pyATS) will consume.

Key outcome: a single file stage1_handoff.json listing devices ready for reload vs not ready.


!!!!!!!!!!!!Folder Layout (typical)

* ansible/stage1_prepare.yml
* ansible/roles/ios_upgrade_stage1/tasks/main.yml
* ansible/inventory/hosts.yml
* ansible/inventory/group_vars/all.yml
* ansible/inventory/group_vars/vault.yml (encrypted with Ansible Vault)
* Output: artifacts/<RUN_ID>/stage1_handoff.json


!!!!!!!!!!!!Inputs

Inventory:
ansible/inventory/hosts.yml

Variables:
ansible/inventory/group_vars/all.yml (image path, md5, operational toggles)

Credentials (Vault):
ansible/inventory/group_vars/vault.yml (encrypted)
Load via --ask-vault-pass or --vault-password-file


!!!!!!!!!!!!Run Command (Vault prompt)

cd ansible
ansible-playbook -i inventory/hosts.yml stage1_prepare.yml --ask-vault-pass

!!!!!!!!!!!!Run Command (Vault password file)

cd ansible
ansible-playbook -i inventory/hosts.yml stage1_prepare.yml --vault-password-file ~/.vault_pass.txt


!!!!!!!!!!!!Output

Handoff (single file):
* artifacts/<RUN_ID>/stage1_handoff.json

This file contains:
* Image metadata (filename, md5, size_mb)
* ready_for_reload: devices that passed all Stage 1 gates/steps
* not_ready: devices that failed + failed_gate + reason

Stage 2 uses ready_for_reload as the source of truth.

