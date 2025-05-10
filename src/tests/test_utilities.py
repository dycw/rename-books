from __future__ import annotations

from pytest import mark, param

from rename_books.utilities import is_empty_or_is_valid_filename


class TestIsEmptyOrIsValidFileName:
    @mark.parametrize(
        ("text", "expected"),
        [param("", True), param("C/C++", False), param("name", True)],
    )
    def test_main(self, *, text: str, expected: bool) -> None:
        assert is_empty_or_is_valid_filename(text) is expected
