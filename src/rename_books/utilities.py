from __future__ import annotations

from pathlib import Path


def change_name(path: Path, name: str, /) -> Path:
    """Change the name of a file."""
    new_path = path.with_name(name)
    suffix = f"{new_path.suffix}{path.suffix}"
    return new_path.with_suffix(suffix)


def change_suffix(path: Path, /, *suffixes: str) -> Path:
    """Change the suffix of a path; accepts parts."""
    return path.with_suffix("".join(suffixes))


def get_dropbox_path() -> Path:
    """Get the Dropbox path."""
    return next(
        path
        for path in [
            Path.home().joinpath("Dropbox"),  # DW-PC-Ubuntu
            Path("/data/derek/Dropbox"),  # DW-NUC
            Path("/mnt/c/Users/Derek/Dropbox"),  # DW-Acer
            Path("/mnt/c/Users/D/Dropbox"),  # DW-PC
        ]
        if path.exists()
    )


def get_temporary_path() -> Path:
    """Get the Dropbox temporary folder path."""
    return get_dropbox_path().joinpath("Temporary")


def is_non_empty(text: str, /) -> bool:
    """Check if a string is the empty string."""
    return text != ""
