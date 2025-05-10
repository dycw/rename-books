from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from re import sub
from typing import Generic, Self, TypeVar, cast

from tabulate import tabulate
from utilities.dataclasses import replace_non_sentinel
from utilities.iterables import one
from utilities.re import ExtractGroupsError, extract_groups
from utilities.sentinel import Sentinel, sentinel

from rename_books.utilities import clean_text

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
    def from_file(cls, path: Path, /) -> MetaData[Any, Any, Any]:
        stem = StemMetaData.from_stem(path.stem)
        return cls(
            directory=path.parent,
            year=stem.year,
            title=stem.title,
            subtitles=stem.subtitles,
            authors=stem.authors,
            suffix=path.suffix,
        )

    @property
    def name(self) -> str:
        """Get the name of the file path."""
        meta = self.with_all_metadata
        return Path(meta.stem).with_suffix(meta.suffix).stem

    @property
    def path(self) -> Path:
        """Get the file path."""
        meta = self.with_all_metadata
        return Path(meta.directory, meta.name)

    def replace(
        self,
        *,
        directory: Path | Sentinel = sentinel,
        year: int | None | Sentinel = sentinel,
        title: str | None | Sentinel = sentinel,
        subtitles: list[str] | Sentinel = sentinel,
        authors: list[str] | Sentinel = sentinel,
        suffix: str | None | Sentinel = sentinel,
    ) -> Self:
        return replace_non_sentinel(
            self,
            directory=directory,
            year=year,
            title=title,
            subtitles=subtitles,
            authors=authors,
            suffix=suffix,
        )

    @property
    def repr_table(self) -> str:
        """The repr as a table."""
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
        return self.stem_meta_data.stem

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
    def with_all_metadata(self) -> MetaData[int, str, str]:
        """Check if the metadata is complete."""
        if (self.year is None) or (self.title is None) or (self.suffix is None):
            raise ValueError(*[f"{self=}"])
        return cast("MetaData[int, str, str]", self)


@dataclass(order=True, unsafe_hash=True, kw_only=True)
class StemMetaData(Generic[_TYear, _TTitle]):
    """The."""

    year: _TYear = None
    title: _TTitle = None
    subtitles: tuple[str, ...] = field(default_factory=tuple)
    authors: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.title is not None:
            self.title = clean_text(self.title)
        self.subtitles = tuple(map(clean_text, self.subtitles))

    @classmethod
    def from_stem(cls, stem: str, /) -> Self:
        try:
            year, title = extract_groups(r"^(\d+)\s+(.+)$", stem)
        except ExtractGroupsError:
            pass
        else:
            return cls(year=int(year), title=cls._strip_text(title))
        with suppress(ExtractGroupsError):
            year, title, authors = extract_groups(r"\((\d+)\)\s+(.+)\s+\((.+)\)", stem)
            return _process_get_defaults(year=year, title=title, authors=authors)
        raise NotImplementedError(stem)

    def replace(
        self,
        *,
        directory: Path | Sentinel = sentinel,
        year: int | None | Sentinel = sentinel,
        title: str | None | Sentinel = sentinel,
        subtitles: list[str] | Sentinel = sentinel,
        authors: list[str] | Sentinel = sentinel,
        suffix: str | None | Sentinel = sentinel,
    ) -> Self:
        return replace_non_sentinel(
            self,
            directory=directory,
            year=year,
            title=title,
            subtitles=subtitles,
            authors=authors,
            suffix=suffix,
        )

    @property
    def repr_table(self) -> str:
        """The repr as a table."""
        data = [
            ["year", self.year],
            ["title", self.title],
            ["subtitles", self.subtitles],
            ["authors", self.authors],
        ]
        return tabulate(data)

    @property
    def stem(self) -> str:
        """Get the stem of the file path."""
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
    def _strip_text(cls, text: str, /) -> str:
        return sub(r"^[\s\-\—]+|[\s\-\—]+$", "", text)


__all__ = ["MetaData", "StemMetaData"]
