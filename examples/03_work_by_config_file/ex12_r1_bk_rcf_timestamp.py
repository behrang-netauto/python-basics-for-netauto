
import getpass
from netmiko import ConnectHandler
from netmiko.exceptions import ReadTimeout
from pathlib import Path
from datetime import datetime

def main() -> None:
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"R1_running_{timestamp}.cfg"

    home_dir = Path.home()
    base_dir = home_dir / "Documents" / "Python" / "Code/netauto_example_01" / "python-basics-for-netauto" / "examples" / "back_up"
    base_dir.mkdir(parents=True, exist_ok=True)

    remote_path_scp_server = base_dir / filename
    
    r1_host = "192.168.2.45"
    scp_host = "192.168.2.31"
    scp_user = "behrang"

    cmd = f"copy running-config scp://{scp_user}@{scp_host}/{remote_path_scp_server}"

    username = input("enter username: ").strip()
    password = getpass.getpass("password: ")

    scp_password = getpass.getpass(f"SCP password for {scp_user}@{scp_host}: ")

    device = {
        "device_type": "cisco_ios",
        "host": r1_host,
        "username": username,
        "password": password,
    }
    
    conn = ConnectHandler(**device)

    try:
        output = conn.send_command_timing(cmd)
        output += conn.send_command_timing("")   #Address or name of remote host
        output += conn.send_command_timing("")   #Destination username
        output += conn.send_command_timing("")   #Destination filename
        output += conn.send_command_timing(scp_password)   #Password

        print(output)

    except ReadTimeout:
        print("maybe the transfer took too long!!!")

    finally:
        conn.disconnect()



if __name__ == "__main__":
    main()


