from __future__ import annotations

from pathlib import Path
from typing import Callable

from pytest import mark

from rename_books.utilities import change_name
from rename_books.utilities import change_suffix
from rename_books.utilities import get_dropbox_path
from rename_books.utilities import get_temporary_path


@mark.parametrize(
    "path, name, expected",
    [
        (
            Path("dir/subdir/name.pdf"),
            "new_name",
            Path("dir/subdir/new_name.pdf"),
        ),
        (
            Path("dir/subdir/node.js 8.pdf"),
            "node.js 9",
            Path("dir/subdir/node.js 9.pdf"),
        ),
    ],
)
def test_change_name(path: Path, name: str, expected: Path) -> None:
    assert change_name(path, name) == expected


@mark.parametrize(
    "path, suffixes, expected",
    [
        (Path("dir/subdir/name.pdf"), [], Path("dir/subdir/name")),
        (Path("dir/subdir/name.pdf"), [".csv"], Path("dir/subdir/name.csv")),
        (
            Path("dir/subdir/name.pdf"),
            [".pdf", ".part"],
            Path("dir/subdir/name.pdf.part"),
        ),
        (
            Path("dir/subdir/name (z-lib.org).pdf"),
            [".pdf", ".part"],
            Path("dir/subdir/name (z-lib.org).pdf.part"),
        ),
    ],
)
def test_change_suffix(path: Path, suffixes: list[str], expected: Path) -> None:
    assert change_suffix(path, *suffixes) == expected


@mark.parametrize("func", [get_dropbox_path, get_temporary_path])
@mark.xfail
def test_get_path(func: Callable[[], Path]) -> None:
    path = func()
    assert isinstance(path, Path)
    assert path.exists()
