
#ensure_ssh_ask_before_genarating_rsa_key_disable_telnet.py
import socket
import subprocess
from typing import TypedDict
import getpass
from netmiko import ConnectHandler
from netmiko import (ReadTimeout, NetmikoAuthenticationException, NetmikoTimeoutException)

class PortCheckResult(TypedDict):
    ip: str
    ports: dict[int, str]
    error: str | None

def pre_check_port(ip: str, ports: tuple[int, ...] = (22, 23), timeout:float = 3.0) -> PortCheckResult:
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

def rsa_key_exists(conn) -> bool:
    out = conn.send_command("sh crypto key mypubkey rsa")
    return "key name:" in out.lower()

def enforce_ssh(ip: str, username: str, password: str, device_type: str = "cisco_ios") ->str:
    device = {
        "ip" : ip,
        "username" : username,
        "password" : password,
        "device_type" : device_type,
    }
    conn = ConnectHandler(**device)
    conn.enable()
    if rsa_key_exists(conn):
        print(f"[{ip}] RSA Key exist!!!")
        config_cmds = [
        "ip domain name test.test",
        "ip ssh version 2",
        "username test privilege 15 secret test",
        "line vty 0 4",
        "login local",
        "transport input ssh",
    ]
    else:
        print(f"[{ip}] RSA Key not found!!!!")
        config_cmds = [
            "ip domain name test.test",
            "crypto key generate rsa modulus 2048",
            "ip ssh version 2",
            "username test privilege 15 secret test",
            "line vty 0 4",
            "login local",
            "transport input ssh",
        ]
    output = conn.send_config_set(config_cmds)
    conn.save_config()
    conn.disconnect()
    return output

def main() -> None:
    devices = [
    {"device_type": "cisco_ios", "site": "A", "ip": "192.168.2.45"},
    {"device_type": "cisco_ios", "site": "B", "ip": "192.168.2.46"},
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
        
        r = pre_check_port(ip)
        
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
            
    print("---------\ntelnet and ssh both are open---------\n")
    for ip in open_both_ips:
        print(f"connecting via ssh------user/pass for {ip}:")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        output = enforce_ssh(ip, username, password)
        print(output)

    print("---------\ntelnet is open---------\n")
    for ip in open_telnet_only_ips:
        print(f"connecting via telnet------user/pass for {ip}:")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        output = enforce_ssh(ip, username, password, device_type = "cisco_ios_telnet")
        print(output)

if __name__ == "__main__":
    main()


            




