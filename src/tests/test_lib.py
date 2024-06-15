from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import mark, param

from rename_books.lib import _Data, _file_stem_needs_processing

if TYPE_CHECKING:
    from pathlib import Path


class TestData:
    @mark.parametrize(
        ("data", "expected"),
        [
            param(
                _Data(year=2000, title="Title", subtitles=[], authors=[]),
                "2000 — Title",
            ),
            param(
                _Data(year=2000, title="Title", subtitles=["Sub"], authors=[]),
                "2000 — Title – Sub",
            ),
            param(
                _Data(year=2000, title="Title", subtitles=["Sub1", "Sub2"], authors=[]),
                "2000 — Title – Sub1 – Sub2",
            ),
            param(
                _Data(year=2000, title="Title", subtitles=[], authors=["Author"]),
                "2000 — Title (Author)",
            ),
            param(
                _Data(year=2000, title="Title", subtitles=["Sub"], authors=["Author"]),
                "2000 — Title – Sub (Author)",
            ),
            param(
                _Data(
                    year=2000,
                    title="Title",
                    subtitles=["Sub1", "Sub2"],
                    authors=["Author"],
                ),
                "2000 — Title – Sub1 – Sub2 (Author)",
            ),
            param(
                _Data(
                    year=2000,
                    title="Title",
                    subtitles=[],
                    authors=["Author1", "Author2"],
                ),
                "2000 — Title (Author1 et al)",
            ),
            param(
                _Data(
                    year=2000,
                    title="Title",
                    subtitles=["Sub"],
                    authors=["Author1", "Author2"],
                ),
                "2000 — Title – Sub (Author1 et al)",
            ),
            param(
                _Data(
                    year=2000,
                    title="Title",
                    subtitles=["Sub1", "Sub2"],
                    authors=["Author1", "Author2"],
                ),
                "2000 — Title – Sub1 – Sub2 (Author1 et al)",
            ),
        ],
    )
    def test_to_name(self, *, data: _Data, expected: str) -> None:
        assert data.to_name() == expected


class TestFileStemNeedsProcessing:
    @mark.parametrize(
        ("stem", "expected"),
        [
            param("2000 — Title", False),
            param("2000 — Title – Sub", False),
            param("2000 — Title – Sub1 – Sub2", False),
            param("2000 — Title (Author)", False),
            param("2000 — Title – Sub (Author)", False),
            param("2000 — Title – Sub1 – Sub2 (Author)", False),
            param("foo", True),
        ],
    )
    def test_main(self, *, stem: Path, expected: bool) -> None:
        assert _file_stem_needs_processing(stem) is expected
