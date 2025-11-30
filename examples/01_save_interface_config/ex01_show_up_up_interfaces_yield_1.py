
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
    gen = iter_up_interfaces(SHOW_IP_INT_BRIEF)

    try:
        first = next(gen)
    except StopIteration:
        print("Es gibt keine verdammte up und up")
        return

    print("First up/up interface:")
    print(first)

    print("\nOther up/up interfaces:")
    for line in gen:
        print(line)

if __name__ == "__main__":
    main()



