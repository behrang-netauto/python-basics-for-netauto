
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class RunContext:
    run_id: str
    artifacts: str
    stage1_dir: str
    stage1_handoff_path: str
    stage2_dir: str
    stage2_results_path: str
    image: Dict[str, Any]
    device_fs: Dict[str, Any]
    behavior: Dict[str, Any]
    cli: Dict[str, Any]
    transfer: Dict[str, Any]
    inventory: Dict[str, Any]
    netbox: Dict[str, Any]


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def build_ctx(run_id: str, config_path: str, vault_path: str) -> RunContext:
    """Build RunContext from config.yml + vault.yml."""
    cfg_path = Path(config_path).expanduser().resolve()
    vault_path_obj = Path(vault_path).expanduser().resolve()

    if not cfg_path.exists():
        raise FileNotFoundError(f"config.yml not found: {cfg_path}")
    if not vault_path_obj.exists():
        raise FileNotFoundError(f"vault.yml not found: {vault_path_obj}")

    config = _load_yaml(cfg_path)
    vault = _load_yaml(vault_path_obj)

    base_dir = cfg_path.parent
    artifacts_root = config.get("artifacts_root", "artifacts")
    artifacts = (base_dir / artifacts_root).resolve()

    stage1_dir = (artifacts / run_id / "stage1").resolve()
    stage1_handoff_path = (stage1_dir / "stage1_handoff.json").resolve()

    stage2_dir = (artifacts / run_id / "stage2").resolve()
    stage2_results_path = (stage2_dir / "stage2_results.json").resolve()

    image = dict(config.get("image", {}))
    device_fs = dict(config.get("device_fs", {}))
    behavior = dict(config.get("behavior", {}))

    cli = dict(config.get("cli", {}))
    transfer = dict(config.get("transfer", {}))
    inventory = dict(config.get("inventory", {}))
    netbox = dict(config.get("netbox", {}))

    backend = str(cli.get("backend", "")).strip().lower()
    method = str(transfer.get("method", "")).strip().lower()
    source = str(inventory.get("source", "")).strip().lower()

    if backend not in {"netmiko", "scrapli"}:
        raise ValueError("config.yml: cli.backend must be 'netmiko' or 'scrapli'")

    if method not in {"scp", "copy_command"}:
        raise ValueError("config.yml: transfer.method must be 'scp' or 'copy_command'")

    if source not in {"yaml", "netbox"}:
        raise ValueError("config.yml: inventory.source must be 'yaml' or 'netbox'")

    if method == "copy_command":
        copy = dict(transfer.get("copy", {}))
        if not copy.get("server_ip"):
            raise ValueError("config.yml: transfer.copy.server_ip is required for copy_command")
        copy.setdefault("server_port", 8000)
        copy.setdefault("protocol", "http")
        transfer["copy"] = copy

    if not image.get("remote_path"):
        raise ValueError("config.yml: image.remote_path is required (e.g. bootflash:/<filename>)")

    if source == "yaml":
        inventory_path = inventory.get("inventory_path")
        if not inventory_path:
            raise ValueError("config.yml: inventory.inventory_path is required when source=yaml")
        inventory["inventory_path"] = str((base_dir / inventory_path).resolve())

    if source == "netbox":
        if not inventory.get("site"):
            raise ValueError("config.yml: inventory.site is required when source=netbox")
        if not netbox.get("base_url"):
            raise ValueError("config.yml: netbox.base_url is required when source=netbox")

        vault_netbox = dict(vault.get("netbox", {}))
        token = vault_netbox.get("token")
        if not token:
            raise ValueError("vault.yml: netbox.token is required when source=netbox")

        netbox["token"] = token
        netbox.setdefault("verify_ssl", True)
        netbox.setdefault("timeout", 20)

    return RunContext(
        run_id=run_id,
        artifacts=str(artifacts),
        stage1_dir=str(stage1_dir),
        stage1_handoff_path=str(stage1_handoff_path),
        stage2_dir=str(stage2_dir),
        stage2_results_path=str(stage2_results_path),
        image=image,
        device_fs=device_fs,
        behavior=behavior,
        cli=cli,
        transfer=transfer,
        inventory=inventory,
        netbox=netbox,
    )