from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from itertools import count, takewhile
from logging import getLogger
from pathlib import Path
from re import search, split, sub
from typing import TYPE_CHECKING, Any, Generic, Literal, Self, TypeVar, cast

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator
from tabulate import tabulate
from utilities.dataclasses import replace_non_sentinel
from utilities.errors import ImpossibleCaseError
from utilities.iterables import one
from utilities.pathlib import ensure_suffix
from utilities.re import (
    ExtractGroupError,
    ExtractGroupsError,
    extract_group,
    extract_groups,
)
from utilities.sentinel import Sentinel, sentinel

from rename_books.utilities import (
    clean_text,
    is_empty,
    is_empty_or_is_valid_filename,
    is_non_empty,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


_LOGGER = getLogger(__name__)
_TYear = TypeVar("_TYear", bound=int | None)
_TSuffix = TypeVar("_TSuffix", bound=str | None)


@dataclass(order=True, unsafe_hash=True, kw_only=True)
class MetaData(Generic[_TYear, _TSuffix]):
    """A set of metadata."""

    directory: Path = field(default_factory=Path.cwd)
    year: _TYear = None
    title_and_subtitles: tuple[str, ...] = field(default_factory=tuple)
    authors: tuple[str, ...] | AuthorEtAl = field(default_factory=tuple)
    suffix: _TSuffix = None

    @classmethod
    def from_path(cls, path: Path, /) -> MetaData[Any, Any]:
        """Construct a set of metadata from a Path."""
        try:
            stem = StemMetaData.from_text(path.stem)
        except StemMetaDataFromTextError as error:
            raise MetaDataFromPathError(*[f"{path=}"]) from error
        return cls(
            directory=path.parent,
            year=stem.year,
            title_and_subtitles=stem.title_and_subtitles,
            authors=stem.authors,
            suffix=cast("_TSuffix", path.suffix),
        )

    @classmethod
    def is_normalized(cls, path: Path, /) -> bool:
        """Check if a path is normalized."""
        try:
            return cls.from_path(path).to_path == path
        except (MetaDataFromPathError, MetaDataWithAllMetaDataError):
            return False

    @property
    def name(self) -> str:
        """Get the name of the file path."""
        meta = self.with_all_metadata
        return ensure_suffix(Path(self.directory, meta.stem), meta.suffix).name

    @classmethod
    def normalize(cls, path: Path, /) -> Path:
        """Normalize a Path."""
        return cls.from_path(path).to_path

    @classmethod
    def process(cls, path: Path, /) -> None:
        """Process a path."""
        meta = cls.from_path(path)
        while True:
            match meta.process_choice():
                case True:
                    target = meta.to_path
                    _LOGGER.info(
                        """Renaming
    %r
--> %r""",
                        str(path),
                        str(target),
                    )
                    _ = path.rename(target)
                    return
                case "year":
                    meta = meta.process_year()
                case "title":
                    meta = meta.process_title_and_subtitles_or_authors(
                        "title/subtitles"
                    )
                case "authors":
                    meta = meta.process_title_and_subtitles_or_authors("authors")

    def process_choice(self) -> Literal[True, "year", "title/subtitles", "authors"]:
        """Check if a set of metadata is ready or needs modification."""
        result = prompt(
            f"{self.repr_table}\nConfirm? [y]es, y[e]ar, [t]itle/subtitles, [a]uthors: ",
            completer=WordCompleter(["y", "e", "t", "a"]),
            default="y",
            mouse_support=True,
            validator=Validator.from_callable(
                lambda text: bool(search(r"(y|e|t|a)", text)),
                error_message="Enter 'y', 'e', 't' or 'a'",
            ),
            vi_mode=True,
        ).strip()
        match result:
            case "y":
                return True
            case "e":
                return "year"
            case "t":
                return "title/subtitles"
            case "a":
                return "authors"
            case _:
                raise ImpossibleCaseError(case=[f"{result=}"])

    def process_year(self) -> Self:
        """Process the year on a set of metadata."""
        year = prompt(
            "Input year: ",
            default="20" if self.year is None else str(self.year),
            mouse_support=True,
            validator=Validator.from_callable(
                lambda text: bool(search(r"^(\d+)$", text)),
                error_message="Enter a valid year",
            ),
            vi_mode=True,
        ).strip()
        return self.replace(year=int(year))

    def process_title_and_subtitles_or_authors(
        self, type_: Literal["title/subtitles", "authors"], /
    ) -> Self:
        """Process the title/subtitles or authors on a set of metadata."""
        match type_:
            case "title/subtitles":
                default = self.title_and_subtitles
            case "authors":
                default = self.authors

        match default:
            case tuple() as default_use:
                ...
            case AuthorEtAl() as author_et_al:
                default_use = (author_et_al.author,)

        def yield_inputs() -> Iterator[str]:
            for i in count():
                try:
                    def_i = default_use[i]
                except IndexError:
                    def_i = ""
                yield prompt(
                    f"Input {type_}: ",
                    default=clean_text(def_i),
                    mouse_support=True,
                    validator=Validator.from_callable(
                        is_empty_or_is_valid_filename,
                        error_message="Enter the empty string, or a valid file name",
                    ),
                    vi_mode=True,
                ).strip()

        result = tuple(takewhile(is_non_empty, yield_inputs()))
        match type_:
            case "title/subtitles":
                return self.replace(title_and_subtitles=result)
            case "authors":
                return self.replace(authors=result)

    def replace(
        self,
        *,
        directory: Path | Sentinel = sentinel,
        year: int | None | Sentinel = sentinel,
        title_and_subtitles: Iterable[str] | Sentinel = sentinel,
        authors: Iterable[str] | Sentinel = sentinel,
        suffix: str | None | Sentinel = sentinel,
    ) -> Self:
        return replace_non_sentinel(
            self,
            directory=directory,
            year=year,
            title_and_subtitles=sentinel
            if isinstance(title_and_subtitles, Sentinel)
            else tuple(title_and_subtitles),
            authors=sentinel if isinstance(authors, Sentinel) else tuple(authors),
            suffix=suffix,
        )

    @property
    def repr_table(self) -> str:
        """The metadata as a table."""
        return tabulate(list(self.yield_repr_table_parts()))

    @property
    def stem(self) -> str:
        """Get the stem of the file path."""
        return self.stem_meta_data.to_text

    @property
    def stem_meta_data(self) -> StemMetaData:
        """Get the metadata of the stem of the file path."""
        return StemMetaData(
            year=self.year,
            title_and_subtitles=self.title_and_subtitles,
            authors=self.authors,
        )

    @property
    def subtitles(self) -> tuple[str, ...]:
        """The subtitles, if any."""
        if len(self.title_and_subtitles) == 0:
            raise MetaDataTitleError(*[f"{self=}"])
        return self.title_and_subtitles[1:]

    @property
    def title(self) -> str:
        """The title."""
        if len(self.title_and_subtitles) == 0:
            raise MetaDataTitleError(*[f"{self=}"])
        return self.title_and_subtitles[0]

    @property
    def to_path(self) -> Path:
        """Construct a Path from the metadata."""
        meta = self.with_all_metadata
        return ensure_suffix(Path(meta.directory, meta.name), meta.suffix)

    @property
    def with_all_metadata(self) -> MetaData[int, str, str]:
        """Check if the metadata is complete."""
        if (
            (self.year is None)
            or (len(self.title_and_subtitles) == 0)
            or (self.suffix is None)
        ):
            raise MetaDataWithAllMetaDataError(*[f"{self=}"])
        return cast("MetaData[int, str]", self)

    def yield_repr_table_parts(self) -> Iterator[tuple[str, Any]]:
        """Yield the part for the metadata as a table."""
        yield "directory", self.directory
        yield from self.stem_meta_data.yield_repr_table_parts()
        yield "suffix", self.suffix


class MetaDataFromPathError(Exception): ...


class MetaDataTitleError(Exception): ...


class MetaDataWithAllMetaDataError(Exception): ...


##


@dataclass(order=True, unsafe_hash=True, kw_only=True)
class StemMetaData(Generic[_TYear]):
    """A set of stem metadata."""

    year: _TYear = None
    title_and_subtitles: tuple[str, ...] = field(default_factory=tuple)
    authors: tuple[str, ...] | AuthorEtAl = field(default_factory=tuple)

    def __post_init__(self) -> None:
        self.title_and_subtitles = tuple(map(clean_text, self.title_and_subtitles))
        if isinstance(self.authors, tuple):
            self.authors = tuple(map(clean_text, self.authors))

    @property
    def author_use(self) -> str | AuthorEtAl | None:
        """The author str/object to use."""
        match self.authors:
            case tuple():
                match len(self.authors):
                    case 0:
                        return None
                    case 1:
                        return one(self.authors)
                    case _:
                        return AuthorEtAl(author=self.authors[0])
            case AuthorEtAl():
                return self.authors

    @classmethod
    def from_text(cls, stem: str, /) -> Self:
        """Construct a set of metadata from a string."""
        try:
            year, title_and_subtitles, authors = extract_groups(
                r"^(\d+)[\s\-\—]+(.+?)[\s\-\—]?(?:\(([\s\w\-\,]+)\))?$", stem
            )
        except ExtractGroupsError:
            pass
        else:
            return cls(
                year=cast("_TYear", int(year)),
                title_and_subtitles=cls._parse_title_and_subtitles(title_and_subtitles),
                authors=cls._parse_authors(authors),
            )
        with suppress(ExtractGroupsError):
            authors, title_and_subtitles, year = extract_groups(
                r"^(.+?)\s*\-\s*(.+)\s+\((\d+)\)$", stem
            )
            return cls(
                year=cast("_TYear", int(year)),
                title_and_subtitles=cls._parse_title_and_subtitles(title_and_subtitles),
                authors=cls._parse_authors(authors),
            )
        with suppress(ExtractGroupsError):
            title_and_subtitles, authors = extract_groups(r"^(.+?)\s*\-\s*(.+)$", stem)
            return cls(
                title_and_subtitles=cls._parse_title_and_subtitles(title_and_subtitles),
                authors=cls._parse_authors(authors),
            )
        raise StemMetaDataFromTextError(*[f"{stem=}"])

    @classmethod
    def is_normalized(cls, text: str, /) -> bool:
        """Check if a string is normalized."""
        try:
            return cls.from_text(text).to_text == text
        except (StemMetaDataFromTextError, StemMetaDataWithAllMetaDataError):
            return False

    @classmethod
    def normalize(cls, text: str, /) -> str:
        """Normalize a string."""
        return cls.from_text(text).to_text

    def replace(
        self,
        *,
        year: int | None | Sentinel = sentinel,
        title_and_subtitles: Iterable[str] | Sentinel = sentinel,
        authors: Iterable[str] | Sentinel = sentinel,
    ) -> Self:
        """Replace elements of the metadata."""
        return replace_non_sentinel(
            self,
            year=year,
            title_and_subtitles=sentinel
            if isinstance(title_and_subtitles, Sentinel)
            else tuple(title_and_subtitles),
            authors=sentinel if isinstance(authors, Sentinel) else tuple(authors),
        )

    @property
    def repr_table(self) -> str:
        """The metadata as a table."""
        return tabulate(list(self.yield_repr_table_parts()))

    @property
    def subtitles(self) -> tuple[str, ...]:
        """The subtitles, if any."""
        if len(self.title_and_subtitles) == 0:
            raise StemMetaDataTitleError(*[f"{self=}"])
        return self.title_and_subtitles[1:]

    @property
    def title(self) -> str:
        """The title."""
        if len(self.title_and_subtitles) == 0:
            raise StemMetaDataTitleError(*[f"{self=}"])
        return self.title_and_subtitles[0]

    @property
    def to_text(self) -> str:
        """Construct a string from the metadata."""
        meta = self.with_all_metadata
        name = f"{meta.year} — {meta.title}"
        if len(subtitles := meta.subtitles) >= 1:
            joined = " – ".join(subtitles)
            name = f"{name} – {joined}"
        match meta.author_use:
            case None:
                return name
            case str() as author:
                return f"{name} ({author})"
            case AuthorEtAl() as authors:
                return f"{name} ({authors.to_string})"

    @property
    def with_all_metadata(self) -> StemMetaData[int]:
        """Check if the metadata is complete."""
        if (self.year is None) or (len(self.title_and_subtitles) == 0):
            raise StemMetaDataWithAllMetaDataError(*[f"{self=}"])
        return cast("StemMetaData[int]", self)

    def yield_repr_table_parts(self) -> Iterator[tuple[str, Any]]:
        """Yield the part for the metadata as a table."""
        yield ("year", self.year)
        for i, ts in enumerate(self.title_and_subtitles):
            if i == 0:
                yield ("title", ts)
            else:
                yield (f"subtitle {i}", ts)
        match self.authors:
            case tuple():
                for i, a in enumerate(self.authors, start=1):
                    yield f"author {i}", a
            case AuthorEtAl() as a:
                yield "author et al", a.author

    @classmethod
    def _parse_authors(cls, text: str, /) -> tuple[str, ...] | AuthorEtAl:
        text = cls._strip_text(text)
        if not text:
            return ()
        with suppress(AuthorEtAlFromStringError):
            return AuthorEtAl.from_string(text)
        return tuple(map(cls._strip_text, split(r",", text)))

    @classmethod
    def _parse_title_and_subtitles(cls, text: str, /) -> tuple[str, ...]:
        text = cls._strip_text(text)
        if not text:
            raise ImpossibleCaseError(case=[f"{text=}"])
        return tuple(map(cls._strip_text, split(r"[–—]", text)))

    @classmethod
    def _strip_text(cls, text: str, /) -> str:
        return sub(r"^[\s\-\—]+|[\s\-\—]+$", "", text)


class StemMetaDataFromTextError(Exception): ...


class StemMetaDataTitleError(Exception): ...


class StemMetaDataWithAllMetaDataError(Exception): ...


##


@dataclass(order=True, unsafe_hash=True, kw_only=True)
class AuthorEtAl:
    """A set of multiple authors."""

    author: str

    def __post_init__(self) -> None:
        self.author = clean_text(self.author)

    @classmethod
    def from_string(cls, text: str, /) -> Self:
        """Construct a set of metadata from a string."""
        try:
            author = extract_group(r"^([\w\-]+) et al$", text)
        except ExtractGroupError as error:
            raise AuthorEtAlFromStringError(*[f"{text=}"]) from error
        return cls(author=author)

    @property
    def to_string(self) -> str:
        """Construct a string from the metadata."""
        return f"{self.author} et al"


class AuthorEtAlFromStringError(Exception): ...


__all__ = ["AuthorEtAl", "MetaData", "StemMetaData"]
