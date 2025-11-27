
"""
!!!anonymous function!!!
sortieren - vlans
"""

vlans = ["10", "2", "100", "20"]

sorted_vlans = sorted(vlans, key=int)
print(sorted_vlans)


print(f"-------------------------------------------------------")


vlans = ["VLAN10", "VLAN2", "VLAN100", "VLAN20"]

sorted_vlans = sorted(
    vlans, key= lambda vlan: int(vlan.replace("VLAN", ""))
)
print(sorted_vlans)

