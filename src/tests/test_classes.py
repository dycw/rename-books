from __future__ import annotations

from pytest import mark, param

from rename_books.classes import MetaData, StemMetaData


class TestFromStem:
    @mark.parametrize(
        ("stem", "expected"),
        [
            param("2000 — Title", StemMetaData(year=2000, title="Title"))
            # param("2000 — Title – Sub.pdf", False),
            # param("2000 — Title – Sub1 – Sub2.pdf", False),
            # param("2000 — Title (Author).pdf", False),
            # param("2000 — Title – Sub (Author).pdf", False),
            # param("2000 — Title – Sub1 – Sub2 (Author).pdf", False),
            # param("foo.epub", True),
            # param("foo.jpg", False),
            # param("foo.pdf", True),
            # param("foo.pdf.download", False),
            # param("foo.epub.download", False),
            # param("foo.pdf.part", False),
            # param("foo.epub.part", False),
        ],
    )
    def test_main(self, *, stem: str, expected: MetaData) -> None:
        result = StemMetaData.from_stem(stem)
        assert result == expected
