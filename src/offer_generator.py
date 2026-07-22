from __future__ import annotations

from src.models import CandidateMatch, OutreachOffer


def build_outreach_offers(matches: list[CandidateMatch]) -> list[OutreachOffer]:
    """Готовит персональные черновики офферов для кандидатов."""
    offers: list[OutreachOffer] = []

    for match in matches:
        personalization_points = build_personalization_points(match)
        subject = f"Бартерное сотрудничество для @{match.username}"
        message = build_offer_message(match, personalization_points)

        offers.append(
            OutreachOffer(
                username=match.username,
                platform=match.platform,
                url=match.url,
                subject=subject,
                message=message,
                personalization_points=personalization_points,
            )
        )

    return offers


def build_personalization_points(match: CandidateMatch) -> list[str]:
    """Собирает персональные акценты для оффера."""
    points: list[str] = []

    if match.matched_topics:
        points.append(f"Подходят темы контента: {', '.join(match.matched_topics)}.")
    if match.matched_visual_tags:
        points.append(f"Подходит визуальная подача: {', '.join(match.matched_visual_tags)}.")
    if match.matched_tone:
        points.append(f"Подходит тон общения с аудиторией: {', '.join(match.matched_tone)}.")

    points.append(f"Платформа для контакта: {match.platform}.")
    return points


def build_offer_message(match: CandidateMatch, personalization_points: list[str]) -> str:
    """Собирает текст персонального сообщения."""
    intro = (
        f"Здравствуйте, @{match.username}! "
        "Мне очень откликнулся ваш контент и то, как вы подаете рекомендации для аудитории."
    )

    topic_part = ""
    if match.matched_topics:
        topic_part = (
            f" Особенно понравилось, что у вас органично сочетаются темы "
            f"{', '.join(match.matched_topics)}."
        )

    visual_part = ""
    if match.matched_visual_tags:
        visual_part = (
            f" Также близка ваша визуальная подача: "
            f"{', '.join(match.matched_visual_tags)}."
        )

    offer_part = (
        " Мы развиваем бренд женской одежды и сейчас ищем блогеров для бартерного сотрудничества. "
        "Будем рады предложить вам вещи на обзор или интеграцию, если такой формат вам интересен."
    )

    close_part = (
        " Если вам откликается идея, с удовольствием расскажу подробнее про бренд, подборку вещей и условия."
    )

    full_message = intro + topic_part + visual_part + offer_part + close_part

    if personalization_points:
        full_message += " Основание выбора: " + " ".join(personalization_points)

    return full_message
