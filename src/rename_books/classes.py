from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from re import split, sub
from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar, cast

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

from rename_books.utilities import clean_text

if TYPE_CHECKING:
    from collections.abc import Iterable


_TYear = TypeVar("_TYear", bound=int | None)
_TTitle = TypeVar("_TTitle", bound=str | None)
_TSuffix = TypeVar("_TSuffix", bound=str | None)


@dataclass(order=True, unsafe_hash=True, kw_only=True)
class MetaData(Generic[_TYear, _TTitle, _TSuffix]):
    """A set of metadata."""

    directory: Path = field(default_factory=Path.cwd)
    year: _TYear = None
    title: _TTitle = None
    subtitles: tuple[str, ...] = field(default_factory=tuple)
    authors: tuple[str, ...] | AuthorEtAl = field(default_factory=tuple)
    suffix: _TSuffix = None

    @classmethod
    def from_path(cls, path: Path, /) -> MetaData[Any, Any, Any]:
        """Construct a set of metadata from a Path."""
        try:
            stem = StemMetaData.from_text(path.stem)
        except StemMetaDataFromTextError as error:
            raise MetaDataFromPathError(*[f"{path=}"]) from error
        return cls(
            directory=path.parent,
            year=stem.year,
            title=stem.title,
            subtitles=stem.subtitles,
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

    def replace(
        self,
        *,
        directory: Path | Sentinel = sentinel,
        year: int | None | Sentinel = sentinel,
        title: str | None | Sentinel = sentinel,
        subtitles: Iterable[str] | Sentinel = sentinel,
        authors: Iterable[str] | Sentinel = sentinel,
        suffix: str | None | Sentinel = sentinel,
    ) -> Self:
        return replace_non_sentinel(
            self,
            directory=directory,
            year=year,
            title=title,
            subtitles=sentinel if isinstance(subtitles, Sentinel) else tuple(subtitles),
            authors=sentinel if isinstance(authors, Sentinel) else tuple(authors),
            suffix=suffix,
        )

    @property
    def repr_table(self) -> str:
        """The metadata as a table."""
        data = [
            ["directory", self.directory],
            ["year", self.year],
            ["title", self.title],
            ["subtitles", self.subtitles],
            ["authors", self.authors],
            ["extension", self.suffix],
        ]
        return tabulate(data)

    @property
    def stem(self) -> str:
        """Get the stem of the file path."""
        return self.stem_meta_data.to_text

    @property
    def stem_meta_data(self) -> StemMetaData:
        """Get the metadata of the stem of the file path."""
        return StemMetaData(
            year=self.year,
            title=self.title,
            subtitles=self.subtitles,
            authors=self.authors,
        )

    @property
    def to_path(self) -> Path:
        """Construct a Path from the metadata."""
        meta = self.with_all_metadata
        return ensure_suffix(Path(meta.directory, meta.name), meta.suffix)

    @property
    def with_all_metadata(self) -> MetaData[int, str, str]:
        """Check if the metadata is complete."""
        if (self.year is None) or (self.title is None) or (self.suffix is None):
            raise MetaDataWithAllMetaDataError(*[f"{self=}"])
        return cast("MetaData[int, str, str]", self)


class MetaDataFromPathError(Exception): ...


class MetaDataWithAllMetaDataError(Exception): ...


##


@dataclass(order=True, unsafe_hash=True, kw_only=True)
class StemMetaData(Generic[_TYear, _TTitle]):
    """A set of stem metadata."""

    year: _TYear = None
    title: _TTitle = None
    subtitles: tuple[str, ...] = field(default_factory=tuple)
    authors: tuple[str, ...] | AuthorEtAl = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.title is not None:
            self.title = clean_text(self.title)
        self.subtitles = tuple(map(clean_text, self.subtitles))

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
            title, subtitles = cls._split_title_and_subtitles(title_and_subtitles)
            return cls(
                year=cast("_TYear", int(year)),
                title=cast("_TTitle", title),
                subtitles=subtitles,
                authors=cls._parse_authors(authors),
            )
        with suppress(ExtractGroupsError):
            authors, title_and_subtitles, year = extract_groups(
                r"^(.+?)\s*\-\s*(.+)\s+\((\d+)\)$", stem
            )
            title, subtitles = cls._split_title_and_subtitles(title_and_subtitles)
            return cls(
                year=cast("_TYear", int(year)),
                title=cast("_TTitle", title),
                subtitles=subtitles,
                authors=cls._parse_authors(authors),
            )
        with suppress(ExtractGroupsError):
            title_and_subtitles, authors = extract_groups(r"^(.+?)\s*\-\s*(.+)$", stem)
            title, subtitles = cls._split_title_and_subtitles(title_and_subtitles)
            return cls(
                title=cast("_TTitle", title),
                subtitles=subtitles,
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
        title: str | None | Sentinel = sentinel,
        subtitles: Iterable[str] | Sentinel = sentinel,
        authors: Iterable[str] | Sentinel = sentinel,
    ) -> Self:
        """Replace elements of the metadata."""
        return replace_non_sentinel(
            self,
            year=year,
            title=title,
            subtitles=sentinel if isinstance(subtitles, Sentinel) else tuple(subtitles),
            authors=sentinel if isinstance(authors, Sentinel) else tuple(authors),
        )

    @property
    def repr_table(self) -> str:
        """The metadata as a table."""
        data = [
            ["year", self.year],
            ["title", self.title],
            ["subtitles", self.subtitles],
            ["authors", self.authors],
        ]
        return tabulate(data)

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
    def with_all_metadata(self) -> StemMetaData[int, str]:
        """Check if the metadata is complete."""
        if (self.year is None) or (self.title is None):
            raise StemMetaDataWithAllMetaDataError(*[f"{self=}"])
        return cast("StemMetaData[int, str]", self)

    @classmethod
    def _parse_authors(cls, text: str, /) -> tuple[str, ...] | AuthorEtAl:
        text = cls._strip_text(text)
        if not text:
            return ()
        with suppress(AuthorEtAlFromStringError):
            return AuthorEtAl.from_string(text)
        return tuple(map(cls._strip_text, split(r",", text)))

    @classmethod
    def _split_title_and_subtitles(cls, text: str, /) -> tuple[str, tuple[str, ...]]:
        text = cls._strip_text(text)
        if not text:
            raise ImpossibleCaseError(case=[f"{text=}"])
        splits = list(map(cls._strip_text, split(r"[–—]", text)))
        title, *subtitles = splits
        return title, tuple(subtitles)

    @classmethod
    def _strip_text(cls, text: str, /) -> str:
        return sub(r"^[\s\-\—]+|[\s\-\—]+$", "", text)


class StemMetaDataFromTextError(Exception): ...


class StemMetaDataWithAllMetaDataError(Exception): ...


##


@dataclass(order=True, unsafe_hash=True, kw_only=True)
class AuthorEtAl:
    """A set of multiple authors."""

    author: str

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
