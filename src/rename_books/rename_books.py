from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from os import rename
from pathlib import Path
from re import search
from sys import stdout

from loguru import logger

from rename_books.errors import Skip
from rename_books.utilities import change_name
from rename_books.utilities import change_suffix
from rename_books.utilities import get_input
from rename_books.utilities import get_list_of_inputs


logger.remove()
logger.add(stdout, format="<bold><red>{time:%H:%M:%S}</red>: {message}</bold>")
DIRECTORY = Path("/data/derek/Dropbox/Temporary/")


def main(*, subtitles: list[str] | None = None) -> None:
    skips: set[Path] = set()
    while True:
        try:
            path = _yield_next_file(skips=skips)
        except StopIteration:
            break
        else:
            try:
                process_name(path, subtitles=subtitles)
            except Skip:
                skips.add(path)


def _yield_next_file(*, skips: set[Path] | None = None) -> Path:
    paths = (
        path
        for path in DIRECTORY.iterdir()
        if path.is_file()
        and path.suffix == ".pdf"
        and not change_suffix(path, ".pdf", ".part").exists()
        and not search(r"^\d+ — .+( – .+)?\(.+\)$", change_suffix(path).name)
    )
    if skips is not None:
        paths = (path for path in paths if path not in skips)
    return next(iter(sorted(paths)))


def process_name(path: Path, *, subtitles: list[str] | None = None) -> None:
    name = path.name
    logger.info(f"Processing {name!r}")
    data = _confirm_data(_get_data(subtitles=subtitles))
    new_name = data.to_name()
    rename(path, change_name(path, new_name))
    logger.info(f"Renamed:\n    {name}\n--> {new_name}")


@dataclass
class _Data:
    year: int
    title: str
    subtitles: list[str]
    authors: list[str]

    def to_name(self) -> str:
        name = f"{self.year} — {self.title}"
        if subtitles := self.subtitles:
            joined = ", ".join(subtitles)
            name = f"{name} – {joined}"
        authors = ", ".join(self.authors)
        return f"{name} ({authors})"


def _get_data(*, subtitles: list[str] | None = None) -> _Data:
    return _Data(
        year=_get_year(),
        title=_get_title(),
        subtitles=_get_subtitles() if subtitles is None else subtitles,
        authors=_get_authors(),
    )


def _get_year() -> int:
    while True:
        text = get_input("Input year", pattern=r"^(\d+)$")
        return int(text)


def _get_title() -> str:
    return get_input("Input title")


def _get_subtitles() -> list[str]:
    return get_list_of_inputs("Input subtitle")


def _get_authors() -> list[str]:
    return get_list_of_inputs("Input author", name_if_empty_error="'Authors'")


def _confirm_data(data: _Data) -> _Data:
    while True:
        choice = get_input(
            f"Confirm data: {data}",
            extra_choices={
                "": "confirm",
                "1": "year",
                "2": "title",
                "3": "subtitles",
                "4": "authors",
            },
            pattern=r"^([1-4])$",
        )
        if choice == "":
            return data
        elif choice == "1":
            data = replace(data, year=_get_year())
        elif choice == "1":
            data = replace(data, title=_get_title())
        elif choice == "1":
            data = replace(data, subtitles=_get_subtitles())
        elif choice == "1":
            data = replace(data, author=_get_authors())
        else:
            raise RuntimeError(f"{choice=}")


if __name__ == "__main__":
    main()
