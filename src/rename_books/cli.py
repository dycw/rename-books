from __future__ import annotations

from typing import TYPE_CHECKING

from click import command
from utilities.logging import basic_config, setup_logging

from rename_books.classes import MetaData
from rename_books.lib import get_decision, get_next_file

if TYPE_CHECKING:
    from pathlib import Path


@command()
def main() -> None:
    basic_config()
    skips: set[Path] = set()
    while (path := get_next_file(skips=skips)) is not None:
        if get_decision(path):
            MetaData.process(path)
        else:
            skips.add(path)


if __name__ == "__main__":
    main()
