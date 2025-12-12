
# ssh_netmiko_show_ip_int_brief.py

import getpass
from netmiko import ConnectHandler
from netmiko.exceptions import (ReadTimeout, NetMikoAuthenticationException, NetmikoTimeoutException)
from pathlib import Path

def main() -> None:
    devices = [
    {"device_type": "cisco_ios", "ip": "192.168.2.45"},
    {"device_type": "cisco_ios", "ip": "192.168.2.46"},
    ]

    COMMAND = "show ip int brief"
    home_dir = Path.home()
    base_dir = home_dir / "Documents" / "Python" / "Code/netauto_example_01" / "python-basics-for-netauto" / "examples" / "04_ssh_paramiko_netmiko"
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    total = 0

    for device in devices:
        ip = device.get("ip", "unknown")
        out_file = logs_dir / f"{ip}_log_sh_ip_br.txt"

        print(f"user/pass for {ip}:")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        device["username"] = username
        device["password"] = password

        conn = None
        try:
            conn = ConnectHandler(**device)
            output = conn.send_command(COMMAND, read_timeout= 15, expect_string=r"#")
            log_block = f"\n-----success-----\n\n{output}\n"

        except (ReadTimeout, NetMikoAuthenticationException, NetmikoTimeoutException) as error:
            log_block = f"\n-----failed-----\n\n{type(error).__name__}: {error}\n"
            
        except Exception as error:
            log_block = f"\n-----failed-----\n\nUnexpected error: {error}\n"

        finally:
            if conn is not None:
                conn.disconnect()
            
        out_file.write_text(log_block, encoding="utf-8")
        total += 1

    print(f"\n{total} logs written\n")

if __name__ == "__main__":
    main()








    

