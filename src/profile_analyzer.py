from __future__ import annotations

from collections import Counter

from src.models import BloggerFeatures, IdealBloggerProfile, SourceBlogger


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

DEFAULT_TOPICS = ["fashion", "lifestyle", "reviews", "shopping"]
DEFAULT_VISUAL_TAGS = ["light", "clean", "soft", "feminine", "ugc"]
DEFAULT_TONE = ["friendly", "native", "warm", "practical"]


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


def build_ideal_blogger_profile(features: list[BloggerFeatures]) -> IdealBloggerProfile:
    """Собирает простой агрегированный профиль базы."""
    summary = summarize_blogger_features(features)

    notes: list[str] = []

    if summary["with_underscore"] > 0:
        notes.append("В базе часто встречаются usernames с нижним подчеркиванием.")
    if summary["with_dot"] > 0:
        notes.append("Часть usernames оформлена через точки, что похоже на персональный стиль аккаунтов.")
    if summary["with_digits"] <= 3:
        notes.append("Большинство usernames выглядят персонально и не перегружены цифрами.")
    if summary["top_keywords"]:
        keyword_list = ", ".join(keyword for keyword, _count in summary["top_keywords"])
        notes.append(f"В usernames встречаются тематические маркеры: {keyword_list}.")

    if not notes:
        notes.append("Явные паттерны в usernames пока не выявлены.")

    notes.append("Для MVP базовыми целевыми темами считаем fashion, lifestyle, reviews и shopping.")
    notes.append("Для MVP базовыми визуальными тегами считаем light, clean, soft, feminine и ugc.")
    notes.append("Для MVP базовым тоном считаем friendly, native, warm и practical.")

    return IdealBloggerProfile(
        total_bloggers=summary["total"],
        avg_username_length=summary["avg_username_length"],
        usernames_with_digits=summary["with_digits"],
        usernames_with_underscore=summary["with_underscore"],
        usernames_with_dot=summary["with_dot"],
        top_keywords=summary["top_keywords"],
        notes=notes,
    )
