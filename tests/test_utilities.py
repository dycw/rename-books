from pathlib import Path
from typing import Callable
from typing import cast
from typing import TypeVar

from pytest import mark

from rename_books.utilities import change_name


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
