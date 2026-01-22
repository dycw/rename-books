from __future__ import annotations

from typing import TYPE_CHECKING

from click import command, version_option
from utilities.click import CONTEXT_SETTINGS
from utilities.logging import basic_config

from rename_books import __version__
from rename_books.classes import MetaData
from rename_books.lib import get_decision, get_next_file

if TYPE_CHECKING:
    from pathlib import Path


@command(**CONTEXT_SETTINGS)
@version_option(version=__version__)
def main() -> None:
    basic_config(obj="rename_books")
    skips: set[Path] = set()
    while (path := get_next_file(skips=skips)) is not None:
        if get_decision(path):
            MetaData.process(path)
        else:
            skips.add(path)


if __name__ == "__main__":
    main()
