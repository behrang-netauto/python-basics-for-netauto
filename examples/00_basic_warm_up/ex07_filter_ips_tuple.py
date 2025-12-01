
from typing import Iterable

def get_filtered_ips(filename: str, suffixes: Iterable[str]) -> list[str]:
    ips: list[str] = []
    try:
        with open(filename, "r") as f:
            for line in f:
                ip = line.strip()
                if not ip:
                    continue
                if ip.endswith(tuple(suffixes)):
                    ips.append(ip)
    
    except OSError as error:
        print(f"Es gibt einen Fehler: {error}")

    else:
        return ips

def main() -> None:
    filterd_ips = get_filtered_ips("ip_addresses.txt", ("3", "4"))
    for ip in filterd_ips:
        print(ip)

if __name__ == "__main__":
    main()

