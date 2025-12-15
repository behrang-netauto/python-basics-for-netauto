
#netmiko_compare_runnig_config.py
import getpass
import socket
from netmiko import ConnectHandler
from netmiko.exceptions import (ReadTimeout, NetmikoAuthenticationException, NetmikoTimeoutException)
from pathlib import Path
from typing import TypedDict
import difflib

class PortCheckResult(TypedDict):
    ip: str
    port: dict[int, str]

def pre_check_port(ip: str, port: int = 22, timeout:float = 3.0) -> PortCheckResult:
    result = {
        "ip": ip,
        "port": {},
    }

    if not ip:
        result["port"][port] = "missing_ip"
        return result

    try:
        with socket.create_connection((ip, port), timeout=timeout):
            result["port"] [port] = "open"
    except (socket.timeout, ConnectionRefusedError, OSError):
                result["port"] [port] = "close"
    return result

def write_html_diff(device_1: Path, device_2: Path, out_html: Path) -> Path:
    a = device_1.read_text(encoding="utf-8", errors="replace").splitlines()
    b = device_2.read_text(encoding="utf-8", errors="replace").splitlines()

    differ = difflib.HtmlDiff(tabsize=4, wrapcolumn=120)
    html = differ.make_file(
          a, 
          b,
          fromdesc=device_1.name,
          todesc=device_2.name,
          context=True,
          numlines=2,
    )
    out_path = out_html / f"{device_1.stem}_vs_{device_2.stem}_compared.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path

def main() -> None:
    devices = [
    {"device_type": "cisco_ios"},
    {"device_type": "cisco_ios"},
    ]

    home_dir = Path.home()
    base_dir = home_dir / "Documents" / "Python" / "Code/netauto_example_01" / "python-basics-for-netauto" / "examples" / "04_ssh_paramiko_netmiko"
    config_dir = base_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    path_files: list[Path] = []

    for idx, device in enumerate(devices, start=1):
        print("------get fucking attributes------")
        ip = input(f"ip for device_{idx}: ").strip()
        out_file = config_dir / f"{ip}_sh_run.txt"

        port_result = pre_check_port(ip)
        if port_result["port"].get(22) == "open":
            path_files.append(out_file)
            username = input(f"Username_Device_{idx}: ").strip()
            password = getpass.getpass(f"Password_Device_{idx}: ")
            device["ip"] = ip
            device["username"] = username
            device["password"] = password

            conn = None
            try:
                conn = ConnectHandler(**device)
                conn.enable()
                conn.send_command("terminal length 0")
                output = conn.send_command("show running-config", read_timeout= 15)
            except (ReadTimeout, NetmikoAuthenticationException, NetmikoTimeoutException) as error:
                output = f"ERROR from {ip}: {error}"
            finally:
                if conn is not None:
                    conn.disconnect()
            out_file.write_text(output, encoding="utf-8")
        else:
             print(f"Device_{idx} has no ssh!!!!")
    if len(path_files) >= 2 :
        out_path = write_html_diff(path_files[0], path_files[1], config_dir)
        print(f"\nDiff written to: {out_path}")
        print("Open this file in your browser to inspect differences.")    
    else:
        print("thers is no file for diff!!!!")


if __name__ == "__main__":
    main()




