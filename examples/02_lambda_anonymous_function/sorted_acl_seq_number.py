
"""
!!!anonymous function!!!
sortieren - acl
"""
acl_lines = [
    "10 permit ip any any",
    "5 deny tcp any any eq 23",
    "20 permit icmp any any",
    "15 deny ip any any",
]

sorted_acl = sorted(
    acl_lines,
    key= lambda line: (
        int(line.split()[0])
    )
)
print(sorted_acl)

