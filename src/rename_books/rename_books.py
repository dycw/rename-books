from collections.abc import Iterator
from dataclasses import dataclass
from itertools import count
from itertools import takewhile
from os import rename
from pathlib import Path
from re import findall
from re import search
from sys import stdout
from typing import cast

from beartype import beartype
from loguru import logger
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator
from tabulate import tabulate

from rename_books.utilities import change_name
from rename_books.utilities import change_suffix
from rename_books.utilities import get_temporary_path
from rename_books.utilities import is_non_empty


logger.remove()
_ = logger.add(
    stdout, format="<bold><red>{time:%H:%M:%S}</red>: {message}</bold>"
)
DIRECTORY = get_temporary_path()


@beartype
def main() -> None:
    skips: set[Path] = set()
    while (path := _get_next_file(skips=skips)) is not None:
        if _get_process_decision(path):
            _process_file(path)
        else:
            skips.add(path)


@beartype
def _get_next_file(*, skips: set[Path] | None = None) -> Path | None:
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
    try:
        return next(iter(sorted(paths)))
    except StopIteration:
        return None


@beartype
def _get_process_decision(path: Path, /) -> bool:
    completer = WordCompleter(["process", "skip"])

    @beartype
    def validator(text: str, /) -> bool:
        return bool(search(r"(process|skip)", text))

    result = prompt(
        f"File = {path.name}\nProcess or skip? ",
        completer=completer,
        default="process",
        mouse_support=True,
        validator=Validator.from_callable(
            validator, error_message="Enter 'process' or 'skip'"
        ),
        vi_mode=True,
    ).strip()
    return result == "process"


@beartype
def _process_file(path: Path, /) -> None:
    if (defaults := _try_get_defaults(path)) is None:
        def_year = def_title = def_authors = None
    else:
        def_year, def_title, def_authors = defaults
    year = _get_year(default=def_year)
    title = _get_title(default=def_title)
    subtitles = _get_subtitles(
        default=None if def_title is None else (def_title, title)
    )
    authors = _get_authors(default=def_authors)
    data = _Data(year, title, subtitles, authors)
    if _confirm_data(data):
        _rename_file_to_data(path, data)
    else:
        _process_file(path)


@beartype
def _try_get_defaults(path: Path, /) -> tuple[int, str, list[str]] | None:
    name = path.name
    try:
        ((year_text, title_text, authors_text),) = cast(
            tuple[str, ...],
            findall(r"^\((\d+)\)\s+(.+)\s+\((.+)\).*.pdf$", name),
        )
    except ValueError:
        return None
    year = int(year_text)
    title = title_text.capitalize()
    authors = [name.split(" ")[-1] for name in authors_text.split(",")]
    return year, title, authors


@beartype
def _get_year(*, default: int | None = None) -> int:
    @beartype
    def validator(text: str, /) -> bool:
        return bool(search(r"^(\d+)$", text))

    text = prompt(
        "Input year: ",
        default="20" if default is None else str(default),
        mouse_support=True,
        validator=Validator.from_callable(
            validator, error_message="Enter a valid year"
        ),
        vi_mode=True,
    ).strip()
    return int(text)


@beartype
def _get_title(*, default: str | None = None) -> str:
    return prompt(
        "Input title: ",
        default="" if default is None else default,
        mouse_support=True,
        vi_mode=True,
    ).strip()


@beartype
def _get_subtitles(*, default: tuple[str, str] | None = None) -> list[str]:
    num_words: int = 0
    if default is None:
        def_title_words = []
    else:
        def_title, title = default
        def_title_words = def_title.split(" ")
        num_words += len(title.split(" "))

    @beartype
    def yield_inputs(num_words: int, /) -> Iterator[str]:
        while True:
            def_i = " ".join(def_title_words[num_words:]).capitalize()
            yield (
                subtitle := prompt(
                    "Input subtitle(s): ",
                    default=def_i,
                    mouse_support=True,
                    vi_mode=True,
                ).strip()
            )
            num_words += len(subtitle.split(" "))

    return list(takewhile(is_non_empty, yield_inputs(num_words)))


@beartype
def _get_authors(*, default: list[str] | None = None) -> list[str]:
    @beartype
    def yield_inputs() -> Iterator[str]:
        for i in count():
            if default is None:
                def_i = ""
            else:
                try:
                    def_i = default[i]
                except IndexError:
                    def_i = ""
            yield prompt(
                "Input author(s): ",
                default=def_i,
                mouse_support=True,
                vi_mode=True,
            ).strip()

    return list(takewhile(is_non_empty, yield_inputs()))


@beartype
@dataclass(repr=False)
class _Data:
    year: int
    title: str
    subtitles: list[str]
    authors: list[str]

    @beartype
    def __repr__(self) -> str:
        data = [
            ["year", self.year],
            ["title", self.title],
            ["subtitles", self.subtitles],
            ["authors", self.authors],
        ]
        return tabulate(data)

    @beartype
    def to_name(self) -> str:
        name = f"{self.year} — {self.title}"
        if subtitles := self.subtitles:
            joined = ", ".join(subtitles)
            name = f"{name} – {joined}"
        authors = ", ".join(self.authors)
        return f"{name} ({authors})"


@beartype
def _confirm_data(data: _Data, /) -> bool:
    completer = WordCompleter(["yes", "no"])

    @beartype
    def validator(text: str, /) -> bool:
        return bool(search(r"(yes|no)", text))

    result = prompt(
        f"{data}\nConfirm? ",
        completer=completer,
        default="yes",
        mouse_support=True,
        validator=Validator.from_callable(
            validator, error_message="Enter 'yes' or 'no'"
        ),
        vi_mode=True,
    ).strip()
    return result == "yes"


@beartype
def _rename_file_to_data(path: Path, data: _Data, /) -> None:
    new_name = data.to_name()
    rename(path, change_name(path, new_name))
    logger.info("Renamed:\n    {}\n--> {}", path.name, new_name)


if __name__ == "__main__":
    main()
