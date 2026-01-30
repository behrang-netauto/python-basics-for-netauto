'''
ping ok + port 22 open → up
else → down

results.json:
{
  "run_started_utc": "2026-01-29T16:20:00+00:00",
  "results": [
    {"site": "A", "ip": "192.168.56.20", "status": "up",   "reason": null},
    {"site": "B", "ip": "192.168.56.21", "status": "down", "reason": "ssh_closed"}
  ]
}
'''
import json
import os
import socket
import subprocess
import logging
from datetime import datetime, timezone
from typing import TypedDict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s : %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("portcheck")


class Device(TypedDict, total=False):
    site: str
    ip: str


class CheckResult(TypedDict):
    site: str
    ip: str
    reachable: bool
    port_22: str  # "open" | "closed" | "unknown"
    status: str   # "up" | "down"
    reason: str | None


def _load_devices(devices_file: str) -> list[Device]:
    devices: list[Device] = [
        {"site": "A", "ip": "192.168.56.20"},
        {"site": "B", "ip": "192.168.56.21"},
    ]
    if devices_file and os.path.exists(devices_file):
        with open(devices_file, "r", encoding="utf-8") as f:
            devices = json.load(f)
    return devices


def _ping_ok(ip: str, ping_count: int) -> bool:
    cmd = ["ping", "-c", str(ping_count), ip]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


def _tcp_open(ip: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def _atomic_write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def main() -> None:
    run_started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log.info("========== RUN START %s ==========", run_started)

    devices_file = os.environ.get("DEVICES_FILE", "/app/shared/devices.json")
    output_file = os.environ.get("OUTPUT_FILE", "/app/shared/results.json")
    timeout = float(os.environ.get("TIMEOUT", "3.0"))
    ping_count = int(os.environ.get("PING_COUNT", "3"))

    devices = _load_devices(devices_file)

    results: list[CheckResult] = []
    up_cnt = down_cnt = 0

    for d in devices:
        ip = (d.get("ip") or "").strip()
        site = (d.get("site") or "UNKNOWN").strip()

        if not ip:
            results.append(
                {"site": site, "ip": "", "reachable": False, "port_22": "unknown", "status": "down", "reason": "missing_ip"}
            )
            down_cnt += 1
            continue

        reachable = _ping_ok(ip, ping_count=ping_count)
        if not reachable:
            results.append(
                {"site": site, "ip": ip, "reachable": False, "port_22": "unknown", "status": "down", "reason": "unreachable_ip"}
            )
            down_cnt += 1
            continue

        ssh_open = _tcp_open(ip, 22, timeout=timeout)
        if ssh_open:
            results.append(
                {"site": site, "ip": ip, "reachable": True, "port_22": "open", "status": "up", "reason": None}
            )
            up_cnt += 1
        else:
            results.append(
                {"site": site, "ip": ip, "reachable": True, "port_22": "closed", "status": "down", "reason": "ssh_closed"}
            )
            down_cnt += 1

    payload = {
        "run_started_utc": run_started,
        "timeout_sec": timeout,
        "ping_count": ping_count,
        "results": results,
        "summary": {"up": up_cnt, "down": down_cnt, "total": len(results)},
    }

    _atomic_write_json(output_file, payload)
    log.info("Wrote results to %s (up=%d down=%d total=%d)", output_file, up_cnt, down_cnt, len(results))


if __name__ == "__main__":
    main()