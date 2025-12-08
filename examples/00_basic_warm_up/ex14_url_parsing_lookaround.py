
import re
def main() -> None:
    url = "http://www.cisco.com/techsupport"

    pattern_protocol = re.compile(r"\w{4,5}(?=:)")
    pattern_host = re.compile(r"(?<=//)[\w.]+(?=/)")    
    #pattern = re.compile(r"(\w{4,5})://([^/]+)/")
    #m = pattern.serch(URL)
    #m.group(0)  #match: "http://www.cisco.com/"
    #m.group(1)  #"http"
    #m.group(2)  #"www.cisco.com"
    protocol_match = pattern_protocol.search(url)
    host_match = pattern_host.search(url)

    if protocol_match:
        print(f"Protocol: {protocol_match.group(0)}")
    else:
        print("protocol not found")
    if host_match:
        print(f"Host: {host_match.group(0)}")
    else:
        print("host not found")

if __name__ == "__main__":
    main()

