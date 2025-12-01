
def main() -> None:
    with open("ip_addresses.txt", "r") as f:
        for line in f:
            ip = line.strip()
            if "." in ip:
                print(f"Found IP: {ip}", type(ip))

if __name__ == "__main__":
    main()



