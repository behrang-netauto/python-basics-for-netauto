________Stage 2 (pyATS) — Reload + Verify (Operational)________

!!!!!!!!!!!Purpose

This stage processes only the devices listed under ready_for_reload in stage1_handoff.json:
* pre → run show version and extract the system image
* reload (serial / one-by-one)
* post → run show version again
* PASS/FAIL rule: PASS if expected_filename (from handoff) is found inside post_system_image (substring match).

!!!!!!!!!!!Folder Layout

* pyats/jobs/stage2_reload_verify_job.py → Job runner
* pyats/tests/stage2_reload_verify.py → Testscript
* pyats/testbeds/testbed.yml → Testbed definition
* Output: artifacts/<RUN_ID>/stage2_pyats/stage2_summary.json

!!!!!!!!!!!Inputs

Testbed file:
*pyats/testbeds/testbed.yml

Stage1 handoff file:
*artifacts/<RUN_ID>/stage1_handoff.json

!!!!!!!!!!!Run Command

pyats run job pyats/jobs/stage2_reload_verify_job.py \
  --testbed-file pyats/testbeds/testbed.yml \
  --handoff-file artifacts/<RUN_ID>/stage1_handoff.json \
  --max-workers 5 \
  --reload-timeout 1200 \
  --reconnect-timeout 900 \
  --reconnect-interval 20

!!!!!!!!!!!Outputs

Summary (single file):
* artifacts/<RUN_ID>/stage2_pyats/stage2_summary.json

This file contains per-device:
* status (true/false)
* reason (only if failed)
* pre_system_image
* post_system_image

