"""Small adapter for AnimaDex's public character search JSON endpoint."""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


BASE_URL = "https://animadex.net"


@dataclass(frozen=True)
class Character:
    slug: str
    name: str
    copyright_name: str
    trigger: str
    tags: tuple[str, ...]
    thumb_url: str


@dataclass(frozen=True)
class SearchPage:
    results: tuple[Character, ...]
    page: int
    pages: int
    total: int


class AnimaDexError(Exception):
    """The remote catalogue could not be read."""


def _string(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def parse_search_page(data: object) -> SearchPage:
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise AnimaDexError("AnimaDex returned an unexpected search response.")

    characters = []
    for row in data["results"]:
        if not isinstance(row, dict):
            continue
        slug = _string(row.get("slug"))
        if not slug:
            continue
        raw_tags = row.get("tags")
        tags = tuple(_string(tag) for tag in raw_tags if _string(tag)) if isinstance(raw_tags, list) else ()
        thumb = _string(row.get("thumb_url"))
        characters.append(Character(
            slug=slug,
            name=_string(row.get("name")) or slug.replace("_", " "),
            copyright_name=_string(row.get("copyright_name")),
            trigger=_string(row.get("trigger")),
            tags=tags,
            thumb_url=urljoin(BASE_URL, thumb) if thumb.startswith("/") else thumb,
        ))

    try:
        page = max(1, int(data.get("page", 1)))
        pages = max(0, int(data.get("pages", 0)))
        total = max(0, int(data.get("total", 0)))
    except (TypeError, ValueError) as exc:
        raise AnimaDexError("AnimaDex returned invalid pagination data.") from exc
    return SearchPage(tuple(characters), page, pages, total)


def search_characters(query: str = "", page: int = 1) -> SearchPage:
    params = urlencode({"q": query.strip(), "page": max(1, int(page))})
    request = Request(
        f"{BASE_URL}/api/characters/search?{params}",
        headers={"Accept": "application/json", "User-Agent": "neoforge-animadex/0.1"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            payload = response.read(2_000_001)
        if len(payload) > 2_000_000:
            raise AnimaDexError("AnimaDex response was unexpectedly large.")
        return parse_search_page(json.loads(payload))
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise AnimaDexError(f"Could not reach AnimaDex: {exc}") from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AnimaDexError("AnimaDex returned unreadable data.") from exc
