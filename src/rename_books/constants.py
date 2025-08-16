from __future__ import annotations

from pathlib import Path

DROPBOX = Path.home().joinpath("Dropbox")
BOOKS_AND_PAPERS = DROPBOX.joinpath("1 – Derek", "Books and papers")
BOOKS = BOOKS_AND_PAPERS.joinpath("Books")
TEMPORARY_PATH = DROPBOX.joinpath("Temporary")


__all__ = ["BOOKS", "BOOKS_AND_PAPERS", "DROPBOX", "TEMPORARY_PATH"]
