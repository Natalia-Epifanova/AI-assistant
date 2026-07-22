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
)
from src.youtube_client import search_youtube_videos, youtube_items_to_json


def format_output_path(path: Path, project_root: Path) -> str:
    """Возвращает путь в коротком виде относительно корня проекта."""
    return str(path.relative_to(project_root))


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

    profile_output_label = format_output_path(profile_output, project_root)
    matches_output_label = format_output_path(matches_output, project_root)
    offers_output_label = format_output_path(offers_output, project_root)
    cleaned_output_label = format_output_path(cleaned_output, project_root)
    problem_output_label = format_output_path(problem_output, project_root)
    youtube_output_label = format_output_path(youtube_output, project_root)
    youtube_candidates_output_label = format_output_path(youtube_candidates_output, project_root)

    print("MVP-обработка завершена.")
    print()
    print("Краткий итог:")
    print(f"- Обработано блогеров: {summary['total']}")
    print(f"- Готовы к анализу: {summary['ok']}")
    print(f"- Требуют ручной проверки: {summary['needs_review']}")
    print(f"- Всего кандидатов найдено: {len(all_candidates)}")
    print(f"- Из демо-датасета: {len(demo_candidates)}")
    print(f"- Из YouTube: {len(youtube_candidates)}")
    print(f"- Подготовлено офферов: {len(offers)}")
    print()
    print("Итоговые файлы:")
    print(f"- Портрет целевого блогера: {profile_output_label}")
    print(f"- Топ кандидатов: {matches_output_label}")
    print(f"- Черновики офферов: {offers_output_label}")
    print(f"- Очищенная база: {cleaned_output_label}")
    if problem_bloggers:
        print(f"- Строки для ручной проверки: {problem_output_label}")
    print()
    print("Топ кандидатов:")
    for item in top_matches:
        print(f"- {item.username} ({item.platform}), score {item.score}")
    print()
    print("Примеры офферов:")
    for item in offers[:3]:
        print(f"- @{item.username}: {item.subject}")

    if youtube_items:
        print()
        print("YouTube-поиск выполнен.")
        print(f"- Найдено видео: {len(youtube_items)}")
        print(f"- Сырые результаты: {youtube_output_label}")
        print(f"- Преобразованные кандидаты: {youtube_candidates_output_label}")
    elif youtube_error:
        print()
        print("YouTube-поиск не был использован в этом запуске.")
        print(f"- Причина: {youtube_error}")
    else:
        print()
        print("YouTube-поиск не был использован в этом запуске.")
        print("- Причина: ключ не найден в .env")

    if problem_bloggers:
        print()
        print("Строки, требующие проверки:")
        for item in problem_bloggers:
            print(
                f"- Excel-строка {item.row_number}: "
                f"значение='{item.raw_value}', username='{item.username}', url='{item.url}'"
            )
