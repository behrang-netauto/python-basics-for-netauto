
"""
This file ist a Python Module!
We will import these functions from another script!
"""

from time import strftime

DEFAULT_VLAN_ID = 1

def build_int_config (interface_name: str,
                      description: str,
                      vlan_id: int = DEFAULT_VLAN_ID) -> str:
    """
    simple access int config
    """
    config = (
        f"interface {interface_name}\n"
        f"\tdescription {description}\n"
        f"\tswitchport mode access\n"
        f"\tswitsch port access vlan {vlan_id}\n"
        f"\tspanning tree portfast\n"
    )
    return config

def make_config_filename (hostname: str) -> str:
    """
    funktion for filename creation!
    """
    timestamp = strftime("%Y-%m-%d_%H-%M")
    erste_hostname = hostname.replace(" ", "-")
    filename = f"{erste_hostname}_{timestamp}.cfg"
    return filename



