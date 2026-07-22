from __future__ import annotations

import json
import re
from pathlib import Path

from src.models import CandidateBlogger, CandidateMatch, IdealBloggerProfile, YouTubeSearchItem
from src.profile_analyzer import DEFAULT_TONE, DEFAULT_TOPICS, DEFAULT_VISUAL_TAGS

PLATFORM_WEIGHTS = {
    "instagram": 3,
    "telegram": 2,
    "youtube_shorts": 2,
}

TOPIC_KEYWORDS = {
    "fashion": ["fashion", "style", "outfit", "lookbook", "dress", "мода", "стиль", "образ"],
    "lifestyle": ["lifestyle", "daily", "everyday", "routine", "casual"],
    "reviews": ["review", "обзор", "reviews", "рекомендации"],
    "shopping": ["shopping", "wildberries", "wb", "haul", "finds", "покупки"],
}

VISUAL_KEYWORDS = {
    "light": ["light", "bright", "clean"],
    "clean": ["clean", "minimal", "aesthetic"],
    "soft": ["soft", "calm", "feminine", "beautiful"],
    "feminine": ["feminine", "girly", "dress", "girl"],
    "ugc": ["review", "try on", "haul", "shorts", "обзор"],
}

TONE_KEYWORDS = {
    "friendly": ["friendly", "favorite", "love", "beautiful"],
    "native": ["daily", "shorts", "lookbook", "style"],
    "warm": ["beautiful", "favorite", "soft"],
    "practical": ["review", "how to", "finds", "wildberries", "wb", "обзор"],
}


def load_candidate_bloggers(json_path: Path) -> list[CandidateBlogger]:
    """Загружает тестовый датасет кандидатов из JSON."""
    with json_path.open("r", encoding="utf-8") as file:
        raw_items = json.load(file)

    candidates: list[CandidateBlogger] = []
    for item in raw_items:
        candidates.append(
            CandidateBlogger(
                id=item["id"],
                source_kind="demo_dataset",
                platform=item["platform"],
                username=item["username"],
                url=item["url"],
                bio=item["bio"],
                topics=item["topics"],
                visual_tags=item["visual_tags"],
                tone=item["tone"],
                audience_size=item["audience_size"],
                engagement_level=item["engagement_level"],
                why_fit=item["why_fit"],
            )
        )

    return candidates


def build_candidates_from_youtube_items(
        youtube_items: list[YouTubeSearchItem],
        start_id: int = 1000,
) -> list[CandidateBlogger]:
    """Преобразует YouTube-результаты в кандидатов для общего матчинга."""
    candidates: list[CandidateBlogger] = []
    seen_channels: set[str] = set()
    next_id = start_id

    for item in youtube_items:
        channel_key = normalize_channel_key(item.channel_title)
        if not channel_key or channel_key == "youtube_channel" or channel_key in seen_channels:
            continue

        seen_channels.add(channel_key)
        combined_text = f"{item.query} {item.title} {item.description}".lower()

        topics = infer_labels(combined_text, TOPIC_KEYWORDS, fallback=["fashion"])
        visual_tags = infer_labels(combined_text, VISUAL_KEYWORDS, fallback=["clean", "ugc"])
        tone = infer_labels(combined_text, TONE_KEYWORDS, fallback=["friendly", "native"])

        candidates.append(
            CandidateBlogger(
                id=next_id,
                source_kind="youtube_live",
                platform="youtube_shorts",
                username=channel_key,
                url=item.video_url,
                bio=item.title,
                topics=topics,
                visual_tags=visual_tags,
                tone=tone,
                audience_size="unknown",
                engagement_level="medium",
                why_fit=(
                    f"Найден через YouTube по запросу '{item.query}', "
                    f"канал '{item.channel_title}'."
                ),
            )
        )
        next_id += 1

    return candidates


def match_candidates(
        ideal_profile: IdealBloggerProfile,
        candidates: list[CandidateBlogger],
        top_n: int = 5,
) -> list[CandidateMatch]:
    """Подбирает лучших кандидатов по скорингу и разнообразию."""
    del ideal_profile

    matches: list[CandidateMatch] = []

    for candidate in candidates:
        matched_topics = [topic for topic in candidate.topics if topic in DEFAULT_TOPICS]
        matched_visual_tags = [tag for tag in candidate.visual_tags if tag in DEFAULT_VISUAL_TAGS]
        matched_tone = [tone_name for tone_name in candidate.tone if tone_name in DEFAULT_TONE]

        score = 0
        score += len(matched_topics) * 3
        score += len(matched_visual_tags) * 2
        score += len(matched_tone) * 2
        score += PLATFORM_WEIGHTS.get(candidate.platform, 0)

        if candidate.engagement_level == "high":
            score += 2
        elif candidate.engagement_level == "medium":
            score += 1

        if candidate.source_kind == "youtube_live":
            score += 2

        reasons = build_match_reasons(candidate, matched_topics, matched_visual_tags, matched_tone)

        matches.append(
            CandidateMatch(
                id=candidate.id,
                source_kind=candidate.source_kind,
                username=candidate.username,
                platform=candidate.platform,
                url=candidate.url,
                score=score,
                matched_topics=matched_topics,
                matched_visual_tags=matched_visual_tags,
                matched_tone=matched_tone,
                reasons=reasons,
            )
        )

    matches.sort(key=lambda item: item.score, reverse=True)
    return select_diverse_top_matches(matches, top_n=top_n, min_youtube=1, allowed_gap=4)


def select_diverse_top_matches(
        matches: list[CandidateMatch],
        top_n: int,
        min_youtube: int,
        allowed_gap: int,
) -> list[CandidateMatch]:
    """Сохраняет сильный топ и не даёт живым YouTube-кандидатам затеряться."""
    top_matches = matches[:top_n]
    youtube_in_top = [item for item in top_matches if item.source_kind == "youtube_live"]

    if len(youtube_in_top) >= min_youtube:
        return top_matches

    youtube_pool = [item for item in matches if item.source_kind == "youtube_live"]
    if not youtube_pool:
        return top_matches

    best_youtube = youtube_pool[0]
    if not top_matches:
        return [best_youtube]

    last_score = top_matches[-1].score
    if best_youtube.score < last_score - allowed_gap:
        return top_matches

    replaced = top_matches[:-1] + [best_youtube]
    replaced.sort(key=lambda item: item.score, reverse=True)
    return replaced


def build_match_reasons(
        candidate: CandidateBlogger,
        matched_topics: list[str],
        matched_visual_tags: list[str],
        matched_tone: list[str],
) -> list[str]:
    """Формирует краткие причины, почему кандидат подходит."""
    reasons: list[str] = []

    if matched_topics:
        reasons.append(f"Совпадают темы: {', '.join(matched_topics)}.")
    if matched_visual_tags:
        reasons.append(f"Совпадают визуальные теги: {', '.join(matched_visual_tags)}.")
    if matched_tone:
        reasons.append(f"Совпадает тон: {', '.join(matched_tone)}.")

    if candidate.source_kind == "youtube_live":
        reasons.append("Кандидат найден через живой YouTube-поиск.")

    reasons.append(f"Платформа кандидата: {candidate.platform}.")
    reasons.append(candidate.why_fit)
    return reasons


def infer_labels(text: str, mapping: dict[str, list[str]], fallback: list[str]) -> list[str]:
    """Извлекает подходящие ярлыки по ключевым словам."""
    labels: list[str] = []

    for label, keywords in mapping.items():
        if any(keyword in text for keyword in keywords):
            labels.append(label)

    return labels or fallback


def normalize_channel_key(channel_title: str) -> str:
    """Нормализует название канала в безопасный идентификатор."""
    text = channel_title.strip().lower()
    text = re.sub(r"[^a-z0-9._]+", "_", text)
    text = text.strip("_")
    return text or "youtube_channel"
