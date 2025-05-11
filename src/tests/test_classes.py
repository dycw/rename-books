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
            param(
                "2000 — Title",
                StemMetaData(year=2000, title_and_subtitles=("Title",)),
                False,
                id="Year, Title",
            ),
            param(
                "2000 — Title – Sub",
                StemMetaData(year=2000, title_and_subtitles=("Title", "Sub")),
                False,
                id="Year, Title, Subtitle",
            ),
            param(
                "2000 — Title – Sub1 – Sub2",
                StemMetaData(year=2000, title_and_subtitles=("Title", "Sub1", "Sub2")),
                False,
                id="Year, Title, Subtitle1, Subtitle2",
            ),
            param(
                "2000 — Title (Author)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title",), authors=("Author",)
                ),
                True,
                id="Year, Title, Author",
            ),
            param(
                "2000 — Title – Sub (Author)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title", "Sub"), authors=("Author",)
                ),
                True,
                id="Year, Title, Subtitle, Author",
            ),
            param(
                "2000 — Title – Sub1 – Sub2 (Author)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title", "Sub1", "Sub2"),
                    authors=("Author",),
                ),
                True,
                id="Year, Title, Subtitle1, Subtitle2, Author",
            ),
            param(
                "2000 — Title (Author et al)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title",),
                    authors=AuthorEtAl(author="Author"),
                ),
                True,
                id="Year, Title, Author et al",
            ),
            param(
                "2000 —\xa0Title (Author et al)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title",),
                    authors=AuthorEtAl(author="Author"),
                ),
                False,
                id="Year, Weird Dash, Title, Author et al",
            ),
            param(
                "2000 — 401(k) Title – Subtitle (Author)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("401(k) Title", "Subtitle"),
                    authors=("Author",),
                ),
                True,
                id="Year, Title with (), Subtitle, Author",
            ),
            param(
                "2000 — title multi-word",
                StemMetaData(year=2000, title_and_subtitles=("Title Multi-Word",)),
                False,
                id="Year, Title without proper case",
            ),
            param(
                "2000 — Title – The Website.com Guide (Author)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title", "The Website.com Guide"),
                    authors=("Author",),
                ),
                True,
                id="Year, Title with '.com'",
            ),
            param(
                "2000 — Title (Author-Second et al)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title",),
                    authors=AuthorEtAl(author="Author-Second"),
                ),
                True,
                id="Year, Title, Author with '-' et al",
            ),
            param(
                "Author - Title (2000)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title",), authors=("Author",)
                ),
                False,
                id="Author, Title, Year",
            ),
            param(
                "Title-Author",
                StemMetaData(title_and_subtitles=("Title",), authors=("Author",)),
                False,
                id="Title, Author",
            ),
            param(
                "Author Sur-Name - Title1 Title2 Title3 Title4 (2000)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title1 Title2 Title3 Title4",),
                    authors=("Author Sur-Name",),
                ),
                False,
                id="Author with '-', Long Title, Year",
            ),
            param(
                "Author M. Sur-Name - Title1 Title2 Title3 Title4 Title5 (2000)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title1 Title2 Title3 Title4 Title5",),
                    authors=("Author M. Sur-Name",),
                ),
                False,
                id="Author with '.' and '-', Long Title, Year",
            ),
            param(
                "Author1, Author2 - Title (2000)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title",),
                    authors=("Author1", "Author2"),
                ),
                False,
                id="Author1, Author2, Title, Year",
            ),
            param(
                "2000 — Title (Sur Name et al)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title",),
                    authors=AuthorEtAl(author="Sur Name"),
                ),
                True,
                id="Year, Title, Author with ' ' et al",
            ),
            param(
                "2000 — Title (Authorè)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title",), authors=("Authorè",)
                ),
                True,
                id="Year, Title, Author with 'è'",
            ),
            param(
                "2000 — Title (Authorï)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title",), authors=("Authorï",)
                ),
                True,
                id="Year, Title, Author with 'ï'",
            ),
            param(
                "2000 — Title (O'Author)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title",), authors=("O'Author",)
                ),
                True,
                id="Year, Title, Author with <'>",
            ),
            param(
                "Author - Title1 Title2 Title3 Title4",
                StemMetaData(
                    title_and_subtitles=("Title1 Title2 Title3 Title4",),
                    authors=("Author",),
                ),
                False,
                id="Author, Long Title",
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
