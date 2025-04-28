from __future__ import annotations

from pathlib import Path

from pytest import mark, param

from rename_books.lib import _clean_text, _Data, _needs_processing, _try_get_defaults


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
        assert _clean_text(text) == expected


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


class TestTryGetDefaults:
    @mark.parametrize(
        ("stem", "year", "title", "authors"),
        [
            param(
                "(Statistics in Practice) Paolo Brandimarte - Numerical Methods in Finance and Economics_ A MATLAB-Based Introduction -Wiley-Interscience (2006)",
                2006,
                "Numerical Methods in Finance and Economics_ a MATLAB-Based Introduction -Wiley-Interscience",
                ["Brandimarte"],
            ),
            param(
                "A Survey of the World’s Top Asset Allocation Strategies (English Edition)-the Idea Farm0",
                None,
                "A Survey of the World's Top Asset Allocation Strategies (English Edition)",
                ["Farm0"],
            ),
        ],
    )
    def test_main(
        self, *, stem: str, year: int, title: str, authors: list[str]
    ) -> None:
        result = _try_get_defaults(stem)
        assert result == (year, title, authors)
