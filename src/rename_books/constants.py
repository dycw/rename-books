from __future__ import annotations

from pathlib import Path
from socket import gethostname


def _get_path_dropbox() -> Path:
    """Get the path to Dropbox."""
    if (hostname := gethostname()) == "DW-Acer":
        return Path("/mnt/c/Documents and Settings/Derek/Dropbox")
    if hostname == "DW-NUC":
        return Path("/data/Dropbox")
    if hostname in {"DW-Mac", "DW-Laptop", "DW-PC", "DW-PC-Ubuntu"}:
        return Path.home().joinpath("Dropbox")
    msg = f"Invalid {hostname=}"
    raise RuntimeError(msg)


DROPBOX = _get_path_dropbox()
BOOKS_AND_PAPERS = DROPBOX.joinpath("1 – Derek", "Books and papers")
BOOKS = BOOKS_AND_PAPERS.joinpath("Books")
TEMPORARY_PATH = DROPBOX.joinpath("Temporary")


__all__ = ["BOOKS", "BOOKS_AND_PAPERS", "DROPBOX", "TEMPORARY_PATH"]
