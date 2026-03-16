from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class RunContext:
    run_id: str
    artifacts: str                 # absolute path
    stage1_dir: str                # absolute path
    stage1_handoff_path: str       # absolute path
    stage2_dir: str                # absolute path
    stage2_results_path: str       # absolute path
    image: Dict[str, Any]
    device_fs: Dict[str, Any]
    behavior: Dict[str, Any]
    cli: Dict[str, Any]
    transfer: Dict[str, Any]


def build_ctx(run_id: str, config_path: str) -> RunContext:
    """Build RunContext from config.yml path."""
    cfg_path = Path(config_path).expanduser().resolve()
    if not cfg_path.exists():
        raise FileNotFoundError(f"config.yml not found: {cfg_path}")

    config = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}

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

    backend = str(cli.get("backend", "")).strip().lower()
    method = str(transfer.get("method", "")).strip().lower()

    if backend not in {"netmiko", "scrapli"}:
      raise ValueError("config.yml: cli.backend must be 'netmiko' or 'scrapli'")

    if method not in {"scp", "copy_command"}:
      raise ValueError("config.yml: transfer.method must be 'scp' or 'copy_command'")

    if method == "copy_command":
        copy = dict(transfer.get("copy", {}))
        if not copy.get("server_ip"):
            raise ValueError("config.yml: transfer.copy.server_ip is required for copy_command")
        copy.setdefault("server_port", 8000)
        copy.setdefault("protocol", "http")
        transfer["copy"] = copy

    # note: remote_path must be provided by user in config.yml
    if not image.get("remote_path"):
        raise ValueError("config.yml: image.remote_path is required (e.g. bootflash:/<filename>)")

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
    )
"""
{
  "run_id": "<run_id>",

  "artifacts": "<abs path to base_dir/artifacts>",
  "stage1_dir": "<abs path to artifacts/run_id/stage1>",
  "stage1_handoff_path": "<abs path to stage1_dir/stage1_handoff.json>",
  "stage2_dir": "<abs path to artifacts/run_id/stage2>",
  "stage2_results_path": "<abs path to stage2_dir/stage2_results.json>",

  "image": {
    "filename": "<from config.yml>",
    "local_full_path": "<from config.yml>",
    "expected_md5": "<from config.yml>",
    "remote_path": "<remote_dir + filename>"
  },

  "device_fs": {
    "remote_fs": "bootflash:",
    "remote_dir": "bootflash:/",
    "space_factor": 1.5
  },

  "behavior": {
    "max_workers": 5,
    "connect_timeout": 15,
    "cmd_timeout": 60,
    "scp_enable_before_upload": true,
    "scp_disable_after_upload": true
  }

  "cli": {
    "backend": "netmiko"  # or "scrapli"
  },

  "transfer": {
    "method": "scp"  # or "copy_command"
    "copy": {
      "server_ip": "<IP address for copy command file server>",
      "server_port": 8000,
      "protocol": "http"
    }
}
"""