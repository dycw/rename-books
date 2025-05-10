from __future__ import annotations

from pathlib import Path

from pytest import mark, param

from rename_books.lib import _needs_processing
from rename_books.utilities import clean_text


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
            param("2000 — Title.pdf", False),
            param("2000 — Title – Sub.pdf", False),
            param("2000 — Title – Sub1 – Sub2.pdf", False),
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
    def test_main(self, *, name: str, expected: bool) -> None:
        result = _needs_processing(Path(name))
        assert result is expected
