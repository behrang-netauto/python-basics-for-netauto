
"""
!!!anonymous function!!!
sortieren - basierend auf Slot und Port
"""

interfaces = ["Gi1/0/10", "Gi1/0/2", "Gi2/0/1", "Gi1/0/1"]

sorted_interface = sorted(
    interfaces, 
    key=lambda x: (
        int(x[2:].split("/")[0]), 
        int(x.split("/")[-1])
    )
)
print(sorted_interface)
