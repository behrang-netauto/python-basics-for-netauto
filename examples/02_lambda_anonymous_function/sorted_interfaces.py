
"""
!!!anonymous function!!!
sortieren - basierend auf letzte Nummer
"""


interfaces = ["Gi1/0/10", "Gi1/0/2", "Gi1/0/1"]

sorted_interface = sorted(interfaces, key= lambda x: int(x.split("/")[-1]))
print(sorted_interface)