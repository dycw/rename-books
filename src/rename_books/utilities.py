from __future__ import annotations

from typing import TYPE_CHECKING

from pathvalidate import is_valid_filename as _is_valid_filename

if TYPE_CHECKING:
    from pathlib import Path


def change_name(path: Path, name: str, /) -> Path:
    """Change the name of a file."""
    new_path = path.with_name(name)
    suffix = f"{new_path.suffix}{path.suffix}"
    return new_path.with_suffix(suffix)


def change_suffix(path: Path, /, *suffixes: str) -> Path:
    """Change the suffix of a path; accepts parts."""
    return path.with_suffix("".join(suffixes))


def clean_text(text: str, /) -> str:
    """Clean the text."""
    return text.replace("’", "'")


def is_empty(text: str, /) -> bool:
    """Check if a string is the empty string."""
    return text == ""


def is_non_empty(text: str, /) -> bool:
    """Check if a string is not the empty string."""
    return text != ""


def is_valid_filename(text: str, /) -> bool:
    """Check if a filename is valid."""
    return is_empty(text) or _is_valid_filename(text)
