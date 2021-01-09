import re
from contextlib import suppress
from logging import basicConfig
from logging import getLogger
from logging import INFO
from os import rename
from pathlib import Path
from re import search
from sys import stdout


basicConfig(
    datefmt="%Y-%m-%d %H:%M:%S",
    format="{asctime}: {msg}",
    level=INFO,
    stream=stdout,
    style="{",
)
LOGGER = getLogger(__name__)


DIRECTORY = Path("/data/derek/Dropbox/Temporary/")


def main() -> None:
    for path in DIRECTORY.iterdir():
        if (
            path.is_file()
            and path.suffix == ".pdf"
            and not search(r"^\d+ — .+( – .+)$", drop_suffix(path).name)
        ):
            with suppress(Quit):
                process_name(path)


def drop_suffix(path: Path) -> Path:
    return path.with_suffix("")


def process_name(
    path: Path,
) -> None:
    LOGGER.info(f"Processing {path.name}...")
    while True:
        input_year = input("Input year ('q' to quit):")
        if input_year == "q":
            raise Quit()
        else:
            pattern = re.compile(r"^(\d+)$")
            if match := pattern.search(input_year):
                year = int(match.group(1))
                break
            else:
                LOGGER.info(f"Year must match {pattern}; {input_year} does not")
    title = input("Title = ('q' for quit)")
    if title == "q":
        raise Quit()
    input_subtitle = input("Subtitle = ")
    if input_subtitle in {"", "q"}:
        subtitle = None
    else:
        subtitle = input_subtitle
    authors = []
    while True:
        input_author = input("Author(s) = (1 by 1)")
        if input_author in {"", "q"}:
            break
        else:
            authors.append(input_author)
    new_name = f"{year} — {title}"
    if subtitle is not None:
        new_name = "–".join([new_name, subtitle])
    if not authors:
        raise Quit()
    joined_authors = ", ".join(authors)
    new_name = " ".join([new_name, joined_authors])
    while True:
        input_confirm = input(f"Confirm new name:\n{new_name}? ('y'/'n')")
        if input_confirm == "y":
            new_path = DIRECTORY.joinpath(new_name).with_suffix(".pdf")
            rename(path, new_path)
        elif input_confirm == "n":
            raise Quit()


class Quit(RuntimeError):
    pass


if __name__ == "__main__":
    main()
