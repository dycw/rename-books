from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from click import command
from utilities.logging import basic_config

from rename_books.classes import MetaData
from rename_books.lib import get_decision, get_next_file

if TYPE_CHECKING:
    from pathlib import Path

_LOGGER = getLogger(__name__)


@command()
def main() -> None:
    basic_config(obj=_LOGGER)
    skips: set[Path] = set()
    while (path := get_next_file(skips=skips)) is not None:
        if get_decision(path):
            MetaData.process(path)
        else:
            skips.add(path)


if __name__ == "__main__":
    main()
