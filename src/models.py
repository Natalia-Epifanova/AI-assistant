from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class SourceBlogger:
    """Строка блогера из исходной таблицы."""

    row_number: int
    source_label: Optional[str]
    raw_value: str
    url: Optional[str]
    username: Optional[str]
    status: str


@dataclass(slots=True)
class BloggerFeatures:
    """Базовые признаки блогера для MVP."""

    row_number: int
    username: str
    url: str
    username_length: int
    has_digits: bool
    has_underscore: bool
    has_dot: bool
    keyword_matches: list[str]
