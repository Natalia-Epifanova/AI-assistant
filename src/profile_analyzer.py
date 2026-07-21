from __future__ import annotations

from collections import Counter

from src.models import BloggerFeatures, SourceBlogger


KEYWORDS = [
    "style",
    "fashion",
    "moda",
    "look",
    "wb",
    "obzor",
    "beauty",
    "blog",
    "live",
    "shop",
]


def build_blogger_features(bloggers: list[SourceBlogger]) -> list[BloggerFeatures]:
    """Собирает базовые признаки по списку блогеров."""
    features: list[BloggerFeatures] = []

    for item in bloggers:
        if not item.username or not item.url:
            continue

        username_lower = item.username.lower()
        keyword_matches = [keyword for keyword in KEYWORDS if keyword in username_lower]

        features.append(
            BloggerFeatures(
                row_number=item.row_number,
                username=item.username,
                url=item.url,
                username_length=len(item.username),
                has_digits=any(char.isdigit() for char in item.username),
                has_underscore="_" in item.username,
                has_dot="." in item.username,
                keyword_matches=keyword_matches,
            )
        )

    return features


def summarize_blogger_features(features: list[BloggerFeatures]) -> dict[str, object]:
    """Считает краткую сводку по признакам базы."""
    if not features:
        return {
            "total": 0,
            "avg_username_length": 0,
            "with_digits": 0,
            "with_underscore": 0,
            "with_dot": 0,
            "top_keywords": [],
        }

    keyword_counter = Counter()
    for item in features:
        keyword_counter.update(item.keyword_matches)

    avg_username_length = sum(item.username_length for item in features) / len(features)

    return {
        "total": len(features),
        "avg_username_length": round(avg_username_length, 2),
        "with_digits": sum(1 for item in features if item.has_digits),
        "with_underscore": sum(1 for item in features if item.has_underscore),
        "with_dot": sum(1 for item in features if item.has_dot),
        "top_keywords": keyword_counter.most_common(5),
    }
