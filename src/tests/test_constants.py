from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import mark, param

from rename_books.constants import DROPBOX, TEMPORARY_PATH

if TYPE_CHECKING:
    from pathlib import Path


class TestPaths:
    @mark.parametrize("path", [param(DROPBOX), param(TEMPORARY_PATH)])
    def test_main(self, *, path: Path) -> None:
        assert path.exists()
