

# ip_reachable_port_telnet_ssh_check_logging_module.py
"""Check basic reachability (ping) and TCP port openness.

    Notes
    - Ping first, then try TCP connect on ports.
    - Writing timestamping results to the journald and log file.
"""

import json
import os
import socket
import subprocess
from typing import TypedDict
from datetime import datetime
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s : %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("portcheck")

class PortCheckResult(TypedDict):
    ip: str
    ports: dict[int, str]
    error: str | None


def _parse_ports(raw: str) -> tuple[int, ...]:
    raw = raw.strip()
    if not raw:
        return (22, 23)
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return tuple(int(p) for p in parts)


def check_port(
    ip: str,
    ports: tuple[int, ...] = (22, 23),
    timeout: float = 3.0,
    ping_count: int = 3,
) -> PortCheckResult:
    result: PortCheckResult = {
        "ip": ip,
        "ports": {},
        "error": None,
    }

    cmd = ["ping", "-c", str(ping_count), ip]
    result_ping = subprocess.run(cmd, capture_output=True, text=True)
    out_put = result_ping.stdout

    if "100% packet loss" in out_put:
        result["error"] = "unreachable_ip"
        return result

    for port in ports:
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                result["ports"][port] = "open"
        except (socket.timeout, ConnectionRefusedError, OSError):
            result["ports"][port] = "close"

    return result


def main() -> None:
    # defaults (fallback)
    
    log.info("==========Starting RUN: port check...==========")

    devices = [
        {"site": "A", "ip": "192.168.56.20"},
        {"site": "B", "ip": "192.168.56.21"},
    ]

    devices_file = os.environ.get("DEVICES_FILE", "")
    ports = _parse_ports(os.environ.get("PORTS", "22,23"))
    timeout = float(os.environ.get("TIMEOUT", "3.0"))
    ping_count = int(os.environ.get("PING_COUNT", "3"))

    if devices_file and os.path.exists(devices_file):
        with open(devices_file, "r", encoding="utf-8") as f:
            devices = json.load(f)

    missing_ips: list[str] = []
    unreachable_device: list[dict] = []
    open_ssh_only_device: list[dict] = []
    open_telnet_only_device: list[dict] = []
    open_both_device: list[dict] = []
    open_neither_device: list[dict] = []

    total_ips = 0

    for device in devices:
        ip = device.get("ip", "")

        if not ip:
            site = device.get("site", "")
            missing_ips.append(site)
            continue

        r = check_port(ip, ports=ports, timeout=timeout, ping_count=ping_count)
        total_ips += 1

        if r["error"] == "unreachable_ip":
            unreachable_device.append(device)
            continue

        if r["ports"].get(22) == "open" and r["ports"].get(23) == "open":
            open_both_device.append(device)
        elif r["ports"].get(22) == "open" and r["ports"].get(23) == "close":
            open_ssh_only_device.append(device)
        elif r["ports"].get(22) == "close" and r["ports"].get(23) == "open":
            open_telnet_only_device.append(device)
        else:
            open_neither_device.append(device)

    log.info("------there is no ip------")
    for site in missing_ips:
        log.info(site)

    log.info("------Unreachable ips------")
    for dev in unreachable_device:
        log.info("%s %s", dev.get("site", "UNKNOWN"), dev.get("ip"))

    log.info("------telnet and ssh both are open------")
    for dev in open_both_device:
        log.info("%s %s", dev.get("site", "UNKNOWN"), dev.get("ip"))

    log.info("------ssh is open------")
    for dev in open_ssh_only_device:
        log.info("%s %s", dev.get("site", "UNKNOWN"), dev.get("ip"))

    log.info("------telnet is open------")
    for dev in open_telnet_only_device:
        log.info("%s %s", dev.get("site", "UNKNOWN"), dev.get("ip"))

    log.info("------neither ssh nor telnet is open------")
    for dev in open_neither_device:
        log.info("%s %s", dev.get("site", "UNKNOWN"), dev.get("ip"))


if __name__ == "__main__":
    main()
