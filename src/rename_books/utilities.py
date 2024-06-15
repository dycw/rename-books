from __future__ import annotations

from pathlib import Path


def change_name(path: Path, name: str, /) -> Path:
    new_path = path.with_name(name)
    suffix = f"{new_path.suffix}{path.suffix}"
    return new_path.with_suffix(suffix)


def change_suffix(path: Path, /, *suffixes: str) -> Path:
    return path.with_suffix("".join(suffixes))


def get_dropbox_path() -> Path:
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
    return get_dropbox_path().joinpath("Temporary")


def is_non_empty(text: str, /) -> bool:
    return text != ""
