
def get_filtered_ips(filename: str) -> list[str]:
    ips: list[str] = []
    with open(filename, "r") as f:
        for line in f:
            ip = line.strip()
            if ip.endswith(("3", "4")):
                ips.append(ip)
    return ips

def main() -> None:
    filterd_ips = get_filtered_ips("ip_addresses.txt")
    for ip in filterd_ips:
        print(ip)


if __name__ == "__main__":
    main()




