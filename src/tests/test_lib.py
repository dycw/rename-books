from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import mark, param

from rename_books.lib import _needs_processing
from rename_books.utilities import clean_text

if TYPE_CHECKING:
    from pathlib import Path


class TestCleanText:
    @mark.parametrize(
        ("text", "expected"),
        [
            param(
                "A Survey of the World’s Top Asset Allocation Strategies",
                "A Survey of the World's Top Asset Allocation Strategies",
            )
        ],
    )
    def test_main(self, *, text: str, expected: str) -> None:
        assert clean_text(text) == expected


class TestNeedsProcessing:
    @mark.parametrize(
        ("name", "expected"),
        [
            param("2000 — Title.pdf", True),
            param("2000 — Title – Sub.pdf", True),
            param("2000 — Title – Sub1 – Sub2.pdf", True),
            param("2000 — Title (Author).pdf", False),
            param("2000 — Title – Sub (Author).pdf", False),
            param("2000 — Title – Sub1 – Sub2 (Author).pdf", False),
            param("foo.epub", True),
            param("foo.jpg", False),
            param("foo.pdf", True),
            param("foo.pdf.download", False),
            param("foo.epub.download", False),
            param("foo.pdf.part", False),
            param("foo.epub.part", False),
        ],
    )
    def test_main(self, *, tmp_path: Path, name: str, expected: bool) -> None:
        path = tmp_path.joinpath(name)
        path.touch()
        result = _needs_processing(path)
        assert result is expected
