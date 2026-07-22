import os
from pathlib import Path

from dotenv import load_dotenv

from src.config import ENV_FILE, OUTPUTS_DIR
from src.load_bloggers import (
    get_problem_bloggers,
    load_source_bloggers,
    save_bloggers_to_json,
    summarize_source_bloggers,
)
from src.matcher import (
    build_candidates_from_youtube_items,
    load_candidate_bloggers,
    match_candidates,
)
from src.offer_generator import build_outreach_offers
from src.profile_analyzer import (
    build_blogger_features,
    build_ideal_blogger_profile,
    summarize_blogger_features,
)
from src.youtube_client import search_youtube_videos, youtube_items_to_json


def run_pipeline() -> None:
    """Запускает базовый конвейер MVP."""
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(ENV_FILE)
    youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")

    source_file = project_root / "data" / "input" / "bloggers.xlsx"
    candidate_file = project_root / "data" / "demo" / "candidate_bloggers.json"

    bloggers = load_source_bloggers(source_file)
    summary = summarize_source_bloggers(bloggers)
    problem_bloggers = get_problem_bloggers(bloggers)
    features = build_blogger_features(bloggers)
    feature_summary = summarize_blogger_features(features)
    ideal_profile = build_ideal_blogger_profile(features)

    demo_candidates = load_candidate_bloggers(candidate_file)
    youtube_items = []
    youtube_candidates = []
    youtube_error = ""

    youtube_output = OUTPUTS_DIR / "youtube_search_results.json"
    youtube_candidates_output = OUTPUTS_DIR / "youtube_candidates.json"

    if youtube_api_key:
        youtube_queries = [
            "fashion outfits women shorts",
            "wildberries clothing review shorts",
            "women style lookbook shorts",
        ]
        try:
            youtube_items = search_youtube_videos(youtube_api_key, youtube_queries, max_results=3)
            save_bloggers_to_json(youtube_items_to_json(youtube_items), youtube_output)
            youtube_candidates = build_candidates_from_youtube_items(youtube_items)
            save_bloggers_to_json(youtube_candidates, youtube_candidates_output)
        except RuntimeError as error:
            youtube_error = str(error)

    all_candidates = demo_candidates + youtube_candidates
    top_matches = match_candidates(ideal_profile, all_candidates, top_n=5)
    offers = build_outreach_offers(top_matches)

    cleaned_output = OUTPUTS_DIR / "source_bloggers_cleaned.json"
    problem_output = OUTPUTS_DIR / "source_bloggers_needs_review.json"
    features_output = OUTPUTS_DIR / "source_bloggers_features.json"
    profile_output = OUTPUTS_DIR / "ideal_blogger_profile.json"
    matches_output = OUTPUTS_DIR / "top_candidate_matches.json"
    offers_output = OUTPUTS_DIR / "outreach_offers.json"

    save_bloggers_to_json(bloggers, cleaned_output)
    save_bloggers_to_json(problem_bloggers, problem_output)
    save_bloggers_to_json(features, features_output)
    save_bloggers_to_json([ideal_profile], profile_output)
    save_bloggers_to_json(top_matches, matches_output)
    save_bloggers_to_json(offers, offers_output)

    print("Базовый каркас MVP готов.")
    print(f"Корень проекта: {project_root}")
    print(f"Ключ YouTube найден: {'да' if youtube_api_key else 'нет'}")
    print(f"Всего блогеров: {summary['total']}")
    print(f"Готовы к анализу: {summary['ok']}")
    print(f"Требуют проверки: {summary['needs_review']}")
    print(f"Очищенные данные сохранены: {cleaned_output}")
    print(f"Проблемные строки сохранены: {problem_output}")
    print(f"Признаки блогеров сохранены: {features_output}")
    print(f"Профиль базы сохранен: {profile_output}")
    print(f"Топ кандидатов сохранен: {matches_output}")
    print(f"Черновики офферов сохранены: {offers_output}")
    print("Краткая сводка по базе:")
    print(f"- Средняя длина username: {feature_summary['avg_username_length']}")
    print(f"- Username с цифрами: {feature_summary['with_digits']}")
    print(f"- Username с нижним подчеркиванием: {feature_summary['with_underscore']}")
    print(f"- Username с точкой: {feature_summary['with_dot']}")
    print(f"- Частые ключевые слова: {feature_summary['top_keywords']}")
    print("Черновой портрет базы:")
    for note in ideal_profile.notes:
        print(f"- {note}")

    print("Источники кандидатов:")
    print(f"- Демо-кандидатов: {len(demo_candidates)}")
    print(f"- YouTube-кандидатов: {len(youtube_candidates)}")

    print("Топ кандидатов для следующего шага:")
    for item in top_matches:
        print(f"- {item.username} ({item.platform}) - score {item.score}")

    print("Подготовлены персональные офферы:")
    for item in offers[:3]:
        print(f"- @{item.username}: {item.subject}")

    if youtube_items:
        print(f"Результаты YouTube сохранены: {youtube_output}")
        print(f"Кандидаты YouTube сохранены: {youtube_candidates_output}")
        print(f"Найдено видео YouTube: {len(youtube_items)}")
        for item in youtube_candidates[:3]:
            print(f"- YouTube-кандидат: {item.username}")
    elif youtube_error:
        print(f"Не удалось получить YouTube-результаты: {youtube_error}")
    else:
        print("YouTube-поиск пропущен: ключ не найден в .env")

    if problem_bloggers:
        print("Строки, требующие проверки:")
        for item in problem_bloggers:
            print(
                f"- Excel-строка {item.row_number}: "
                f"значение='{item.raw_value}', username='{item.username}', url='{item.url}'"
            )
