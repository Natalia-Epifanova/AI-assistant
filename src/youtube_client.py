from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from src.models import YouTubeSearchItem


def search_youtube_videos(api_key: str, queries: list[str], max_results: int = 3) -> list[YouTubeSearchItem]:
    """Ищет видео на YouTube по списку запросов."""
    items: list[YouTubeSearchItem] = []

    for query in queries:
        payload = fetch_youtube_search_payload(api_key, query, max_results)

        for raw_item in payload.get("items", []):
            video_id = raw_item.get("id", {}).get("videoId")
            snippet = raw_item.get("snippet", {})

            if not video_id:
                continue

            items.append(
                YouTubeSearchItem(
                    query=query,
                    video_id=video_id,
                    title=snippet.get("title", ""),
                    channel_title=snippet.get("channelTitle", ""),
                    description=snippet.get("description", ""),
                    published_at=snippet.get("publishedAt", ""),
                    video_url=f"https://www.youtube.com/watch?v={video_id}",
                )
            )

    return items


def fetch_youtube_search_payload(api_key: str, query: str, max_results: int) -> dict[str, Any]:
    """Выполняет запрос к YouTube Data API."""
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": str(max_results),
        "order": "relevance",
        "videoDuration": "short",
        "key": api_key,
    }
    url = "https://www.googleapis.com/youtube/v3/search?" + urlencode(params)

    try:
        with urlopen(url, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ошибка YouTube API: {error.code}. {message}") from error
    except URLError as error:
        raise RuntimeError(f"Сетевая ошибка YouTube API: {error.reason}") from error


def youtube_items_to_json(items: list[YouTubeSearchItem]) -> list[dict[str, Any]]:
    """Преобразует результаты YouTube в JSON-совместимый вид."""
    return [asdict(item) for item in items]
