from dataclasses import dataclass
from dataclasses import replace
from os import rename
from pathlib import Path
from re import search
from sys import stdout

from beartype import beartype
from loguru import logger

from rename_books.errors import Skip
from rename_books.utilities import change_name
from rename_books.utilities import change_suffix
from rename_books.utilities import get_input
from rename_books.utilities import get_list_of_inputs
from rename_books.utilities import get_temporary_path


logger.remove()
logger.add(stdout, format="<bold><red>{time:%H:%M:%S}</red>: {message}</bold>")
DIRECTORY = get_temporary_path()


@beartype
def main(*, subtitles: list[str] | None = None) -> None:
    skips: set[Path] = set()
    while True:
        try:
            path = _yield_next_file(skips=skips)
        except StopIteration:
            break
        else:
            try:
                _process_file(path, subtitles=subtitles)
            except Skip:
                skips.add(path)


@beartype
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


@beartype
def _process_file(path: Path, *, subtitles: list[str] | None = None) -> None:
    name = path.name
    logger.info("Processing {!r}", name)
    data = _confirm_data(_get_data(subtitles=subtitles))
    new_name = data.to_name()
    rename(path, change_name(path, new_name))
    logger.info("Renamed:\n    {!r}\n--> {!r}", name, new_name)


@beartype
@dataclass
class _Data:
    year: int
    title: str
    subtitles: list[str]
    authors: list[str]

    @beartype
    def to_name(self) -> str:
        name = f"{self.year} — {self.title}"
        if subtitles := self.subtitles:
            joined = ", ".join(subtitles)
            name = f"{name} – {joined}"
        authors = ", ".join(self.authors)
        return f"{name} ({authors})"


@beartype
def _get_data(*, subtitles: list[str] | None = None) -> _Data:
    return _Data(
        year=_get_year(),
        title=_get_title(),
        subtitles=_get_subtitles() if subtitles is None else subtitles,
        authors=_get_authors(),
    )


@beartype
def _get_year() -> int:
    while True:
        text = get_input("Input year", pattern=r"^(\d+)$")
        return int(text)


@beartype
def _get_title() -> str:
    return get_input("Input title")


@beartype
def _get_subtitles() -> list[str]:
    return get_list_of_inputs("Input subtitle(s)")


@beartype
def _get_authors() -> list[str]:
    return get_list_of_inputs(
        "Input author(s)", name_if_empty_error="'Authors'"
    )


@beartype
def _confirm_data(data: _Data, /) -> _Data:
    while True:
        choice = get_input(
            f"""\
Confirm data:
    year      = {data.year}
    title     = {data.title}
    subtitles = {data.subtitles}
    authors   = {data.authors}
""",
            extra_choices={
                "1": "year",
                "2": "title",
                "3": "subtitles",
                "4": "authors",
                "Enter": "confirm",
            },
            pattern=r"^([1-4]?)$",
        )
        if choice == "":
            return data
        elif choice == "1":
            data = replace(data, year=_get_year())
        elif choice == "2":
            data = replace(data, title=_get_title())
        elif choice == "3":
            data = replace(data, subtitles=_get_subtitles())
        elif choice == "4":
            data = replace(data, authors=_get_authors())
        else:
            raise RuntimeError(f"{choice=}")


if __name__ == "__main__":
    main()
