
def main() -> None:
    with open("ip_addresses.txt", "r") as f:
        for line in f:
            ip = line.strip()
            if ip.endswith(("3" , "4")):
                print(ip)
        
if __name__ == "__main__":
    main()



print(f"------------------------------------------------------")



def main() -> None:
    with open("ip_addresses.txt", "r") as f:
        for line in f:
            ip = line.strip()
            if not ip:     # "" 0 {} [] None
                continue
            last_char = ip[-1]
            if last_char in ("3" , "4"):
                print(ip)

if __name__ == "__main__":
    main()
