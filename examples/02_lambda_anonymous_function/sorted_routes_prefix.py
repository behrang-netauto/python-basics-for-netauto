
"""
!!!anonymous function!!!
sortieren - route_prefix
"""
routes = [
    "10.0.0.0/24",
    "10.0.0.0/8",
    "10.1.0.0/16",
    "192.168.0.0/16",
    "172.16.0.0/16",
]
def route_key(r):
    net, mask = r.split("/")
    octet1, octet2, octet3, octet4 = net.split(".")
    return (
        int(octet1),
        int(octet2),
        int(octet3),
        int(octet4),
        -int(mask),
    )
sorted_route = sorted(routes, key=route_key)
print(sorted_route)

