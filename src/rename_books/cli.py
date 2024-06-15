from __future__ import annotations

from typing import TYPE_CHECKING

from click import command
from utilities.loguru import setup_loguru

from rename_books.lib import get_decision, get_next_file, process_file

if TYPE_CHECKING:
    from pathlib import Path

setup_loguru()


@command()
def main() -> None:
    skips: set[Path] = set()
    while (path := get_next_file(skips=skips)) is not None:
        if get_decision(path):
            process_file(path)
        else:
            skips.add(path)


if __name__ == "__main__":
    main()
