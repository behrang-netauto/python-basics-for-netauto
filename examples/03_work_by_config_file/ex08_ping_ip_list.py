
import getpass
from netmiko import ConnectHandler
from netmiko.exceptions import ReadTimeout

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
    
    for ip in ips:
        cmd = f"{COMMAND} {ip}"
        print(f"\n-----PING {ip}-----")
        try:
            out_put = conn.send_command(
                cmd,
                read_timeout=15,
                expect_string=r"#",
                )
        except ReadTimeout:
            print(f"timeout while pingig {ip}, aber keine sorge!!!")
            continue

        print(out_put)

    conn.disconnect()

if __name__ == "__main__":
    main()








    