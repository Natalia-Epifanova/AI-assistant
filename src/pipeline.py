from pathlib import Path

from src.config import OUTPUTS_DIR
from src.load_bloggers import (
    get_problem_bloggers,
    load_source_bloggers,
    save_bloggers_to_json,
    summarize_source_bloggers,
)
from src.profile_analyzer import build_blogger_features, summarize_blogger_features


def run_pipeline() -> None:
    """Запускает базовый конвейер MVP."""
    project_root = Path(__file__).resolve().parent.parent
    source_file = project_root / "data" / "input" / "bloggers.xlsx"
    bloggers = load_source_bloggers(source_file)
    summary = summarize_source_bloggers(bloggers)
    problem_bloggers = get_problem_bloggers(bloggers)
    features = build_blogger_features(bloggers)
    feature_summary = summarize_blogger_features(features)

    cleaned_output = OUTPUTS_DIR / "source_bloggers_cleaned.json"
    problem_output = OUTPUTS_DIR / "source_bloggers_needs_review.json"
    features_output = OUTPUTS_DIR / "source_bloggers_features.json"

    save_bloggers_to_json(bloggers, cleaned_output)
    save_bloggers_to_json(problem_bloggers, problem_output)
    save_bloggers_to_json(features, features_output)

    print("Базовый каркас MVP готов.")
    print(f"Корень проекта: {project_root}")
    print(f"Всего блогеров: {summary['total']}")
    print(f"Готовы к анализу: {summary['ok']}")
    print(f"Требуют проверки: {summary['needs_review']}")
    print(f"Очищенные данные сохранены: {cleaned_output}")
    print(f"Проблемные строки сохранены: {problem_output}")
    print(f"Признаки блогеров сохранены: {features_output}")
    print("Краткая сводка по базе:")
    print(f"- Средняя длина username: {feature_summary['avg_username_length']}")
    print(f"- Username с цифрами: {feature_summary['with_digits']}")
    print(f"- Username с нижним подчеркиванием: {feature_summary['with_underscore']}")
    print(f"- Username с точкой: {feature_summary['with_dot']}")
    print(f"- Частые ключевые слова: {feature_summary['top_keywords']}")

    if problem_bloggers:
        print("Строки, требующие проверки:")
        for item in problem_bloggers:
            print(
                f"- Excel-строка {item.row_number}: "
                f"значение='{item.raw_value}', username='{item.username}', url='{item.url}'"
            )
