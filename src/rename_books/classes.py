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
from utilities.re import ExtractGroupsError, extract_groups
from utilities.sentinel import Sentinel, sentinel

from rename_books.utilities import clean_text

if TYPE_CHECKING:
    from collections.abc import Iterable


_TYear = TypeVar("_TYear", bound=int | None)
_TTitle = TypeVar("_TTitle", bound=str | None)
_TSuffix = TypeVar("_TSuffix", bound=str | None)


@dataclass(repr=False, kw_only=True)
class MetaData(Generic[_TYear, _TTitle, _TSuffix]):
    """A set of metadata."""

    directory: Path = field(default_factory=Path.cwd)
    year: _TYear = None
    title: _TTitle = None
    subtitles: tuple[str, ...] = field(default_factory=tuple)
    authors: tuple[str, ...] = field(default_factory=tuple)
    suffix: _TSuffix = None

    @property
    def table(self) -> str:
        data = [
            ["directory", self.directory],
            ["year", self.year],
            ["title", self.title],
            ["subtitles", self.subtitles],
            ["authors", self.authors],
            ["extension", self.suffix],
        ]
        return tabulate(data)

    @classmethod
    def from_path(cls, path: Path, /) -> MetaData[Any, Any, Any]:
        """Construct a set of metadata from a Path."""
        stem = StemMetaData.from_string(path.stem)
        return cls(
            directory=path.parent,
            year=stem.year,
            title=stem.title,
            subtitles=stem.subtitles,
            authors=stem.authors,
            suffix=cast("_TSuffix", path.suffix),
        )

    @property
    def name(self) -> str:
        """Get the name of the file path."""
        meta = self.with_all_metadata
        return Path(meta.stem).with_suffix(meta.suffix).stem

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
        return self.stem_meta_data.to_string

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
        return Path(meta.directory, meta.name)

    @property
    def with_all_metadata(self) -> MetaData[int, str, str]:
        """Check if the metadata is complete."""
        if (self.year is None) or (self.title is None) or (self.suffix is None):
            raise ValueError(*[f"{self=}"])
        return cast("MetaData[int, str, str]", self)


@dataclass(order=True, unsafe_hash=True, kw_only=True)
class StemMetaData(Generic[_TYear, _TTitle]):
    """A set of stem metadata."""

    year: _TYear = None
    title: _TTitle = None
    subtitles: tuple[str, ...] = field(default_factory=tuple)
    authors: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.title is not None:
            self.title = clean_text(self.title)
        self.subtitles = tuple(map(clean_text, self.subtitles))

    @classmethod
    def from_string(cls, stem: str, /) -> Self:
        """Construct a set of metadata from a string."""
        try:
            year, title_and_subtitles, authors = extract_groups(
                r"^(\d+)[\s\-\—]+(.+?)[\s\-\—]?(?:\(([\w,]+)\))?$", stem
            )
        except ExtractGroupsError:
            pass
        else:
            title, subtitles = cls._split_title_and_subtitles(title_and_subtitles)
            authors = cls._split_authors(authors)
            return cls(
                year=cast("_TYear", int(year)),
                title=cast("_TTitle", title),
                subtitles=subtitles,
                authors=authors,
            )
        raise NotImplementedError

        try:
            year, title = extract_groups(r"^(\d+)[\s\-\—]+(.+)$", stem)
        except ExtractGroupsError:
            pass
        else:
            title, subtitles = cls._split_title_and_subtitles(title)
            return cls(year=int(year), title=title, subtitles=subtitles)
        with suppress(ExtractGroupsError):
            year, title, authors = extract_groups(r"\((\d+)\)\s+(.+)\s+\((.+)\)", stem)
            return _process_get_defaults(year=year, title=title, authors=authors)
        raise NotImplementedError(stem)

    @property
    def is_formatted(self) -> bool:
        """Check if a string is formatted."""
        try:
            _ = self.with_all_metadata
        except ValueError:
            return False
        return True

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
    def to_string(self) -> str:
        """Construct a string from the metadata."""
        meta = self.with_all_metadata
        name = f"{meta.year} — {meta.title}"
        if len(subtitles := meta.subtitles) >= 1:
            joined = " – ".join(subtitles)
            name = f"{name} – {joined}"
        match len(meta.authors):
            case 0:
                return name
            case 1:
                return f"{name} ({one(meta.authors)})"
            case _:
                return f"{name} ({meta.authors[0]} et al)"

    @property
    def with_all_metadata(self) -> StemMetaData[int, str]:
        """Check if the metadata is complete."""
        if (self.year is None) or (self.title is None):
            raise ValueError(*[f"{self=}"])
        return cast("StemMetaData[int, str]", self)

    @classmethod
    def _split_authors(cls, text: str, /) -> tuple[str, ...]:
        text = cls._strip_text(text)
        if not text:
            return ()
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


__all__ = ["MetaData", "StemMetaData"]
