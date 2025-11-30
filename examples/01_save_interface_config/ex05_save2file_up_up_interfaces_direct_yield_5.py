
SHOW_IP_INT_BRIEF = """
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     10.0.0.1       YES manual up                    up
GigabitEthernet0/1     unassigned     YES unset  administratively down down
GigabitEthernet0/2     192.168.1.1    YES manual up                    up
Loopback0              1.1.1.1        YES manual up                    up
"""
def iter_up_interfaces(output: str):
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("Interface"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[-1] == "up" and parts[-2] == "up":
            yield line

def main() -> None:
    with open("up_interfaces_3.txt", "w", encoding="utf-8") as f:
        for line in iter_up_interfaces(SHOW_IP_INT_BRIEF):
            f.write(line + "\n")

if __name__ == "__main__":
    main()

