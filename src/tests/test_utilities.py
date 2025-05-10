from __future__ import annotations

from pathlib import Path

from pytest import mark, param

from rename_books.utilities import (
    change_name,
    change_suffix,
    is_empty_or_is_valid_filename,
)


class TestChangeName:
    @mark.parametrize(
        ("path", "name", "expected"),
        [
            (Path("dir/subdir/name.pdf"), "new_name", Path("dir/subdir/new_name.pdf")),
            (
                Path("dir/subdir/node.js 8.pdf"),
                "node.js 9",
                Path("dir/subdir/node.js 9.pdf"),
            ),
        ],
    )
    def test_main(self, *, path: Path, name: str, expected: Path) -> None:
        assert change_name(path, name) == expected


class TestChangeSuffix:
    @mark.parametrize(
        ("path", "suffixes", "expected"),
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
    def test_main(self, *, path: Path, suffixes: list[str], expected: Path) -> None:
        assert change_suffix(path, *suffixes) == expected


class TestIsValidFileName:
    @mark.parametrize(
        ("text", "expected"),
        [
            param("", False),
            param("C/C++", False),
            param("name", True),
        ],
    )
    def test_main(self, *, text: str, expected: bool) -> None:
        assert is_empty_or_is_valid_filename(text) is expected
