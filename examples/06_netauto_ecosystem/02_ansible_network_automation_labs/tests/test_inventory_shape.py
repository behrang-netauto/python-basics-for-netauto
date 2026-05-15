from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_FILE = PROJECT_ROOT / "inventory" / "inventory_lab.yml"


def load_inventory() -> dict:
    return yaml.safe_load(INVENTORY_FILE.read_text())


def test_inventory_has_expected_groups():
    inventory = load_inventory()

    children = inventory["all"]["children"]
    assert "network_devices" in children

    network_children = children["network_devices"]["children"]
    assert "ios" in network_children
    assert "nxos" in network_children


def test_ios_inventory_shape():
    inventory = load_inventory()
    ios_group = inventory["all"]["children"]["network_devices"]["children"]["ios"]

    ios_vars = ios_group["vars"]
    ios_hosts = ios_group["hosts"]

    assert ios_vars["ansible_connection"] == "ansible.netcommon.network_cli"
    assert ios_vars["ansible_network_os"] == "cisco.ios.ios"
    assert ios_vars["ansible_become"] is True
    assert ios_vars["ansible_become_method"] == "enable"

    assert set(ios_hosts) == {"csr1000v", "iol_r1"}

    for host_name, host_vars in ios_hosts.items():
        assert "ansible_host" in host_vars, f"{host_name} must define ansible_host"
        assert "platform" in host_vars, f"{host_name} must define platform"
        assert "device_model" in host_vars, f"{host_name} must define device_model"


def test_nxos_inventory_shape():
    inventory = load_inventory()
    nxos_group = inventory["all"]["children"]["network_devices"]["children"]["nxos"]

    nxos_vars = nxos_group["vars"]
    nxos_hosts = nxos_group["hosts"]

    assert nxos_vars["ansible_connection"] == "ansible.netcommon.network_cli"
    assert nxos_vars["ansible_network_os"] == "cisco.nxos.nxos"

    assert set(nxos_hosts) == {"nxos1"}

    for host_name, host_vars in nxos_hosts.items():
        assert "ansible_host" in host_vars, f"{host_name} must define ansible_host"
        assert "platform" in host_vars, f"{host_name} must define platform"
        assert "device_model" in host_vars, f"{host_name} must define device_model"


def test_network_devices_use_paramiko_backend():
    inventory = load_inventory()
    network_vars = inventory["all"]["children"]["network_devices"]["vars"]

    assert network_vars["ansible_network_cli_ssh_type"] == "paramiko"


def test_inventory_does_not_contain_plaintext_passwords():
    raw_inventory = INVENTORY_FILE.read_text().lower()

    forbidden_patterns = [
        "ansible_password:",
        "ansible_become_password:",
        "password:",
        "token:",
        "secret:",
        "api_key:",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in raw_inventory, f"inventory must not contain {pattern}"
