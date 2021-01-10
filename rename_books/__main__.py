from contextlib import suppress
from logging import basicConfig
from logging import getLogger
from logging import INFO
from os import rename
from pathlib import Path
from re import search
from sys import stdout
from typing import List


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
    name = path.name
    LOGGER.info(f"Processing {name}...")
    while True:
        if (input_year := input("Input year ('q' to quit): ")) == "q":
            raise Quit()
        elif match := search(r"^(\d+)$", input_year):
            year = int(match.group(1))
            break
        else:
            LOGGER.info(f"{input_year!r} is an invalid year")
    while True:
        if (input_title := input("Input title ('q' to quit): ")) == "q":
            raise Quit()
        elif match := search(r"^(.+)$", input_title):
            title = match.group(1).strip()
            break
        else:
            LOGGER.info(f"{input_title!r} is an invalid title")
    new_name = f"{year} — {title}"
    while True:
        if (input_subtitle := input("Input subtitle ('q' to quit): ")) == "q":
            raise Quit()
        elif input_subtitle == "":
            break
        elif match := search(r"^(.+)$", input_subtitle):
            subtitle = match.group(1).strip()
            new_name = f"{new_name} – {subtitle}"
            break
        else:
            LOGGER.info(f"{input_subtitle!r} is an invalid subtitle")
    authors: List[str] = []
    while True:
        next_n = len(authors) + 1
        if (
            input_author := input(f"Input author #{next_n} ('q' to quit): ")
        ) == "q":
            raise Quit()
        elif input_author == "":
            if authors:
                joined_authors = ", ".join(authors)
                new_name = f"{new_name} ({joined_authors})"
                break
        elif match := search(r"^(.+)$", input_author):
            author = match.group(1).strip()
            authors.append(author)
        else:
            LOGGER.info(f"{input_author!r} is an invalid author")
    while True:
        input_confirm = input(f"Confirm new name:\n{new_name}? ('y'/'n') ")
        if input_confirm == "y":
            new_path = path.parent.joinpath(new_name).with_suffix(".pdf")
            rename(path, new_path)
            LOGGER.info(f"Renamed:\n    {name}\n--> {new_name}\n")
            break
        elif input_confirm == "n":
            raise Quit()


class Quit(RuntimeError):
    pass


if __name__ == "__main__":
    main()
