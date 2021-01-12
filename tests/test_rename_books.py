from pathlib import Path
from typing import Callable
from typing import cast
from typing import List
from typing import TypeVar

from pytest import mark

from main import change_name
from main import change_suffix

T = TypeVar("T")


@cast(
    Callable[[T], T],
    mark.parametrize(
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
    ),
)
def test_change_name(path: Path, name: str, expected: Path) -> None:
    assert change_name(path, name) == expected


@cast(
    Callable[[T], T],
    mark.parametrize(
        "path, suffixes, expected",
        [
            (
                Path("dir/subdir/name.pdf"),
                [],
                Path("dir/subdir/name"),
            ),
            (
                Path("dir/subdir/name.pdf"),
                [".csv"],
                Path("dir/subdir/name.csv"),
            ),
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
    ),
)
def test_change_suffix(path: Path, suffixes: List[str], expected: Path) -> None:
    assert change_suffix(path, *suffixes) == expected


# CSS Master by Tiffany B Brown (z-lib.org).pdf
