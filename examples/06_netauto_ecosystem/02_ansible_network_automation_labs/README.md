# Ansible Network Automation Labs

This lab is a refactored Ansible network automation workflow for Cisco IOS / IOS XE and NX-OS devices.

The goal is not to build a production Ansible framework. The goal is to show practical, readable, evidence-driven network automation fundamentals with a clear Git history, local validation, and CI quality checks.

## Refactor summary

This folder was refactored from a small Ansible lab with a basic inventory and two playbooks into a staged network automation mini-project.

The refactor added:

- a clearer project structure
- IOS / IOS XE and NX-OS inventory grouping
- inventory-local `group_vars`
- encrypted device credentials with Ansible Vault
- seven ordered playbooks
- Jinja2 template rendering
- data-driven IOS baseline configuration
- conditional SNMPv3 configuration
- verification and evidence collection
- offline pytest checks
- Ansible linting and YAML linting
- a GitHub Actions quality gate

The lab is intentionally kept simple and readable instead of being converted into a full role-based Ansible framework.

## Scope

This lab covers:

- inventory-driven execution
- encrypted credentials with Ansible Vault
- Cisco IOS / IOS XE and NX-OS command execution
- IOS facts collection
- running-config backup
- SNMPv3 candidate configuration rendering
- idempotent IOS baseline configuration with `ios_config`
- data-driven interface configuration with loops
- conditional SNMPv3 configuration based on pre-checks
- Jinja2 filters such as `map`, `join`, `regex_search`, `split`, `reject`, `list`, and `length`
- post-change verification and evidence collection
- offline CI-style checks with `yamllint`, `ansible-lint`, `ruff`, `compileall`, and `pytest`

## Lab devices

| Host | Platform | Management IP | Purpose |
|---|---|---:|---|
| `csr1000v` | IOS XE | `192.168.2.64` | IOS XE automation target |
| `iol_r1` | IOS / IOL | `192.168.2.65` | IOS automation target |
| `nxos1` | NX-OS | `192.168.2.66` | NX-OS connectivity and backup target |

## Project structure

```text
02_ansible_network_automation_labs/
├── README.md
├── ansible.cfg
├── requirements.yml
├── requirements.txt
├── pytest.ini
├── .yamllint.yml
├── .ansible-lint
├── inventory/
│   ├── inventory_lab.yml
│   └── group_vars/
│       ├── ios/
│       │   └── vars.yml
│       └── network_devices/
│           └── vault.yml
├── playbooks/
│   ├── 01_connectivity_check.yml
│   ├── 02_gather_ios_facts.yml
│   ├── 03_backup_running_config.yml
│   ├── 04_render_snmpv3_config.yml
│   ├── 05_apply_baseline_config.yml
│   ├── 06_apply_snmpv3_config.yml
│   └── 07_verify_and_collect_evidence.yml
├── templates/
│   └── snmpv3_config.j2
├── tests/
│   ├── fixtures/
│   │   └── snmpv3_template_vars.yml
│   ├── test_inventory_shape.py
│   └── test_snmpv3_template_render.py
├── artifacts/
│   └── .keep
└── evidence_pack/
    ├── command_outputs/
    ├── rendered_configs/
    └── logs/
```

Repository-level CI workflow:

```text
.github/workflows/ansible-labs-ci.yml
```

## Playbooks

| Playbook | Purpose |
|---|---|
| `01_connectivity_check.yml` | Checks TCP/22 reachability and runs basic platform-specific show commands |
| `02_gather_ios_facts.yml` | Collects IOS / IOS XE facts and renders a small facts report |
| `03_backup_running_config.yml` | Backs up running-config from IOS / IOS XE and NX-OS devices |
| `04_render_snmpv3_config.yml` | Renders IOS SNMPv3 candidate configuration from a Jinja2 template |
| `05_apply_baseline_config.yml` | Applies a small IOS baseline using `cisco.ios.ios_config`, including data-driven loopback configuration |
| `06_apply_snmpv3_config.yml` | Applies SNMPv3 config only when the named objects are missing |
| `07_verify_and_collect_evidence.yml` | Verifies SNMPv3 state and collects final evidence |

## Automation patterns covered

This lab intentionally demonstrates several common Ansible network automation patterns.

### Pattern 1 — Collect, register, evidence

Used in:

- `01_connectivity_check.yml`
- `02_gather_ios_facts.yml`
- `03_backup_running_config.yml`

Example pattern:

```text
collect command output
register result
write evidence file/report
```

The lab writes evidence files instead of relying only on `debug` output.

### Pattern 2 — Collect, parse, decide

Used in:

- `06_apply_snmpv3_config.yml`

Example pattern:

```text
collect existing device state
register output
parse output with filters/regex
set decision facts
run config task only when needed
```

The SNMPv3 playbook checks whether the SNMPv3 view, group, and user already exist before pushing configuration.

### Pattern 3 — Data-driven configuration

Used in:

- `05_apply_baseline_config.yml`

The IOS baseline uses structured variables for loopback configuration. Common interface intent is stored in group variables, while per-device loopback IPs are stored in inventory.

Example concept:

```text
common loopback structure in group_vars
per-device IP data in inventory
loop over baseline loopbacks
apply interface config with ios_config
```

This keeps configuration data separate from task logic.

### Pattern 4 — Platform-specific modules with a shared workflow

Used in:

- `01_connectivity_check.yml`
- `03_backup_running_config.yml`

The workflow is shared, but the platform-specific modules differ:

```text
IOS / IOS XE → cisco.ios.ios_command
NX-OS        → cisco.nxos.nxos_command
```

This shows how a single operational workflow can support multiple Cisco platforms.

### Pattern 5 — Model-driven / NETCONF path

This lab currently focuses on `network_cli`, `ios_command`, `nxos_command`, and `ios_config`.

A future extension can add a NETCONF/YANG path:

```text
Ansible playbook
    ↓
ansible.netcommon.netconf connection plugin
    ↓
netconf_get / netconf_config
    ↓
YANG-modeled data/config
```

This is intentionally left as a separate follow-up scope so the current lab remains focused and readable.

## Variables and secrets

Non-secret IOS variables are stored in:

```text
inventory/group_vars/ios/vars.yml
```

Examples:

- baseline configuration data
- SNMPv3 object names
- verification checks
- evidence-related variables

Encrypted credentials and SNMPv3 secrets are stored in:

```text
inventory/group_vars/network_devices/vault.yml
```

The vault file is encrypted with Ansible Vault.

Example local usage:

```bash
ansible-vault view inventory/group_vars/network_devices/vault.yml
```

## Local setup

Python version used for this lab:

```text
Python 3.12.8
```

Create and activate the virtual environment:

```bash
python -m venv .venv-ansible
source .venv-ansible/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
```

## Running a playbook

Example:

```bash
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)

ansible-playbook \
  playbooks/01_connectivity_check.yml \
  -i inventory/inventory_lab.yml \
  --vault-password-file ~/.ansible/vault_pass.txt \
  -e run_id="$RUN_ID"
```

## Ad-hoc command examples

IOS / IOS XE:

```bash
ansible ios \
  -i inventory/inventory_lab.yml \
  -m cisco.ios.ios_command \
  -a "commands='show snmp user'" \
  --vault-password-file ~/.ansible/vault_pass.txt
```

NX-OS:

```bash
ansible nxos \
  -i inventory/inventory_lab.yml \
  -m cisco.nxos.nxos_command \
  -a "commands='show interface brief'" \
  --vault-password-file ~/.ansible/vault_pass.txt
```

## Evidence model

Execution evidence is written under:

```text
evidence_pack/
```

Examples:

```text
evidence_pack/command_outputs/<run_id>/
evidence_pack/rendered_configs/<run_id>/
evidence_pack/logs/<run_id>/
```

Runtime-only generated files belong under:

```text
artifacts/
```

and are not committed except for `.keep`.

Raw configuration and command-output evidence may contain sensitive operational details. Review and redact evidence before committing.

Examples of values that should be redacted before Git commit:

```text
snmp-server user SNMPUser1 MONITOR-GRP v3 auth sha ******* priv aes 128 *******
User name: *******
```

Running-config backup files are treated as sensitive evidence and should not be committed unless explicitly reviewed and redacted.

## Quality checks

### Local checks

```bash
yamllint -c .yamllint.yml . "$HOME/repo/python-basics-for-netauto/.github/workflows/ansible-labs-ci.yml" __**run from project directory**__
ruff check tests
python -m compileall tests
pytest -q tests
ansible-lint playbooks/
```

Syntax check all playbooks:

```bash
for pb in playbooks/*.yml; do
  ansible-playbook \
    --syntax-check "$pb" \
    -i inventory/inventory_lab.yml \
    --vault-password-file ~/.ansible/vault_pass.txt
done
```

A local CI-style log can be saved under:

```text
evidence_pack/logs/<run_id>/local_ci_quality_checks.log
```

### GitHub Actions CI

The workflow file is located at:

```text
.github/workflows/ansible-labs-ci.yml
```

The CI workflow is designed as an offline quality gate. It does not connect to real network devices.

It checks:

- Python dependency installation
- Ansible collection installation
- Ansible module availability
- YAML linting
- Ruff linting for Python tests
- Python syntax compilation
- Ansible linting
- inventory parsing
- Ansible playbook syntax
- offline pytest checks

The workflow uses a repository secret named:

```text
ANSIBLE_VAULT_PASSWORD
```

This secret is used to create a temporary vault password file inside the GitHub Actions runner.

## Tests

This lab includes two offline pytest checks:

```text
tests/test_inventory_shape.py
tests/test_snmpv3_template_render.py
```

`test_inventory_shape.py` validates the minimum expected inventory structure, including IOS and NX-OS groups.

`test_snmpv3_template_render.py` renders the SNMPv3 Jinja2 template with fixture data and checks that the expected IOS SNMPv3 configuration lines are produced.

## Notes

This is a lab-oriented workflow. It intentionally keeps the playbooks simple and readable instead of using a larger role-based Ansible structure.

The main learning goals are:

- using inventory and group variables correctly
- separating secrets with Ansible Vault
- executing Cisco network modules
- applying IOS configuration with `ios_config`
- checking idempotent behavior
- using data-driven configuration with loops
- using conditionals and filters
- collecting evidence for each automation step
- adding a CI quality gate for an Ansible network automation lab

## Follow-up ideas

Possible follow-up work:

- add a minimal NETCONF/YANG read-only playbook with `ansible.netcommon.netconf`
- add a small data-driven NETCONF/YANG check list
- expand pytest checks for variable structure
- add a lightweight top-level repository index that links this lab to other network automation projects
