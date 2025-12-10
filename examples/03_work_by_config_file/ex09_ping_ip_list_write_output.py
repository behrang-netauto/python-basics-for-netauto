
import getpass
from netmiko import ConnectHandler
from netmiko.exceptions import ReadTimeout
from pathlib import Path

def ask_filename(default_name: str = "ip_list.txt") -> str:
    filename = input(f"your file name: | [{default_name}]").strip()
    if not filename:
        return default_name
    return filename
def read_file(filename: str) -> list[str]:
    with open(filename, "r", encoding= "utf-8") as f:
        return [line.strip() for line in f if line.strip()]
def main() -> None:
    HOST = "192.168.2.45"
    COMMAND = "ping"

    username = input("username: ").strip()
    password = getpass.getpass("password: ")

    device = {
        "device_type" : "cisco_ios",
        "host" : HOST,
        "username" : username,
        "password" : password,
    }
    conn = ConnectHandler(**device)

    filename = ask_filename()
    
    try:
        ips = read_file(filename)
    except FileNotFoundError:
        print("file not found")
        conn.disconnect()
        return
    home_dir = Path.home()
    base_dir = home_dir / "Documents" / "Python" / "Code/netauto_example_01" / "python-basics-for-netauto" / "examples" / "03_work_by_config_file"
    out_file = base_dir / "log_ping.txt"

    with out_file.open("w", encoding="utf-8") as f:    #Path.open(mode="r", encoding=None,...)
            for ip in ips:
                cmd = f"{COMMAND} {ip}"
                try:
                    out_put = conn.send_command(
                        cmd,
                        read_timeout=15,
                        expect_string=r"#",
                    )
                    log_block = f"\n-----PING {ip}-----\n{out_put}\n"
                except ReadTimeout:
                    msg = f"timeout while pingig {ip}"
                    log_block = f"\n-----PING {ip}-----\n{msg}\n"
                
                f.write(log_block)

    print(f"\nlog written to: {out_file}")

    conn.disconnect()

if __name__ == "__main__":
    main()








    