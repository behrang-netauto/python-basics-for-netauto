
"""
!!!anonymous function!!!
sortieren - routes_aggregated_specific
"""

routes = [
    "O        10.0.0.0/8 [110/2] via 192.0.2.1, 00:00:12, GigabitEthernet0/0",
    "O        10.0.0.0/24 [110/2] via 192.0.2.2, 00:01:12, GigabitEthernet0/1",
    "C        10.1.0.0/16 is directly connected, GigabitEthernet0/2",
    "O        192.168.0.0/16 [110/3] via 198.51.100.1, 00:00:30, GigabitEthernet0/3",
    "O        172.16.0.0/16 [110/5] via 192.0.2.5, 00:00:45, GigabitEthernet0/4",
]
def extract_prefix(line: str) -> str:
    for token in line.split():
        if "/" in token and "." in token:
            return(token)
    return None

def route_key_aggregated(line: str):
    route_prefix = extract_prefix(line)
    net, mask = route_prefix.split("/")
    octet1, octet2, octet3, octet4 = net.split(".")
    return (int(octet1), int(octet2), int(octet3), int(octet4), int(mask))

route_aggregated_sort = sorted(routes, key=route_key_aggregated)

for r in route_aggregated_sort:
    print(r)

print(f"------------------------------------------------------------------")

def route_key_specific(line: str):
    route_prefix = extract_prefix(line)
    net, mask = route_prefix.split("/")
    octet1, octet2, octet3, octet4 = net.split(".")
    return(int(octet1), int(octet2), int(octet3), int(octet4), -int(mask))

route_specific_sort = sorted(routes, key=route_key_specific)

for r in route_specific_sort:
    print(r)





