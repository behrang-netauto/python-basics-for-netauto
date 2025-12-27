
#snmp_push_config_ssh_connection
import getpass
import json
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import (ReadTimeout, NetmikoAuthenticationException, NetmikoTimeoutException)
from datetime import datetime

def push_snmp(
        cmds: list[str], 
        config_cmds: list[str], 
        username: str, password: str, 
        ip: str, 
        device_type: str = "cisco_ios",
        secret: str | None = None,
        ) -> str:
    
    final_out = {
        "cfg_out": None,
        "save_out": None,
        "outs": None,
        "error": None,
    }
    
    device = {
        "ip" : ip,
        "username" : username,
        "password" : password,
        "device_type" : device_type,
    }

    if secret:
        device["secret"] = secret

    conn = None
    outs = None
    try:
        conn = ConnectHandler(**device)
        
        if not conn.check_enable_mode():
            if secret:
                conn.enable()
            else:
                raise RuntimeError("thers is neither secret nor pri 15!!!!")
        
        cfg_out = conn.send_config_set(config_cmds)
        final_out["cfg_out"] = cfg_out
        
        save_out = ""
        try:
            save_out = conn.save_config()
        except Exception:
            save_out += "\n" + conn.send_command("write memory")
        final_out["save_out"] = save_out
        
        conn.send_command("terminal length 0")
        outs = {c: conn.send_command(c, use_textfsm=True) for c in cmds}
        
    except (ReadTimeout, NetmikoAuthenticationException, NetmikoTimeoutException) as error:
        final_out["error"] = f"{type(error).__name__}: {error}"

    except Exception as error:
        final_out["error"] = f"Unexpected Error:{error}"
    
    finally:
        if conn is not None:
            conn.disconnect()
        final_out["outs"] = outs

    return final_out

def main() -> dict:
    devices = [
    {"device_type": "cisco_ios", "site": "A", "ip": "192.168.2.45"},
    {"device_type": "cisco_ios", "site": "B", "ip": "192.168.2.48"},
    ]
    cmds = ["show snmp user", "show snmp group"]
    
    config_cmds = [
            "snmp-server view MONITOR-VIEW iso included",
            "snmp-server group MONITOR-GRP v3 priv read MONITOR-VIEW",
            "snmp-server user SNMPUser1 MONITOR-GRP v3 auth sha AUTHPass1 priv aes 128 PRIVPass1",
            "snmp-server enable traps",
            "snmp-server host 192.168.2.55 version 3 priv SNMPUser1",
        ]
    
    home_dir = Path.home()
    base_dir = home_dir / "Documents" / "Python" / "Code/netauto_example_01" / "python-basics-for-netauto" / "examples" / "05_snmp_paramiko_netmiko"
    logs_dir = base_dir / "snmp_logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    for device in devices:
        ip = device.get("ip", "")
        site = device.get("site", "UNKNOWN")
        
        if not ip:
            continue
        
        out_file = logs_dir / f"{timestamp}_{site}_{ip}_snmp_show_commands.cfg"

        print(f"connecting via ssh------user/pass for {ip}:")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        secret = getpass.getpass("Enable secret (blank if none): ").strip()
        final_out = push_snmp(cmds, config_cmds, username, password, ip, secret=secret)

        print(json.dumps(final_out, indent=2))

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(final_out, f, indent=2)
            
if __name__ == "__main__":
    main()

    
'''
send_multiline:

try:
    outs = conn.send_multiline(cmds)
except AttributeError:
    outs = "\n\n".join(conn.send_command(c) for c in cmds)

'''
#raw_user = conn.send_command("show snmp user", use_textfsm=False)
#print(raw_user)
        
    