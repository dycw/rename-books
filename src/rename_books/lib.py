from __future__ import annotations

from re import search
from typing import TYPE_CHECKING

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator

from rename_books.constants import TEMPORARY_PATH
from rename_books.utilities import change_suffix

if TYPE_CHECKING:
    from pathlib import Path


def get_next_file(*, skips: set[Path] | None = None) -> Path | None:
    """Get the next file to process, if it exists."""
    paths = (
        path
        for path in TEMPORARY_PATH.iterdir()
        if path.is_file()
        and _needs_processing(path)
        and not change_suffix(path, ".pdf", ".part").exists()
    )
    if skips is not None:
        paths = (path for path in paths if path not in skips)
    try:
        return next(iter(sorted(paths)))
    except StopIteration:
        return None


def _needs_processing(path: Path, /) -> bool:
    """Check if a file needs processing."""
    return (not search(r"^\d+ — .+( – .+)?(\(.+\))?$", path.name)) and (
        path.suffix in {".epub", ".pdf"}
    )


def get_decision(path: Path, /) -> bool:
    """Get the decision for a given path."""
    result = prompt(
        f"File = {path.name}\nProcess or skip? ",
        completer=WordCompleter(["process", "skip"]),
        default="process",
        mouse_support=True,
        validator=Validator.from_callable(
            lambda text: bool(search(r"(process|skip)", text)),
            error_message="Enter 'process' or 'skip'",
        ),
        vi_mode=True,
    ).strip()
    return result == "process"
