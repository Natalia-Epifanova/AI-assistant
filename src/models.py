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


@dataclass(slots=True)
class IdealBloggerProfile:
    """Простой агрегированный профиль базы блогеров."""

    total_bloggers: int
    avg_username_length: float
    usernames_with_digits: int
    usernames_with_underscore: int
    usernames_with_dot: int
    top_keywords: list[tuple[str, int]]
    notes: list[str]


@dataclass(slots=True)
class CandidateBlogger:
    """Кандидат для подбора похожих блогеров."""

    id: int
    platform: str
    username: str
    url: str
    bio: str
    topics: list[str]
    visual_tags: list[str]
    tone: list[str]
    audience_size: str
    engagement_level: str
    why_fit: str


@dataclass(slots=True)
class CandidateMatch:
    """Результат подбора кандидата."""

    id: int
    username: str
    platform: str
    url: str
    score: int
    matched_topics: list[str]
    matched_visual_tags: list[str]
    matched_tone: list[str]
    reasons: list[str]
