from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class SourceBlogger:
    """Строка блогера из исходной таблицы."""

    row_number: int
    source_label: Optional[str]
    raw_value: str
    url: Optional[str]
    username: Optional[str]
    status: str
