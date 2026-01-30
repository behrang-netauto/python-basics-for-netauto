'''
portcheck (every 3 min)
   |
   | writes /shared/results.json
   v
alerter (every 3 min, right after portcheck)
   |
   | reads results.json
   | reads previous state.json
   | diff
   | if change -> send email to Mailpit SMTP
   v
updates /shared/state.json


results.json:
{
  "run_started_utc": "2026-01-29T16:20:00+00:00",
  "results": [
    {"site": "A", "ip": "192.168.56.20", "status": "up",   "reason": null},
    {"site": "B", "ip": "192.168.56.21", "status": "down", "reason": "ssh_closed"}
  ]
}
current = {
  "192.168.56.20": {"site":"A","ip":"192.168.56.20","status":"up","reason":None},
  "192.168.56.21": {"site":"B","ip":"192.168.56.21","status":"down","reason":"ssh_closed"},
}
'''
import json
import os
import logging
from datetime import datetime, timezone
from email.message import EmailMessage
import smtplib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s : %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("alerter")


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def _send_mail(subject: str, body: str) -> None:
    smtp_host = os.environ.get("SMTP_HOST", "127.0.0.1")
    smtp_port = int(os.environ.get("SMTP_PORT", "1025"))  # Mailpit default
    mail_from = os.environ.get("MAIL_FROM", "portcheck@lab.local")
    mail_to = os.environ.get("MAIL_TO", "ops@lab.local")

    msg = EmailMessage()
    msg["From"] = mail_from
    msg["To"] = mail_to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=5) as s:
        s.send_message(msg)


def main() -> None:
    results_file = os.environ.get("RESULTS_FILE", "/app/shared/results.json")
    state_file = os.environ.get("STATE_FILE", "/app/shared/state.json")

    if not os.path.exists(results_file):
        raise SystemExit(f"results file not found: {results_file}")

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = _read_json(results_file)
    results = payload.get("results", [])

    current = {}  # key -> status
    for r in results:
        key = r.get("ip") or r.get("site") or "UNKNOWN"
        current[key] = {
            "site": r.get("site", "UNKNOWN"),
            "ip": r.get("ip", ""),
            "status": r.get("status", "down"),
            "reason": r.get("reason"),
        }

    if not os.path.exists(state_file):
        _write_json(state_file, {"last_update_utc": now, "state": current})
        log.info("No previous state. Baseline saved to %s (no email).", state_file)
        return

    prev_payload = _read_json(state_file)
    prev = prev_payload.get("state", {})

    changes = []
    for key, cur in current.items():
        old = prev.get(key)
        if not old:
            changes.append((key, "new", cur["status"], cur))
            continue
        if old.get("status") != cur["status"]:
            changes.append((key, old.get("status"), cur["status"], cur))

    # state update always
    _write_json(state_file, {"last_update_utc": now, "state": current})

    if not changes:
        log.info("No state change. Updated %s.", state_file)
        return

    lines = [f"Time (UTC): {now}", "", "Changes:"]
    for key, old_s, new_s, cur in changes:
        lines.append(f"- {cur['site']} ({cur['ip']}) : {old_s} -> {new_s}  reason={cur.get('reason')}")
    body = "\n".join(lines)

    subject = f"[PORTCHECK] {len(changes)} change(s) detected"
    _send_mail(subject, body)
    log.info("Email sent to %s via SMTP %s:%s", os.environ.get("MAIL_TO", "ops@lab.local"),
             os.environ.get("SMTP_HOST", "127.0.0.1"), os.environ.get("SMTP_PORT", "1025"))


if __name__ == "__main__":
    main()