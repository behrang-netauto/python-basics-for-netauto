!!!!!!!!!!!!!!!!!! IOS Upgrade — Hybrid Workflow (Ansible Stage1 + pyATS Stage2)

This scenario implements a two-stage IOS upgrade workflow:

- **Stage 1 (Ansible):** pre-checks + image upload + boot preparation + generates a handoff contract
- **Stage 2 (pyATS/Genie):** reads the handoff file, runs pre/post verification, performs controlled reload, and writes a final summary


## Where to find details
- Stage 1 documentation: `ansible/README.md`
- Stage 2 documentation: `pyats/README.md`

## Artifacts
Artifacts are grouped under a single **run_id** directory.
All outputs are stored under:
- `artifacts/<run_id>/...`

