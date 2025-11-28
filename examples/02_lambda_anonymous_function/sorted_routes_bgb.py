
"""
DCI# sh bgp ipv4 unicast 

   Network            Next Hop            Metric     LocPrf     Weight Path
*>e10.2.0.1/32        10.10.1.6                0                     0 65001 ?
*>e10.3.0.2/32        10.10.1.6                0                     0 65001 ?
*>e10.10.0.1/32       10.10.1.2                0                     0 65002 ?
*>e10.10.0.2/32       10.10.1.6                0                     0 65001 ?
*>e10.10.1.0/30       10.10.1.2                0                     0 65002 ?
*>e10.10.1.4/30       10.10.1.6                0                     0 65001 ?
*>e20.2.0.1/32        10.10.1.2                0                     0 65002 ?
*>e20.3.0.2/32        10.10.1.2                0                     0 65002 ?
*>l100.100.100.100/32 0.0.0.0                           100      32768 i
"""
bgp_lines = [
    "*>e10.2.0.1/32        10.10.1.6                0                     0 65001 ?",
    "*>e10.3.0.2/32        10.10.1.6                0                     0 65001 ?",
    "*>e10.10.0.1/32       10.10.1.2                0                     0 65002 ?",
    "*>e10.10.0.2/32       10.10.1.6                0                     0 65001 ?",
    "*>e10.10.1.0/30       10.10.1.2                0                     0 65002 ?",
    "*>e10.10.1.4/30       10.10.1.6                0                     0 65001 ?",
    "*>e20.2.0.1/32        10.10.1.2                0                     0 65002 ?",
    "*>e20.3.0.2/32        10.10.1.2                0                     0 65002 ?",
    "*>l100.100.100.100/32 0.0.0.0                           100      32768 i",
]
def extract_prefix_from_bgp(line: str) -> str:
    for token in line.split():
        if "/" in token and "." in token:
            i = 0
            while i < len(token) and not token[i].isdigit():
                i += 1
            return token[i:]
    return None
def prefix_key(prefix: str):
    net, mask = prefix.split("/")
    octet1, octet2, octet3, octet4 = net.split(".")
    return (int(octet1), int(octet2), int(octet3), int(octet4), int(mask))

sorted_bgp = sorted(
    bgp_lines,
    key= lambda line: prefix_key(extract_prefix_from_bgp(line))
)
for line in sorted_bgp:
    print(line)

         
