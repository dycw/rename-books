from __future__ import annotations

from pathlib import Path

from pytest import mark, param

from rename_books.lib import _Data, _needs_processing


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
        assert _needs_processing(Path(name)) is expected
