
# ip_reachable_port_telnet_ssh_check_use_dict.py

import socket
import subprocess
from typing import TypedDict

class PortCheckResult(TypedDict):
    ip: str
    ports: dict[int, str]
    error: str | None

def check_port(ip: str, ports: tuple[int, ...] = (22, 23), timeout:float = 3.0) -> PortCheckResult:
    result = {
        "ip": ip,
        "ports": {},
        "error": None,
    }
    cmd = ["ping", "-c", "3", ip]
    result_ping = subprocess.run(cmd, capture_output=True, text=True)
    out_put = result_ping.stdout

    if "100% packet loss" in out_put:
        result["error"] = "unreachable_ip"
        return result
    #if result_ping.returncode != 0:
    #    result["error"] = "unreachable_ip"
    #    return result
    for port in ports:
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                result["ports"] [port] = "open"
        except (socket.timeout, ConnectionRefusedError, OSError):
                result["ports"] [port] = "close"
    
    return result
    
def main() -> None:
    devices = [
    {"site": "A", "ip": "192.168.2.45"},
    {"site": "B", "ip": "192.168.2.46"},
    ]

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

        r = check_port(ip)
        
        total_ips += 1

        if r["error"] == "unreachable_ip":
            unreachable_device.append(device)
            continue
        elif r["ports"].get(22) == "open" and r["ports"].get(23) == "open":
            open_both_device.append(device)
            continue
        elif r["ports"].get(22) == "open" and r["ports"].get(23) == "close":
            open_ssh_only_device.append(device)
            continue
        elif r["ports"].get(22) == "close" and r["ports"].get(23) == "open":
            open_telnet_only_device.append(device)
            continue
        else:
            open_neither_device.append(device)

    print("------ther is no ip------")
    for site in missing_ips:
        print(site)
    print("------Unreachable ips------")
    for dev in unreachable_device:
        print(dev.get("site", "UNKNOWN"), dev.get("ip"))
    print("------telnet and ssh both are open------")
    for dev in open_both_device:
        print(dev.get("site", "UNKNOWN"), dev.get("ip"))
    print("------telnet is open------")
    for dev in open_telnet_only_device:
        print(dev.get("site", "UNKNOWN"), dev.get("ip"))

if __name__ == "__main__":
    main()


 '''
IP→Device-Mapping für schnelles Lookup :::::::::: (Index über IP)
du kannst aus einer Liste von Geräten (devices) ein Dictionary (device_by_ip) bauen,
das jede IP-Adresse direkt auf das zugehörige Device-Dictionary abbildet.
Dadurch kannst du später in einer Schleife über IPs schnell die Device-Infos (z. B. site, device_type) nachschlagen, 
ohne jedes Mal die komplette Liste zu durchsuchen.

devices = [
    {"device_type": "cisco_ios", "site": "A", "ip": "192.168.2.45"},
    {"device_type": "cisco_ios", "site": "B", "ip": "192.168.2.46"},
]
device_by_ip = {d["ip"]: d for d in devices}

Ergebnis:
{
  "192.168.2.45": {"device_type": "cisco_ios", "site": "A", "ip": "192.168.2.45"},
  "192.168.2.46": {"device_type": "cisco_ios", "site": "B", "ip": "192.168.2.46"},
}

for ip in open_telnet_only_ips:
    dev = device_by_ip.get(ip, {})
    site = dev.get("site", "UNKNOWN")
    print(f"Connecting via telnet for {site} ({ip})")
    .
    .
    .

*******
Wenn zwei Geräte dieselbe IP haben, überschreibt der letzte Eintrag den vorherigen im Dictionary.
*******

 '''           


