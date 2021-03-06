from contextlib import suppress
from logging import INFO
from logging import basicConfig
from logging import info
from os import rename
from pathlib import Path
from re import search
from sys import stdout

from rename_books.utilities import change_name
from rename_books.utilities import change_suffix


basicConfig(
    datefmt="%Y-%m-%d %H:%M:%S",
    format="{asctime}: {msg}",
    level=INFO,
    stream=stdout,
    style="{",
)
DIRECTORY = Path("/data/derek/Dropbox/Temporary/")


def process_name(path: Path) -> None:
    name = path.name
    info(f"Processing:\n    {name}")
    while True:
        if (input_year := input("Input year (or 's'/'q'): ")) == "s":
            raise Skip()
        elif input_year == "q":
            raise Quit()
        elif match := search(r"^(\d+)$", input_year):
            year = int(match.group(1))
            break
        else:
            info(f"{input_year!r} is an invalid year")
    while True:
        if (input_title := input("Input title (or 's'/'q'): ")) == "s":
            raise Skip()
        elif input_title == "q":
            raise Quit()
        elif match := search(r"^(.+)$", input_title):
            title = match.group(1).strip()
            break
        else:
            info(f"{input_title!r} is an invalid title")
    new_name = f"{year} — {title}"
    subtitles: list[str] = ["A very short introduction"]
    new_name = " – ".join([new_name] + subtitles)
    authors: list[str] = []
    while True:
        next_n = len(authors) + 1
        if (
            input_author := input(f"Input author #{next_n} (or 's'/'q'): ")
        ) == "s":
            raise Skip()
        elif input_author == "q":
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
            info(f"{input_author!r} is an invalid author")
    while True:
        input_confirm = input(f"Confirm new name:\n{new_name}? ('y'/'n') ")
        if input_confirm == "y":
            new_path = change_name(path, new_name)
            rename(path, new_path)
            info(f"Renamed:\n    {name}\n--> {new_name}\n")
            break
        elif input_confirm == "n":
            raise Quit()


class Skip(RuntimeError):
    pass


class Quit(RuntimeError):
    pass


if __name__ == "__main__":
    skips: set[Path] = set()
    with suppress(Quit):
        while True:
            try:
                path = next(
                    path
                    for path in sorted(DIRECTORY.iterdir())
                    if path.is_file()
                    and path.suffix == ".pdf"
                    and not change_suffix(path, ".pdf", ".part").exists()
                    and not search(
                        r"^\d+ — .+( – .+)?\(.+\)$", change_suffix(path).name
                    )
                    and path not in skips
                )
            except StopIteration:
                break
            else:
                try:
                    process_name(path)
                except Skip:
                    skips.add(path)
