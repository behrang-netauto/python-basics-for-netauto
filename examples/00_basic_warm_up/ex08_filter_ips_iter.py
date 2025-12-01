
from typing import Iterable

def get_filtered_ips(filename: str, suffixes: Iterable[str]) -> Iterable[str]:  
    try:
        with open(filename, "r") as f:
            for line in f:
                ip = line.strip()
                if not ip:
                    continue
                if ip.endswith(tuple(suffixes)):
                    yield ip
    except OSError as error:
        print(f"Es gibt einen Fehler: {error}")
def main() -> None:
    gen = get_filtered_ips("ip_addresses.txt", ("3", "4"))
    for ip in gen:
        print(ip)
if __name__ == "__main__":
    main()
