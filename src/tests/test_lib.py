from __future__ import annotations

from pytest import mark, param

from rename_books.lib import _Data


class TestData:
    @mark.parametrize(
        ("data", "expected"),
        [
            param(
                _Data(year=2000, title="Title", subtitles=[], authors=[]),
                "2000 — Title",
            ),
            param(
                _Data(year=2000, title="Title", subtitles=["Sub1"], authors=[]),
                "2000 — Title – Sub1",
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
                _Data(year=2000, title="Title", subtitles=["Sub1"], authors=["Author"]),
                "2000 — Title – Sub1 (Author)",
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
                    subtitles=["Sub1"],
                    authors=["Author1", "Author2"],
                ),
                "2000 — Title – Sub1 (Author1 et al)",
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
