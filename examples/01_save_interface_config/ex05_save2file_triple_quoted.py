
SHOW_IP_INT_BRIEF = """
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     10.0.0.1       YES manual up                    up
GigabitEthernet0/1     unassigned     YES unset  administratively down down
GigabitEthernet0/2     192.168.1.1    YES manual up                    up
Loopback0              1.1.1.1        YES manual up                    up
"""
def main() -> None:
    for line in SHOW_IP_INT_BRIEF.splitlines(keepends= True):
        try:
            with open("config.txt", "w", encoding= "utf-8") as f:
                f.write("\n"+ line+ "\n")
        except OSError as error:
            print(f"einen Fehler: {error}")
        else:
            print("Es hat geklappt")
            print("Schau mal, was das ist")
            try:
                with open("config.txt", "r", encoding= "utf-8") as f:
                    content = f.read()
                    for line in content.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        print(line)
            except OSError as error:
                print(f"einen Fehler: {error}")

if __name__ == "__main__":
    main()
