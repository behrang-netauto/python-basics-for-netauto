
"""
!!!anonymous function!!!
sortieren - ip address
"""
ips = ["10.0.0.1", "10.0.0.20", "10.0.0.3", "192.168.1.5", "172.16.0.1"]

sorted_ip_address = sorted(
    ips, key=lambda ip: tuple(int(octet) for octet in ip.split("."))
    )

print(sorted_ip_address)


