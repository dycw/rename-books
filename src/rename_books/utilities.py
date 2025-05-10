from __future__ import annotations

from typing import TYPE_CHECKING

from pathvalidate import is_valid_filename
from titlecase import titlecase

if TYPE_CHECKING:
    from pathlib import Path


def change_suffix(path: Path, /, *suffixes: str) -> Path:
    """Change the suffix of a path; accepts parts."""
    return path.with_suffix("".join(suffixes))


def clean_text(text: str, /) -> str:
    """Clean the text."""
    return titlecase(text.replace("’", "'"))


def is_empty(text: str, /) -> bool:
    """Check if a string is the empty string."""
    return text == ""


def is_non_empty(text: str, /) -> bool:
    """Check if a string is not the empty string."""
    return text != ""


def is_empty_or_is_valid_filename(text: str, /) -> bool:
    """Check if a filename is valid."""
    return is_empty(text) or is_valid_filename(text)


__all__ = [
    "change_suffix",
    "clean_text",
    "is_empty",
    "is_empty_or_is_valid_filename",
    "is_non_empty",
]
