from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import count, takewhile
from re import search
from typing import TYPE_CHECKING, Any, Literal, cast, override

from loguru import logger
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator
from tabulate import tabulate
from utilities.iterables import one
from utilities.re import ExtractGroupsError, extract_groups

from rename_books.constants import TEMPORARY_PATH
from rename_books.utilities import (
    change_name,
    change_suffix,
    is_non_empty,
    is_valid_filename,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


def get_next_file(*, skips: set[Path] | None = None) -> Path | None:
    """Get the next file to process, if it exists."""
    paths = (
        path
        for path in TEMPORARY_PATH.iterdir()
        if path.is_file()
        and _needs_processing(path)
        and not change_suffix(path, ".pdf", ".part").exists()
    )
    if skips is not None:
        paths = (path for path in paths if path not in skips)
    try:
        return next(iter(sorted(paths)))
    except StopIteration:
        return None


def _needs_processing(path: Path, /) -> bool:
    """Check if a file needs processing."""
    return (not search(r"^\d+ — .+( – .+)?(\(.+\))?$", path.name)) and (
        path.suffix in {".epub", ".pdf"}
    )


def get_decision(path: Path, /) -> bool:
    """Get the decision for a given path."""
    completer = WordCompleter(["process", "skip"])

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


def process_file(path: Path, /) -> None:
    """Process a file."""
    if (defaults := _try_get_defaults(path)) is None:
        def_year = def_title = def_authors = None
    else:
        def_year, def_title, def_authors = defaults
    year = _get_year(default=def_year)
    title = _get_title(default=def_title)
    subtitles = _get_subtitles_init(
        default=None if def_title is None else (def_title, title)
    )
    authors = _get_authors(default=def_authors)
    data = _Data(year=year, title=title, subtitles=subtitles, authors=authors)
    while True:
        match _confirm_data(data):
            case True:
                return _rename_file_to_data(path, data)
            case "year":
                data = replace(data, year=_get_year(default=data.year))
            case "title":
                data = replace(data, title=_get_title(default=data.title))
            case "subtitles":
                data = replace(
                    data, subtitles=_get_subtitles_post(default=data.subtitles)
                )
            case "authors":
                data = replace(data, authors=_get_authors(default=data.authors))


def _try_get_defaults(path: Path, /) -> tuple[int, str, list[str]] | None:
    """Try get a set of defaults for a given path."""
    name = path.name
    try:
        year_text, title_text, authors_text = extract_groups(
            r"^\((\d+)\)\s+(.+)\s+\((.+)\).*.(?:epub|pdf)$", name
        )
    except ExtractGroupsError:
        return None
    year = int(year_text)
    title = title_text.capitalize()
    authors = [name.split(" ")[-1] for name in authors_text.split(",")]
    return year, title, authors


def _get_year(*, default: int | None = None) -> int:
    """Get the prompt year."""

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


def _get_title(*, default: str | None = None) -> str:
    """Get the prompt title."""
    return prompt(
        "Input title: ",
        default="" if default is None else default,
        mouse_support=True,
        validator=Validator.from_callable(
            is_valid_filename, error_message="Enter a valid file path"
        ),
        vi_mode=True,
    ).strip()


def _get_subtitles_init(*, default: tuple[str, str] | None = None) -> list[str]:
    """Get the prompt subtitles (initial part)."""
    num_words: int = 0
    if default is None:
        def_title_words = []
    else:
        def_title, title = default
        def_title_words = def_title.split(" ")
        num_words += len(title.split(" "))

    def yield_inputs(num_words: int, /) -> Iterator[str]:
        while True:
            def_i = " ".join(def_title_words[num_words:]).capitalize()
            yield (
                subtitle := prompt(
                    "Input subtitle(s): ",
                    default=def_i,
                    mouse_support=True,
                    validator=Validator.from_callable(
                        is_valid_filename, error_message="Enter a valid file path"
                    ),
                    vi_mode=True,
                ).strip()
            )
            num_words += len(subtitle.split(" "))

    return list(takewhile(is_non_empty, yield_inputs(num_words)))


def _get_subtitles_post(*, default: list[str]) -> list[str]:
    """Get the prompt subtitles (post part)."""
    return _get_subtitles_post_or_authors(default=default, desc="subtitle")


def _get_authors(*, default: list[str] | None = None) -> list[str]:
    """Get the prompt authors."""
    return _get_subtitles_post_or_authors(default=default, desc="author")


def _get_subtitles_post_or_authors(
    *, default: list[str] | None = None, desc: str
) -> list[str]:
    """Get the prompt post-subtitles or authors."""

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
                f"Input {desc}(s): ",
                default=def_i,
                mouse_support=True,
                validator=Validator.from_callable(
                    is_valid_filename, error_message="Enter a valid file path"
                ),
                vi_mode=True,
            ).strip()

    return list(takewhile(is_non_empty, yield_inputs()))


@dataclass(frozen=True, kw_only=True, repr=False)
class _Data:
    year: int
    title: str
    subtitles: list[str]
    authors: list[str]

    @override
    def __repr__(self) -> str:
        data = [
            ["year", self.year],
            ["title", self.title],
            ["subtitles", self.subtitles],
            ["authors", self.authors],
        ]
        return tabulate(data)

    def to_name(self) -> str:
        name = f"{self.year} — {self.title}"
        if len(subtitles := self.subtitles) >= 1:
            joined = " – ".join(subtitles)
            name = f"{name} – {joined}"
        match len(self.authors):
            case 0:
                return name
            case 1:
                return f"{name} ({one(self.authors)})"
            case _:
                return f"{name} ({self.authors[0]} et al)"


def _confirm_data(
    data: _Data, /
) -> Literal[True, "year", "title", "subtitles", "authors"]:
    """Confirm if set of data is acceptable."""
    completer = WordCompleter(["yes", "year", "title", "subtitles", "authors"])

    def validator(text: str, /) -> bool:
        return bool(search(r"(yes|year|title|subtitles|authors)", text))

    result = prompt(
        f"{data}\nConfirm? ",
        completer=completer,
        default="yes",
        mouse_support=True,
        validator=Validator.from_callable(
            validator,
            error_message="Enter 'yes', 'year', 'title', 'subtitles' or 'authors'",
        ),
        vi_mode=True,
    ).strip()
    return cast(Any, True if result == "yes" else result)


def _rename_file_to_data(path: Path, data: _Data, /) -> None:
    """Rename a file given a set of confirmed data."""
    new_name = data.to_name()
    _ = path.rename(change_name(path, new_name))
    logger.info("Renamed:\n    {}\n--> {}", path.name, new_name)
