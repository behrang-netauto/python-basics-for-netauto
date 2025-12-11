
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
    
def analyze_log(log_path: Path) -> None:
    total = 0
    ok_ips: list[str] = []
    fail_ips: list[str] = []
    unknown_ips: list[str] = []
    netmiko_timeout_ips: list[str] = []
    current_ip: str | None = None
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("-----PING"):
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[1].strip("-")
                    current_ip = ip
            elif line.startswith("STATUS:"):
                if current_ip is None:
                    continue
                total += 1
                status = line.split(":", 1)[1].strip()
                if status == "PING_OK":
                    ok_ips.append(current_ip)
                elif status == "PING_FAIL_ICMP":
                    fail_ips.append(current_ip)
                elif status == "PING_UNKNOWN":
                    unknown_ips.append(current_ip)
                elif status == "NETMIKO_TIMEOUT":
                    netmiko_timeout_ips.append(current_ip)
    
    print(f"Total IPs: {total}")
    print(f"  PING_OK:         {len(ok_ips)}")
    print(f"  PING_FAIL_ICMP:  {len(fail_ips)}")
    print(f"  PING_UNKNOWN:    {len(unknown_ips)}")
    print(f"  NETMIKO_TIMEOUT: {len(netmiko_timeout_ips)}")

    if fail_ips or netmiko_timeout_ips:
        print("\nFailed / Problematic IPs:")
    for ip in fail_ips:
        print(f"  ICMP fail:       {ip}")
    for ip in netmiko_timeout_ips:
        print(f"  Netmiko timeout: {ip}")
    
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
    base_dir.mkdir(parents=True, exist_ok=True)
    out_file = base_dir / "log_ping_pars.txt"

    with out_file.open("w", encoding="utf-8") as f:    #Path.open(mode="r", encoding=None,...)
            for ip in ips:
                cmd = f"{COMMAND} {ip}"
                try:
                    out_put = conn.send_command(
                        cmd,
                        read_timeout=15,
                        expect_string=r"#",
                    )
                    if "Success rate is 0 percent" in out_put:
                        status = "PING_FAIL_ICMP"
                    elif "Success rate is" in out_put:
                        status = "PING_OK"
                    else:
                        status = "PING_UNKNOWN"

                    log_block = f"\n-----PING {ip}-----\nSTATUS: {status}\n{out_put}\n"
                
                except ReadTimeout:
                    status = "NETMIKO_TIMEOUT"
                    msg = f"STATUS: {status}\n (no CLI prompt for pingig {ip})"
                    
                    log_block = f"\n-----PING {ip}-----\n{msg}\n"
                
                f.write(log_block)

    print(f"\nlog written to: {out_file}")

    conn.disconnect()

    analyze_log(out_file)


if __name__ == "__main__":
    main()








    

