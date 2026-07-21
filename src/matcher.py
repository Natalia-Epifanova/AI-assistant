from __future__ import annotations

import json
from pathlib import Path

from src.models import CandidateBlogger, CandidateMatch, IdealBloggerProfile
from src.profile_analyzer import DEFAULT_TONE, DEFAULT_TOPICS, DEFAULT_VISUAL_TAGS


PLATFORM_WEIGHTS = {
    "instagram": 3,
    "telegram": 2,
    "youtube_shorts": 2,
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


def match_candidates(
    ideal_profile: IdealBloggerProfile,
    candidates: list[CandidateBlogger],
    top_n: int = 5,
) -> list[CandidateMatch]:
    """Подбирает лучших кандидатов по простому скорингу."""
    del ideal_profile

    matches: list[CandidateMatch] = []

    for candidate in candidates:
        matched_topics = [topic for topic in candidate.topics if topic in DEFAULT_TOPICS]
        matched_visual_tags = [tag for tag in candidate.visual_tags if tag in DEFAULT_VISUAL_TAGS]
        matched_tone = [tone for tone in candidate.tone if tone in DEFAULT_TONE]

        score = 0
        score += len(matched_topics) * 3
        score += len(matched_visual_tags) * 2
        score += len(matched_tone) * 2
        score += PLATFORM_WEIGHTS.get(candidate.platform, 0)

        if candidate.engagement_level == "high":
            score += 2
        elif candidate.engagement_level == "medium":
            score += 1

        reasons = build_match_reasons(candidate, matched_topics, matched_visual_tags, matched_tone)

        matches.append(
            CandidateMatch(
                id=candidate.id,
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
    return matches[:top_n]


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

    reasons.append(f"Платформа кандидата: {candidate.platform}.")
    reasons.append(candidate.why_fit)
    return reasons
