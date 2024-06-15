from __future__ import annotations

from pathlib import Path
from socket import gethostname


def _get_path_dropbox() -> Path:
    """Get the path to Dropbox."""
    if (hostname := gethostname()) == "DW-Acer":
        return Path("/mnt/c/Documents and Settings/Derek/Dropbox")
    if hostname == "DW-NUC":
        return Path("/data/Dropbox")
    if hostname in {"DW-Mac", "DW-PC", "DW-PC-Ubuntu"}:
        return Path.home().joinpath("Dropbox")
    msg = f"Invalid {hostname=}"
    raise RuntimeError(msg)


DROPBOX = _get_path_dropbox()
TEMPORARY_PATH = DROPBOX.joinpath("Temporary")
