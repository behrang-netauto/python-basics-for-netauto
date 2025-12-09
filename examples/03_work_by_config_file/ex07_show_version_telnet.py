
import getpass
from netmiko import ConnectHandler
from pathlib import Path
import re

def main() -> None:

    pattern = re.compile(r"\((X86\S+)\),\s+(Version\s+[\w.]+),", re.I)

    HOST = "192.168.2.45"
    COMMAND = "sh version"

    device = {
        "host": HOST,
        "username": user,
        "password": password,
    }
    
    user = input("enter user nsme: ").strip()
    password = getpass.getpass("password: ")

    conn = ConnectHandler(**device)
    output = conn.send_command(COMMAND)
    conn.disconnect()

    home_dir = Path.home()
    base_dir = home_dir / "Documents" / "Python" / "Code/netauto_example_01" / "python-basics-for-netauto" / "examples" / "03_work_by_config_file"
    out_file = base_dir / "sh_version.txt"
    out_file.write_text(output)

    math_version = pattern.search(out_file)

    if math_version:
        part_num = math_version.group(1)
        version = math_version.group(2)
        print(f"{part_num} {version}")
    else:
        print("not found!!")

if __name__ == "__main__":
    main()


