from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import mark, param
from utilities.pytest import skipif_ci

from rename_books.constants import BOOKS, BOOKS_AND_PAPERS, DROPBOX, TEMPORARY_PATH

if TYPE_CHECKING:
    from pathlib import Path


class TestPaths:
    @mark.parametrize(
        "path",
        [param(BOOKS), param(BOOKS_AND_PAPERS), param(DROPBOX), param(TEMPORARY_PATH)],
    )
    @skipif_ci
    def test_main(self, *, path: Path) -> None:
        assert path.is_dir()
        assert path.exists()
