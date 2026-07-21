from pathlib import Path

from src.load_bloggers import load_source_bloggers, summarize_source_bloggers


def run_pipeline() -> None:
    """Запускает базовый конвейер MVP."""
    project_root = Path(__file__).resolve().parent.parent
    source_file = project_root / "data" / "input" / "bloggers.xlsx"
    bloggers = load_source_bloggers(source_file)
    summary = summarize_source_bloggers(bloggers)

    print("Базовый каркас MVP готов.")
    print(f"Корень проекта: {project_root}")
    print(f"Всего блогеров: {summary['total']}")
    print(f"Готовы к анализу: {summary['ok']}")
    print(f"Требуют проверки: {summary['needs_review']}")
