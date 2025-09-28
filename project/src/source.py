from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Iterable, Iterator

class SourceType(Enum):
    RAW = auto()       # один исходный CSV 
    BY_YEAR = auto()   # папка файлов по годам
    BY_WEEK = auto()   # папка файлов по неделям
    FILES = auto()     # заданный список файлов

@dataclass(frozen=True)
class Source:
    kind: SourceType
    path: Path | None = None
    files: tuple[Path, ...] = ()

    @staticmethod
    def raw(csv_path: Path):
        return Source(SourceType.RAW, csv_path)

    @staticmethod
    def by_year(dir_path: Path):
        return Source(SourceType.BY_YEAR, dir_path)

    @staticmethod
    def by_week(dir_path: Path):
        return Source(SourceType.BY_WEEK, dir_path)

    @staticmethod
    def files(files: Iterable[Path]):
        return Source(SourceType.FILES, None, tuple(files))


##ввозвращает файлы для чтения
def iter_source_files(src: Source) -> Iterator[Path]:
    """Возвращает список файлов для чтения в определённом порядке."""
    if src.kind == SourceType.RAW:
        yield src.path  # type: ignore[arg-type]
    elif src.kind in (SourceType.BY_YEAR, SourceType.BY_WEEK):
        for p in sorted(src.path.glob("*.csv")):  # type: ignore[union-attr]
            yield p
    else:
        for p in src.files:
            yield p
