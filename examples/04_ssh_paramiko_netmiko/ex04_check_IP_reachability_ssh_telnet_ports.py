
# ip_reachable_port_telnet_ssh_check.py
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
    unreachable_ips: list[str] = []
    open_ssh_only_ips: list[str] = []
    open_telnet_only_ips: list[str] = []
    open_both_ips: list[str] = []
    open_neither_ips: list[str] = []

    total_ips = 0
    for device in devices:
        ip = device.get("ip", "")
        site = device.get("site", "")
        
        if not ip:
            missing_ips.append(site)
            continue

        r = check_port(ip)
        
        total_ips += 1

        if r["error"] == "unreachable_ip":
            unreachable_ips.append(ip)
            continue
        elif r["ports"].get(22) == "open" and r["ports"].get(23) == "open":
            open_both_ips.append(ip)
            continue
        elif r["ports"].get(22) == "open" and r["ports"].get(23) == "close":
            open_ssh_only_ips.append(ip)
            continue
        elif r["ports"].get(22) == "close" and r["ports"].get(23) == "open":
            open_telnet_only_ips.append(ip)
            continue
        else:
            open_neither_ips.append(ip)

    for site in missing_ips:
        print(f"  ther is no ip:       {site}")
    for ip in unreachable_ips:
        print(f"  Unreachable ips:     {ip}")
    for ip in open_both_ips:
        print(f"telnet and ssh both are open:    {ip}")
    for ip in open_telnet_only_ips:
        print(f"telnet is open:       {ip}") 

if __name__ == "__main__":
    main()


            


