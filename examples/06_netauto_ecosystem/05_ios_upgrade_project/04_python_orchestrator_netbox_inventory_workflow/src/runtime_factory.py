
from __future__ import annotations

from typing import Tuple

from .netmiko_driver import NetmikoDriver
from .scrapli_driver import ScrapliDriver
from .file_transfer import ScpTransfer, CopyCommandTransfer


def build_runtime(ctx) -> Tuple[object, object]:
    """
    Returns (cli, xfer) runtime objects.
    Pairing rules (strict):
      backend=netmiko  -> method=scp
      backend=scrapli  -> method=copy_command
    """
    backend = str(ctx.cli.get("backend", "")).strip().lower()
    method = str(ctx.transfer.get("method", "")).strip().lower()

    # build cli
    if backend == "netmiko":
        cli = NetmikoDriver()
    elif backend == "scrapli":
        cli = ScrapliDriver()
    else:
        # ctx.build_ctx already validates; keep defensive
        raise ValueError(f"unsupported cli.backend={backend!r}")

    # build xfer + validate pairing
    if backend == "netmiko" and method == "scp":
        xfer = ScpTransfer()
    elif backend == "scrapli" and method == "copy_command":
        xfer = CopyCommandTransfer()
    else:
        raise ValueError(
            f"unsupported runtime pairing: cli.backend={backend!r}, transfer.method={method!r}"
        )

    return cli, xfer