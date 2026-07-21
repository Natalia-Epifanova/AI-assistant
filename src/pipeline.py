from pathlib import Path


def run_pipeline() -> None:
    """Entry point for the MVP pipeline."""
    project_root = Path(__file__).resolve().parent.parent
    print("AI assistant MVP scaffold is ready.")
    print(f"Project root: {project_root}")
