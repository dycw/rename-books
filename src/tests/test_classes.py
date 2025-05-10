from __future__ import annotations

from typing import TYPE_CHECKING

from hypothesis import given
from hypothesis.strategies import DrawFn, composite, sampled_from
from pytest import mark, param

from rename_books.classes import AuthorEtAl, MetaData, StemMetaData
from rename_books.constants import BOOKS

if TYPE_CHECKING:
    from pathlib import Path


@composite
def existing_paths(draw: DrawFn, /) -> Path:
    return draw(sampled_from(list(BOOKS.rglob("**/*.pdf"))))


class TestFromText:
    @mark.parametrize(
        ("text", "expected", "is_normalized"),
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
            param(
                "2000 — Title (Author et al)",
                StemMetaData(
                    year=2000, title="Title", authors=AuthorEtAl(author="Author")
                ),
                True,
            ),
            param(
                "2000 —\xa0Title (Author et al)",
                StemMetaData(
                    year=2000, title="Title", authors=AuthorEtAl(author="Author")
                ),
                False,
            ),
            param(
                "2000 — 401(k) Title – Subtitle (Author)",
                StemMetaData(
                    year=2000,
                    title="401(k) Title",
                    subtitles=("Subtitle",),
                    authors=("Author",),
                ),
                True,
            ),
            param(
                "2000 — title multi-word",
                StemMetaData(year=2000, title="Title Multi-Word"),
                False,
            ),
            param(
                "2000 — Title – The Global-View.com Guide (Author)",
                StemMetaData(
                    year=2000,
                    title="Title",
                    subtitles=("The Global-View.com Guide",),
                    authors=("Author",),
                ),
                True,
            ),
            param(
                "2000 — Title (Author-Second et al)",
                StemMetaData(
                    year=2000, title="Title", authors=AuthorEtAl(author="Author-Second")
                ),
                True,
            ),
            param(
                "Paolo Brandimarte - Numerical Methods in Finance and Economics (2006)",
                StemMetaData(
                    year=2006,
                    title="Numerical Methods in Finance and Economics",
                    authors=("Paolo Brandimarte",),
                ),
                False,
            ),
            param(
                "Title-Author", StemMetaData(title="Title", authors=("Author",)), False
            ),
        ],
    )
    def test_main(self, *, text: str, expected: MetaData, is_normalized: bool) -> None:
        result = StemMetaData.from_text(text)
        assert result == expected
        assert result.is_normalized(text) is is_normalized

    @given(path=existing_paths())
    def test_on_dropbox(self, *, path: Path) -> None:
        _ = MetaData.from_path(path)
