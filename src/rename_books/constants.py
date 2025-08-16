from __future__ import annotations

from pathlib import Path


def _get_path_dropbox() -> Path:
    """Get the path to Dropbox."""
    return Path.home().joinpath("Dropbox")


DROPBOX = _get_path_dropbox()
BOOKS_AND_PAPERS = DROPBOX.joinpath("1 – Derek", "Books and papers")
BOOKS = BOOKS_AND_PAPERS.joinpath("Books")
TEMPORARY_PATH = DROPBOX.joinpath("Temporary")


__all__ = ["BOOKS", "BOOKS_AND_PAPERS", "DROPBOX", "TEMPORARY_PATH"]
