
from __future__ import annotations

from typing import Any, Dict


class ScpTransfer:
    """
    Pairing assumption:
      cli.backend == "netmiko"
      transfer.method == "scp"
    handle is a Netmiko connection handle.
    """

    def upload(self, handle, ctx, device: Dict[str, Any], creds: Dict[str, Any]) -> None:
        # Netmiko file_transfer needs file_system + dest_file
        from netmiko import file_transfer as nm_file_transfer

        local_full_path = ctx.image["local_full_path"]
        filename = ctx.image["filename"]
        remote_dir = ctx.device_fs["remote_dir"]  # e.g. "bootflash:/"

        nm_file_transfer(
            handle,
            source_file=local_full_path,
            dest_file=filename,
            file_system=remote_dir,
            direction="put",
            overwrite_file=True,
        )
        return


class CopyCommandTransfer:
    """
    Pairing assumption:
      cli.backend == "scrapli"
      transfer.method == "copy_command"
    handle is a Scrapli connection handle.
    We run copy command over the existing session (no extra sessions).
    """

    def upload(self, handle, ctx, device: Dict[str, Any], creds: Dict[str, Any]) -> None:
        filename = ctx.image["filename"]
        remote_path = ctx.image.get("remote_path") or f'{ctx.device_fs["remote_dir"]}{filename}'

        copy_meta = ctx.transfer.get("copy", {})
        server_ip = copy_meta["server_ip"]
        server_port = int(copy_meta.get("server_port", 8000))
        protocol = str(copy_meta.get("protocol", "http")).strip().lower()

        url = f"{protocol}://{server_ip}:{server_port}/{filename}"
        cmd = f"copy {url} {remote_path}"

        # Common prompts: Destination filename? [<...>], [confirm]
        interactions = [
            (cmd, r"Destination filename|\[confirm\]|#", False),
            ("", r"\[confirm\]|#", False),   # press Enter for destination filename or confirm
            ("", r"#", False),              # final Enter if needed
        ]

        try:
            handle.send_interactive(interactions, timeout_ops=ctx.behavior.get("cmd_timeout", 30))
        except Exception:
            # After successful copy, device might still be fine; but on errors we want to fail fast.
            raise

        return