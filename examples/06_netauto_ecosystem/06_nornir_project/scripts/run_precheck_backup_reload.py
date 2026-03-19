
from __future__ import annotations

import json
import os
import socket
import time
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from scrapli import Scrapli

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = PROJECT_ROOT / "artifacts"
VAULT_PATH = PROJECT_ROOT / "vault.yml"
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_run_dirs(run_id: str) -> Tuple[Path, Path]:
    run_dir = (ARTIFACTS_ROOT / run_id).resolve()
    backups_dir = run_dir / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    return run_dir, backups_dir


def load_creds() -> Dict[str, str]:
    data = yaml.safe_load(VAULT_PATH.read_text(encoding="utf-8"))
    creds = data.get("credentials", {})
    if not creds.get("username") or not creds.get("password"):
        raise ValueError("vault.yml: credentials.username/password are required")
    return {"username": creds["username"], "password": creds["password"]}


def init_device_state() -> Dict[str, Any]:
    return {
        "precheck": {"ok": False, "system_image": "", "error": "not_run"},
        "backup": {"ok": False, "path": "", "error": "not_run"},
        "reload": {"ok": False, "error": "not_run"},
        "final": {"ok": False, "reason": ""},
    }


def parse_system_image(show_ver: str) -> str:
    m = re.search(r'System image file is\s+"([^"]+)"', show_ver)
    if m:
        return m.group(1).strip()
    # Fallback without quotes:
    m = re.search(r"System image file is\s+(\S+)", show_ver)
    if m:
        return m.group(1).strip()
    
    raise ValueError("system image path not found in show version output")


def wait_for_ssh_back(
        host: str, 
        port: int,
        username: str,
        password: str,
        timeout_sec: int = 900, 
        interval_sec: int = 10
) -> Tuple[bool, str]:
    deadline = time.time() + timeout_sec
    last_err = ""

    while time.time() < deadline:
        try:
            conn = Scrapli(
                host=host,
                port=int(port),
                auth_username=username,
                auth_password=password,
                auth_strict_key=False,
                platform="cisco_iosxe",
                timeout_socket=interval_sec,
                timeout_transport=interval_sec,
                timeout_ops=interval_sec,
            )
            conn.open()
            conn.close()
            return True, ""
        except Exception as e:
            last_err = str(e)
            time.sleep(interval_sec)
    return False, f"error by wait_for_ssh: timeout ({last_err})"


def send_reload_interactive(conn, timeout_ops: int = 30) -> Tuple[bool, str]:
    """
    Returns: (accepted_ok, error)
      - accepted_ok=True  => reload command accepted (confirm sent)
      - accepted_ok=False => failed before confirm
    """
    try:
        resp = conn.send_interactive(
            [("reload", r"\[yes/no\]|\[confirm\]|Proceed with reload", False)],
            timeout_ops=timeout_ops,
        )
        out = getattr(resp, "result", "") or str(resp)

        # If the device asks about saving config (yes/no), we answer "no"
        if re.search(r"\[yes/no\]|System configuration has been modified", out, re.IGNORECASE):
            resp2 = conn.send_interactive(
                [("no", r"\[confirm\]|Proceed with reload", False)],
                timeout_ops=timeout_ops,
            )
            out2 = getattr(resp2, "result", "") or str(resp2)
            out = out + "\n" + out2

        # Now we must confirm reload (Enter)
        if re.search(r"\[confirm\]|Proceed with reload", out, re.IGNORECASE):
            conn.send_interactive([("", r".*", False)], timeout_ops=timeout_ops)
            return True, ""

        return False, "error by reload_command: did not reach confirm prompt"

    except Exception as e:
        msg = str(e)
        if re.search(r"closed|disconnect|reset|EOF", msg, re.IGNORECASE):
            return True, ""
        return False, f"error by reload_command: {msg}"


def main() -> int:
    run_id = os.environ.get("RUN_ID") or utc_run_id()
    run_dir, backups_dir = ensure_run_dirs(run_id)

    creds = load_creds()
    nr = InitNornir(config_file=str(CONFIG_PATH))

    nr.inventory.defaults.username = creds["username"]
    nr.inventory.defaults.password = creds["password"]

    report: Dict[str, Any] = {
        "run_id": run_id,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "devices": {},
    }

    for name in nr.inventory.hosts.keys():
        report["devices"][name] = init_device_state()

    # Phase A: precheck (parallel)
    r_pre = nr.run(task=send_command, command="show version")
    for name, mr in r_pre.items():
        st = report["devices"][name]
        if mr.failed:
            st["precheck"] = {"ok": False, "system_image": "", "error": f"error by precheck: {str(mr.exception)}"}
            st["final"] = {"ok": False, "reason": "precheck_failed"}
            continue
        try:
            sysimg = parse_system_image(mr.result)
            st["precheck"] = {"ok": True, "system_image": sysimg, "error": ""}
        except Exception as e:
            st["precheck"] = {"ok": False, "system_image": "", "error": f"error by precheck: {e}"}
            st["final"] = {"ok": False, "reason": "precheck_failed"}

    # Phase B: backup (parallel) only for precheck-ok
    nr_bak = nr.filter(filter_func=lambda h: report["devices"][h.name]["precheck"]["ok"] is True)
    r_bak = nr_bak.run(task=send_command, command="show running-config")
    for name, mr in r_bak.items():
        st = report["devices"][name]
        if mr.failed:
            st["backup"] = {"ok": False, "path": "", "error": f"error by backup: {str(mr.exception)}"}
            st["final"] = {"ok": False, "reason": "backup_failed"}
            continue
        try:
            p = backups_dir / f"{name}.cfg"
            p.write_text(mr.result, encoding="utf-8")
            if not p.exists():
                raise RuntimeError("backup file write failed (file not found after write)")
            st["backup"] = {"ok": True, "path": str(p), "error": ""}
        except Exception as e:
            st["backup"] = {"ok": False, "path": "", "error": f"error by backup: {e}"}
            st["final"] = {"ok": False, "reason": "backup_failed"}

    # Phase C: reload serial (only for backup-ok)
    targets = [n for n, st in report["devices"].items() if st["precheck"]["ok"] and st["backup"]["ok"]]
    for name in targets:
        st = report["devices"][name]
        try:
            host_obj = nr.inventory.hosts[name]
            conn = host_obj.get_connection("scrapli", nr.config)

            accepted, err = send_reload_interactive(conn, timeout_ops=30)
            if not accepted:
                st["reload"] = {"ok": False, "error": err}
                st["final"] = {"ok": False, "reason": "reload_failed"}
                continue

            ok_ssh, err_ssh = wait_for_ssh_back(
                host_obj.hostname, 
                int(host_obj.port or 22),
                username=creds["username"],
                password=creds["password"],
                timeout_sec=900, 
                interval_sec=10
            )
            if not ok_ssh:
                st["reload"] = {"ok": False, "error": err_ssh}
                st["final"] = {"ok": False, "reason": "reload_failed"}
                continue

            st["reload"] = {"ok": True, "error": ""}
            st["final"] = {"ok": True, "reason": ""}

        except Exception as e:
            st["reload"] = {"ok": False, "error": f"reload_failed: {e}"}
            st["final"] = {"ok": False, "reason": "reload_failed"}

    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    out_path = run_dir / "report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())