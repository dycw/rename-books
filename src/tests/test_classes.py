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
                id="Year — Title",
            ),
            param(
                "2000 — Title – Sub",
                StemMetaData(year=2000, title_and_subtitles=("Title", "Sub")),
                False,
                id="Year — Title – Sub",
            ),
            param(
                "2000 — Title – Sub1 – Sub2",
                StemMetaData(year=2000, title_and_subtitles=("Title", "Sub1", "Sub2")),
                False,
                id="Year — Title – Sub1 – Sub2",
            ),
            param(
                "2000 — Title (Author)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title",), authors=("Author",)
                ),
                True,
                id="Year — Title (Author)",
            ),
            param(
                "2000 — Title – Sub (Author)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title", "Sub"), authors=("Author",)
                ),
                True,
                id="Year — Title – Sub (Author)",
            ),
            param(
                "2000 — Title – Sub1 – Sub2 (Author)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title", "Sub1", "Sub2"),
                    authors=("Author",),
                ),
                True,
                id="Year — Title – Sub1 – Sub2 (Author)",
            ),
            param(
                "2000 — Title (Author et al)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title",),
                    authors=AuthorEtAl(author="Author"),
                ),
                True,
                id="2000 — Title (Author et al)",
            ),
            param(
                "(2000) Title - Sub (Author)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title", "Sub"), authors=("Author",)
                ),
                False,
                id="(Year) Title - Sub, (Author)",
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
                "2000 — 401(k) Title – Sub (Author)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("401(k) Title", "Sub"),
                    authors=("Author",),
                ),
                True,
                id="Year, Title with (), Sub, Author",
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
                id="Author - Title (Year)",
            ),
            param(
                "Title-Author",
                StemMetaData(title_and_subtitles=("Title",), authors=("Author",)),
                False,
                id="Title-Author",
            ),
            param(
                "Author Sur-Name - Title Sub1 Sub2 (2000)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title Sub1 Sub2",),
                    authors=("Author Sur-Name",),
                ),
                False,
                id="Author Sur-Name (with '-') - Title Sub2 Sub3 (Year)",
            ),
            param(
                "Author M. Sur-Name - Title1 Sub1 Sub2 (2000)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title1 Sub1 Sub2",),
                    authors=("Author M. Sur-Name",),
                ),
                False,
                id="Author M. Sur-Name (with '.' and '-') - Title Sub1 Sub2 (Year)",
            ),
            param(
                "Author1, Author2 - Title (2000)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title",),
                    authors=("Author1", "Author2"),
                ),
                False,
                id="Author1, Author2 - Title (Year)",
            ),
            param(
                "2000 — Title (Sur Name et al)",
                StemMetaData(
                    year=2000,
                    title_and_subtitles=("Title",),
                    authors=AuthorEtAl(author="Sur Name"),
                ),
                True,
                id="Year — Title (Sur Name et al) (with ' ' and et al)",
            ),
            param(
                "2000 — Title (Authorè)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title",), authors=("Authorè",)
                ),
                True,
                id="Year — Title (Authorè) (with 'è')",
            ),
            param(
                "2000 — Title (Authorï)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title",), authors=("Authorï",)
                ),
                True,
                id="Year — Title (Authorï) (with 'ï')",
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
                "Author - Title Sub1 Sub2 Sub3 Sub4 Sub5",
                StemMetaData(
                    title_and_subtitles=("Title Sub1 Sub2 Sub3 Sub4 Sub5",),
                    authors=("Author",),
                ),
                False,
                id="Author - Title Sub1 Sub2 Sub3 Sub4 Sub5",
            ),
            param(
                "(2000) Title - Sub (Author) (Z-Library)",
                StemMetaData(
                    year=2000, title_and_subtitles=("Title", "Sub"), authors=("Author",)
                ),
                False,
                id="(Year) Title - Sub (Author) (Z-Library)",
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


class TestParseTitleAndSubtitles:
    @mark.parametrize(
        ("text", "expected"),
        [
            param("Title", ("Title",)),
            param("Title — Sub", ("Title", "Sub")),
            param("Title – Sub", ("Title", "Sub")),
            param("Title - Sub", ("Title", "Sub")),
            param("Title Multi-Word", ("Title Multi-Word",)),
            param("Title Multi-Word - Sub", ("Title Multi-Word", "Sub")),
        ],
    )
    def test_main(self, *, text: str, expected: tuple[str, ...]) -> None:
        result = StemMetaData._parse_title_and_subtitles(text)
        assert result == expected
