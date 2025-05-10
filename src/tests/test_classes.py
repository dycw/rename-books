from __future__ import annotations

from typing import TYPE_CHECKING

from hypothesis import given
from hypothesis.strategies import DrawFn, composite, sampled_from
from pytest import mark, param

from rename_books.classes import MetaData, StemMetaData
from rename_books.constants import BOOKS

if TYPE_CHECKING:
    from pathlib import Path


@composite
def existing_paths(draw: DrawFn, /) -> Path:
    return draw(sampled_from(list(BOOKS.rglob("**/*.pdf"))))


class TestFromStem:
    @mark.parametrize(
        ("stem", "expected", "is_formatted"),
        [
            param("2000 — Title", StemMetaData(year=2000, title="Title"), True),
            param(
                "2000 — Title – Sub",
                StemMetaData(year=2000, title="Title", subtitles=("Sub",)),
                True,
            ),
            param(
                "2000 — Title – Sub1 – Sub2",
                StemMetaData(year=2000, title="Title", subtitles=("Sub1", "Sub2")),
                True,
            ),
            param(
                "2000 — Title (Author)",
                StemMetaData(year=2000, title="Title", authors=("Author",)),
                True,
            ),
            param(
                "2000 — Title – Sub (Author)",
                StemMetaData(
                    year=2000, title="Title", subtitles=("Sub",), authors=("Author",)
                ),
                True,
            ),
            param(
                "2000 — Title – Sub1 – Sub2 (Author)",
                StemMetaData(
                    year=2000,
                    title="Title",
                    subtitles=("Sub1", "Sub2"),
                    authors=("Author",),
                ),
                True,
            ),
            # param("foo.epub", True),
            # param("foo.jpg", False),
            # param("foo", True),
            # param("foo.download", False),
            # param("foo.epub.download", False),
            # param("foo.part", False),
            # param("foo.epub.part", False),
        ],
    )
    def test_main(self, *, stem: str, expected: MetaData, is_formatted: bool) -> None:
        result = StemMetaData.from_string(stem)
        assert result == expected
        assert result.is_formatted is is_formatted
        if result.is_formatted:
            assert result.to_string == stem

    @given(path=existing_paths())
    def test_on_dropbox(self, *, path: Path) -> None:
        MetaData.from_path
